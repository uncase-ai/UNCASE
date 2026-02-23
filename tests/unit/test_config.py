"""Tests for configuration loading."""

from __future__ import annotations

from uncase.config import UNCASESettings


class TestSettings:
    def test_defaults(self) -> None:
        settings = UNCASESettings(database_url="sqlite+aiosqlite://")
        assert settings.uncase_env == "development"
        assert settings.uncase_log_level == "DEBUG"
        assert settings.uncase_default_locale == "es"
        assert settings.api_port == 8000

    def test_is_production(self) -> None:
        settings = UNCASESettings(uncase_env="production", database_url="sqlite+aiosqlite://")
        assert settings.is_production is True

    def test_not_production(self) -> None:
        settings = UNCASESettings(uncase_env="development", database_url="sqlite+aiosqlite://")
        assert settings.is_production is False

    def test_cors_origins_list(self) -> None:
        settings = UNCASESettings(
            api_cors_origins="http://a.com, http://b.com",
            database_url="sqlite+aiosqlite://",
        )
        assert settings.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_privacy_defaults(self) -> None:
        settings = UNCASESettings(database_url="sqlite+aiosqlite://")
        assert settings.uncase_pii_confidence_threshold == 0.85
        assert settings.uncase_dp_epsilon == 8.0
