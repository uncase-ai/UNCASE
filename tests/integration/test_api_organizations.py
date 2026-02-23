"""Integration tests for organization CRUD and API key lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.integration
class TestOrganizationCRUD:
    async def test_create_organization(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/organizations",
            json={"name": "Test Org"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Org"
        assert data["slug"] == "test-org"
        assert data["is_active"] is True
        assert "id" in data

    async def test_get_organization(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Get Test"},
        )
        org_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/organizations/{org_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"

    async def test_get_nonexistent_org(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/organizations/nonexistent")
        assert response.status_code == 404

    async def test_update_organization(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Update Test"},
        )
        org_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/organizations/{org_id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    async def test_duplicate_slug_rejected(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/organizations",
            json={"name": "Unique Org", "slug": "unique-slug"},
        )
        response = await client.post(
            "/api/v1/organizations",
            json={"name": "Another Org", "slug": "unique-slug"},
        )
        assert response.status_code == 409


@pytest.mark.integration
class TestAPIKeyLifecycle:
    async def _create_org(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Key Test Org"},
        )
        return resp.json()["id"]

    async def test_create_api_key(self, client: AsyncClient) -> None:
        org_id = await self._create_org(client)
        response = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Test Key", "scopes": "read,write"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "plain_key" in data
        assert data["plain_key"].startswith("uc_test_")
        assert data["name"] == "Test Key"

    async def test_list_api_keys(self, client: AsyncClient) -> None:
        org_id = await self._create_org(client)
        await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Key 1"},
        )
        await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Key 2"},
        )

        response = await client.get(f"/api/v1/organizations/{org_id}/api-keys")
        assert response.status_code == 200
        keys = response.json()
        assert len(keys) == 2

    async def test_revoke_api_key(self, client: AsyncClient) -> None:
        org_id = await self._create_org(client)
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Revoke Me"},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.delete(f"/api/v1/organizations/{org_id}/api-keys/{key_id}")
        assert response.status_code == 204

        # Verify it's revoked
        list_resp = await client.get(f"/api/v1/organizations/{org_id}/api-keys")
        keys = list_resp.json()
        revoked = next(k for k in keys if k["key_id"] == key_id)
        assert revoked["is_active"] is False

    async def test_rotate_api_key(self, client: AsyncClient) -> None:
        org_id = await self._create_org(client)
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Rotate Me", "scopes": "read,write"},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.post(f"/api/v1/organizations/{org_id}/api-keys/{key_id}/rotate")
        assert response.status_code == 200
        data = response.json()
        assert "plain_key" in data
        assert data["key_id"] != key_id
        assert data["name"] == "Rotate Me"
