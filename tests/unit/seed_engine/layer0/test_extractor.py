"""Tests for the Layer 0 Extractor — all LLM calls are mocked."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.extractor import ExtractedField, ExtractionResult, SeedExtractor

# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def config() -> Layer0Config:
    return Layer0Config()


@pytest.fixture()
def mock_anthropic_client() -> AsyncMock:
    """Return a mock Anthropic client."""
    client = AsyncMock()
    return client


@pytest.fixture()
def extractor(config: Layer0Config, mock_anthropic_client: AsyncMock) -> SeedExtractor:
    """Extractor with a mocked Anthropic client."""
    return SeedExtractor(config=config, anthropic_client=mock_anthropic_client)


# ===================================================================
# ExtractionResult model
# ===================================================================


class TestExtractionResultModel:
    """Test ExtractionResult and ExtractedField Pydantic models."""

    def test_extracted_field_creation(self) -> None:
        """ExtractedField can be instantiated."""
        field = ExtractedField(
            field_name="cliente_perfil.tipo_cliente",
            value="particular",
            confidence=0.95,
            reasoning="User explicitly stated 'soy un particular'.",
        )
        assert field.confidence == 0.95
        assert field.value == "particular"

    def test_extraction_result_creation(self) -> None:
        """ExtractionResult can hold multiple fields."""
        result = ExtractionResult(
            fields=[
                ExtractedField(field_name="a", value="x", confidence=0.9),
                ExtractedField(field_name="b", value="y", confidence=0.7),
            ],
            notes="Test extraction.",
        )
        assert len(result.fields) == 2


# ===================================================================
# SeedExtractor.extract — mock _call_llm directly
# ===================================================================


class TestExtractorWithMockedLLM:
    """Test extraction by mocking _call_llm (bypasses instructor/anthropic)."""

    async def test_extract_returns_dict(self, extractor: SeedExtractor) -> None:
        """extract() returns a dict of field_name -> {value, confidence}."""
        mock_result = ExtractionResult(
            fields=[
                ExtractedField(
                    field_name="cliente_perfil.tipo_cliente",
                    value="particular",
                    confidence=0.95,
                ),
                ExtractedField(
                    field_name="cliente_perfil.urgencia",
                    value="decidiendo",
                    confidence=0.85,
                ),
            ]
        )

        extractor._call_llm = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

        result = await extractor.extract(
            conversation_history=[
                {"role": "interviewer", "content": "¿Qué tipo de cliente es?"},
                {"role": "user", "content": "Soy un particular que está decidiendo."},
            ],
            current_schema_state={},
        )

        assert "cliente_perfil.tipo_cliente" in result
        assert result["cliente_perfil.tipo_cliente"]["value"] == "particular"
        assert result["cliente_perfil.tipo_cliente"]["confidence"] == 0.95
        assert result["cliente_perfil.urgencia"]["confidence"] == 0.85

    async def test_extract_handles_api_failure(self, extractor: SeedExtractor) -> None:
        """extract() returns empty dict on API failure."""
        extractor._call_llm = AsyncMock(side_effect=Exception("API Error"))  # type: ignore[method-assign]

        result = await extractor.extract(
            conversation_history=[
                {"role": "user", "content": "test"},
            ],
            current_schema_state={},
        )

        assert result == {}

    async def test_extract_empty_conversation(self, extractor: SeedExtractor) -> None:
        """extract() handles empty conversation gracefully."""
        mock_result = ExtractionResult(fields=[])
        extractor._call_llm = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

        result = await extractor.extract(
            conversation_history=[],
            current_schema_state={},
        )

        assert result == {}

    async def test_extract_multiple_fields(self, extractor: SeedExtractor) -> None:
        """extract() handles multiple fields in one pass."""
        mock_result = ExtractionResult(
            fields=[
                ExtractedField(field_name="cliente_perfil.tipo_cliente", value="empresa", confidence=0.9),
                ExtractedField(field_name="intencion.uso_principal", value="negocio", confidence=0.88),
                ExtractedField(field_name="escenario.complejidad", value="complejo", confidence=0.75),
            ]
        )
        extractor._call_llm = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

        result = await extractor.extract(
            conversation_history=[{"role": "user", "content": "Somos una empresa..."}],
            current_schema_state={},
        )

        assert len(result) == 3
        assert result["escenario.complejidad"]["confidence"] == 0.75


# ===================================================================
# SeedExtractor — prompt building
# ===================================================================


class TestPromptBuilding:
    """Test internal prompt construction."""

    def test_prompt_includes_conversation(self, extractor: SeedExtractor) -> None:
        """Built prompt includes the conversation history."""
        prompt = extractor._build_prompt(
            conversation_history=[
                {"role": "interviewer", "content": "¿Tipo de cliente?"},
                {"role": "user", "content": "Soy empresa."},
            ],
            current_state={"idioma": "es"},
        )
        assert "tipo de cliente" in prompt.lower()
        assert "empresa" in prompt.lower()

    def test_prompt_includes_current_state(self, extractor: SeedExtractor) -> None:
        """Built prompt includes the current schema state."""
        prompt = extractor._build_prompt(
            conversation_history=[],
            current_state={"cliente_perfil.tipo_cliente": "particular"},
        )
        assert "particular" in prompt

    def test_prompt_includes_field_descriptions(self, extractor: SeedExtractor) -> None:
        """Built prompt includes field descriptions when provided."""
        prompt = extractor._build_prompt(
            conversation_history=[],
            current_state={},
            field_descriptions={"cliente_perfil.tipo_cliente": "Tipo de cliente"},
        )
        assert "Tipo de cliente" in prompt
