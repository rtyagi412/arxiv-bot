import time
from collections.abc import Callable
from typing import Any

import pytest

from app.db import check_database
from conftest import Compose, free_port


@pytest.mark.integration
def test_live_database_ok(postgres: Compose, run: Callable[..., Any]) -> None:
    assert run(check_database(postgres.settings)) is True


@pytest.mark.integration
def test_refused_port_degraded(postgres: Compose, run: Callable[..., Any]) -> None:
    settings = postgres.settings.model_copy(update={"db_port": free_port()})
    assert run(check_database(settings)) is False


@pytest.mark.integration
def test_unroutable_host_bounded_by_timeout(postgres: Compose, run: Callable[..., Any]) -> None:
    settings = postgres.settings.model_copy(
        update={"db_host": "10.255.255.1", "db_connect_timeout_seconds": 1}
    )
    start = time.monotonic()
    assert run(check_database(settings)) is False
    assert time.monotonic() - start < 3
