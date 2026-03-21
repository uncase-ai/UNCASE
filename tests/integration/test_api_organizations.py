"""Integration tests for organization CRUD and API key lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


async def _bootstrap_org(client: AsyncClient, name: str = "Test Org") -> tuple[str, str]:
    """Create an org and bootstrap its first admin API key.

    Returns (org_id, plain_api_key).
    """
    create_resp = await client.post("/api/v1/organizations", json={"name": name})
    assert create_resp.status_code == 201
    org_id = create_resp.json()["id"]

    # First key creation is open (bootstrap)
    key_resp = await client.post(
        f"/api/v1/organizations/{org_id}/api-keys",
        json={"name": "admin-key", "scopes": "admin"},
    )
    assert key_resp.status_code == 201
    plain_key = key_resp.json()["plain_key"]
    return org_id, plain_key


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
        org_id, api_key = await _bootstrap_org(client, "Get Test")

        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"

    async def test_get_organization_requires_auth(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Auth Test"},
        )
        org_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/organizations/{org_id}")
        assert response.status_code == 422  # missing X-API-Key header

    async def test_get_nonexistent_org(self, client: AsyncClient) -> None:
        _, api_key = await _bootstrap_org(client, "Key Holder")
        response = await client.get(
            "/api/v1/organizations/nonexistent",
            headers={"X-API-Key": api_key},
        )
        # 403 because the key's org doesn't match "nonexistent"
        assert response.status_code == 403

    async def test_update_organization(self, client: AsyncClient) -> None:
        org_id, api_key = await _bootstrap_org(client, "Update Test")

        response = await client.put(
            f"/api/v1/organizations/{org_id}",
            json={"name": "Updated Name"},
            headers={"X-API-Key": api_key},
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
    async def test_bootstrap_first_key(self, client: AsyncClient) -> None:
        """First API key creation is open (no auth required)."""
        org_id, api_key = await _bootstrap_org(client, "Bootstrap Org")
        assert api_key.startswith("uc_test_")

    async def test_second_key_requires_auth(self, client: AsyncClient) -> None:
        """Subsequent key creation requires admin auth."""
        org_id, api_key = await _bootstrap_org(client, "Second Key Org")

        # Create second key WITH auth — should succeed
        response = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Second Key", "scopes": "read,write"},
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 201

    async def test_second_key_without_auth_rejected(self, client: AsyncClient) -> None:
        """Second key creation without auth is rejected."""
        org_id, _ = await _bootstrap_org(client, "No Auth Org")

        response = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Unauthorized Key"},
        )
        assert response.status_code == 401

    async def test_list_api_keys(self, client: AsyncClient) -> None:
        org_id, api_key = await _bootstrap_org(client, "List Keys Org")

        # Create a second key
        await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Key 2"},
            headers={"X-API-Key": api_key},
        )

        response = await client.get(
            f"/api/v1/organizations/{org_id}/api-keys",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        keys = response.json()
        assert len(keys) == 2

    async def test_revoke_api_key(self, client: AsyncClient) -> None:
        org_id, api_key = await _bootstrap_org(client, "Revoke Org")

        # Create a second key to revoke
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Revoke Me"},
            headers={"X-API-Key": api_key},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.delete(
            f"/api/v1/organizations/{org_id}/api-keys/{key_id}",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 204

        # Verify it's revoked
        list_resp = await client.get(
            f"/api/v1/organizations/{org_id}/api-keys",
            headers={"X-API-Key": api_key},
        )
        keys = list_resp.json()
        revoked = next(k for k in keys if k["key_id"] == key_id)
        assert revoked["is_active"] is False

    async def test_rotate_api_key(self, client: AsyncClient) -> None:
        org_id, api_key = await _bootstrap_org(client, "Rotate Org")

        # Create a second key to rotate
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "Rotate Me", "scopes": "read,write"},
            headers={"X-API-Key": api_key},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys/{key_id}/rotate",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert "plain_key" in data
        assert data["key_id"] != key_id
        assert data["name"] == "Rotate Me"
