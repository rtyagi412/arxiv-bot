# Plan 001: Local FastAPI and PostgreSQL Health Check

References: `docs/features/001-api-postgres/intent.md` (accepted), `spec.md` (header: "accepted", treated as approved on re-run of /generate-plan; no open [BLOCKER]).
This content is saved to `docs/features/001-api-postgres/plan.md` after plan approval.

## 1. Overview

Add `GET /health` to a host-run FastAPI app. It checks the API (always ok) and PostgreSQL (real `SELECT 1` over a fresh psycopg v3 async connection with timeout) separately, returns both plus an overall status, 200 when all ok, 503 when degraded. PostgreSQL runs via Docker Compose, bound to 127.0.0.1.
Scope: FR-1..FR-14 only. No migrations, tables, CRUD, auth, API containerization.

Repo state inspected: `src/app/{__init__,config}.py` (Settings, prefix `ARXIV_BOT_`, `get_settings` lru_cache), `tests/test_config.py`, ruff (E,F,I,UP,B,SIM; line 100), pytest (`pythonpath=src`), `.gitignore` already ignores `.env`. Installed: fastapi 0.142.4, uvicorn 0.54.0, psycopg 3.3.6, httpx. Docker 29.5 + Compose v5 present. Not installed: pytest-asyncio (not needed, see tests). No `docker-compose.yml`, `.env.example`, `conftest.py`, `main.py` yet.

## 2. Files to change

