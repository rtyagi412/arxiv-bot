# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python FastAPI backend using PostgreSQL. FastAPI runs on the host machine; PostgreSQL runs in
Docker Compose. The project follows the AI-Native SDLC.

## Commands

Requires `uv` and Docker. Copy `.env.example` to `.env` first (never commit `.env`).

```
uv sync                                  # install dependencies
docker compose up -d --wait              # start PostgreSQL, wait until healthy
uv run uvicorn app.main:app --app-dir src --host 127.0.0.1 --loop asyncio:SelectorEventLoop
uv run pytest                            # unit tests, no Docker needed
uv run pytest -m integration             # Docker integration tests
uv run pytest tests/test_health.py::test_aggregate_all_ok   # single test
uv run ruff check
uv run ruff format --check
```

## Architecture and gotchas

Code lives in `src/app/` (the distribution name in `pyproject.toml` is still `arxiv-bot`; the old
`arxiv_bot` package is gone). pytest finds it through `pythonpath = ["src"]`, but running uvicorn
needs `--app-dir src`.

- **Health check** (`health.py`, `db.py`): `GET /health` checks the API and the database
  separately and returns both plus an overall status. Healthy is 200; any degraded service is 503.
  The database check opens a fresh psycopg async connection per request (no pool) and runs
  `SELECT 1` bounded by `asyncio.timeout`. Exception text is never logged or returned, because
  psycopg errors can contain the host, user or other connection details.
- **Windows event loop**: psycopg's async API does not work on the default Windows (Proactor)
  loop. Always run uvicorn with `--loop asyncio:SelectorEventLoop`. Tests use `run_async` in
  `tests/conftest.py` (`asyncio.run(..., loop_factory=asyncio.SelectorEventLoop)`) instead of
  Starlette's `TestClient`. Without this, `/health` is a permanent, misleading 503.
- **Config** (`config.py`): settings come from `ARXIV_BOT_`-prefixed env vars or `.env`. `main.py`
  loads settings at import, so a missing `DB_USER`, `DB_PASSWORD` or `DB_NAME` stops startup on
  purpose. This is distinct from the database being unavailable, which is served as a 503.
- **Ports**: `ARXIV_BOT_DB_PORT` (default 5436) is the host port, shared by the app and Compose.
  The container always listens on 5432 (`docker-compose.yml` maps `host:5432`). Compose binds
  to `127.0.0.1` only.
- **Compose volume**: the named volume keeps the credentials from the first `up`. After changing
  DB credentials, run `docker compose down -v`, otherwise `/health` stays degraded.
- **Integration tests** (`-m integration`, excluded from the default run): they start their own
  throwaway Compose project (`arxiv-bot-test`) with a random password and free port, and tear
  down the volume afterwards. Mocks are not accepted as proof of database connectivity.
  `tests/test_lifecycle.py` runs the exact documented uvicorn command as a subprocess.

## Development Workflow

Follow this sequence: Plan → Design → Build → Test → Deploy → Maintain

Each feature lives in `docs/features/NNN-feature-name/` and contains:
- intent.md — problem, outcome, constraints, success criteria
- spec.md — requirements and technical design
- plan.md — implementation plan and verification steps

Slash commands in `.claude/commands/` (`generate-spec`, `generate-plan`, `implement-plan`) and the
`verifier` and `code-reviewer` agents in `.claude/agents/` implement this workflow.

### Rules

1. Read intent.md and spec.md before planning.
2. Use Claude Code plan mode before implementation.
3. Do not implement until plan.md is approved.
4. Map implementation tasks to functional requirements.
5. Run relevant tests before reporting completion.
6. Report deviations from spec.md or plan.md.
7. Never silently introduce new requirements.

### Hooks

PreToolUse hooks in `.claude/hooks/` run on Write and Edit and are written in pure bash (no `jq`):
- `protect-artifacts.sh` blocks edits to approved `intent.md`, `spec.md` and `plan.md`. For an
  intentional revision, restart Claude Code with `CLAUDE_ALLOW_ARTIFACT_EDITS=1`.
- `protect-secrets.sh` blocks writes to `.env`, key files and credential files. `.env.example` is
  allowed. Create `.env` yourself (for example `copy .env.example .env`).

## Skills

Use relevant project skills from `.claude/skills/`: api-design, database-design, test-strategy,
secure-api-review.

## Security and Verification

- Do not expose internal database errors in API responses.
- Test successful API responses, dependency failure scenarios, and recovery after dependencies
  become available.
- Report commands executed and their results.

## Project Conventions

- Keep changes scoped to the accepted feature.
- Prefer simple solutions over unnecessary abstractions.
- Keep documentation synchronized with implementation.
