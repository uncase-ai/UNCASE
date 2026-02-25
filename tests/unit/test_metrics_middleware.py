"""Tests for the Prometheus metrics endpoint and middleware counters."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.integration
class TestMetricsEndpoint:
    """Test the /metrics Prometheus endpoint."""

    async def test_metrics_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/metrics")
        assert response.status_code == 200

    async def test_metrics_content_type(self, client: AsyncClient) -> None:
        response = await client.get("/metrics")
        assert "text/plain" in response.headers["content-type"]

    async def test_metrics_contains_active_requests(self, client: AsyncClient) -> None:
        response = await client.get("/metrics")
        assert "uncase_active_requests" in response.text

    async def test_metrics_contains_help_lines(self, client: AsyncClient) -> None:
        response = await client.get("/metrics")
        text = response.text
        assert "# HELP uncase_http_requests_total" in text
        assert "# TYPE uncase_http_requests_total counter" in text

    async def test_metrics_tracks_requests(self, client: AsyncClient) -> None:
        # Make a request to generate metrics
        await client.get("/health")
        response = await client.get("/metrics")
        text = response.text
        assert "uncase_http_requests_total" in text
