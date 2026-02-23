"""Integration tests for tool management API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


def _make_tool_definition(
    *,
    name: str = "test_custom_tool",
    domains: list[str] | None = None,
    category: str = "testing",
) -> dict:
    """Build a valid ToolDefinition dict with fictional data."""
    return {
        "name": name,
        "description": "A fictional test tool used for integration testing purposes only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string.",
                },
            },
            "required": ["query"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "domains": domains or ["automotive.sales"],
        "category": category,
        "execution_mode": "simulated",
        "version": "1.0",
    }


@pytest.mark.integration
class TestListTools:
    async def test_list_tools(self, client: AsyncClient) -> None:
        """GET /api/v1/tools/ returns the built-in automotive tools."""
        response = await client.get("/api/v1/tools")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # At minimum the 5 built-in automotive tools should be present
        assert len(data) >= 5

        names = {tool["name"] for tool in data}
        assert "buscar_inventario" in names
        assert "cotizar_vehiculo" in names

    async def test_list_tools_by_domain(self, client: AsyncClient) -> None:
        """Filter tools by domain returns only matching tools."""
        response = await client.get("/api/v1/tools", params={"domain": "automotive.sales"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

        for tool in data:
            assert "automotive.sales" in tool["domains"]

    async def test_list_tools_by_domain_empty(self, client: AsyncClient) -> None:
        """Filter by a non-existent domain returns an empty list."""
        response = await client.get("/api/v1/tools", params={"domain": "nonexistent.domain"})
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.integration
class TestGetTool:
    async def test_get_tool(self, client: AsyncClient) -> None:
        """Retrieve a specific built-in tool by name."""
        response = await client.get("/api/v1/tools/buscar_inventario")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "buscar_inventario"
        assert "description" in data
        assert "input_schema" in data
        assert "output_schema" in data
        assert "automotive.sales" in data["domains"]

    async def test_get_tool_not_found(self, client: AsyncClient) -> None:
        """Return 404 for a tool name that does not exist."""
        response = await client.get("/api/v1/tools/nonexistent_tool_xyz")
        assert response.status_code == 404


@pytest.mark.integration
class TestRegisterTool:
    async def test_register_tool(self, client: AsyncClient) -> None:
        """Register a custom tool and verify it is returned."""
        tool_data = _make_tool_definition(name="integration_test_register")

        response = await client.post("/api/v1/tools", json=tool_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "integration_test_register"
        assert data["category"] == "testing"

    async def test_register_duplicate_tool(self, client: AsyncClient) -> None:
        """Re-registering the same tool name returns 409."""
        tool_data = _make_tool_definition(name="integration_dup_test")

        first = await client.post("/api/v1/tools", json=tool_data)
        assert first.status_code == 201

        second = await client.post("/api/v1/tools", json=tool_data)
        assert second.status_code == 409


@pytest.mark.integration
class TestSimulateTool:
    async def test_simulate_tool(self, client: AsyncClient) -> None:
        """Simulate execution of buscar_inventario with arguments."""
        arguments = {"marca": "Toyota", "tipo": "SUV"}

        response = await client.post(
            "/api/v1/tools/buscar_inventario/simulate",
            json=arguments,
        )
        assert response.status_code == 200

        data = response.json()
        assert "tool_call_id" in data
        assert data["tool_name"] == "buscar_inventario"
        assert data["status"] == "success"
        assert "result" in data
        assert "duration_ms" in data

    async def test_simulate_tool_not_found(self, client: AsyncClient) -> None:
        """Simulating a non-existent tool returns 404."""
        response = await client.post(
            "/api/v1/tools/nonexistent_tool_xyz/simulate",
            json={"query": "test"},
        )
        assert response.status_code == 404
