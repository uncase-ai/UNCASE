"""Integration tests for generation API endpoints (Layer 3 synthetic conversation generation).

The generation endpoint calls LiteLLM under the hood, so we mock the LLM call
to avoid real API requests.
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
    """Build a minimal valid SeedSchema dict for generation requests."""
    seed: dict[str, object] = {
        "seed_id": "seed-gen-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["usuario", "asistente"],
        "objetivo": "Cotizar un vehiculo ficticio.",
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


def _mock_litellm_conversation_response() -> MagicMock:
    """Build a mock litellm response that looks like a generated conversation JSON."""
    import json

    conversation = {
        "conversation_id": "conv-gen-mock-001",
        "seed_id": "seed-gen-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            {
                "turno": 1,
                "rol": "usuario",
                "contenido": "Hola, me interesa un vehiculo ficticio.",
            },
            {
                "turno": 2,
                "rol": "asistente",
                "contenido": "Con gusto le ayudo. Tenemos modelos ficticios disponibles.",
            },
        ],
        "es_sintetica": True,
    }

    message = MagicMock()
    message.content = json.dumps(conversation)
    message.tool_calls = None

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = "stop"

    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.mark.integration
class TestGenerateConversations:
    """Test POST /api/v1/generate."""

    async def test_generate_missing_seed(self, client: AsyncClient) -> None:
        """Missing seed in the request body should return 422."""
        body = {"count": 1}
        response = await client.post("/api/v1/generate", json=body)
        assert response.status_code == 422

    async def test_generate_invalid_domain(self, client: AsyncClient) -> None:
        """Seed with unsupported domain should return 422."""
        body = {
            "seed": _make_seed_dict(dominio="unsupported.domain"),
            "count": 1,
        }
        response = await client.post("/api/v1/generate", json=body)
        assert response.status_code == 422

    async def test_generate_invalid_count(self, client: AsyncClient) -> None:
        """Count of 0 should return 422."""
        body = {
            "seed": _make_seed_dict(),
            "count": 0,
        }
        response = await client.post("/api/v1/generate", json=body)
        assert response.status_code == 422

    @patch("uncase.services.generator.LiteLLMGenerator")
    async def test_generate_happy_path(
        self,
        mock_generator_cls: MagicMock,
        client: AsyncClient,
    ) -> None:
        """Successful generation with mocked LLM generator."""
        # Build a mock conversation object that the generator returns
        from uncase.schemas.conversation import Conversation, ConversationTurn

        mock_conversation = Conversation(
            conversation_id="conv-gen-mock-001",
            seed_id="seed-gen-001",
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="usuario",
                    contenido="Hola, me interesa un vehiculo ficticio.",
                ),
                ConversationTurn(
                    turno=2,
                    rol="asistente",
                    contenido="Con gusto le ayudo. Tenemos modelos ficticios disponibles.",
                ),
            ],
            es_sintetica=True,
        )

        mock_instance = MagicMock()
        mock_instance.generate = AsyncMock(return_value=[mock_conversation])
        mock_generator_cls.return_value = mock_instance

        body = {
            "seed": _make_seed_dict(),
            "count": 1,
            "evaluate_after": False,
        }
        response = await client.post("/api/v1/generate", json=body)
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert "generation_summary" in data
        assert data["generation_summary"]["total_generated"] >= 1
