"""Integration tests for authentication and authorization enforcement.

Verifies:
1. Endpoints requiring auth return 422 (missing header) or 401 (invalid key)
2. Cross-org access is denied (key from org A cannot access org B's data)
3. Scope enforcement (read-only key cannot access admin endpoints)
"""

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

    key_resp = await client.post(
        f"/api/v1/organizations/{org_id}/api-keys",
        json={"name": "admin-key", "scopes": "admin"},
    )
    assert key_resp.status_code == 201
    plain_key = key_resp.json()["plain_key"]
    return org_id, plain_key


async def _create_scoped_key(
    client: AsyncClient,
    org_id: str,
    admin_key: str,
    scopes: str,
    name: str = "scoped-key",
) -> str:
    """Create an additional API key with specific scopes.

    Returns the plain key string.
    """
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/api-keys",
        json={"name": name, "scopes": scopes},
        headers={"X-API-Key": admin_key},
    )
    assert resp.status_code == 201
    return resp.json()["plain_key"]


# ===================================================================
# 1. Missing auth header → 422 / invalid key → 401
# ===================================================================


@pytest.mark.integration
class TestMissingAuth:
    """Endpoints that require auth reject requests without proper credentials."""

    async def test_get_organization_no_header(self, client: AsyncClient) -> None:
        """GET /organizations/{id} without X-API-Key returns 422 (missing header)."""
        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Auth Missing Org"},
        )
        org_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/organizations/{org_id}")
        assert response.status_code == 422

    async def test_get_organization_invalid_key(self, client: AsyncClient) -> None:
        """GET /organizations/{id} with invalid key returns 401."""
        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Auth Invalid Org"},
        )
        org_id = create_resp.json()["id"]

        # Bootstrap the org so it has a key (needed for the endpoint to not 422)
        await _bootstrap_org(client, "Key Holder Invalid")

        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"X-API-Key": "uc_test_totally_invalid_key_12345"},
        )
        assert response.status_code == 401

    async def test_list_api_keys_no_header(self, client: AsyncClient) -> None:
        """GET /organizations/{id}/api-keys without auth returns 422."""
        org_id, _ = await _bootstrap_org(client, "List Keys No Auth")

        response = await client.get(f"/api/v1/organizations/{org_id}/api-keys")
        assert response.status_code == 422

    async def test_list_api_keys_invalid_key(self, client: AsyncClient) -> None:
        """GET /organizations/{id}/api-keys with invalid key returns 401."""
        org_id, _ = await _bootstrap_org(client, "List Keys Bad Key")

        response = await client.get(
            f"/api/v1/organizations/{org_id}/api-keys",
            headers={"X-API-Key": "uc_test_fake_key_000"},
        )
        assert response.status_code == 401

    async def test_update_organization_no_header(self, client: AsyncClient) -> None:
        """PUT /organizations/{id} without auth returns 422."""
        org_id, _ = await _bootstrap_org(client, "Update No Auth")

        response = await client.put(
            f"/api/v1/organizations/{org_id}",
            json={"name": "Should Fail"},
        )
        assert response.status_code == 422

    async def test_revoke_key_no_header(self, client: AsyncClient) -> None:
        """DELETE /organizations/{id}/api-keys/{key_id} without auth returns 422."""
        org_id, api_key = await _bootstrap_org(client, "Revoke No Auth")

        # Create a key to try to revoke
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "target-key"},
            headers={"X-API-Key": api_key},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.delete(
            f"/api/v1/organizations/{org_id}/api-keys/{key_id}",
        )
        assert response.status_code == 422

    async def test_webhooks_create_no_header(self, client: AsyncClient) -> None:
        """POST /webhooks without X-API-Key returns 422."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/hook",
                "events": ["seed.created"],
            },
        )
        assert response.status_code == 422

    async def test_webhooks_list_no_header(self, client: AsyncClient) -> None:
        """GET /webhooks without X-API-Key returns 422."""
        response = await client.get("/api/v1/webhooks")
        assert response.status_code == 422

    async def test_webhooks_create_invalid_key(self, client: AsyncClient) -> None:
        """POST /webhooks with invalid key returns 401."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/hook",
                "events": ["seed.created"],
            },
            headers={"X-API-Key": "uc_test_bogus_key_xyz"},
        )
        assert response.status_code == 401


# ===================================================================
# 2. Cross-org access denied
# ===================================================================


