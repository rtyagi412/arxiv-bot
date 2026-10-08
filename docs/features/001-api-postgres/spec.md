# Spec 001: Local FastAPI and PostgreSQL Health Check

Source: [intent.md](intent.md) (status: accepted). Spec status: accepted.

## 1. Scope

Add a locally run FastAPI app that exposes `GET /health`. The endpoint reports API and PostgreSQL
health independently, plus an overall status. PostgreSQL runs in Docker Compose. Everything listed
as out of scope in intent.md stays out of scope: no migrations, tables, CRUD, auth, API
containerization, or production config.

## 2. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-1 | `docker-compose.yml` defines a PostgreSQL service. `docker compose up -d` starts it with no local PostgreSQL install. |
| FR-2 | The FastAPI app runs on the host (not in Docker) via a documented command and starts without PostgreSQL running. |
| FR-3 | The app reads DB connection settings from environment variables (`ARXIV_BOT_` prefix, via the existing `Settings`) and connects to the containerized PostgreSQL through a host-published port. |
| FR-4 | `GET /health` checks the API and the database as two separate checks. |
| FR-5 | The API check reports `"ok"` whenever the handler runs. |
| FR-6 | The database check opens a real connection and runs a trivial query (`SELECT 1`). It reports `"ok"` on success and `"degraded"` on any failure or timeout. |
| FR-7 | The database check is bounded by a configurable timeout. It must not hang the response. |
| FR-8 | A database failure never prevents the route from responding, and never raises an unhandled exception. |
| FR-9 | Overall `status` is `"ok"` only if every service is `"ok"`. Otherwise it is `"degraded"`. |
| FR-10 | All healthy: HTTP 200, body `{"status":"ok","services":{"api":"ok","database":"ok"}}`. |
| FR-11 | Database unavailable: HTTP 503, body `{"status":"degraded","services":{"api":"ok","database":"degraded"}}`. |
| FR-12 | Each request performs a fresh check, so the endpoint recovers to FR-10 once PostgreSQL is back, with no app restart. |
| FR-13 | Responses and logs never include credentials, connection URLs, stack traces, or database error text. |
| FR-14 | Provide a `.env.example` with placeholder values only. Real `.env` is git-ignored. |

## 3. Non-functional requirements

- **Security:** no secrets in the repo. Compose publishes the DB port on `127.0.0.1` only. The database password is `SecretStr` and is never logged.
- **Reliability:** the health check has a default timeout of about 2 s, so the worst-case response is bounded.
- **Simplicity:** no ORM, no pool, no migrations. One short-lived connection per check (see C-3).
- **Maintainability:** new application code under `src/app/`, lint-clean under the existing ruff config, tests under `tests/`.
- **Docs:** README documents start, stop, run, and test commands.

## 4. Architecture and components

```
Developer ── GET /health ──> FastAPI (host, uvicorn)
                               ├─ api check      (in-process, always "ok")
                               └─ database check ──TCP 127.0.0.1:<port>──> PostgreSQL (Docker Compose)
```

| Component | Responsibility |
|-----------|----------------|
| `src/app/config.py` (existing, moved from `src/arxiv_bot/`; extend) | Add DB settings: host, port, user, password (`SecretStr`), db name, connect timeout. Required DB settings are validated at startup (see C-5). |
| `src/app/db.py` (new) | `async check_database(settings) -> bool`: `psycopg.AsyncConnection.connect` with timeout, run `SELECT 1`, catch all exceptions, close. |
| `src/app/health.py` (new) | Router with an `async def` handler for `GET /health`, response model, overall-status aggregation. |
| `src/app/main.py` (new) | FastAPI app, includes the health router. Run with `uvicorn app.main:app`. |
| `docker-compose.yml` (new) | `postgres` service, env-driven credentials, named volume, `127.0.0.1` port mapping. |
| `.env.example` (new) | Placeholder variables. |

Networking: the host process reaches the container through the published port on `localhost`. The
Compose-internal hostname does not apply, because FastAPI runs outside Docker.

## 5. API contract

`GET /health`: no input, no authentication (public by design for this feature).

| Condition | Status | Body |
|-----------|--------|------|
| API and DB ok | 200 | `{"status":"ok","services":{"api":"ok","database":"ok"}}` |
| DB down/timeout/auth failure | 503 | `{"status":"degraded","services":{"api":"ok","database":"degraded"}}` |

Schema: `status` and each `services.*` value are one of `"ok"` or `"degraded"`. The body keys are
identical in both cases. Only the API check always reports `"ok"` (FR-5). If the handler itself
fails with an unexpected error, FastAPI returns its standard 500. This is not a documented health state.

## 6. Data models and configuration

No database tables or persistence models.

Settings (env prefix `ARXIV_BOT_`; names are proposals for plan review):

| Setting | Default | Notes |
|---------|---------|-------|
| `DB_HOST` | `127.0.0.1` | |
| `DB_PORT` | `5432` | Must match the Compose published port. |
| `DB_USER` | none (required) | |
| `DB_PASSWORD` | none (required) | `SecretStr`, supplied via `.env`/env only. |
| `DB_NAME` | none (required) | |
| `DB_CONNECT_TIMEOUT_SECONDS` | `2` | Bounds FR-7. |

Compose reads the same credentials from the environment/`.env`, with no hard-coded values in the file.

## 7. Error handling and edge cases

- Container stopped, port closed, or connection refused: DB `"degraded"`, HTTP 503.
- DB host unreachable or connect hangs: timeout fires, then `"degraded"`.
- Wrong credentials or unknown database: `"degraded"`. The cause is not exposed; only a generic, secret-free server-side log line is allowed (FR-13).
- DB up but still starting (not accepting connections): `"degraded"`, then recovers on a later request.
- Missing required DB settings: the app refuses to start (hard stop, C-5). Add a test (T-10): starting with a missing setting fails with a non-zero exit and no secret in the output.
- Concurrent requests: each makes an independent connection. There is no shared state.
- DB restart mid-query: the check is treated as a failure for that request only.

