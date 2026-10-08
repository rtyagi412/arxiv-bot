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
uv run pytest              # run tests
```

## Configuration

Settings are read from environment variables prefixed `ARXIV_BOT_`, or from a `.env` file
(see `src/arxiv_bot/config.py`).