Modify:
- `src/app/config.py`: add `db_host`, `db_port`, `db_user`, `db_password: SecretStr`, `db_name`, `db_connect_timeout_seconds` (FR-3, FR-7, C-5).
- `tests/test_config.py`: `test_defaults` builds `Settings(_env_file=None)`, which will now fail on required fields. Update it to supply DB env vars via monkeypatch and add a missing-setting test. (Deviation note: spec doesn't mention this, but it follows from C-5.)
- `README.md`: Compose up/down, run command, test commands, `.env` setup (FR-2, docs NFR).
- `.gitignore`: no change needed (`.env` already ignored).

Create:
- `docker-compose.yml`: `postgres` service, pinned image, env-driven creds, named volume, `127.0.0.1:${ARXIV_BOT_DB_PORT}:5432`, `pg_isready` healthcheck (FR-1, C-7).
- `.env.example`: placeholders only (FR-14).
- `src/app/db.py`: `async check_database(settings) -> bool` (FR-6, 7, 8, 13).
- `src/app/health.py`: router, response model, pure `aggregate_status()`, handler (FR-4, 5, 9, 10, 11, 12).
- `src/app/main.py`: `app = FastAPI()`, include router; settings loaded at import so missing config is a hard stop (FR-2, C-5).
- `tests/conftest.py`: `integration` marker handling, Compose helpers (start/stop/wait), env fixture.
- `tests/test_health.py`, `tests/test_db.py`, `tests/test_startup.py`, `tests/test_repo_hygiene.py`.
- `pyproject.toml`: register the `integration` marker and set `addopts = ["-m", "not integration"]` so the default `uv run pytest` is Docker-free (deps already installed).

## 3. Implementation steps (each small and verifiable)

1. **Config** (FR-3, FR-7): extend `Settings`; required fields have no defaults; defaults host 127.0.0.1, port 5432 (see Q1), timeout 2. Fix `test_config.py`. Verify: `uv run pytest tests/test_config.py`.
2. **Compose + env template** (FR-1, FR-14): write `docker-compose.yml`, `.env.example`. Compose requires vars with `${VAR:?}` so no hard-coded creds. Verify: `docker compose config`, `docker compose up -d`, `docker compose ps` shows healthy.
3. **DB check** (FR-6, 7, 8, 13): `AsyncConnection.connect(..., connect_timeout=N)` wrapped in `asyncio.timeout(N)`; `async with` so it always closes; `except Exception` returns False; log one generic line (`"database health check failed"`) with no exception text and no `exc_info`. Connect via keyword args (host, port, user, password, dbname), never a URL. Verify: T-2.
4. **Health route** (FR-4, 5, 9, 10, 11): `aggregate_status(services) -> "ok"|"degraded"` pure function; handler awaits `check_database` fresh each call (FR-12), sets 200/503 via `JSONResponse` or response param; `Literal["ok","degraded"]` response model. Verify: T-5, T-1.
5. **App entry** (FR-2, 3): `main.py`. Run command: `uv run uvicorn app.main:app --host 127.0.0.1 --loop asyncio:SelectorEventLoop` (C-2 and C-4). Verify: app starts with DB stopped (T-8).
6. **Tests** (all FR): see section 6.
7. **README** + final full run: lint, format check, full tests, record commands and results.

Dependencies: 1 before 3, 4, 5; 2 before integration tests; 3 before 4; 4 before 5.

## 4. Architecture decisions

- **Async psycopg on Windows (C-2, verified):** uvicorn 0.54 uses `ProactorEventLoop` on win32 (`uvicorn/loops/asyncio.py`), which psycopg async rejects. Chosen: documented run flag `--loop asyncio:SelectorEventLoop` (uvicorn accepts a custom import string, `config.py:get_loop_factory`). Rejected: setting the global event-loop policy in app code (deprecated in newer Python, hidden side effect); switching to sync psycopg in a thread (deviates from the spec's approved async design). Risk: someone runs bare `uvicorn app.main:app` on Windows; then the DB check returns degraded forever with a misleading 503. Mitigation: README note documents the flag and the symptom; T-1 catches it. No startup guard (Q2 decision).
- **Tests on Windows:** starlette `TestClient` runs its own loop (Proactor), which breaks psycopg async. Use `httpx.AsyncClient(transport=ASGITransport(app))` inside `asyncio.run(..., loop_factory=asyncio.SelectorEventLoop)` helper, no pytest-asyncio dependency. Rejected: adding pytest-asyncio (new dependency not approved; spec says no new requirements).
- **Connection per request, no pool** (C-3) as the spec says. Rejected: pool (spec explicitly excludes).
- **Settings loaded in `main.py` at import** so missing `DB_USER/PASSWORD/NAME` stops startup with non-zero exit (C-5). Pydantic's missing-field error lists names, not values.
- **Compose:** `postgres:17` pinned (Q1), named volume, `pg_isready` healthcheck so tests can wait deterministically. Healthcheck is a Compose-only detail; the API check is still a real `SELECT 1` (not a container-running check).
- **Integration tests drive real Docker** via `subprocess` calling `docker compose stop/start postgres`. Rejected: mocks for connectivity (forbidden by test-strategy skill). Blackhole test (T-7) uses a non-routable address (e.g. `10.255.255.1`) with timeout set to 1 s.

## 5. Risks

- **Most risky step: step 5/6, event loop + psycopg on Windows.** Mitigate by proving T-1 first with the exact run command before writing the other tests.
- Port 5432 may clash with a local PostgreSQL: default host port stays configurable via `ARXIV_BOT_DB_PORT` (shared by Compose and the app), see Q1.
- Container "healthy" but not accepting from the host yet: test helper polls with bounded retry against `/health` itself or `pg_isready`.
- Docker-dependent tests are slow or unavailable in CI: marked `integration`; unit suite runs without Docker (C-8).
- Security: no secrets committed; `.env` ignored; port bound to 127.0.0.1; password `SecretStr`; error text never logged or returned (T-6 asserts body and captured logs, including psycopg's messages that can name the host/user); documented `--host 127.0.0.1` (C-4).
- Compatibility: renamed package `app` already in place; README already references `src/app/config.py`.
- Stray `intent` item (C-9): not found in the repo root; nothing to do.

## 6. Test plan (FR to test)

Fast/unit (no Docker): T-5 aggregation; config tests; T-9 hygiene (`git check-ignore .env`, `.env.example` has no real values); T-10 missing setting.
Integration (`-m integration`, needs Docker, DB up): T-1, T-2, T-6, T-7. Lifecycle (stop/start Compose): T-3, T-4, T-8.

| FR | Test |
|----|------|
| FR-1 | T-8 `docker compose up -d` reaches healthy; no local PG used |
| FR-2 | T-8 app starts with DB stopped; T-1 |
| FR-3 | config test (env override of DB settings); T-1 connects through published port |
| FR-4 | T-1, T-3 (both keys in one body) |
| FR-5 | T-1, T-3 (`api: ok` in both states) |
| FR-6 | T-2 (live ok, refused port degraded) |
| FR-7 | T-7 (returns within timeout + margin) |
| FR-8 | T-3, T-6, T-7 (no unhandled exception, response served) |
| FR-9 | T-5 |
| FR-10 | T-1 exact body + 200 |
| FR-11 | T-3 exact body + 503 |
| FR-12 | T-4 recovery without restarting the app |
| FR-13 | T-6 (wrong password; body and logs have no password/URL/trace/DB text) |
| FR-14 | T-9 |

Success criteria 1 to 7 map via spec section 9, unchanged.

## 7. Verification

Commands (PowerShell, repo root):
1. `copy .env.example .env` and fill local dummy values (not committed).
2. `docker compose up -d`; `docker compose ps` -> postgres healthy.
3. `uv run uvicorn app.main:app --host 127.0.0.1 --loop asyncio:SelectorEventLoop`; `curl -i http://127.0.0.1:8000/health` -> 200 exact FR-10 body.
4. `docker compose stop postgres`; curl -> 503 exact FR-11 body, within ~2 s.
5. `docker compose start postgres`; curl (retry) -> 200, no app restart.
6. `uv run ruff check`, `uv run ruff format --check` -> clean.
7. `uv run pytest` (unit) and `uv run pytest -m integration` -> all pass, exit 0.
8. Start app with a required var unset -> non-zero exit, no secret in output.

Acceptance: every FR in the section 6 table has a passing test; success criteria 1 to 7 demonstrated; commands and results reported in the completion report; any deviation reported.

## 8. Open questions

All resolved by the user:

1. **Q1 (spec Q1/C-7): Resolved.** `postgres:17`, default host port 5432, overridable via `ARXIV_BOT_DB_PORT` (for example 5433 if a local PostgreSQL is installed).
2. **Q2: Resolved.** No startup guard. The Windows event-loop requirement (`--loop asyncio:SelectorEventLoop`) is documented as a note in the README only, including the symptom (permanent 503 if the flag is omitted).
3. **Q3: Resolved (recommended approach).** Integration tests are excluded from the default run via `addopts = ["-m", "not integration"]` in `pyproject.toml`. Run them explicitly with `uv run pytest -m integration`.

## Deviations from spec.md

- `tests/test_config.py` must change (required settings break the existing default test).
- Spec header says "awaiting approval"; proceeding on your re-run, please confirm at approval.
- Spec C-7/Q1 is now resolved by the user (`postgres:17`, port 5432 with override); `spec.md` section 12 should be updated to match once the plan is approved.
