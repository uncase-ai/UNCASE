"""Tests for the template configuration service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from uncase.schemas.template_config import TemplateConfigResponse, TemplateConfigUpdateRequest
from uncase.services.template_service import TemplateService
from uncase.templates import TemplateRegistry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class _FakeTemplate(BaseChatTemplate):
    """Minimal concrete template for testing purposes."""

    def __init__(self, template_name: str) -> None:
        self._name = template_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Fake {self._name}"

    @property
    def supports_tool_calls(self) -> bool:
        return False

    def render(
        self,
        conversation: object,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[object] | None = None,
    ) -> str:
        return f"<rendered by {self._name}>"

    def get_special_tokens(self) -> list[str]:
        return []


def _make_template_registry(*names: str) -> TemplateRegistry:
    """Build a TemplateRegistry with fictional templates."""
    registry = TemplateRegistry()
    for name in names:
        registry.register(_FakeTemplate(name))
    return registry


class TestTemplateServiceGetConfig:
    async def test_get_config_returns_none_when_not_set(self, async_session: AsyncSession) -> None:
        """get_config returns None if no config exists for the org."""
        service = TemplateService(async_session)
        result = await service.get_config(organization_id="org-no-config")
        assert result is None

    async def test_get_config_returns_existing(self, async_session: AsyncSession) -> None:
        """get_config returns the config after it has been created."""
        service = TemplateService(async_session)
        # Create via get_or_create first
        created = await service.get_or_create_config(organization_id="org-get-001")

        result = await service.get_config(organization_id="org-get-001")
        assert result is not None
        assert result.id == created.id
        assert result.organization_id == "org-get-001"


class TestTemplateServiceGetOrCreate:
    async def test_get_or_create_config_creates_default(self, async_session: AsyncSession) -> None:
        """get_or_create_config creates a default config when none exists."""
        service = TemplateService(async_session)
        result = await service.get_or_create_config(organization_id="org-create-001")

        assert result.id is not None
        assert result.organization_id == "org-create-001"
        assert result.default_template == "chatml"
        assert result.default_tool_call_mode == "none"
        assert result.default_system_prompt is None
        assert result.preferred_templates == []
        assert result.export_format == "txt"

    async def test_get_or_create_config_returns_existing(self, async_session: AsyncSession) -> None:
        """get_or_create_config returns the existing config on subsequent calls."""
        service = TemplateService(async_session)
        first = await service.get_or_create_config(organization_id="org-idempotent")
        second = await service.get_or_create_config(organization_id="org-idempotent")

        assert first.id == second.id

    async def test_get_or_create_config_none_org(self, async_session: AsyncSession) -> None:
        """get_or_create_config works with organization_id=None (global config)."""
        service = TemplateService(async_session)
        result = await service.get_or_create_config(organization_id=None)

        assert result.id is not None
        assert result.organization_id is None
        assert result.default_template == "chatml"


class TestTemplateServiceUpdateConfig:
    async def test_update_config_creates_if_missing(self, async_session: AsyncSession) -> None:
        """update_config creates the config if it does not exist (upsert)."""
        service = TemplateService(async_session)
        update = TemplateConfigUpdateRequest(
            default_template="llama",
            export_format="jsonl",
        )
        result = await service.update_config(update, organization_id="org-upsert-001")

        assert result.id is not None
        assert result.organization_id == "org-upsert-001"
        assert result.default_template == "llama"
        assert result.export_format == "jsonl"

    async def test_update_config_updates_existing(self, async_session: AsyncSession) -> None:
        """update_config modifies only the specified fields on an existing config."""
        service = TemplateService(async_session)

        # Create initial config
        initial = await service.get_or_create_config(organization_id="org-update-001")
        assert initial.default_template == "chatml"
        assert initial.export_format == "txt"

        # Update only default_template
        update = TemplateConfigUpdateRequest(default_template="alpaca")
        result = await service.update_config(update, organization_id="org-update-001")

        assert result.id == initial.id
        assert result.default_template == "alpaca"
        # export_format should remain unchanged
        assert result.export_format == "txt"

    async def test_update_config_all_fields(self, async_session: AsyncSession) -> None:
        """update_config can update all fields simultaneously."""
        service = TemplateService(async_session)
        await service.get_or_create_config(organization_id="org-all-fields")

        update = TemplateConfigUpdateRequest(
            default_template="mistral",
            default_tool_call_mode="inline",
            default_system_prompt="Fictional system prompt for synthetic testing.",
            preferred_templates=["mistral", "chatml", "llama"],
            export_format="parquet",
        )
        result = await service.update_config(update, organization_id="org-all-fields")

        assert result.default_template == "mistral"
        assert result.default_tool_call_mode == "inline"
        assert result.default_system_prompt == "Fictional system prompt for synthetic testing."
        assert result.preferred_templates == ["mistral", "chatml", "llama"]
        assert result.export_format == "parquet"


class TestTemplateServiceResolve:
    def test_resolve_template_for_org_uses_default(self) -> None:
        """resolve_template_for_org returns the template from the config."""
        registry = _make_template_registry("chatml", "llama", "alpaca")

        with (
            patch("uncase.services.template_service.register_all_templates"),
            patch("uncase.services.template_service.get_template_registry", return_value=registry),
        ):
            service = TemplateService(MagicMock())  # session not needed for resolve
            config = TemplateConfigResponse(
                id="cfg-001",
                organization_id="org-resolve-001",
                default_template="llama",
                default_tool_call_mode="none",
                default_system_prompt=None,
                preferred_templates=[],
                export_format="txt",
                created_at="2026-01-01T00:00:00",
                updated_at="2026-01-01T00:00:00",
            )
            template = service.resolve_template_for_org(config)

        assert template.name == "llama"

    def test_resolve_template_for_org_falls_back_to_chatml(self) -> None:
        """resolve_template_for_org falls back to chatml when the requested template is missing."""
        registry = _make_template_registry("chatml")

        with (
            patch("uncase.services.template_service.register_all_templates"),
            patch("uncase.services.template_service.get_template_registry", return_value=registry),
        ):
            service = TemplateService(MagicMock())
            config = TemplateConfigResponse(
                id="cfg-002",
                organization_id="org-resolve-002",
                default_template="nonexistent_template",
                default_tool_call_mode="none",
                default_system_prompt=None,
                preferred_templates=[],
                export_format="txt",
                created_at="2026-01-01T00:00:00",
                updated_at="2026-01-01T00:00:00",
            )
            template = service.resolve_template_for_org(config)

        assert template.name == "chatml"

    def test_resolve_template_for_org_none_config_uses_chatml(self) -> None:
        """resolve_template_for_org defaults to chatml when config is None."""
        registry = _make_template_registry("chatml", "llama")

        with (
            patch("uncase.services.template_service.register_all_templates"),
            patch("uncase.services.template_service.get_template_registry", return_value=registry),
        ):
            service = TemplateService(MagicMock())
            template = service.resolve_template_for_org(None)

        assert template.name == "chatml"

    def test_resolve_template_calls_register_all(self) -> None:
        """resolve_template_for_org calls register_all_templates to ensure templates are loaded."""
        registry = _make_template_registry("chatml")

        with (
            patch("uncase.services.template_service.register_all_templates") as mock_register,
            patch("uncase.services.template_service.get_template_registry", return_value=registry),
        ):
            service = TemplateService(MagicMock())
            service.resolve_template_for_org(None)

        mock_register.assert_called_once()
