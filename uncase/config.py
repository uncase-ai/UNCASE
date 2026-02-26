"""UNCASE configuration via Pydantic Settings."""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UNCASESettings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- General --
    uncase_env: Literal["development", "staging", "production"] = "development"
    uncase_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    uncase_default_locale: Literal["es", "en"] = "es"

    # -- API --
    api_port: int = 8000
    api_secret_key: str = "cambiar-en-produccion"
    api_cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # -- Database --
    database_url: str = "postgresql+asyncpg://uncase:uncase@localhost:5432/uncase"

    # -- Redis (rate limiting, optional) --
    redis_url: str = ""

    # -- LLM Providers --
    litellm_api_key: str = ""
    anthropic_api_key: str = ""

    # -- MLflow --
    mlflow_tracking_uri: str = "http://localhost:5000"

    # -- Privacy --
    uncase_pii_confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    uncase_dp_epsilon: float = Field(default=8.0, gt=0.0)

    # -- E2B Sandboxes --
    e2b_api_key: str = ""
    e2b_template_id: str = "base"
    e2b_max_parallel: int = Field(default=5, ge=1, le=20)
    e2b_sandbox_timeout: int = Field(default=300, ge=30, le=600)
    e2b_enabled: bool = False
    e2b_webhook_secret: str = ""

    # -- Directories --
    uncase_models_dir: str = "./models"
    uncase_exports_dir: str = "./exports"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.uncase_env == "production"

    @property
    def sandbox_available(self) -> bool:
        """Check if E2B sandbox is configured and enabled."""
        return self.e2b_enabled and bool(self.e2b_api_key)

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


def get_settings() -> UNCASESettings:
    """Create and return settings instance."""
    return UNCASESettings()
