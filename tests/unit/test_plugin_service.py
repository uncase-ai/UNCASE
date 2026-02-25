"""Tests for the plugin installation service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from uncase.exceptions import PluginAlreadyInstalledError, PluginNotFoundError
from uncase.plugins.registry import PluginRegistry
from uncase.plugins.schemas import PluginManifest
from uncase.schemas.installed_plugin import PluginConfigUpdateRequest
from uncase.services.plugin_service import PluginService
from uncase.tools.registry import ToolRegistry
from uncase.tools.schemas import ToolDefinition

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_manifest(**overrides: object) -> PluginManifest:
    """Build a fictional PluginManifest for testing."""
    defaults: dict[str, object] = {
        "id": "fictional-automotive-toolkit",
        "name": "Fictional Automotive Toolkit",
        "description": "A fictional plugin with automotive tools for testing.",
        "version": "1.0.0",
        "author": "UNCASE Test Team",
        "domains": ["automotive.sales"],
        "tags": ["automotive", "fictional"],
        "tools": [
            ToolDefinition(
                name="fictional_vehicle_lookup",
                description="Fictional vehicle lookup tool for test scenarios.",
                input_schema={"type": "object", "properties": {"vin": {"type": "string"}}},
                domains=["automotive.sales"],
            ),
            ToolDefinition(
                name="fictional_price_estimator",
                description="Fictional price estimator tool for test scenarios.",
                input_schema={"type": "object", "properties": {"model": {"type": "string"}}},
                domains=["automotive.sales"],
            ),
        ],
        "source": "official",
    }
    defaults.update(overrides)
    return PluginManifest(**defaults)  # type: ignore[arg-type]


def _make_plugin_registry(*manifests: PluginManifest) -> PluginRegistry:
    """Build a PluginRegistry with the given manifests in its catalog."""
    registry = PluginRegistry.__new__(PluginRegistry)
    registry._catalog = {m.id: m for m in manifests}
    registry._installed = {}
    return registry


def _make_tool_registry() -> ToolRegistry:
    """Build an empty ToolRegistry."""
    return ToolRegistry()


class TestPluginServiceInstall:
    async def test_install_plugin_success(self, async_session: AsyncSession) -> None:
        """Installing a plugin from the catalog persists it and registers tools."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            resp = await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-install-001",
            )

        assert resp.id is not None
        assert resp.plugin_id == "fictional-automotive-toolkit"
        assert resp.plugin_name == "Fictional Automotive Toolkit"
        assert resp.plugin_version == "1.0.0"
        assert resp.plugin_source == "official"
        assert "fictional_vehicle_lookup" in resp.tools_registered
        assert "fictional_price_estimator" in resp.tools_registered
        assert resp.domains == ["automotive.sales"]
        assert resp.is_active is True
        assert resp.organization_id == "org-install-001"

        # Tools should be registered in the tool registry
        assert "fictional_vehicle_lookup" in tool_registry
        assert "fictional_price_estimator" in tool_registry

    async def test_install_plugin_not_in_catalog_raises(self, async_session: AsyncSession) -> None:
        """Installing a plugin not in the catalog raises PluginNotFoundError."""
        empty_plugin_registry = _make_plugin_registry()
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=empty_plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            with pytest.raises(PluginNotFoundError, match="not found"):
                await service.install_plugin("nonexistent-plugin")

    async def test_install_plugin_already_installed_raises(self, async_session: AsyncSession) -> None:
        """Installing a plugin that is already installed raises PluginAlreadyInstalledError."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-dup-001",
            )

            with pytest.raises(PluginAlreadyInstalledError, match="already installed"):
                await service.install_plugin(
                    "fictional-automotive-toolkit",
                    organization_id="org-dup-001",
                )

    async def test_install_plugin_does_not_reregister_existing_tools(self, async_session: AsyncSession) -> None:
        """If a tool is already in the tool registry, install does not fail."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()
        # Pre-register one tool
        tool_registry.register(manifest.tools[0])

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            resp = await service.install_plugin("fictional-automotive-toolkit")

        # Both tool names should appear in tools_registered
        assert "fictional_vehicle_lookup" in resp.tools_registered
        assert "fictional_price_estimator" in resp.tools_registered


class TestPluginServiceUninstall:
    async def test_uninstall_plugin_success(self, async_session: AsyncSession) -> None:
        """Uninstalling a plugin removes it from DB and de-registers tools."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-uninst-001",
            )

            # Tools should be registered
            assert "fictional_vehicle_lookup" in tool_registry

            await service.uninstall_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-uninst-001",
            )

        # Tools should be removed since no other org uses them
        assert "fictional_vehicle_lookup" not in tool_registry
        assert "fictional_price_estimator" not in tool_registry

        # Plugin should no longer be installed
        result = await service.is_installed(
            "fictional-automotive-toolkit",
            organization_id="org-uninst-001",
        )
        assert result is False

    async def test_uninstall_plugin_not_installed_raises(self, async_session: AsyncSession) -> None:
        """Uninstalling a plugin that is not installed raises PluginNotFoundError."""
        plugin_registry = _make_plugin_registry()
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            with pytest.raises(PluginNotFoundError, match="not installed"):
                await service.uninstall_plugin("fictional-automotive-toolkit")

    async def test_uninstall_keeps_tools_if_other_orgs_use_plugin(self, async_session: AsyncSession) -> None:
        """Tools are NOT removed if another org still has the plugin installed."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            # Install for two orgs
            await service.install_plugin("fictional-automotive-toolkit", organization_id="org-a")
            await service.install_plugin("fictional-automotive-toolkit", organization_id="org-b")

            # Uninstall for org-a
            await service.uninstall_plugin("fictional-automotive-toolkit", organization_id="org-a")

        # Tools should still be registered because org-b still has the plugin
        assert "fictional_vehicle_lookup" in tool_registry


