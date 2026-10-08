import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest

from conftest import ROOT, Compose, free_port, wait_for

HEALTHY = {"status": "ok", "services": {"api": "ok", "database": "ok"}}
DEGRADED = {"status": "degraded", "services": {"api": "ok", "database": "degraded"}}


def fetch(port: int) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=10) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)
    except OSError:
        return 0, None


@contextmanager
def running_app(postgres: Compose) -> Iterator[int]:
    """The documented run command, as a real process on the host."""
    port = free_port()
    # Exactly the README command (no PYTHONPATH help), so a broken import path is caught.
    env = {**os.environ, **postgres.env}
    command = [sys.executable, "-m", "uvicorn", "app.main:app", "--app-dir", "src"]
    command += ["--host", "127.0.0.1", "--port", str(port)]
    command += ["--loop", "asyncio:SelectorEventLoop"]
    proc = subprocess.Popen(
        command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        assert wait_for(lambda: fetch(port)[0] != 0, timeout=30), "app did not start"
        yield port
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.mark.integration
def test_healthy_over_http(postgres: Compose) -> None:
    with running_app(postgres) as port:
        assert fetch(port) == (200, HEALTHY)


@pytest.mark.integration
def test_degrades_and_recovers_without_app_restart(postgres: Compose) -> None:
    with running_app(postgres) as port:
        assert fetch(port) == (200, HEALTHY)

        postgres.stop()
        assert fetch(port) == (503, DEGRADED)

        postgres.start()
        assert wait_for(lambda: fetch(port) == (200, HEALTHY), timeout=60)


@pytest.mark.integration
def test_app_starts_with_database_stopped(postgres: Compose) -> None:
    postgres.stop()
    with running_app(postgres) as port:
        assert fetch(port) == (503, DEGRADED)
