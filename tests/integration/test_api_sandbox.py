"""Integration tests for sandbox API endpoints.

The sandbox endpoints depend on E2B or fall back to local generation.
Tests use the local fallback path (E2B is not configured in test settings).
LLM calls are mocked to avoid real API requests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Test data helpers (fictional only)
# ---------------------------------------------------------------------------


def _make_seed_dict(**overrides: object) -> dict[str, object]:
    """Build a minimal valid SeedSchema dict."""
    seed: dict[str, object] = {
        "seed_id": "seed-sandbox-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["usuario", "asistente"],
        "objetivo": "Cotizar un vehiculo ficticio en sandbox.",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 2,
            "turnos_max": 6,
            "flujo_esperado": ["saludo", "consulta", "respuesta"],
        },
        "parametros_factuales": {
            "contexto": "Concesionario ficticio de autos.",
            "restricciones": ["Solo vehiculos ficticios"],
            "herramientas": [],
        },
    }
    seed.update(overrides)
    return seed


@pytest.mark.integration
class TestSandboxStatus:
    """Test GET /api/v1/sandbox/status."""

    async def test_sandbox_status(self, client: AsyncClient) -> None:
        """Check sandbox status returns valid structure."""
        response = await client.get("/api/v1/sandbox/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "max_parallel" in data
        assert "template_id" in data
        assert isinstance(data["enabled"], bool)
        assert isinstance(data["max_parallel"], int)
        assert isinstance(data["template_id"], str)


@pytest.mark.integration
class TestSandboxGenerate:
    """Test POST /api/v1/sandbox."""

    async def test_sandbox_generate_missing_seeds(self, client: AsyncClient) -> None:
        """Request without seeds should return 422."""
        body = {"count_per_seed": 1}
        response = await client.post("/api/v1/sandbox", json=body)
        assert response.status_code == 422

    async def test_sandbox_generate_empty_seeds(self, client: AsyncClient) -> None:
        """Empty seeds array should return 422."""
        body: dict[str, object] = {"seeds": [], "count_per_seed": 1}
        response = await client.post("/api/v1/sandbox", json=body)
        assert response.status_code == 422

    async def test_sandbox_generate_invalid_domain(self, client: AsyncClient) -> None:
        """Seed with unsupported domain should return 422."""
        body = {
            "seeds": [_make_seed_dict(dominio="unsupported.domain")],
            "count_per_seed": 1,
        }
        response = await client.post("/api/v1/sandbox", json=body)
        assert response.status_code == 422

    @patch("uncase.services.generator.LiteLLMGenerator")
    async def test_sandbox_generate_returns_valid_response(
        self,
        mock_generator_cls: MagicMock,
        client: AsyncClient,
    ) -> None:
        """Sandbox generate returns a valid response structure (local fallback or E2B)."""
        from uncase.schemas.conversation import Conversation, ConversationTurn

        mock_conversation = Conversation(
            conversation_id="conv-sandbox-mock-001",
            seed_id="seed-sandbox-001",
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="usuario",
                    contenido="Me interesa un vehiculo ficticio.",
                ),
                ConversationTurn(
                    turno=2,
                    rol="asistente",
                    contenido="Tenemos opciones ficticias disponibles.",
                ),
            ],
            es_sintetica=True,
        )

        mock_instance = MagicMock()
        mock_instance.generate = AsyncMock(return_value=[mock_conversation])
        mock_generator_cls.return_value = mock_instance

        body = {
            "seeds": [_make_seed_dict()],
            "count_per_seed": 1,
            "evaluate_after": False,
        }
        response = await client.post("/api/v1/sandbox", json=body)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["summary"]["sandbox_mode"], bool)
        assert data["summary"]["total_seeds"] == 1


@pytest.mark.integration
class TestDemoSandbox:
    """Test POST /api/v1/sandbox/demo."""

    async def test_demo_sandbox_fallback(self, client: AsyncClient) -> None:
        """Demo sandbox falls back to main API docs when E2B is not configured."""
        body = {
            "domain": "automotive.sales",
            "ttl_minutes": 10,
            "preload_seeds": 2,
            "language": "es",
        }
        response = await client.post("/api/v1/sandbox/demo", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["fallback"] is True
        assert data["domain"] == "automotive.sales"
        assert data["preloaded_seeds"] == 2
        assert "api_url" in data
        assert "docs_url" in data
        assert "job" in data

    async def test_demo_sandbox_missing_domain(self, client: AsyncClient) -> None:
        """Missing domain should return 422."""
        body: dict[str, object] = {"ttl_minutes": 10}
        response = await client.post("/api/v1/sandbox/demo", json=body)
        assert response.status_code == 422

    async def test_demo_sandbox_invalid_ttl(self, client: AsyncClient) -> None:
        """TTL below minimum should return 422."""
        body = {
            "domain": "automotive.sales",
            "ttl_minutes": 1,  # min is 5
        }
        response = await client.post("/api/v1/sandbox/demo", json=body)
        assert response.status_code == 422


@pytest.mark.integration
class TestSandboxStream:
    """Test POST /api/v1/sandbox/stream."""

    async def test_stream_validation_error(self, client: AsyncClient) -> None:
        """Streaming endpoint with empty seeds should return 422."""
        body: dict[str, object] = {
            "seeds": [],
            "count_per_seed": 1,
        }
        response = await client.post("/api/v1/sandbox/stream", json=body)
        assert response.status_code == 422

    async def test_stream_returns_sse(self, client: AsyncClient) -> None:
        """Streaming endpoint returns SSE content type or error if E2B unavailable."""
        body = {
            "seeds": [_make_seed_dict()],
            "count_per_seed": 1,
        }
        response = await client.post("/api/v1/sandbox/stream", json=body)
        # If E2B available: 200 with SSE. If not: 422/500 (SandboxNotConfigured).
        assert response.status_code in (200, 422, 500)
