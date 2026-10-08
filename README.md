# arxiv-bot

## Setup

```
uv sync
uv run pre-commit install
```

## Commands

```
uv run ruff check          # lint
uv run ruff check --fix    # lint and auto-fix
uv run ruff format         # format
uv run pytest              # unit tests (no Docker needed)
uv run pytest -m integration   # integration tests (need Docker; start their own throwaway PostgreSQL)
```

## Configuration

Settings are read from environment variables prefixed `ARXIV_BOT_`, or from a `.env` file
(see `src/app/config.py`).

```
copy .env.example .env     # then replace the change_me_* placeholders; never commit .env
```

`ARXIV_BOT_DB_USER`, `ARXIV_BOT_DB_PASSWORD` and `ARXIV_BOT_DB_NAME` are required. The app
refuses to start without them. `ARXIV_BOT_DB_PORT` (default 5436) is the host port, used by both
the app and Docker Compose (the container always listens on 5432 internally). Change it if 5436
is already taken.

The database volume keeps the credentials from the first `docker compose up`. After changing
`ARXIV_BOT_DB_USER`, `ARXIV_BOT_DB_PASSWORD` or `ARXIV_BOT_DB_NAME`, run `docker compose down -v`
(this deletes the data) and start again, otherwise `/health` stays degraded.

## Run locally

PostgreSQL runs in Docker Compose (published on `127.0.0.1` only). The API runs on the host.

```
docker compose up -d --wait     # start PostgreSQL
uv run uvicorn app.main:app --app-dir src --host 127.0.0.1 --loop asyncio:SelectorEventLoop
curl -i http://127.0.0.1:8000/health
docker compose stop postgres    # /health now returns 503 (degraded)
docker compose start postgres   # /health recovers to 200 without restarting the app
docker compose down             # stop and remove the container (add -v to delete the data volume)
```

`GET /health` returns `{"status":"ok","services":{"api":"ok","database":"ok"}}` with HTTP 200,
or `{"status":"degraded","services":{"api":"ok","database":"degraded"}}` with HTTP 503 when
PostgreSQL is unavailable.

**Windows:** keep `--loop asyncio:SelectorEventLoop`. psycopg's async API does not work with
uvicorn's default Windows event loop, so without the flag `/health` reports the database as
degraded (permanent 503) even when PostgreSQL is up.
