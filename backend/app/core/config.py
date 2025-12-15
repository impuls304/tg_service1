from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    app_name: str = "Мастер на дом"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(
        default="sqlite:///./data/master_service.db", alias="DATABASE_URL"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    frontend_dir: Path = Field(
        default=Path(__file__).resolve().parents[3] / "frontend",
        alias="FRONTEND_DIR",
    )
    static_mount_path: str = Field(default="/web", alias="STATIC_MOUNT_PATH")
    telegram_bot_token: Optional[str] = Field(
        default=None, alias="TELEGRAM_BOT_TOKEN"
    )
    telegram_master_chat_id: Optional[int] = Field(
        default=None, alias="TELEGRAM_MASTER_CHAT_ID"
    )
    telegram_webhook_secret: Optional[str] = Field(
        default=None, alias="TELEGRAM_WEBHOOK_SECRET"
    )
    webhook_base_url: Optional[AnyUrl] = Field(
        default=None, alias="TELEGRAM_WEBHOOK_BASE_URL"
    )
    cors_allow_origins: List[str] = Field(
        default=["https://web.telegram.org", "https://telegram.org", "*"],
        alias="CORS_ALLOW_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance to avoid reparsing the environment."""

    return Settings()
