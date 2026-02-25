"""Integration tests for the Plugins API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.plugins import get_catalog, get_registry

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.fixture(autouse=True)
def _reset_plugin_registry() -> None:
    """Ensure each test starts with a clean installed state.

    The catalog remains populated with built-in plugins, but any
    previously installed plugins are uninstalled.
    """
    registry = get_registry()
    for pid in list(registry._installed):
        registry.uninstall(pid)


@pytest.mark.integration
class TestListPlugins:
    """Test GET /api/v1/plugins — catalog browsing."""

    async def test_list_all(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least the built-in plugins
        catalog = get_catalog()
        assert len(data) == len(catalog)

    async def test_filter_by_domain(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins", params={"domain": "automotive.sales"})
        assert response.status_code == 200
        data = response.json()
        for plugin in data:
            assert "automotive.sales" in plugin["domains"]

    async def test_filter_by_tag(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins", params={"tag": "medical"})
        assert response.status_code == 200
        data = response.json()
        for plugin in data:
            assert "medical" in plugin["tags"]

    async def test_filter_by_source(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins", params={"source": "official"})
        assert response.status_code == 200
        data = response.json()
        for plugin in data:
            assert plugin["source"] == "official"

    async def test_filter_nonexistent_domain(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins", params={"domain": "nonexistent.domain"})
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.integration
class TestGetPlugin:
    """Test GET /api/v1/plugins/{plugin_id}."""

    async def test_get_existing_plugin(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        response = await client.get(f"/api/v1/plugins/{plugin_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == plugin_id

    async def test_get_nonexistent_plugin(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins/nonexistent-plugin-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestInstallPlugin:
    """Test POST /api/v1/plugins/{plugin_id}/install."""

    async def test_install_plugin(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        response = await client.post(f"/api/v1/plugins/{plugin_id}/install")
        assert response.status_code == 201
        data = response.json()
        assert data["plugin_id"] == plugin_id
        assert "tools_registered" in data

    async def test_install_nonexistent_plugin(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/plugins/nonexistent-plugin/install")
        assert response.status_code == 404

    async def test_install_already_installed(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        # Install once
        first = await client.post(f"/api/v1/plugins/{plugin_id}/install")
        assert first.status_code == 201
        # Install again — should conflict
        second = await client.post(f"/api/v1/plugins/{plugin_id}/install")
        assert second.status_code == 409


@pytest.mark.integration
class TestUninstallPlugin:
    """Test DELETE /api/v1/plugins/{plugin_id}/install."""

    async def test_uninstall_installed_plugin(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        # Install first
        await client.post(f"/api/v1/plugins/{plugin_id}/install")
        # Uninstall
        response = await client.delete(f"/api/v1/plugins/{plugin_id}/install")
        assert response.status_code == 204

    async def test_uninstall_not_installed(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        response = await client.delete(f"/api/v1/plugins/{plugin_id}/install")
        assert response.status_code == 404


@pytest.mark.integration
class TestInstalledPlugins:
    """Test GET /api/v1/plugins/installed."""

    async def test_list_installed_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/plugins/installed")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_installed_after_install(self, client: AsyncClient) -> None:
        catalog = get_catalog()
        if not catalog:
            pytest.skip("No built-in plugins available")
        plugin_id = catalog[0].id
        await client.post(f"/api/v1/plugins/{plugin_id}/install")

        response = await client.get("/api/v1/plugins/installed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["plugin_id"] == plugin_id


@pytest.mark.integration
class TestPublishPlugin:
    """Test POST /api/v1/plugins — community publish."""

    async def test_publish_community_plugin(self, client: AsyncClient) -> None:
        payload = {
            "id": "test-community-plugin-001",
            "name": "Test Community Plugin",
            "description": "A fictional community plugin for testing purposes.",
            "version": "0.1.0",
            "author": "Test Author",
            "domains": ["automotive.sales"],
            "tags": ["test", "community"],
            "tools": [],
            "source": "official",  # should be overridden to community
            "verified": True,  # should be overridden to False
        }
        response = await client.post("/api/v1/plugins", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test-community-plugin-001"
        assert data["source"] == "community"
        assert data["verified"] is False

    async def test_publish_duplicate_plugin(self, client: AsyncClient) -> None:
        payload = {
            "id": "test-community-dup",
            "name": "Dup Plugin",
            "description": "Duplicate test plugin.",
            "version": "1.0.0",
            "domains": [],
            "tags": [],
            "tools": [],
        }
        first = await client.post("/api/v1/plugins", json=payload)
        assert first.status_code == 201
        # Second publish should fail with duplicate
        second = await client.post("/api/v1/plugins", json=payload)
        assert second.status_code == 409
