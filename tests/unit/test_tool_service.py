"""Tests for the custom tool service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from uncase.exceptions import CustomToolNotFoundError, DuplicateError, ValidationError
from uncase.schemas.custom_tool import CustomToolCreateRequest, CustomToolUpdateRequest
from uncase.services.tool_service import ToolService
from uncase.tools.registry import ToolRegistry
from uncase.tools.schemas import ToolDefinition

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_tool_registry(*names: str) -> ToolRegistry:
    """Build a ToolRegistry pre-loaded with fictional tool names."""
    registry = ToolRegistry()
    for name in names:
        registry.register(
            ToolDefinition(
                name=name,
                description=f"Built-in tool {name} for testing purposes.",
                input_schema={"type": "object", "properties": {}},
            )
        )
    return registry


def _make_create(**overrides: object) -> CustomToolCreateRequest:
    """Build a valid CustomToolCreateRequest with fictional defaults."""
    defaults: dict[str, object] = {
        "name": "fictional_crm_lookup",
        "description": "Fictional CRM lookup tool for synthetic test scenarios.",
        "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"name": {"type": "string"}}},
        "domains": ["automotive.sales"],
        "category": "crm",
        "requires_auth": False,
        "execution_mode": "simulated",
        "version": "1.0",
        "metadata": {"fictional": True},
    }
    defaults.update(overrides)
    return CustomToolCreateRequest(**defaults)  # type: ignore[arg-type]


class TestToolServiceCreate:
    async def test_create_custom_tool_success(self, async_session: AsyncSession) -> None:
        """Creating a custom tool persists it and returns the correct response."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            req = _make_create()
            resp = await service.create_custom_tool(req, organization_id="org-test-001")

        assert resp.id is not None
        assert resp.name == "fictional_crm_lookup"
        assert resp.description == "Fictional CRM lookup tool for synthetic test scenarios."
        assert resp.domains == ["automotive.sales"]
        assert resp.category == "crm"
        assert resp.requires_auth is False
        assert resp.execution_mode == "simulated"
        assert resp.version == "1.0"
        assert resp.metadata == {"fictional": True}
        assert resp.is_active is True
        assert resp.is_builtin is False
        assert resp.organization_id == "org-test-001"

    async def test_create_custom_tool_duplicate_builtin_raises(self, async_session: AsyncSession) -> None:
        """Creating a custom tool that collides with a built-in tool raises DuplicateError."""
        registry_with_builtin = _make_tool_registry("fictional_crm_lookup")
        with patch("uncase.services.tool_service.get_registry", return_value=registry_with_builtin):
            service = ToolService(async_session)
            req = _make_create(name="fictional_crm_lookup")
            with pytest.raises(DuplicateError, match="conflicts with a built-in tool"):
                await service.create_custom_tool(req)

    async def test_create_custom_tool_duplicate_in_db_raises(self, async_session: AsyncSession) -> None:
        """Creating a custom tool with a name that already exists in DB raises DuplicateError."""
        registry_first = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=registry_first):
            service = ToolService(async_session)
            req = _make_create()
            await service.create_custom_tool(req, organization_id="org-test-001")

        # Use a fresh empty registry for the second call so it passes the
        # built-in check and hits the DB duplicate check instead.
        registry_second = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=registry_second):
            service = ToolService(async_session)
            with pytest.raises(DuplicateError, match="already exists"):
                await service.create_custom_tool(req, organization_id="org-test-001")

    async def test_create_registers_in_memory(self, async_session: AsyncSession) -> None:
        """Creating a custom tool also registers it in the in-memory registry."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            req = _make_create()
            await service.create_custom_tool(req)

        assert "fictional_crm_lookup" in empty_registry


class TestToolServiceList:
    async def test_list_custom_tools_with_filters(self, async_session: AsyncSession) -> None:
        """Listing custom tools respects domain and category filters."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            await service.create_custom_tool(
                _make_create(name="tool_auto_one", domains=["automotive.sales"], category="crm"),
                organization_id="org-a",
            )
            await service.create_custom_tool(
                _make_create(name="tool_med_one", domains=["medical.consultation"], category="diagnostics"),
                organization_id="org-a",
            )
            await service.create_custom_tool(
                _make_create(name="tool_auto_two", domains=["automotive.sales"], category="crm"),
                organization_id="org-b",
            )

            # Filter by org
            result = await service.list_custom_tools(organization_id="org-a")
            assert result.total == 2

            # Filter by category
            result = await service.list_custom_tools(organization_id="org-a", category="crm")
            assert result.total == 1
            assert result.items[0].name == "tool_auto_one"

    async def test_list_custom_tools_pagination(self, async_session: AsyncSession) -> None:
        """Listing custom tools respects page and page_size."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            for i in range(5):
                await service.create_custom_tool(
                    _make_create(name=f"tool_page_{i}"),
                )

            p1 = await service.list_custom_tools(page=1, page_size=2)
            assert len(p1.items) == 2
            assert p1.total == 5
            assert p1.page == 1
            assert p1.page_size == 2

            p2 = await service.list_custom_tools(page=2, page_size=2)
            assert len(p2.items) == 2

            p3 = await service.list_custom_tools(page=3, page_size=2)
            assert len(p3.items) == 1

    async def test_list_custom_tools_invalid_page_raises(self, async_session: AsyncSession) -> None:
        """Listing with page < 1 raises ValidationError."""
        service = ToolService(async_session)
        with pytest.raises(ValidationError, match="Page must be >= 1"):
            await service.list_custom_tools(page=0)


class TestToolServiceUpdate:
    async def test_update_custom_tool_success(self, async_session: AsyncSession) -> None:
        """Updating a custom tool persists the changes."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            req = _make_create()
            created = await service.create_custom_tool(req)

            update_req = CustomToolUpdateRequest(
                description="Updated fictional description for the CRM tool.",
                category="updated_crm",
                version="2.0",
            )
            updated = await service.update_custom_tool(created.id, update_req)

        assert updated.description == "Updated fictional description for the CRM tool."
        assert updated.category == "updated_crm"
        assert updated.version == "2.0"
        # Unchanged fields remain the same
        assert updated.name == "fictional_crm_lookup"
        assert updated.domains == ["automotive.sales"]

    async def test_update_custom_tool_not_found_raises(self, async_session: AsyncSession) -> None:
        """Updating a non-existent tool raises CustomToolNotFoundError."""
        service = ToolService(async_session)
        update_req = CustomToolUpdateRequest(description="Does not matter.")
        with pytest.raises(CustomToolNotFoundError):
            await service.update_custom_tool("nonexistent-tool-id", update_req)


