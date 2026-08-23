from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://alerts:alerts@localhost:5432/serbia_alerts"
    DB_PASSWORD: str = "alerts"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True

    APP_URL: str = "http://localhost:8000"
    ADMIN_PASSWORD: str = ""
    SECRET_KEY: str = "change-me"

    TIMEZONE: str = "Europe/Belgrade"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