class TestPluginServiceList:
    async def test_list_installed_filters_by_org(self, async_session: AsyncSession) -> None:
        """list_installed returns only plugins for the specified org."""
        manifest_a = _make_manifest(id="fictional-toolkit-alpha", name="Alpha Toolkit")
        manifest_b = _make_manifest(id="fictional-toolkit-beta", name="Beta Toolkit")
        plugin_registry = _make_plugin_registry(manifest_a, manifest_b)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin("fictional-toolkit-alpha", organization_id="org-list-a")
            await service.install_plugin("fictional-toolkit-beta", organization_id="org-list-b")

            result_a = await service.list_installed(organization_id="org-list-a")
            result_b = await service.list_installed(organization_id="org-list-b")

        assert result_a.total == 1
        assert result_a.items[0].plugin_id == "fictional-toolkit-alpha"

        assert result_b.total == 1
        assert result_b.items[0].plugin_id == "fictional-toolkit-beta"

    async def test_list_installed_empty(self, async_session: AsyncSession) -> None:
        """list_installed returns empty for an org with no plugins."""
        service = PluginService(async_session)
        result = await service.list_installed(organization_id="org-empty")
        assert result.total == 0
        assert result.items == []


class TestPluginServiceConfig:
    async def test_update_plugin_config_success(self, async_session: AsyncSession) -> None:
        """Updating plugin config persists the changes."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-cfg-001",
            )

            update = PluginConfigUpdateRequest(
                config={"api_endpoint": "https://fictional-api.example.com/v1"},
                is_active=True,
            )
            resp = await service.update_plugin_config(
                "fictional-automotive-toolkit",
                update,
                organization_id="org-cfg-001",
            )

        assert resp.config == {"api_endpoint": "https://fictional-api.example.com/v1"}
        assert resp.is_active is True

    async def test_update_plugin_config_deactivate(self, async_session: AsyncSession) -> None:
        """Deactivating a plugin via config update sets is_active to False."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-deact-001",
            )

            update = PluginConfigUpdateRequest(is_active=False)
            resp = await service.update_plugin_config(
                "fictional-automotive-toolkit",
                update,
                organization_id="org-deact-001",
            )

        assert resp.is_active is False

    async def test_update_plugin_config_not_installed_raises(self, async_session: AsyncSession) -> None:
        """Updating config for a plugin that is not installed raises PluginNotFoundError."""
        service = PluginService(async_session)
        update = PluginConfigUpdateRequest(config={"key": "value"})
        with pytest.raises(PluginNotFoundError, match="not installed"):
            await service.update_plugin_config("nonexistent-plugin", update)


class TestPluginServiceIsInstalled:
    async def test_is_installed_returns_true_when_active(self, async_session: AsyncSession) -> None:
        """is_installed returns True for an active installation."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-check-001",
            )

            result = await service.is_installed(
                "fictional-automotive-toolkit",
                organization_id="org-check-001",
            )

        assert result is True

    async def test_is_installed_returns_false_when_not_installed(self, async_session: AsyncSession) -> None:
        """is_installed returns False when nothing is installed."""
        service = PluginService(async_session)
        result = await service.is_installed(
            "fictional-automotive-toolkit",
            organization_id="org-none-001",
        )
        assert result is False

    async def test_is_installed_returns_false_when_deactivated(self, async_session: AsyncSession) -> None:
        """is_installed returns False when the plugin is deactivated."""
        manifest = _make_manifest()
        plugin_registry = _make_plugin_registry(manifest)
        tool_registry = _make_tool_registry()

        with (
            patch("uncase.services.plugin_service.get_plugin_registry", return_value=plugin_registry),
            patch("uncase.services.plugin_service.get_tool_registry", return_value=tool_registry),
        ):
            service = PluginService(async_session)
            await service.install_plugin(
                "fictional-automotive-toolkit",
                organization_id="org-deact-chk",
            )

            # Deactivate
            update = PluginConfigUpdateRequest(is_active=False)
            await service.update_plugin_config(
                "fictional-automotive-toolkit",
                update,
                organization_id="org-deact-chk",
            )

            result = await service.is_installed(
                "fictional-automotive-toolkit",
                organization_id="org-deact-chk",
            )

        assert result is False
