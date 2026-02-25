"""Integration tests for health endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase._version import __version__

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.integration
class TestHealthEndpoints:
    """Test GET /health — basic liveness probe."""

    async def test_health(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_health_returns_current_version(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        data = response.json()
        assert data["version"] == __version__


@pytest.mark.integration
class TestHealthDBEndpoint:
    """Test GET /health/db — liveness + database connectivity."""

    async def test_health_db(self, client: AsyncClient) -> None:
        response = await client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data

    async def test_health_db_shows_connected(self, client: AsyncClient) -> None:
        response = await client.get("/health/db")
        data = response.json()
        assert data["database"] == "connected"

    async def test_health_db_returns_version(self, client: AsyncClient) -> None:
        response = await client.get("/health/db")
        data = response.json()
        assert data["version"] == __version__
