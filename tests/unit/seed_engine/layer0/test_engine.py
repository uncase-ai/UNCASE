"""Integration test for the Layer 0 Agentic Extraction Engine.

Simulates a complete 5+ turn interview conversation with mocked LLM
providers. Tests the full flow: Engine → State Manager → Extractor →
Interviewer and back.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.engine import AgenticExtractionEngine
from uncase.core.seed_engine.layer0.extractor import ExtractionResult, ExtractedField, SeedExtractor
from uncase.core.seed_engine.layer0.interviewer.base_provider import BaseLLMProvider
from uncase.core.seed_engine.layer0.interviewer.interviewer import Interviewer
from uncase.core.seed_engine.layer0.schemas.automotriz import SeedAutomotriz
from uncase.core.seed_engine.layer0.state_manager import ActionType


# ── Mock Provider ───────────────────────────────────────────────────


class MockInterviewerProvider(BaseLLMProvider):
    """Provider that returns sequential questions."""

    def __init__(self) -> None:
        self._call_count = 0
        self._questions = [
            "¡Hola! Bienvenido. ¿Qué tipo de cliente será el participante?",
            "¿Cuál es la urgencia de la compra?",
            "¿Cuál es el uso principal del vehículo?",
            "¿Por qué canal se realizará la conversación?",
            "¿Qué tipo de escenario de ventas desea simular?",
            "¿Qué nivel de complejidad tiene el escenario?",
            "¿Qué tono espera para la conversación?",
            "¿Cuál es el nivel de experiencia del cliente comprando vehículos?",
            "Perfecto, aquí está el resumen de lo capturado...",
        ]

    @property
    def provider_name(self) -> str:
        return "mock_interviewer"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        idx = min(self._call_count, len(self._questions) - 1)
        self._call_count += 1
        return self._questions[idx]


# ── Simulated conversation data ─────────────────────────────────────

SIMULATED_CONVERSATION = [
    {
        "user_response": "Soy un cliente particular, estoy explorando opciones.",
        "extraction": {
            "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95},
            "cliente_perfil.urgencia": {"value": "explorando", "confidence": 0.9},
        },
    },
    {
        "user_response": "El vehículo será para uso familiar, principalmente.",
        "extraction": {
            "intencion.uso_principal": {"value": "familia", "confidence": 0.92},
        },
    },
    {
        "user_response": "La conversación será por WhatsApp.",
        "extraction": {
            "contexto_conversacion.canal": {"value": "whatsapp", "confidence": 0.95},
        },
    },
    {
        "user_response": "Es una venta directa, de complejidad media.",
        "extraction": {
            "escenario.tipo_escenario": {"value": "venta_directa", "confidence": 0.93},
            "escenario.complejidad": {"value": "medio", "confidence": 0.9},
        },
    },
    {
        "user_response": "El tono debe ser empático. Es la primera vez que compro.",
        "extraction": {
            "escenario.tono_esperado": {"value": "empático", "confidence": 0.88},
            "cliente_perfil.nivel_experiencia_compra": {"value": "primera_vez", "confidence": 0.92},
        },
    },
]


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def config() -> Layer0Config:
    return Layer0Config(max_turns=10)


@pytest.fixture()
def mock_provider() -> MockInterviewerProvider:
    return MockInterviewerProvider()


@pytest.fixture()
def mock_extractor(config: Layer0Config) -> SeedExtractor:
    """Extractor with mocked LLM that returns predefined extraction results."""
    ext = SeedExtractor(config=config, anthropic_client=AsyncMock())
    return ext


# ===================================================================
# Integration: Turn-by-turn conversation
# ===================================================================


class TestTurnByTurnIntegration:
    """Test the engine's process_turn API with a full simulated conversation."""

    async def test_full_conversation_5_turns(
        self,
        config: Layer0Config,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """Simulate a complete 5-turn interview and verify the seed is filled."""
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        # Get initial question
        initial = await engine.get_initial_question()
        assert initial["type"] == "question"
        assert initial["content"]

        # Process 5 turns with mocked extraction
        for i, turn in enumerate(SIMULATED_CONVERSATION):
            # Mock the extractor to return the predefined result
            mock_ext.extract = AsyncMock(return_value=turn["extraction"])  # type: ignore[method-assign]

            result = await engine.process_turn(turn["user_response"])

            assert result["type"] in {"question", "summary"}
            assert "progress" in result

            progress = result["progress"]
            assert progress["turn"] == i + 1

            # If we got a summary, the loop completed
            if result["type"] == "summary":
                break

        # Verify the seed has captured the main fields
        final_schema = engine.state.get_seed_final()
        assert isinstance(final_schema, SeedAutomotriz)
        assert final_schema.cliente_perfil.tipo_cliente == "particular"
        assert final_schema.intencion.uso_principal == "familia"
        assert final_schema.contexto_conversacion.canal == "whatsapp"
        assert final_schema.escenario.tipo_escenario == "venta_directa"

    async def test_conversation_respects_max_turns(
        self,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """Engine stops when max_turns is reached."""
        config = Layer0Config(max_turns=3)
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())
        mock_ext.extract = AsyncMock(return_value={})  # type: ignore[method-assign]

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        await engine.get_initial_question()

        for i in range(4):
            result = await engine.process_turn("No sé")
            if result["type"] == "summary":
                break

        assert engine.state.turn_count <= 3

    async def test_stop_signal_ends_loop(
        self,
        config: Layer0Config,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """User saying 'listo' ends the conversation."""
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())
        mock_ext.extract = AsyncMock(return_value={})  # type: ignore[method-assign]

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        await engine.get_initial_question()
        result = await engine.process_turn("listo")

        assert result["type"] == "summary"
        assert engine.state.is_complete is True


# ===================================================================
# Integration: Full loop completion
# ===================================================================


class TestFullLoopCompletion:
    """Test that the engine completes when all required fields are filled."""

    async def test_completes_when_all_required_filled(
        self,
        config: Layer0Config,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """Engine reports completion after all required fields have high confidence."""
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        await engine.get_initial_question()

        # Feed all required fields in one extraction
        from uncase.core.seed_engine.layer0.schemas.automotriz import REQUIRED_FIELDS_AUTOMOTRIZ

        all_fields = {name: {"value": "test_value", "confidence": 0.95} for name in REQUIRED_FIELDS_AUTOMOTRIZ}
        mock_ext.extract = AsyncMock(return_value=all_fields)  # type: ignore[method-assign]

        result = await engine.process_turn("Les doy toda la información necesaria.")

        # After processing, the state should be complete
        assert engine.state.is_complete is True

    async def test_history_is_recorded(
        self,
        config: Layer0Config,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """Conversation history is properly recorded."""
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())
        mock_ext.extract = AsyncMock(return_value={})  # type: ignore[method-assign]

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        await engine.get_initial_question()
        await engine.process_turn("Soy un particular.")

        history = engine.history
        # Should have: initial question + user response + next question
        assert len(history) >= 2
        assert any(msg["role"] == "user" for msg in history)
        assert any(msg["role"] == "interviewer" for msg in history)


# ===================================================================
# Integration: Error recovery
# ===================================================================


class TestErrorRecovery:
    """Test that the engine recovers gracefully from extraction errors."""

    async def test_extraction_failure_doesnt_crash(
        self,
        config: Layer0Config,
        mock_provider: MockInterviewerProvider,
    ) -> None:
        """When extraction fails, the loop continues with the next question."""
        schema = SeedAutomotriz()
        interviewer = Interviewer(mock_provider, config)
        mock_ext = SeedExtractor(config=config, anthropic_client=AsyncMock())

        engine = AgenticExtractionEngine(
            config=config,
            schema=schema,
            extractor=mock_ext,
            interviewer=interviewer,
        )

        await engine.get_initial_question()

        # First turn: extraction fails
        mock_ext.extract = AsyncMock(side_effect=Exception("API down"))  # type: ignore[method-assign]
        result = await engine.process_turn("Soy empresa.")

        # Should still return a question (not crash)
        assert result["type"] in {"question", "summary"}
        assert engine.state.turn_count == 1

        # Second turn: extraction works
        mock_ext.extract = AsyncMock(  # type: ignore[method-assign]
            return_value={"cliente_perfil.tipo_cliente": {"value": "empresa", "confidence": 0.9}}
        )
        result = await engine.process_turn("Es para negocio.")
        assert engine.state.turn_count == 2


# ===================================================================
# Integration: Engine factory
# ===================================================================


class TestEngineFactory:
    """Test engine initialization with different configurations."""

    def test_default_initialization(self) -> None:
        """Engine can be created with all defaults (providers will be lazy-loaded)."""
        # This won't call any API — just tests construction
        config = Layer0Config(interviewer_provider="gemini")
        # We need to pass a mock provider to avoid actual API init
        mock = MockInterviewerProvider()
        engine = AgenticExtractionEngine(
            config=config,
            provider=mock,
        )
        assert engine.state.turn_count == 0

    def test_custom_schema(self) -> None:
        """Engine accepts a custom schema instance."""
        schema = SeedAutomotriz(idioma="en")
        mock = MockInterviewerProvider()
        engine = AgenticExtractionEngine(
            config=Layer0Config(),
            schema=schema,
            provider=mock,
        )
        assert engine.state.schema.idioma == "en"
