"""Tests for the LiteLLM-based synthetic conversation generator (Layer 3).

All test data is fictional — no real PII.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.factories import make_seed
from uncase.core.generator.litellm_generator import (
    GenerationConfig,
    LiteLLMGenerator,
    _build_feedback_augmentation,
    _build_system_prompt,
    _parse_llm_response,
)
from uncase.exceptions import GenerationError
from uncase.schemas.conversation import ConversationTurn
from uncase.schemas.quality import QualityMetrics, QualityReport


# ─── GenerationConfig tests ───


class TestGenerationConfig:
    """Tests for the GenerationConfig dataclass."""

    def test_default_values(self) -> None:
        config = GenerationConfig()

        assert config.model == "claude-sonnet-4-20250514"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.language_override is None
        assert config.max_retries == 2
        assert config.temperature_variation == 0.05
        assert config.api_base is None

    def test_custom_values(self) -> None:
        config = GenerationConfig(
            model="gpt-4o",
            temperature=0.9,
            max_tokens=2048,
            language_override="en",
            max_retries=5,
            temperature_variation=0.1,
            api_base="https://api.example.com",
        )

        assert config.model == "gpt-4o"
        assert config.temperature == 0.9
        assert config.max_tokens == 2048
        assert config.language_override == "en"
        assert config.max_retries == 5
        assert config.temperature_variation == 0.1
        assert config.api_base == "https://api.example.com"


# ─── _build_system_prompt tests ───


class TestBuildSystemPrompt:
    """Tests for the system prompt builder."""

    def test_includes_domain_context(self) -> None:
        seed = make_seed(dominio="automotive.sales")
        prompt = _build_system_prompt(seed)

        assert "automotive sales domain" in prompt
        assert "dealership" in prompt.lower()

    def test_includes_all_six_domains(self) -> None:
        domains = [
            "automotive.sales",
            "medical.consultation",
            "legal.advisory",
            "finance.advisory",
            "industrial.support",
            "education.tutoring",
        ]
        for domain in domains:
            seed = make_seed(dominio=domain)
            prompt = _build_system_prompt(seed)
            # Each domain should have unique content
            assert domain.split(".")[0] in prompt.lower()

    def test_each_domain_has_specific_context(self) -> None:
        """Each supported domain should produce distinct prompt context."""
        prompts = {}
        for domain in ["automotive.sales", "medical.consultation", "legal.advisory"]:
            seed = make_seed(dominio=domain)
            prompts[domain] = _build_system_prompt(seed)

        # Prompts for different domains should be different
        assert prompts["automotive.sales"] != prompts["medical.consultation"]
        assert prompts["legal.advisory"] != prompts["automotive.sales"]

    def test_includes_objective(self) -> None:
        seed = make_seed(objetivo="Consulta ficticia sobre vehiculos de prueba")
        prompt = _build_system_prompt(seed)

        assert "Consulta ficticia sobre vehiculos de prueba" in prompt

    def test_includes_roles_and_descriptions(self) -> None:
        seed = make_seed(
            roles=["medico", "paciente"],
            descripcion_roles={
                "medico": "Medico ficticio especialista",
                "paciente": "Paciente ficticio con sintomas",
            },
        )
        prompt = _build_system_prompt(seed)

        assert '"medico"' in prompt
        assert '"paciente"' in prompt
        assert "Medico ficticio especialista" in prompt
        assert "Paciente ficticio con sintomas" in prompt

    def test_includes_turn_constraints(self) -> None:
        from uncase.schemas.seed import PasosTurnos

        seed = make_seed(
            pasos_turnos=PasosTurnos(
                turnos_min=4,
                turnos_max=12,
                flujo_esperado=["saludo", "diagnostico", "tratamiento"],
            ),
        )
        prompt = _build_system_prompt(seed)

        assert "4" in prompt and "12" in prompt
        assert "saludo" in prompt
        assert "diagnostico" in prompt
        assert "tratamiento" in prompt

    def test_includes_factual_constraints(self) -> None:
        from uncase.schemas.seed import ParametrosFactuales

        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario ficticio de prueba",
                restricciones=["Solo vehiculos 2024", "Precios en MXN"],
                herramientas=["crm"],
                metadata={},
            ),
        )
        prompt = _build_system_prompt(seed)

        assert "Solo vehiculos 2024" in prompt
        assert "Precios en MXN" in prompt

    def test_includes_tools_section(self) -> None:
        from uncase.schemas.seed import ParametrosFactuales

        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario ficticio de prueba",
                restricciones=[],
                herramientas=["crm", "calculadora_financiera"],
                metadata={},
            ),
        )
        prompt = _build_system_prompt(seed)

        assert "crm" in prompt
        assert "calculadora_financiera" in prompt
        assert "herramientas_usadas" in prompt

    def test_language_override(self) -> None:
        seed = make_seed(idioma="es")
        prompt = _build_system_prompt(seed, language="en")

        assert "English" in prompt

    def test_default_language_from_seed(self) -> None:
        seed = make_seed(idioma="es")
        prompt = _build_system_prompt(seed)

        assert "Spanish" in prompt

    def test_output_format_instructions(self) -> None:
        seed = make_seed()
        prompt = _build_system_prompt(seed)

        assert "JSON array" in prompt
        assert '"turno"' in prompt
        assert '"rol"' in prompt
        assert '"contenido"' in prompt
        assert '"herramientas_usadas"' in prompt

    def test_quality_requirements_section(self) -> None:
        seed = make_seed()
        prompt = _build_system_prompt(seed)

        assert "NEVER include any real personal information" in prompt
        assert "factual accuracy" in prompt.lower() or "Factual Constraints" in prompt

    def test_no_tools_section_when_empty(self) -> None:
        from uncase.schemas.seed import ParametrosFactuales

        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario ficticio",
                restricciones=[],
                herramientas=[],
                metadata={},
            ),
        )
        prompt = _build_system_prompt(seed)

        assert "Available Tools" not in prompt


# ─── _build_feedback_augmentation tests ───


class TestBuildFeedbackAugmentation:
    """Tests for quality feedback augmentation of prompts."""

    def _make_report(self, failures: list[str]) -> QualityReport:
        return QualityReport(
            conversation_id="test_conv_001",
            seed_id="test_seed_001",
            metrics=QualityMetrics(
                rouge_l=0.5,
                fidelidad_factual=0.5,
                diversidad_lexica=0.5,
                coherencia_dialogica=0.5,
                privacy_score=0.0,
                memorizacion=0.0,
            ),
            composite_score=0.5,
            passed=False,
            failures=failures,
        )

    def test_no_failures_returns_empty(self) -> None:
        report = self._make_report([])
        assert _build_feedback_augmentation(report) == ""

    def test_coherence_failure_adds_instructions(self) -> None:
        report = self._make_report(["coherencia_dialogica=0.60 (min 0.85)"])
        result = _build_feedback_augmentation(report)

        assert "Dialog Coherence" in result
        assert "responds to or builds upon" in result

    def test_diversity_failure_adds_instructions(self) -> None:
        report = self._make_report(["diversidad_lexica=0.40 (min 0.55)"])
        result = _build_feedback_augmentation(report)

        assert "Lexical Diversity" in result
        assert "varied vocabulary" in result

    def test_rouge_failure_adds_instructions(self) -> None:
        report = self._make_report(["rouge_l=0.50 (min 0.65)"])
        result = _build_feedback_augmentation(report)

        assert "Structural Coherence" in result

    def test_fidelity_failure_adds_instructions(self) -> None:
        report = self._make_report(["fidelidad_factual=0.80 (min 0.90)"])
        result = _build_feedback_augmentation(report)

        assert "Factual Fidelity" in result

    def test_privacy_failure_adds_critical_instructions(self) -> None:
        report = self._make_report(["privacy_score=0.05 (must be 0.0)"])
        result = _build_feedback_augmentation(report)

        assert "Privacy (CRITICAL)" in result
        assert "ABSOLUTELY NO" in result

    def test_memorization_failure_adds_instructions(self) -> None:
        report = self._make_report(["memorizacion=0.02 (must be < 0.01)"])
        result = _build_feedback_augmentation(report)

        assert "Originality" in result

    def test_multiple_failures_all_addressed(self) -> None:
        report = self._make_report([
            "coherencia_dialogica=0.60 (min 0.85)",
            "diversidad_lexica=0.40 (min 0.55)",
            "privacy_score=0.05 (must be 0.0)",
        ])
        result = _build_feedback_augmentation(report)

        assert "Dialog Coherence" in result
        assert "Lexical Diversity" in result
        assert "Privacy (CRITICAL)" in result


# ─── _parse_llm_response tests ───


class TestParseLlmResponse:
    """Tests for LLM response parsing strategies."""

    def _seed(self) -> object:
        return make_seed()

    def test_parse_clean_json_array(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hola, en que puedo ayudarle?", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Busco un vehiculo.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2
        assert turns[0].rol == "vendedor"
        assert turns[1].rol == "cliente"

    def test_parse_json_in_markdown_code_block(self) -> None:
        seed = make_seed()
        raw = """Here is the conversation:
