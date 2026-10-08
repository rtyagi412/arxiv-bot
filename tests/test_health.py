import logging
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from app import health
from app.config import Settings
from conftest import Compose

HEALTHY = {"status": "ok", "services": {"api": "ok", "database": "ok"}}
DEGRADED = {"status": "degraded", "services": {"api": "ok", "database": "degraded"}}


def test_aggregate_all_ok() -> None:
    assert health.aggregate_status({"api": "ok", "database": "ok"}) == "ok"


@pytest.mark.parametrize(
    "services",
    [
        {"api": "ok", "database": "degraded"},
        {"api": "degraded", "database": "ok"},
        {"api": "degraded", "database": "degraded"},
    ],
)
def test_aggregate_any_degraded(services: dict[str, Any]) -> None:
    assert health.aggregate_status(services) == "degraded"


def get_health(
    run: Callable[..., Any], monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> httpx.Response:
    monkeypatch.setattr(health, "get_settings", lambda: settings)
    app = FastAPI()
    app.include_router(health.router)

    async def call() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/health")

    return run(call())


@pytest.mark.integration
def test_healthy(
    postgres: Compose, run: Callable[..., Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    response = get_health(run, monkeypatch, postgres.settings)
    assert response.status_code == 200
    assert response.json() == HEALTHY


@pytest.mark.integration
def test_database_stopped_returns_503(
    postgres: Compose, run: Callable[..., Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    postgres.stop()
    response = get_health(run, monkeypatch, postgres.settings)
    assert response.status_code == 503
    assert response.json() == DEGRADED


@pytest.mark.integration
def test_wrong_password_degraded_and_no_leak(
    postgres: Compose,
    run: Callable[..., Any],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    wrong = "wrong-password-sentinel"
    settings = postgres.settings.model_copy(update={"db_password": SecretStr(wrong)})
    with caplog.at_level(logging.DEBUG):
        response = get_health(run, monkeypatch, settings)
    assert response.status_code == 503
    assert response.json() == DEGRADED
    real = postgres.settings.db_password.get_secret_value()
    for text in (response.text, caplog.text):
        assert wrong not in text
        assert real not in text
        assert "postgresql://" not in text
        assert "Traceback" not in text
        assert "password authentication" not in text