@pytest.mark.integration
class TestCrossOrgDenied:
    """API key from org A cannot access org B's resources."""

    async def test_get_org_with_wrong_key(self, client: AsyncClient) -> None:
        """Key from org A returns 403 when trying to read org B."""
        org_a_id, key_a = await _bootstrap_org(client, "Org Alpha")
        org_b_id, _key_b = await _bootstrap_org(client, "Org Beta")

        response = await client.get(
            f"/api/v1/organizations/{org_b_id}",
            headers={"X-API-Key": key_a},
        )
        assert response.status_code == 403

    async def test_update_org_with_wrong_key(self, client: AsyncClient) -> None:
        """Key from org A returns 403 when trying to update org B."""
        _org_a_id, key_a = await _bootstrap_org(client, "Org Update Alpha")
        org_b_id, _key_b = await _bootstrap_org(client, "Org Update Beta")

        response = await client.put(
            f"/api/v1/organizations/{org_b_id}",
            json={"name": "Hijacked Name"},
            headers={"X-API-Key": key_a},
        )
        assert response.status_code == 403

    async def test_list_keys_of_other_org(self, client: AsyncClient) -> None:
        """Key from org A returns 403 when listing org B's API keys."""
        _org_a_id, key_a = await _bootstrap_org(client, "Org Keys Alpha")
        org_b_id, _key_b = await _bootstrap_org(client, "Org Keys Beta")

        response = await client.get(
            f"/api/v1/organizations/{org_b_id}/api-keys",
            headers={"X-API-Key": key_a},
        )
        assert response.status_code == 403

    async def test_create_key_in_other_org(self, client: AsyncClient) -> None:
        """Key from org A returns 403 when creating a key in org B."""
        _org_a_id, key_a = await _bootstrap_org(client, "Org Create Alpha")
        org_b_id, _key_b = await _bootstrap_org(client, "Org Create Beta")

        response = await client.post(
            f"/api/v1/organizations/{org_b_id}/api-keys",
            json={"name": "sneaky-key", "scopes": "admin"},
            headers={"X-API-Key": key_a},
        )
        assert response.status_code == 403

    async def test_revoke_key_in_other_org(self, client: AsyncClient) -> None:
        """Key from org A returns 403 when revoking a key in org B."""
        _org_a_id, key_a = await _bootstrap_org(client, "Org Revoke Alpha")
        org_b_id, key_b = await _bootstrap_org(client, "Org Revoke Beta")

        # Create a key in org B to target
        create_resp = await client.post(
            f"/api/v1/organizations/{org_b_id}/api-keys",
            json={"name": "target-key"},
            headers={"X-API-Key": key_b},
        )
        target_key_id = create_resp.json()["key_id"]

        response = await client.delete(
            f"/api/v1/organizations/{org_b_id}/api-keys/{target_key_id}",
            headers={"X-API-Key": key_a},
        )
        assert response.status_code == 403


# ===================================================================
# 3. Scope enforcement
# ===================================================================


@pytest.mark.integration
class TestScopeEnforcement:
    """Read-only keys cannot access admin-scoped endpoints."""

    async def test_read_key_cannot_get_organization(self, client: AsyncClient) -> None:
        """A read-only key is denied access to GET /organizations/{id} (requires admin)."""
        org_id, admin_key = await _bootstrap_org(client, "Scope Read Org")
        read_key = await _create_scoped_key(client, org_id, admin_key, "read", "read-only-key")

        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"X-API-Key": read_key},
        )
        assert response.status_code == 403

    async def test_read_key_cannot_update_organization(self, client: AsyncClient) -> None:
        """A read-only key is denied access to PUT /organizations/{id} (requires admin)."""
        org_id, admin_key = await _bootstrap_org(client, "Scope Update Org")
        read_key = await _create_scoped_key(client, org_id, admin_key, "read", "read-key-update")

        response = await client.put(
            f"/api/v1/organizations/{org_id}",
            json={"name": "Should Fail"},
            headers={"X-API-Key": read_key},
        )
        assert response.status_code == 403

    async def test_read_key_cannot_list_api_keys(self, client: AsyncClient) -> None:
        """A read-only key is denied access to GET /organizations/{id}/api-keys (requires admin)."""
        org_id, admin_key = await _bootstrap_org(client, "Scope List Keys Org")
        read_key = await _create_scoped_key(client, org_id, admin_key, "read", "read-key-list")

        response = await client.get(
            f"/api/v1/organizations/{org_id}/api-keys",
            headers={"X-API-Key": read_key},
        )
        assert response.status_code == 403

    async def test_read_key_cannot_revoke_keys(self, client: AsyncClient) -> None:
        """A read-only key is denied access to DELETE /organizations/{id}/api-keys/{key_id}."""
        org_id, admin_key = await _bootstrap_org(client, "Scope Revoke Org")
        read_key = await _create_scoped_key(client, org_id, admin_key, "read", "read-key-revoke")

        # Create a target key
        create_resp = await client.post(
            f"/api/v1/organizations/{org_id}/api-keys",
            json={"name": "target-key"},
            headers={"X-API-Key": admin_key},
        )
        key_id = create_resp.json()["key_id"]

        response = await client.delete(
            f"/api/v1/organizations/{org_id}/api-keys/{key_id}",
            headers={"X-API-Key": read_key},
        )
        assert response.status_code == 403

    async def test_write_key_cannot_access_admin_endpoints(self, client: AsyncClient) -> None:
        """A write-scoped key is denied access to admin-only endpoints."""
        org_id, admin_key = await _bootstrap_org(client, "Scope Write Org")
        write_key = await _create_scoped_key(client, org_id, admin_key, "read,write", "write-key")

        # GET org requires admin scope
        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"X-API-Key": write_key},
        )
        assert response.status_code == 403

    async def test_admin_key_succeeds_on_admin_endpoints(self, client: AsyncClient) -> None:
        """An admin-scoped key can access admin endpoints (positive control)."""
        org_id, admin_key = await _bootstrap_org(client, "Scope Admin Org")

        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"X-API-Key": admin_key},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Scope Admin Org"