```json
[
  {"turno": 1, "rol": "vendedor", "contenido": "Buenos dias.", "herramientas_usadas": []},
  {"turno": 2, "rol": "cliente", "contenido": "Hola, busco informacion.", "herramientas_usadas": []}
]
```"""

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2
        assert turns[0].contenido == "Buenos dias."

    def test_parse_json_from_surrounding_text(self) -> None:
        seed = make_seed()
        raw = """I'll generate the conversation now.
[
  {"turno": 1, "rol": "vendedor", "contenido": "Bienvenido al concesionario.", "herramientas_usadas": []},
  {"turno": 2, "rol": "cliente", "contenido": "Gracias, busco un sedan.", "herramientas_usadas": []}
]
That's the output."""

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2

    def test_parse_renumbers_turns_sequentially(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 5, "rol": "vendedor", "contenido": "Primera linea.", "herramientas_usadas": []},
            {"turno": 10, "rol": "cliente", "contenido": "Segunda linea.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert turns[0].turno == 1
        assert turns[1].turno == 2

    def test_parse_skips_empty_content(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hola.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "", "herramientas_usadas": []},
            {"turno": 3, "rol": "vendedor", "contenido": "Que necesita?", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2
        assert turns[0].contenido == "Hola."
        assert turns[1].contenido == "Que necesita?"

    def test_parse_handles_missing_turno_field(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"rol": "vendedor", "contenido": "Buenos dias.", "herramientas_usadas": []},
            {"rol": "cliente", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2
        assert turns[0].turno == 1
        assert turns[1].turno == 2

    def test_parse_handles_missing_herramientas(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Buenos dias."},
            {"turno": 2, "rol": "cliente", "contenido": "Hola."},
        ])

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 2
        assert turns[0].herramientas_usadas == []

    def test_parse_preserves_tool_usage(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Busco en inventario.", "herramientas_usadas": ["crm"]},
            {"turno": 2, "rol": "cliente", "contenido": "Gracias.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert turns[0].herramientas_usadas == ["crm"]
        assert turns[1].herramientas_usadas == []

    def test_parse_unknown_role_assigned_from_seed(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente"])
        raw = json.dumps([
            {"turno": 1, "rol": "", "contenido": "Buenos dias.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        # Empty role should be replaced with seed role
        assert turns[0].rol in {"vendedor", "cliente"}

    def test_parse_raises_on_invalid_json(self) -> None:
        seed = make_seed()

        with pytest.raises(GenerationError, match="Failed to parse"):
            _parse_llm_response("This is not JSON at all", seed)

    def test_parse_raises_on_json_object_not_array(self) -> None:
        seed = make_seed()

        with pytest.raises(GenerationError, match="Expected JSON array"):
            _parse_llm_response('{"key": "value"}', seed)

    def test_parse_raises_on_empty_array(self) -> None:
        seed = make_seed()

        with pytest.raises(GenerationError, match="empty array"):
            _parse_llm_response("[]", seed)

    def test_parse_raises_when_all_turns_invalid(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": ""},
            {"turno": 2, "rol": "cliente", "contenido": "   "},
        ])

        with pytest.raises(GenerationError, match="No valid turns"):
            _parse_llm_response(raw, seed)

    def test_parse_skips_non_dict_items(self) -> None:
        seed = make_seed()
        raw = json.dumps([
            "not a dict",
            {"turno": 1, "rol": "vendedor", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        turns = _parse_llm_response(raw, seed)

        assert len(turns) == 1
        assert turns[0].contenido == "Hola."


# ─── LiteLLMGenerator tests ───


class TestLiteLLMGenerator:
    """Tests for the LiteLLMGenerator class."""

    def test_init_default_config(self) -> None:
        gen = LiteLLMGenerator()

        assert gen._config.model == "claude-sonnet-4-20250514"
        assert gen._config.temperature == 0.7
        assert gen._api_key is None
        assert gen._api_base is None

    def test_init_custom_config(self) -> None:
        config = GenerationConfig(model="gpt-4o", temperature=0.5)
        gen = LiteLLMGenerator(config=config, api_key="test-key", api_base="https://api.example.com")

        assert gen._config.model == "gpt-4o"
        assert gen._api_key == "test-key"
        assert gen._api_base == "https://api.example.com"

    def test_api_base_from_config_fallback(self) -> None:
        config = GenerationConfig(api_base="https://config.example.com")
        gen = LiteLLMGenerator(config=config)

        assert gen._api_base == "https://config.example.com"

    def test_api_base_direct_overrides_config(self) -> None:
        config = GenerationConfig(api_base="https://config.example.com")
        gen = LiteLLMGenerator(config=config, api_base="https://direct.example.com")

        assert gen._api_base == "https://direct.example.com"

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_single_conversation(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Buenos dias, bienvenido al concesionario.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Hola, estoy interesado en un vehiculo.", "herramientas_usadas": []},
            {"turno": 3, "rol": "vendedor", "contenido": "Con gusto, que tipo de vehiculo busca?", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator()
        result = await gen.generate(seed, count=1)

        assert len(result) == 1
        conv = result[0]
        assert conv.seed_id == seed.seed_id
        assert conv.dominio == "automotive.sales"
        assert conv.idioma == "es"
        assert conv.es_sintetica is True
        assert conv.num_turnos == 3
        assert conv.metadata["generator"] == "litellm"

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_multiple_conversations(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Bienvenido.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Gracias.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator()
        result = await gen.generate(seed, count=3)

        assert len(result) == 3
        ids = {c.conversation_id for c in result}
        assert len(ids) == 3

        for conv in result:
            assert conv.es_sintetica is True
            assert conv.seed_id == seed.seed_id

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_temperature_variation(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hola.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        config = GenerationConfig(temperature=0.7, temperature_variation=0.1)
        gen = LiteLLMGenerator(config=config)
        await gen.generate(seed, count=3)

        assert mock_acompletion.call_count == 3
        temps = [call.kwargs["temperature"] for call in mock_acompletion.call_args_list]
        assert len(set(temps)) > 1

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_language_override(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed(idioma="es")
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hello, how can I help you?", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "I need information about vehicles.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        config = GenerationConfig(language_override="en")
        gen = LiteLLMGenerator(config=config)
        result = await gen.generate(seed, count=1)

        assert result[0].idioma == "en"

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_empty_response_raises(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=""))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator()

        with pytest.raises(GenerationError, match="empty response"):
            await gen.generate(seed, count=1)

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_invalid_json_response_raises(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="This is not valid JSON"))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator()

        with pytest.raises(GenerationError, match="Failed to parse"):
            await gen.generate(seed, count=1)

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_retries_without_response_format(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hola.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.side_effect = [RuntimeError("response_format not supported"), mock_response]

        gen = LiteLLMGenerator()
        result = await gen.generate(seed, count=1)

        assert len(result) == 1
        assert mock_acompletion.call_count == 2

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_all_retries_exhausted_raises(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()

        mock_acompletion.side_effect = RuntimeError("API unavailable")

        config = GenerationConfig(max_retries=2)
        gen = LiteLLMGenerator(config=config)

        with pytest.raises(GenerationError, match="failed after"):
            await gen.generate(seed, count=1)

        assert mock_acompletion.call_count == 3

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_passes_api_key(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Hola.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator(api_key="sk-test-ficticio-123")
        await gen.generate(seed, count=1)

        call_kwargs = mock_acompletion.call_args.kwargs
        assert call_kwargs["api_key"] == "sk-test-ficticio-123"

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_metadata_includes_model_and_index(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Buenos dias.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Hola.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator()
        result = await gen.generate(seed, count=2)

        assert result[0].metadata["generation_index"] == "0"
        assert result[1].metadata["generation_index"] == "1"
        assert result[0].metadata["model"] == "claude-sonnet-4-20250514"

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_with_feedback(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()
        raw_response = json.dumps([
            {"turno": 1, "rol": "vendedor", "contenido": "Bienvenido al concesionario.", "herramientas_usadas": []},
            {"turno": 2, "rol": "cliente", "contenido": "Gracias, busco informacion.", "herramientas_usadas": []},
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_response))]
        mock_acompletion.return_value = mock_response

        report = QualityReport(
            conversation_id="test_conv_001",
            seed_id=seed.seed_id,
            metrics=QualityMetrics(
                rouge_l=0.5,
                fidelidad_factual=0.5,
                diversidad_lexica=0.5,
                coherencia_dialogica=0.5,
                privacy_score=0.0,
                memorizacion=0.0,
            ),
            composite_score=0.5,
            passed=False,
            failures=["coherencia_dialogica=0.50 (min 0.85)"],
        )

        gen = LiteLLMGenerator()
        result = await gen.generate_with_feedback(seed, report)

        assert len(result) == 1
        assert result[0].metadata["feedback_from"] == "test_conv_001"
        assert result[0].metadata["previous_score"] == "0.5"

        # Verify the prompt included feedback-specific instructions
        call_kwargs = mock_acompletion.call_args.kwargs
        system_msg = call_kwargs["messages"][0]["content"]
        assert "Dialog Coherence" in system_msg
        user_msg = call_kwargs["messages"][1]["content"]
        assert "IMPROVED" in user_msg
        assert "0.50" in user_msg

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_generate_unexpected_error_wrapped(self, mock_acompletion: AsyncMock) -> None:
        seed = make_seed()

        # Return a response whose `.choices` access raises TypeError
        mock_response = MagicMock()
        type(mock_response).choices = property(lambda self: (_ for _ in ()).throw(TypeError("unexpected attribute")))
        mock_acompletion.return_value = mock_response

        gen = LiteLLMGenerator(config=GenerationConfig(max_retries=0))

        with pytest.raises(GenerationError):
            await gen.generate(seed, count=1)


# ─── Domain-parametrized prompt validation ───


class TestDomainPromptCoverage:
    """Parametrized tests ensuring all domains produce valid prompts."""

    @pytest.mark.parametrize(
        "domain,expected_keyword",
        [
            ("automotive.sales", "vehicle"),
            ("medical.consultation", "patient"),
            ("legal.advisory", "legal"),
            ("finance.advisory", "financial"),
            ("industrial.support", "industrial"),
            ("education.tutoring", "student"),
        ],
    )
    def test_domain_prompt_contains_keyword(self, domain: str, expected_keyword: str) -> None:
        seed = make_seed(dominio=domain)
        prompt = _build_system_prompt(seed)

        assert expected_keyword in prompt.lower()

    @pytest.mark.parametrize(
        "domain",
        [
            "automotive.sales",
            "medical.consultation",
            "legal.advisory",
            "finance.advisory",
            "industrial.support",
            "education.tutoring",
        ],
    )
    def test_all_domains_include_json_format(self, domain: str) -> None:
        seed = make_seed(dominio=domain)
        prompt = _build_system_prompt(seed)

        assert "JSON array" in prompt
        assert '"turno"' in prompt
