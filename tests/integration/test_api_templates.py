"""Integration tests for template rendering API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


def _make_conversation_dict(
    *,
    seed_id: str = "seed-test-001",
    dominio: str = "automotive.sales",
) -> dict:
    """Build a minimal Conversation dict with fictional data."""
    return {
        "seed_id": seed_id,
        "dominio": dominio,
        "idioma": "es",
        "turnos": [
            {
                "turno": 1,
                "rol": "usuario",
                "contenido": "Busco un vehículo familiar con buen rendimiento.",
            },
            {
                "turno": 2,
                "rol": "asistente",
                "contenido": "Con gusto le ayudo. ¿Tiene alguna preferencia de marca o presupuesto?",
            },
        ],
        "es_sintetica": True,
        "metadata": {},
    }


@pytest.mark.integration
class TestListTemplates:
    async def test_list_templates(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/templates")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for item in data:
            assert "name" in item
            assert "display_name" in item
            assert "supports_tool_calls" in item
            assert isinstance(item["supports_tool_calls"], bool)
            assert "special_tokens" in item


@pytest.mark.integration
class TestRenderTemplate:
    async def test_render_template(self, client: AsyncClient) -> None:
        """Render a conversation with the chatml template."""
        body = {
            "conversations": [_make_conversation_dict()],
            "template_name": "chatml",
            "tool_call_mode": "none",
        }

        response = await client.post("/api/v1/templates/render", json=body)
        assert response.status_code == 200

        data = response.json()
        assert "rendered" in data
        assert isinstance(data["rendered"], list)
        assert data["count"] == 1
        assert data["template_name"] == "chatml"
        assert len(data["rendered"][0]) > 0

    async def test_render_template_multiple_conversations(self, client: AsyncClient) -> None:
        """Render multiple conversations in a single request."""
        body = {
            "conversations": [
                _make_conversation_dict(seed_id="seed-a"),
                _make_conversation_dict(seed_id="seed-b"),
            ],
            "template_name": "chatml",
        }

        response = await client.post("/api/v1/templates/render", json=body)
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 2
        assert len(data["rendered"]) == 2

    async def test_render_template_not_found(self, client: AsyncClient) -> None:
        """Return 404 when the template name does not exist."""
        body = {
            "conversations": [_make_conversation_dict()],
            "template_name": "nonexistent_template_xyz",
        }

        response = await client.post("/api/v1/templates/render", json=body)
        assert response.status_code == 404

    async def test_render_template_with_system_prompt(self, client: AsyncClient) -> None:
        """Render with a custom system prompt."""
        body = {
            "conversations": [_make_conversation_dict()],
            "template_name": "chatml",
            "system_prompt": "You are an automotive sales assistant.",
        }

        response = await client.post("/api/v1/templates/render", json=body)
        assert response.status_code == 200
        assert "You are an automotive sales assistant." in response.json()["rendered"][0]


@pytest.mark.integration
class TestExportTemplate:
    async def test_export_template(self, client: AsyncClient) -> None:
        """Export should return text/plain content."""
        body = {
            "conversations": [_make_conversation_dict()],
            "template_name": "chatml",
        }

        response = await client.post("/api/v1/templates/export", json=body)
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "Content-Disposition" in response.headers
        assert len(response.text) > 0

    async def test_export_template_not_found(self, client: AsyncClient) -> None:
        """Export with unknown template should return 404."""
        body = {
            "conversations": [_make_conversation_dict()],
            "template_name": "nonexistent_template_xyz",
        }

        response = await client.post("/api/v1/templates/export", json=body)
        assert response.status_code == 404
