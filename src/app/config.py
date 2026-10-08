from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ARXIV_BOT_",
        extra="ignore",
    )

    log_level: str = "INFO"

    db_host: str = "127.0.0.1"
    db_port: int = 5436
    db_user: str
    db_password: SecretStr
    db_name: str
    db_connect_timeout_seconds: float = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
