from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "KeepiQ"
    app_env: str = "development"
    app_debug: bool = True
    app_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:5173"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 30

    database_url: str = "sqlite+aiosqlite:///./keepiq.db"
    alembic_database_url: str = "sqlite:///./keepiq.db"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_webhook_secret: str = "keepiq-webhook-secret"
    telegram_webhook_path: str = "/telegram/webhook"
    telegram_use_webhook: bool = False
    telegram_mini_app_url: str = "http://localhost:5173"

    default_timezone: str = "Europe/Moscow"
    default_date_time: str = "10:00"
    morning_summary_time: str = "09:00"
    evening_summary_time: str = "21:00"
    event_reminder_hours_before: int = 3
    allow_dev_auth: bool = True
    dev_telegram_user_id: int = 100001
    dev_telegram_username: str = "demo_user"
    dev_telegram_first_name: str = "Demo"

    openai_api_key: str = ""
    openai_reasoning_model: str = "gpt-5-mini"
    openai_transcription_model: str = "gpt-4o-mini-transcribe"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_vision_model: str = "gpt-4.1-mini"

    search_embeddings_enabled: bool = False
    worker_poll_interval_seconds: int = 30
    log_level: str = "INFO"
    callback_action_ttl_hours: int = Field(default=24, ge=1, le=168)


@lru_cache
def get_settings() -> Settings:
    return Settings()