class TestToolServiceDelete:
    async def test_delete_custom_tool_success(self, async_session: AsyncSession) -> None:
        """Deleting a custom tool removes it from DB and in-memory registry."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            req = _make_create()
            created = await service.create_custom_tool(req)

            await service.delete_custom_tool(created.id)

        # Should not be in the in-memory registry
        assert "fictional_crm_lookup" not in empty_registry

        # Should raise not found from DB
        with pytest.raises(CustomToolNotFoundError):
            await service.get_custom_tool(created.id)

    async def test_delete_custom_tool_not_found_raises(self, async_session: AsyncSession) -> None:
        """Deleting a non-existent tool raises CustomToolNotFoundError."""
        empty_registry = _make_tool_registry()
        with patch("uncase.services.tool_service.get_registry", return_value=empty_registry):
            service = ToolService(async_session)
            with pytest.raises(CustomToolNotFoundError):
                await service.delete_custom_tool("nonexistent-tool-id")


class TestToolServiceResolve:
    async def test_resolve_tools_for_org_merges_all_sources(self, async_session: AsyncSession) -> None:
        """resolve_tools_for_org merges built-in, custom, and plugin tools."""
        # Set up a registry with one built-in tool
        builtin_tool = ToolDefinition(
            name="builtin_inventory_check",
            description="Built-in inventory check tool for testing.",
            input_schema={"type": "object", "properties": {}},
            domains=["automotive.sales"],
        )
        registry = ToolRegistry()
        registry.register(builtin_tool)

        with patch("uncase.services.tool_service.get_registry", return_value=registry):
            service = ToolService(async_session)

            # Create a custom tool in the DB
            await service.create_custom_tool(
                _make_create(name="custom_crm_tool", domains=["automotive.sales"]),
                organization_id="org-resolve-test",
            )

            # Resolve for the org + domain
            tools = await service.resolve_tools_for_org(
                organization_id="org-resolve-test",
                domain="automotive.sales",
            )

        tool_names = [t.name for t in tools]
        # Both built-in and custom tools should appear
        assert "builtin_inventory_check" in tool_names
        assert "custom_crm_tool" in tool_names
        # Result should be sorted by name
        assert tool_names == sorted(tool_names)

    async def test_resolve_tools_for_org_no_domain_returns_all(self, async_session: AsyncSession) -> None:
        """resolve_tools_for_org without domain returns all built-in + custom tools."""
        registry = _make_tool_registry("builtin_alpha", "builtin_beta")
        with patch("uncase.services.tool_service.get_registry", return_value=registry):
            service = ToolService(async_session)
            await service.create_custom_tool(
                _make_create(name="custom_gamma", domains=[]),
            )

            tools = await service.resolve_tools_for_org()

        tool_names = [t.name for t in tools]
        assert "builtin_alpha" in tool_names
        assert "builtin_beta" in tool_names
        assert "custom_gamma" in tool_names
