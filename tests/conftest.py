import asyncio
import os
import secrets
import socket
import subprocess
import time
from collections.abc import Callable, Coroutine, Iterator
from pathlib import Path
from typing import Any

import pytest

from app.config import Settings

ROOT = Path(__file__).resolve().parent.parent
PROJECT = "arxiv-bot-test"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_async[T](coro: Coroutine[Any, Any, T]) -> T:
    # psycopg's async API cannot use the Windows default (Proactor) event loop.
    return asyncio.run(coro, loop_factory=asyncio.SelectorEventLoop)


class Compose:
    """Drives a throwaway Compose project (own volume, random password, free port)."""

    def __init__(self) -> None:
        self.env = {
            "ARXIV_BOT_DB_USER": "arxiv_test",
            "ARXIV_BOT_DB_PASSWORD": secrets.token_urlsafe(16),
            "ARXIV_BOT_DB_NAME": "arxiv_test",
            "ARXIV_BOT_DB_PORT": str(free_port()),
        }
        self.settings = Settings(
            _env_file=None,
            db_user=self.env["ARXIV_BOT_DB_USER"],
            db_password=self.env["ARXIV_BOT_DB_PASSWORD"],
            db_name=self.env["ARXIV_BOT_DB_NAME"],
            db_port=int(self.env["ARXIV_BOT_DB_PORT"]),
        )

    def run(self, *args: str, timeout: int = 180) -> None:
        subprocess.run(
            ["docker", "compose", "-p", PROJECT, *args],
            cwd=ROOT,
            env={**os.environ, **self.env},
            check=True,
            capture_output=True,
            timeout=timeout,
        )

    def up(self) -> None:
        self.run("up", "-d", "--wait")

    def stop(self) -> None:
        self.run("stop", "postgres")

    def start(self) -> None:
        # `up --wait` restarts a stopped service and waits for its healthcheck.
        self.up()


@pytest.fixture(scope="session")
def compose() -> Iterator[Compose]:
    c = Compose()
    try:
        c.up()
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.fail(f"Docker Compose PostgreSQL could not be started: {exc}")
    try:
        yield c
    finally:
        c.run("down", "-v")


@pytest.fixture
def postgres(compose: Compose) -> Iterator[Compose]:
    """PostgreSQL running at test start; restored if a test stops it."""
    compose.start()
    yield compose
    compose.start()


@pytest.fixture
def run() -> Callable[..., Any]:
    return run_async


def wait_for(predicate: Callable[[], bool], timeout: float = 60, interval: float = 1) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False
