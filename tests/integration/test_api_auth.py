"""Integration tests for the Auth API endpoints."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from uncase.services.auth import _create_jwt

if TYPE_CHECKING:
    from httpx import AsyncClient


# Must match the `api_secret_key` in conftest.py settings fixture
SECRET = "test-secret"  # noqa: S105


@pytest.mark.integration
class TestVerifyEndpoint:
    """Test POST /api/v1/auth/verify — no DB required."""

    async def test_verify_valid_token(self, client: AsyncClient) -> None:
        token = _create_jwt(
            {"sub": "org123", "org_id": "org123", "role": "admin", "scopes": "read write admin"},
            SECRET,
            timedelta(hours=1),
        )
        response = await client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["org_id"] == "org123"
        assert data["role"] == "admin"

    async def test_verify_expired_token(self, client: AsyncClient) -> None:
        token = _create_jwt(
            {"sub": "org123"},
            SECRET,
            timedelta(seconds=-1),
        )
        response = await client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    async def test_verify_no_auth_header(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    async def test_verify_malformed_header(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": "NotBearer token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    async def test_verify_garbage_token(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": "Bearer garbage.token.here"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


@pytest.mark.integration
class TestLoginEndpoint:
    """Test POST /api/v1/auth/login — requires valid API key in DB."""

    async def test_login_invalid_key(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={"api_key": "invalid-key-that-does-not-exist"},
        )
        # Should fail authentication
        assert response.status_code in (401, 404, 500)

    async def test_login_empty_key(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={"api_key": ""},
        )
        assert response.status_code in (401, 404, 422, 500)

    async def test_login_missing_field(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={},
        )
        assert response.status_code == 422  # Pydantic validation error


@pytest.mark.integration
class TestRefreshEndpoint:
    """Test POST /api/v1/auth/refresh."""

    async def test_refresh_invalid_token(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code in (401, 500)

    async def test_refresh_access_token_rejected(self, client: AsyncClient) -> None:
        """An access token (without type=refresh) should be rejected."""
        access_token = _create_jwt(
            {"sub": "org123", "org_id": "org123", "role": "admin"},
            SECRET,
            timedelta(hours=1),
        )
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        # Should fail — not a refresh token
        assert response.status_code in (401, 500)

    async def test_refresh_missing_field(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/refresh",
            json={},
        )
        assert response.status_code == 422
