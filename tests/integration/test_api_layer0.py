"""Integration tests for Layer 0 extraction API endpoints.

Layer 0 uses an agentic extraction engine with LLM providers (Gemini/Claude).
We mock the LLM provider to avoid real API calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_initial_question() -> dict[str, object]:
    """Return a mock initial question message."""
    return {
        "type": "question",
        "content": "Bienvenido. Cuenteme sobre el escenario de ventas que desea modelar.",
        "progress": {
            "total_fields": 10,
            "filled_fields": 0,
            "confidence": 0.0,
        },
    }


def _mock_turn_response() -> dict[str, object]:
    """Return a mock turn response (question)."""
    return {
        "type": "question",
        "content": "Excelente. Que tipo de vehiculo se vende en este escenario?",
        "progress": {
            "total_fields": 10,
            "filled_fields": 2,
            "confidence": 0.2,
        },
    }


@pytest.mark.integration
class TestStartExtraction:
    """Test POST /api/v1/seeds/extract/start."""

    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.get_initial_question",
        new_callable=AsyncMock,
    )
    @patch("uncase.core.seed_engine.layer0.engine._create_provider")
    async def test_start_extraction(
        self,
        mock_provider: AsyncMock,
        mock_initial_question: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Start a new extraction session and get the initial question."""
        mock_initial_question.return_value = _mock_initial_question()

        body = {
            "industry": "automotive",
            "max_turns": 10,
            "locale": "es",
        }
        response = await client.post("/api/v1/seeds/extract/start", json=body)
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert data["message"]["type"] == "question"

    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.get_initial_question",
        new_callable=AsyncMock,
    )
    @patch("uncase.core.seed_engine.layer0.engine._create_provider")
    async def test_start_extraction_defaults(
        self,
        mock_provider: AsyncMock,
        mock_initial_question: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Start extraction with default parameters."""
        mock_initial_question.return_value = _mock_initial_question()

        body: dict[str, object] = {}
        response = await client.post("/api/v1/seeds/extract/start", json=body)
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data

    async def test_start_extraction_invalid_industry(self, client: AsyncClient) -> None:
        """Unsupported industry should return 500 (ValueError from engine)."""
        body = {
            "industry": "nonexistent_industry",
            "max_turns": 10,
        }
        # The engine raises ValueError for unsupported industries.
        # Depending on the ASGI transport, this surfaces as a 500 or raises directly.
        try:
            response = await client.post("/api/v1/seeds/extract/start", json=body)
            assert response.status_code == 500
        except (ValueError, ExceptionGroup):
            # Direct propagation through ASGI transport is also acceptable
            pass


@pytest.mark.integration
class TestProcessTurn:
    """Test POST /api/v1/seeds/extract/turn."""

    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.process_turn",
        new_callable=AsyncMock,
    )
    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.get_initial_question",
        new_callable=AsyncMock,
    )
    @patch("uncase.core.seed_engine.layer0.engine._create_provider")
    async def test_process_turn(
        self,
        mock_provider: AsyncMock,
        mock_initial_question: AsyncMock,
        mock_process_turn: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Process a turn in an existing session."""
        mock_initial_question.return_value = _mock_initial_question()
        mock_process_turn.return_value = _mock_turn_response()

        # Start session first
        start_resp = await client.post(
            "/api/v1/seeds/extract/start",
            json={"industry": "automotive"},
        )
        assert start_resp.status_code == 201
        session_id = start_resp.json()["session_id"]

        # Process a turn
        body = {
            "session_id": session_id,
            "user_message": "Vendemos autos compactos y SUVs.",
        }
        response = await client.post("/api/v1/seeds/extract/turn", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "message" in data
        assert "is_complete" in data

    async def test_process_turn_invalid_session(self, client: AsyncClient) -> None:
        """Turn with nonexistent session should return 404."""
        body = {
            "session_id": "nonexistent-session-id",
            "user_message": "Test message.",
        }
        response = await client.post("/api/v1/seeds/extract/turn", json=body)
        assert response.status_code == 404

    async def test_process_turn_missing_message(self, client: AsyncClient) -> None:
        """Turn without user_message should return 422."""
        body = {
            "session_id": "some-session",
        }
        response = await client.post("/api/v1/seeds/extract/turn", json=body)
        assert response.status_code == 422


@pytest.mark.integration
class TestGetProgress:
    """Test GET /api/v1/seeds/extract/{session_id}/progress."""

    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.get_initial_question",
        new_callable=AsyncMock,
    )
    @patch("uncase.core.seed_engine.layer0.engine._create_provider")
    async def test_get_progress(
        self,
        mock_provider: AsyncMock,
        mock_initial_question: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Get progress for an existing session."""
        mock_initial_question.return_value = _mock_initial_question()

        start_resp = await client.post(
            "/api/v1/seeds/extract/start",
            json={"industry": "automotive"},
        )
        session_id = start_resp.json()["session_id"]

        response = await client.get(f"/api/v1/seeds/extract/{session_id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "progress" in data

    async def test_get_progress_invalid_session(self, client: AsyncClient) -> None:
        """Progress for nonexistent session should return 404."""
        response = await client.get("/api/v1/seeds/extract/nonexistent-session/progress")
        assert response.status_code == 404


@pytest.mark.integration
class TestEndSession:
    """Test DELETE /api/v1/seeds/extract/{session_id}."""

    @patch(
        "uncase.core.seed_engine.layer0.engine.AgenticExtractionEngine.get_initial_question",
        new_callable=AsyncMock,
    )
    @patch("uncase.core.seed_engine.layer0.engine._create_provider")
    async def test_end_session(
        self,
        mock_provider: AsyncMock,
        mock_initial_question: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Delete an existing session."""
        mock_initial_question.return_value = _mock_initial_question()

        start_resp = await client.post(
            "/api/v1/seeds/extract/start",
            json={"industry": "automotive"},
        )
        session_id = start_resp.json()["session_id"]

        response = await client.delete(f"/api/v1/seeds/extract/{session_id}")
        assert response.status_code == 204

        # Verify session is gone
        progress_resp = await client.get(f"/api/v1/seeds/extract/{session_id}/progress")
        assert progress_resp.status_code == 404

    async def test_end_session_not_found(self, client: AsyncClient) -> None:
        """Delete nonexistent session should return 404."""
        response = await client.delete("/api/v1/seeds/extract/nonexistent-session")
        assert response.status_code == 404
