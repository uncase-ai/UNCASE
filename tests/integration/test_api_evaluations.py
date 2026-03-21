"""Integration tests for evaluation API endpoints (Layer 2 quality assessment)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Test data helpers (fictional only)
# ---------------------------------------------------------------------------


def _make_seed_dict(**overrides: object) -> dict[str, object]:
    """Build a minimal valid SeedSchema dict."""
    seed: dict[str, object] = {
        "seed_id": "seed-eval-001",
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


def _make_conversation_dict(**overrides: object) -> dict[str, object]:
    """Build a minimal valid Conversation dict."""
    conv: dict[str, object] = {
        "conversation_id": "conv-eval-001",
        "seed_id": "seed-eval-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            {
                "turno": 1,
                "rol": "usuario",
                "contenido": "Busco un vehiculo familiar ficticio.",
            },
            {
                "turno": 2,
                "rol": "asistente",
                "contenido": "Tenemos opciones ficticias de sedan y SUV.",
            },
        ],
        "es_sintetica": True,
    }
    conv.update(overrides)
    return conv


@pytest.mark.integration
class TestEvaluateSingle:
    """Test POST /api/v1/evaluations (single conversation evaluation)."""

    async def test_evaluate_single(self, client: AsyncClient) -> None:
        """Evaluate a single conversation-seed pair."""
        body = {
            "conversation": _make_conversation_dict(),
            "seed": _make_seed_dict(),
        }
        response = await client.post("/api/v1/evaluations", json=body)
        assert response.status_code == 200
        data = response.json()
        assert "composite_score" in data
        assert "passed" in data
        assert "metrics" in data
        assert "conversation_id" in data
        assert data["conversation_id"] == "conv-eval-001"

    async def test_evaluate_single_missing_seed(self, client: AsyncClient) -> None:
        """Missing seed should return 422."""
        body = {
            "conversation": _make_conversation_dict(),
        }
        response = await client.post("/api/v1/evaluations", json=body)
        assert response.status_code == 422

    async def test_evaluate_single_missing_conversation(self, client: AsyncClient) -> None:
        """Missing conversation should return 422."""
        body = {
            "seed": _make_seed_dict(),
        }
        response = await client.post("/api/v1/evaluations", json=body)
        assert response.status_code == 422


@pytest.mark.integration
class TestEvaluateBatch:
    """Test POST /api/v1/evaluations/batch."""

    async def test_evaluate_batch(self, client: AsyncClient) -> None:
        """Evaluate a batch of conversation-seed pairs."""
        body = {
            "pairs": [
                {
                    "conversation": _make_conversation_dict(conversation_id="conv-b1"),
                    "seed": _make_seed_dict(seed_id="seed-b1"),
                },
                {
                    "conversation": _make_conversation_dict(conversation_id="conv-b2"),
                    "seed": _make_seed_dict(seed_id="seed-b2"),
                },
            ],
        }
        response = await client.post("/api/v1/evaluations/batch", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert "passed" in data
        assert "failed" in data
        assert "pass_rate" in data
        assert "avg_composite_score" in data
        assert "reports" in data

    async def test_evaluate_batch_empty(self, client: AsyncClient) -> None:
        """Empty batch should return 422."""
        body: dict[str, list[object]] = {"pairs": []}
        response = await client.post("/api/v1/evaluations/batch", json=body)
        assert response.status_code == 422


@pytest.mark.integration
class TestListReports:
    """Test GET /api/v1/evaluations/reports."""

    async def test_list_reports_empty(self, client: AsyncClient) -> None:
        """List reports when no evaluations have been run."""
        response = await client.get("/api/v1/evaluations/reports")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_reports_after_evaluation(self, client: AsyncClient) -> None:
        """Run an evaluation, then list reports."""
        # First, run an evaluation
        body = {
            "conversation": _make_conversation_dict(),
            "seed": _make_seed_dict(),
        }
        eval_resp = await client.post("/api/v1/evaluations", json=body)
        assert eval_resp.status_code == 200

        # Now list reports
        response = await client.get("/api/v1/evaluations/reports")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1


@pytest.mark.integration
class TestGetThresholds:
    """Test GET /api/v1/evaluations/thresholds."""

    async def test_get_thresholds(self, client: AsyncClient) -> None:
        """Retrieve current quality thresholds."""
        response = await client.get("/api/v1/evaluations/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert "rouge_l_min" in data
        assert "fidelidad_min" in data
        assert "formula" in data
