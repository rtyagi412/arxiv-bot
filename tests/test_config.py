import pytest

from arxiv_bot.config import Settings


def test_defaults() -> None:
    assert Settings(_env_file=None).log_level == "INFO"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARXIV_BOT_LOG_LEVEL", "DEBUG")
    assert Settings(_env_file=None).log_level == "DEBUG"
