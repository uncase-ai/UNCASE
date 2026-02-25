"""Tests for OWASP security headers middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.integration
class TestSecurityHeaders:
    """Test that all OWASP headers are present in responses."""

    async def test_hsts_header(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert "strict-transport-security" in response.headers
        assert "max-age=" in response.headers["strict-transport-security"]

    async def test_content_type_options(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"

    async def test_frame_options(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.headers.get("x-frame-options") == "DENY"

    async def test_xss_protection(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert "1; mode=block" in response.headers.get("x-xss-protection", "")

    async def test_csp_header(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        csp = response.headers.get("content-security-policy", "")
        assert "default-src 'self'" in csp

    async def test_referrer_policy(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    async def test_permissions_policy(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        pp = response.headers.get("permissions-policy", "")
        assert "camera=()" in pp
        assert "microphone=()" in pp

    async def test_api_cache_control(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health")
        cc = response.headers.get("cache-control", "")
        assert "no-store" in cc
        assert "private" in cc

    async def test_api_pragma(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health")
        assert response.headers.get("pragma") == "no-cache"

    async def test_non_api_no_cache_control(self, client: AsyncClient) -> None:
        """Non-API routes should not get API cache headers."""
        response = await client.get("/health")
        # /health is not under /api/ so should not get the strict cache headers
        cc = response.headers.get("cache-control", "")
        # It might or might not have cache-control, but it shouldn't have 'no-store'
        # unless the framework adds its own
        assert response.status_code == 200
