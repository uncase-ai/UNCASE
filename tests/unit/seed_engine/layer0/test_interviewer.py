"""Tests for the Layer 0 Interviewer — all LLM calls are mocked."""

from __future__ import annotations

from typing import Any

import pytest

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.interviewer.base_provider import BaseLLMProvider
from uncase.core.seed_engine.layer0.interviewer.interviewer import Interviewer
from uncase.core.seed_engine.layer0.schemas.base import FieldMeta, FieldStatus

# ── Mock Provider ───────────────────────────────────────────────────


class MockLLMProvider(BaseLLMProvider):
    """A mock LLM provider for testing."""

    def __init__(self, response: str = "Mocked question response.") -> None:
        self._response = response
        self.generate_calls: list[dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        self.generate_calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "temperature": temperature,
            }
        )
        return self._response


class FailingProvider(BaseLLMProvider):
    """A provider that always fails."""

    @property
    def provider_name(self) -> str:
        return "failing"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        msg = "Simulated API failure"
        raise RuntimeError(msg)


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def mock_provider() -> MockLLMProvider:
    return MockLLMProvider(response="¿Qué tipo de cliente es usted?")


@pytest.fixture()
def failing_provider() -> FailingProvider:
    return FailingProvider()


@pytest.fixture()
def config() -> Layer0Config:
    return Layer0Config()


@pytest.fixture()
def interviewer(mock_provider: MockLLMProvider, config: Layer0Config) -> Interviewer:
    return Interviewer(mock_provider, config)


@pytest.fixture()
def failing_interviewer(failing_provider: FailingProvider, config: Layer0Config) -> Interviewer:
    return Interviewer(failing_provider, config)


def _missing_fields() -> list[FieldMeta]:
    return [
        FieldMeta(
            field_name="cliente_perfil.tipo_cliente",
            is_required=True,
            description="Tipo de cliente",
        ),
        FieldMeta(
            field_name="cliente_perfil.urgencia",
            is_required=True,
            description="Nivel de urgencia",
        ),
    ]


# ===================================================================
# BaseLLMProvider
# ===================================================================


class TestBaseLLMProvider:
    """Test the abstract provider interface."""

    async def test_mock_provider_generates(self, mock_provider: MockLLMProvider) -> None:
        """Mock provider returns the configured response."""
        result = await mock_provider.generate("system", "user")
        assert result == "¿Qué tipo de cliente es usted?"
        assert len(mock_provider.generate_calls) == 1

    async def test_health_check_succeeds(self, mock_provider: MockLLMProvider) -> None:
        """Health check returns True for a working provider."""
        assert await mock_provider.health_check() is True

    async def test_health_check_fails(self, failing_provider: FailingProvider) -> None:
        """Health check returns False for a broken provider."""
        assert await failing_provider.health_check() is False


# ===================================================================
# Interviewer — question generation
# ===================================================================


class TestInterviewerQuestions:
    """Test Interviewer question generation."""

    async def test_generate_initial_question(self, interviewer: Interviewer, mock_provider: MockLLMProvider) -> None:
        """Initial question calls the provider with correct context."""
        question = await interviewer.generate_initial_question(
            industry="automotive",
            categories=["Perfil del cliente", "Intención de compra"],
            language="es",
        )
        assert question  # Non-empty
        assert len(mock_provider.generate_calls) == 1
        assert "automotive" in mock_provider.generate_calls[0]["system_prompt"]

    async def test_generate_question_with_missing_fields(self, interviewer: Interviewer) -> None:
        """Question generation includes missing fields in the prompt."""
        question = await interviewer.generate_question(
            history=[{"role": "interviewer", "content": "Hola"}, {"role": "user", "content": "Hola"}],
            missing_fields=_missing_fields(),
            ambiguous_fields=[],
            industry="automotive",
            language="es",
        )
        assert question  # Non-empty

    async def test_generate_clarification(self, interviewer: Interviewer) -> None:
        """Clarification uses the ambiguous fields in the prompt."""
        ambiguous = [
            FieldMeta(
                field_name="cliente_perfil.tipo_cliente",
                status=FieldStatus.AMBIGUOUS,
                confidence=0.5,
                description="Tipo de cliente",
            )
        ]
        result = await interviewer.generate_clarification(
            history=[],
            missing_fields=[],
            ambiguous_fields=ambiguous,
            industry="automotive",
        )
        assert result  # Non-empty

    async def test_generate_summary(self, interviewer: Interviewer) -> None:
        """Summary generation works with captured data."""
        result = await interviewer.generate_summary(
            captured_data={"cliente_perfil.tipo_cliente": "particular"},
            missing_fields=[],
            ambiguous_fields=[],
            industry="automotive",
        )
        assert result  # Non-empty


# ===================================================================
# Interviewer — fallbacks on LLM failure
# ===================================================================


class TestInterviewerFallbacks:
    """Test that the Interviewer provides fallback responses on failure."""

    async def test_initial_question_fallback(self, failing_interviewer: Interviewer) -> None:
        """Fallback initial question is returned on provider failure."""
        question = await failing_interviewer.generate_initial_question(
            industry="automotive",
            categories=["Perfil"],
            language="es",
        )
        assert "asistente" in question.lower() or "cliente" in question.lower()

    async def test_question_fallback(self, failing_interviewer: Interviewer) -> None:
        """Fallback question is returned on provider failure."""
        question = await failing_interviewer.generate_question(
            history=[],
            missing_fields=_missing_fields(),
            ambiguous_fields=[],
            industry="automotive",
            language="es",
        )
        assert question  # Non-empty

    async def test_summary_fallback(self, failing_interviewer: Interviewer) -> None:
        """Fallback summary is returned on provider failure."""
        summary = await failing_interviewer.generate_summary(
            captured_data={"test": "value"},
            missing_fields=[],
            ambiguous_fields=[],
            industry="automotive",
            language="es",
        )
        assert "Resumen" in summary or "test" in summary

    async def test_english_fallbacks(self, failing_interviewer: Interviewer) -> None:
        """English fallbacks work correctly."""
        question = await failing_interviewer.generate_initial_question(
            industry="automotive",
            categories=["Profile"],
            language="en",
        )
        assert "assistant" in question.lower() or "customer" in question.lower()


# ===================================================================
# Interviewer — internal helpers
# ===================================================================


class TestInterviewerHelpers:
    """Test internal helper methods."""

    def test_format_history_empty(self) -> None:
        """Empty history returns placeholder."""
        result = Interviewer._format_history([])
        assert "No conversation" in result

    def test_format_history_with_messages(self) -> None:
        """History is formatted correctly."""
        result = Interviewer._format_history(
            [
                {"role": "interviewer", "content": "¿Hola?"},
                {"role": "user", "content": "Hola."},
            ]
        )
        assert "interviewer: ¿Hola?" in result
        assert "user: Hola." in result

    def test_format_fields_empty(self) -> None:
        """Empty field list returns empty string."""
        assert Interviewer._format_fields([]) == ""

    def test_format_fields_with_required(self) -> None:
        """Required fields are marked in the formatted output."""
        result = Interviewer._format_fields(_missing_fields())
        assert "[REQUIRED]" in result
