import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.fixture
def db_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARXIV_BOT_DB_USER", "test_user")
    monkeypatch.setenv("ARXIV_BOT_DB_PASSWORD", "test_password")
    monkeypatch.setenv("ARXIV_BOT_DB_NAME", "test_db")


@pytest.mark.usefixtures("db_env")
def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.log_level == "INFO"
    assert settings.db_host == "127.0.0.1"
    assert settings.db_port == 5436
    assert settings.db_connect_timeout_seconds == 2


@pytest.mark.usefixtures("db_env")
def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARXIV_BOT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ARXIV_BOT_DB_PORT", "5433")
    settings = Settings(_env_file=None)
    assert settings.log_level == "DEBUG"
    assert settings.db_port == 5433


@pytest.mark.usefixtures("db_env")
def test_password_is_secret() -> None:
    settings = Settings(_env_file=None)
    assert "test_password" not in repr(settings)
    assert "test_password" not in str(settings)


@pytest.mark.parametrize("name", ["DB_USER", "DB_PASSWORD", "DB_NAME"])
def test_missing_required_setting_fails(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    for var in ("DB_USER", "DB_PASSWORD", "DB_NAME"):
        monkeypatch.setenv(f"ARXIV_BOT_{var}", "x")
    monkeypatch.delenv(f"ARXIV_BOT_{name}")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