## 8. Test strategy

Unit tests use no mocked database connection as proof of connectivity. Per test-strategy, mocks
may not stand in for the real connection.

| ID | Level | Test |
|----|-------|------|
| T-1 | Integration | Healthy: with Compose PostgreSQL up, `GET /health` is 200 with the exact FR-10 body. |
| T-2 | Integration | `check_database` against the live DB returns ok; against an unused local port (real refusal) returns degraded. |
| T-3 | Integration/E2E | Stop the PostgreSQL service: `GET /health` is 503 with the exact FR-11 body. |
| T-4 | Integration/E2E | Start the service again, poll with a bounded retry: 200 with both `"ok"`, with no app restart. |
| T-5 | Unit | Aggregation: statuses `ok`+`ok` give overall `ok`; any `degraded` gives overall `degraded` (pure function). |
| T-6 | Integration | Wrong password: 503 degraded, and the body and captured logs contain no password or connection URL. |
| T-7 | Integration | Unroutable host or blackhole address: response returns within timeout plus a small margin. |
| T-8 | Smoke | `docker compose up -d` brings the service to healthy/accepting connections. App starts with the DB stopped. |
| T-9 | Static | `.env` is git-ignored. `.env.example` has placeholders only. `ruff check` is clean. |

Tests that stop or start Compose are marked (for example `integration`) and need Docker.
`uv run pytest` exits non-zero on any failure. Exact commands and results are recorded at
completion.

## 9. Traceability

| Success criterion | Functional requirements | Verification |
|-------------------|------------------------|--------------|
| 1. `docker compose up -d` starts PostgreSQL | FR-1, FR-14 | T-8 |
| 2. FastAPI starts locally | FR-2, FR-3 | T-8, T-1 |
| 3. Healthy gives 200 and body | FR-4, FR-5, FR-6, FR-9, FR-10 | T-1, T-2, T-5 |
| 4. PostgreSQL stopped gives 503 and body | FR-6, FR-7, FR-8, FR-9, FR-11, FR-13 | T-3, T-6, T-7 |
| 5. Restart restores 200 | FR-12 | T-4 |
| 6. Independent statuses in one response | FR-4, FR-5, FR-6, FR-9 | T-1, T-3, T-5 |
| 7. No local PostgreSQL install needed | FR-1 | T-8 |

## 10. Dependencies

- **Earlier work:** the project scaffold (uv, ruff, pytest, pre-commit, `pydantic-settings` `Settings`). Intent 001 is the first feature.
- **New packages (approved and installed via uv):** `fastapi`, `uvicorn`, `psycopg[binary]` (v3, async use), and `httpx` (dev, test client).
- **External:** Docker with Compose on the developer machine.
- **Future intents:** later DB-backed features (migrations, models, CRUD) will reuse the connection settings. This spec deliberately does not create pooling or session abstractions for them.

## 11. Areas of concern

**[BLOCKER]**

None open. B-1 (deleted `src/arxiv_bot/__init__.py` and `config.py`) is resolved: both were restored from HEAD.

**[WATCH]**

- **C-1: Resolved.** Driver is `psycopg` v3, used asynchronously.
- **C-2: Resolved.** The handler is `async def` with `psycopg.AsyncConnection`, so the event loop is not blocked. On Windows, psycopg async needs the selector event loop (not the default Proactor). Check how `uvicorn` starts at plan time.
- **C-10: Resolved.** All code lives in `src/app/`. `config.py` and `__init__.py` were moved from `src/arxiv_bot/` (now removed), and `tests/test_config.py` and the README reference were updated. The distribution name in `pyproject.toml` remains `arxiv-bot`.
- **C-3: Connection per request, no pool.** Simple and recovers trivially (FR-12), but a public unauthenticated endpoint can trigger a DB connection per call. Acceptable for local dev; revisit for production, which is out of scope.
- **C-4: Unauthenticated endpoint.** Intentional per intent.md (auth is out of scope). It exposes only coarse statuses. It must remain bound to localhost in dev. Recommendation: document the default `uvicorn` host as `127.0.0.1`.
- **C-5: Resolved.** Required DB settings (`DB_USER`, `DB_PASSWORD`, `DB_NAME`) have no defaults. If any is missing the app fails to start (hard stop) with a clear, secret-free error. This is distinct from DB unavailability, which still yields a served 503 response.
- **C-6: Overall-status semantics are only defined for two states.** Intent defines `ok` and `degraded` only. The spec uses exactly those and adds no "down"/"unhealthy" state. It also treats API as always `"ok"` (FR-5), because the API has no independent failure signal in scope.
- **C-7: Compose defaults.** Postgres image tag/version, volume persistence, and whether to add a Compose `healthcheck` are not specified in intent.md. This spec assumes a pinned tag and a named volume. These are implementation details to confirm at plan time. Data persistence isn't required by the intent, since there is no data.
- **C-8: Docker-dependent tests.** T-3/T-4 manipulate containers, so they cannot run in environments without Docker and will be slower. Recommendation: mark them as integration tests and run them separately from a fast unit suite.
- **C-9: Stray `intent` entry at repo root.** An item named `intent` appears in the repo root listing. It is unrelated to this feature, so I did not inspect it. It is listed only for awareness.

## 12. Open questions

1. C-7: preferred PostgreSQL version and port (default 5432, which may clash with a local install)?

Resolved: deleted files restored; driver is psycopg v3 async; dependencies approved and installed; all code in `src/app/` (C-10); missing DB settings cause a hard stop at startup (C-5).
