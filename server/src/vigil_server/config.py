"""Server settings via pydantic-settings."""

from __future__ import annotations

import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("vigil_server.config")

_DEFAULT_API_KEY = "dev-api-key-change-me"


class Settings(BaseSettings):
    """Vigil server configuration.

    All settings can be overridden via environment variables prefixed
    with ``VIGIL_`` (e.g. ``VIGIL_DATABASE_URL``).
    """

    model_config = SettingsConfigDict(env_prefix="VIGIL_", env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./vigil.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Auth
    api_key: str = _DEFAULT_API_KEY
    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def is_sqlite(self) -> bool:
        """Return True when using a SQLite database."""
        return self.database_url.startswith("sqlite")

    def check_api_key_security(self) -> None:
        """Warn or raise if the default API key is used.

        In production (``VIGIL_ENV != 'development'``), using the default
        key raises a :class:`ValueError`.  In development it emits a
        warning.
        """
        if self.api_key != _DEFAULT_API_KEY:
            return

        env = os.getenv("VIGIL_ENV", "development")
        if env != "development":
            raise ValueError(
                "Default API key must not be used in production. "
                "Set VIGIL_API_KEY to a secure value."
            )
        logger.warning(
            "Using default API key — do NOT use in production. Set VIGIL_API_KEY to a secure value."
        )

    def check_jwt_secret_security(self) -> None:
        """Warn or raise if the default JWT secret is used in production."""
        if self.jwt_secret != "dev-jwt-secret-change-me":
            return

        env = os.getenv("VIGIL_ENV", "development")
        if env != "development":
            raise ValueError(
                "Default JWT secret must not be used in production. "
                "Set VIGIL_JWT_SECRET to a secure value."
            )
        logger.warning(
            "Using default JWT secret — do NOT use in production. "
            "Set VIGIL_JWT_SECRET to a secure value."
        )


settings = Settings()
settings.check_api_key_security()
settings.check_jwt_secret_security()
