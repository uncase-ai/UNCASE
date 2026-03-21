"""Tests for the generator service — business logic for synthetic conversation generation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from uncase.config import UNCASESettings
from uncase.exceptions import GenerationError
from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.generation import GenerateResponse, GenerationSummary
from uncase.schemas.quality import QualityMetrics, QualityReport
from uncase.schemas.seed import MetricasCalidad, ParametrosFactuales, PasosTurnos, Privacidad, SeedSchema
from uncase.services.generator import GeneratorService

# ---------------------------------------------------------------------------
# Helpers — fictional test data factories
# ---------------------------------------------------------------------------


def _make_settings(**overrides: object) -> UNCASESettings:
    """Build test settings with safe defaults."""
    defaults: dict[str, object] = {
        "uncase_env": "development",
        "uncase_log_level": "DEBUG",
        "database_url": "sqlite+aiosqlite://",
        "litellm_api_key": "sk-test-fictitious-key",
        "anthropic_api_key": "",
        "gemini_api_key": "",
        "google_api_key": "",
    }
    defaults.update(overrides)
    return UNCASESettings(**defaults)  # type: ignore[arg-type]


def _make_seed(**overrides: object) -> SeedSchema:
    """Build a valid SeedSchema with fictional defaults."""
    defaults: dict[str, object] = {
        "seed_id": "seed-test-abc123",
        "dominio": "automotive.sales",
        "idioma": "es",
        "objetivo": "Consulta ficticia sobre vehiculos de prueba",
        "tono": "profesional",
        "roles": ["vendedor", "cliente"],
        "descripcion_roles": {
            "vendedor": "Asesor de ventas ficticio",
            "cliente": "Cliente ficticio interesado",
        },
        "pasos_turnos": PasosTurnos(
            turnos_min=4,
            turnos_max=12,
            flujo_esperado=["saludo", "consulta", "resolucion"],
        ),
        "parametros_factuales": ParametrosFactuales(
            contexto="Concesionario ficticio de prueba",
            restricciones=["Restriccion de prueba"],
            herramientas=["crm"],
            metadata={},
        ),
        "privacidad": Privacidad(),
        "metricas_calidad": MetricasCalidad(),
    }
    defaults.update(overrides)
    return SeedSchema(**defaults)  # type: ignore[arg-type]


def _make_conversation(seed_id: str = "seed-test-abc123", num_turns: int = 4) -> Conversation:
    """Build a fictional Conversation with the given number of turns."""
    roles = ["vendedor", "cliente"]
    turns = [
        ConversationTurn(
            turno=i + 1,
            rol=roles[i % 2],
            contenido=f"Contenido ficticio del turno {i + 1} para pruebas.",
        )
        for i in range(num_turns)
    ]
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=turns,
        es_sintetica=True,
    )


def _make_quality_report(
    *,
    passed: bool = True,
    composite_score: float = 0.85,
    failures: list[str] | None = None,
    conversation_id: str = "conv-test-001",
    seed_id: str = "seed-test-abc123",
) -> QualityReport:
    """Build a fictional QualityReport."""
    return QualityReport(
        conversation_id=conversation_id,
        seed_id=seed_id,
        metrics=QualityMetrics(
            rouge_l=0.65,
            fidelidad_factual=0.90,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.85,
            tool_call_validity=1.0,
            privacy_score=0.0,
            memorizacion=0.0,
        ),
        composite_score=composite_score,
        passed=passed,
        failures=failures or [],
    )


# ---------------------------------------------------------------------------
# TestGeneratorServiceInit — constructor and config resolution
# ---------------------------------------------------------------------------


class TestGeneratorServiceInit:
    def test_default_settings_when_none(self) -> None:
        service = GeneratorService()
        assert service._settings is not None
        assert service._evaluator is not None

    def test_custom_settings(self) -> None:
        settings = _make_settings(litellm_api_key="sk-custom-test")
        service = GeneratorService(settings=settings)
        assert service._settings.litellm_api_key == "sk-custom-test"

    def test_session_stored(self) -> None:
        mock_session = MagicMock()
        service = GeneratorService(session=mock_session)
        assert service._session is mock_session

    def test_session_none_by_default(self) -> None:
        service = GeneratorService()
        assert service._session is None


# ---------------------------------------------------------------------------
# TestResolveApiKey
# ---------------------------------------------------------------------------


class TestResolveApiKey:
    def test_prefers_litellm_key(self) -> None:
        settings = _make_settings(
            litellm_api_key="sk-litellm",
            anthropic_api_key="sk-anthropic",
            gemini_api_key="sk-gemini",
        )
        service = GeneratorService(settings=settings)
        assert service._resolve_api_key() == "sk-litellm"

    def test_falls_back_to_anthropic(self) -> None:
        settings = _make_settings(
            litellm_api_key="",
            anthropic_api_key="sk-anthropic-fallback",
            gemini_api_key="",
        )
        service = GeneratorService(settings=settings)
        assert service._resolve_api_key() == "sk-anthropic-fallback"

    def test_falls_back_to_gemini(self) -> None:
        settings = _make_settings(
            litellm_api_key="",
            anthropic_api_key="",
            gemini_api_key="sk-gemini-fallback",
        )
        service = GeneratorService(settings=settings)
        assert service._resolve_api_key() == "sk-gemini-fallback"

    def test_falls_back_to_google(self) -> None:
        settings = _make_settings(
            litellm_api_key="",
            anthropic_api_key="",
            gemini_api_key="",
            google_api_key="sk-google-fallback",
        )
        service = GeneratorService(settings=settings)
        assert service._resolve_api_key() == "sk-google-fallback"

    def test_returns_none_when_no_keys(self) -> None:
        settings = _make_settings(
            litellm_api_key="",
            anthropic_api_key="",
            gemini_api_key="",
            google_api_key="",
        )
        service = GeneratorService(settings=settings)
        assert service._resolve_api_key() is None


# ---------------------------------------------------------------------------
# TestBuildConfig
# ---------------------------------------------------------------------------


class TestBuildConfig:
    def test_default_model(self) -> None:
        service = GeneratorService(settings=_make_settings())
        config = service._build_config()
        assert config.model == "claude-sonnet-4-20250514"
        assert config.temperature == 0.7

    def test_custom_model_and_temperature(self) -> None:
        service = GeneratorService(settings=_make_settings())
        config = service._build_config(model="gemini/gemini-2.5-pro", temperature=0.9)
        assert config.model == "gemini/gemini-2.5-pro"
        assert config.temperature == 0.9

    def test_language_override(self) -> None:
        service = GeneratorService(settings=_make_settings())
        config = service._build_config(language_override="en")
        assert config.language_override == "en"

    def test_api_base(self) -> None:
        service = GeneratorService(settings=_make_settings())
        config = service._build_config(api_base="http://localhost:11434")
        assert config.api_base == "http://localhost:11434"

    def test_none_model_uses_default(self) -> None:
        service = GeneratorService(settings=_make_settings())
        config = service._build_config(model=None)
        assert config.model == "claude-sonnet-4-20250514"


# ---------------------------------------------------------------------------
# TestResolveFromProvider
# ---------------------------------------------------------------------------


class TestResolveFromProvider:
    async def test_returns_none_tuple_without_session(self) -> None:
        service = GeneratorService(session=None, settings=_make_settings())
        api_key, model, api_base = await service._resolve_from_provider("provider-123")
        assert api_key is None
        assert model is None
        assert api_base is None

    async def test_resolves_from_provider_with_session(self) -> None:
        mock_session = MagicMock()
        settings = _make_settings()

        mock_provider = MagicMock()
        mock_provider.default_model = "claude-sonnet-4-20250514"
        mock_provider.provider_type = "anthropic"
        mock_provider.api_base = None

        with (
            patch("uncase.services.provider.ProviderService") as mock_ps_cls,
            patch("uncase.services.provider.normalize_model_for_litellm", return_value="claude-sonnet-4-20250514"),
        ):
            mock_ps = mock_ps_cls.return_value
            mock_ps._get_or_raise = AsyncMock(return_value=mock_provider)
            mock_ps.decrypt_provider_key = MagicMock(return_value="sk-decrypted-key")

            service = GeneratorService(session=mock_session, settings=settings)
            api_key, model, api_base = await service._resolve_from_provider("provider-123")

        assert api_key == "sk-decrypted-key"
        assert model == "claude-sonnet-4-20250514"
        assert api_base is None


# ---------------------------------------------------------------------------
# TestGenerate — main orchestration method
# ---------------------------------------------------------------------------


class TestGenerate:
    """Test the main generate() method with mocked LLM and evaluator."""

    @pytest.fixture()
    def service(self) -> GeneratorService:
        return GeneratorService(settings=_make_settings())

    async def test_generate_single_conversation(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report())

            response = await service.generate(seed, count=1, evaluate_after=True)

        assert isinstance(response, GenerateResponse)
        assert len(response.conversations) == 1
        assert response.generation_summary.total_generated == 1
        assert response.generation_summary.total_passed == 1
        assert response.reports is not None
        assert len(response.reports) == 1

    async def test_generate_multiple_conversations(self, service: GeneratorService) -> None:
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(3)]

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)

            report_pass = _make_quality_report(passed=True, composite_score=0.9)
            report_fail = _make_quality_report(
                passed=False,
                composite_score=0.3,
                failures=["diversidad_lexica=0.40 (min 0.55)"],
            )
            mock_evaluator.evaluate = AsyncMock(side_effect=[report_pass, report_fail, report_pass])

            response = await service.generate(seed, count=3, evaluate_after=True)

        assert response.generation_summary.total_generated == 3
        assert response.generation_summary.total_passed == 2
        assert response.generation_summary.avg_composite_score is not None
        expected_avg = round((0.9 + 0.3 + 0.9) / 3, 4)
        assert response.generation_summary.avg_composite_score == expected_avg

    async def test_generate_without_evaluation(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, evaluate_after=False)

        assert response.reports is None
        assert response.generation_summary.total_passed is None
        assert response.generation_summary.avg_composite_score is None
        assert response.generation_summary.total_generated == 1

    async def test_generate_empty_conversations_skip_evaluation(self, service: GeneratorService) -> None:
        seed = _make_seed()

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[])

            response = await service.generate(seed, count=1, evaluate_after=True)

        # Evaluation should not be called when there are no conversations
        mock_evaluator.evaluate.assert_not_called()
        assert response.reports is None
        assert response.generation_summary.total_generated == 0

    async def test_generate_uses_default_model(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, evaluate_after=False)

        assert response.generation_summary.model_used == "claude-sonnet-4-20250514"

    async def test_generate_with_custom_model(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, model="gemini/gemini-2.5-pro", evaluate_after=False)

        assert response.generation_summary.model_used == "gemini/gemini-2.5-pro"

    async def test_generate_with_temperature(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, temperature=1.2, evaluate_after=False)

        assert response.generation_summary.temperature == 1.2

    async def test_generate_with_language_override(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            await service.generate(seed, count=1, language_override="en", evaluate_after=False)

        # Verify the config was built with language_override
        call_kwargs = mock_gen_cls.call_args
        config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
        assert config.language_override == "en"

    async def test_generate_records_duration(self, service: GeneratorService) -> None:
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, evaluate_after=False)

        assert response.generation_summary.duration_seconds >= 0.0

    async def test_generate_summary_structure(self, service: GeneratorService) -> None:
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(2)]

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report(passed=True, composite_score=0.88))

            response = await service.generate(seed, count=2, evaluate_after=True)

        summary = response.generation_summary
        assert isinstance(summary, GenerationSummary)
        assert summary.total_generated == 2
        assert summary.total_passed == 2
        assert summary.avg_composite_score == 0.88
        assert summary.duration_seconds >= 0.0


# ---------------------------------------------------------------------------
# TestGenerateProviderResolution
# ---------------------------------------------------------------------------


class TestGenerateProviderResolution:
    async def test_generate_with_provider_id(self) -> None:
        settings = _make_settings(litellm_api_key="")
        mock_session = MagicMock()
        service = GeneratorService(session=mock_session, settings=settings)
        seed = _make_seed()
        mock_conv = _make_conversation()

        with (
            patch.object(
                service,
                "_resolve_from_provider",
                new_callable=AsyncMock,
                return_value=("sk-provider-key", "gemini/gemini-2.5-pro", "https://api.example.com"),
            ) as mock_resolve,
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, provider_id="prov-test-001", evaluate_after=False)

            # Should have called _resolve_from_provider
            mock_resolve.assert_awaited_once_with("prov-test-001")
        assert response.generation_summary.model_used == "gemini/gemini-2.5-pro"

    async def test_explicit_model_overrides_provider_model(self) -> None:
        settings = _make_settings(litellm_api_key="")
        mock_session = MagicMock()
        service = GeneratorService(session=mock_session, settings=settings)
        seed = _make_seed()
        mock_conv = _make_conversation()

        with (
            patch.object(
                service,
                "_resolve_from_provider",
                new_callable=AsyncMock,
                return_value=("sk-provider-key", "gemini/gemini-2.5-pro", None),
            ),
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(
                seed,
                count=1,
                model="claude-sonnet-4-20250514",
                provider_id="prov-test-001",
                evaluate_after=False,
            )

        # Explicit model should override provider model
        assert response.generation_summary.model_used == "claude-sonnet-4-20250514"

    async def test_generate_without_provider_uses_env_key(self) -> None:
        settings = _make_settings(litellm_api_key="sk-env-key")
        service = GeneratorService(settings=settings)
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            await service.generate(seed, count=1, evaluate_after=False)

        # Verify the generator was constructed with the env key
        call_kwargs = mock_gen_cls.call_args
        assert call_kwargs.kwargs.get("api_key") == "sk-env-key"


# ---------------------------------------------------------------------------
# TestGenerateErrors — error handling and edge cases
# ---------------------------------------------------------------------------


class TestGenerateErrors:
    async def test_generation_error_propagates(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=GenerationError("LLM returned empty response"))

            with pytest.raises(GenerationError, match="LLM returned empty response"):
                await service.generate(seed, count=1)

    async def test_unexpected_error_wrapped_in_generation_error(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=TimeoutError("Connection timed out"))

            with pytest.raises(GenerationError, match=r"Generation failed.*Connection timed out"):
                await service.generate(seed, count=1)

    async def test_llm_timeout_raises_generation_error(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=TimeoutError("Request timed out after 90s"))

            with pytest.raises(GenerationError):
                await service.generate(seed, count=1)

    async def test_runtime_error_wrapped(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=RuntimeError("LLM service unavailable"))

            with pytest.raises(GenerationError, match=r"Generation failed.*LLM service unavailable"):
                await service.generate(seed, count=1)

    async def test_value_error_wrapped(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=ValueError("Invalid model name"))

            with pytest.raises(GenerationError, match=r"Generation failed.*Invalid model name"):
                await service.generate(seed, count=1)


# ---------------------------------------------------------------------------
# TestGenerateWithFeedback
# ---------------------------------------------------------------------------


class TestGenerateWithFeedback:
    async def test_feedback_generation_basic(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(
            passed=False,
            composite_score=0.45,
            failures=["diversidad_lexica=0.40 (min 0.55)", "coherencia_dialogica=0.50 (min 0.65)"],
        )
        mock_conv = _make_conversation()

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report(passed=True, composite_score=0.88))

            response = await service.generate_with_feedback(seed, previous_report, evaluate_after=True)

        assert isinstance(response, GenerateResponse)
        assert len(response.conversations) == 1
        assert response.reports is not None
        assert len(response.reports) == 1
        assert response.generation_summary.total_generated == 1

    async def test_feedback_generation_without_evaluation(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.35)
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])

            response = await service.generate_with_feedback(seed, previous_report, evaluate_after=False)

        assert response.reports is None
        assert response.generation_summary.total_passed is None
        assert response.generation_summary.total_generated == 1

    async def test_feedback_with_custom_model(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.40)
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])

            response = await service.generate_with_feedback(
                seed,
                previous_report,
                model="gemini/gemini-2.5-pro",
                evaluate_after=False,
            )

        assert response.generation_summary.model_used == "gemini/gemini-2.5-pro"

    async def test_feedback_with_custom_temperature(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.30)
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])

            response = await service.generate_with_feedback(
                seed,
                previous_report,
                temperature=0.9,
                evaluate_after=False,
            )

        assert response.generation_summary.temperature == 0.9

    async def test_feedback_empty_conversations_skip_evaluation(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.20)

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[])

            response = await service.generate_with_feedback(seed, previous_report, evaluate_after=True)

        mock_evaluator.evaluate.assert_not_called()
        assert response.reports is None
        assert response.generation_summary.total_generated == 0

    async def test_feedback_records_duration(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.50)
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])

            response = await service.generate_with_feedback(seed, previous_report, evaluate_after=False)

        assert response.generation_summary.duration_seconds >= 0.0

    async def test_feedback_uses_env_api_key(self) -> None:
        settings = _make_settings(litellm_api_key="sk-feedback-env-key")
        service = GeneratorService(settings=settings)
        seed = _make_seed()
        previous_report = _make_quality_report(passed=False, composite_score=0.40)
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate_with_feedback = AsyncMock(return_value=[mock_conv])

            await service.generate_with_feedback(seed, previous_report, evaluate_after=False)

        call_kwargs = mock_gen_cls.call_args
        assert call_kwargs.kwargs.get("api_key") == "sk-feedback-env-key"


# ---------------------------------------------------------------------------
# TestGenerateEvaluationIntegration — evaluation pass/fail scenarios
# ---------------------------------------------------------------------------


class TestGenerateEvaluationIntegration:
    async def test_all_conversations_pass(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(3)]

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report(passed=True, composite_score=0.92))

            response = await service.generate(seed, count=3, evaluate_after=True)

        assert response.generation_summary.total_passed == 3
        assert response.generation_summary.avg_composite_score == 0.92

    async def test_all_conversations_fail(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(2)]

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)
            mock_evaluator.evaluate = AsyncMock(
                return_value=_make_quality_report(
                    passed=False,
                    composite_score=0.30,
                    failures=["rouge_l=0.10 (min 0.20)"],
                )
            )

            response = await service.generate(seed, count=2, evaluate_after=True)

        assert response.generation_summary.total_passed == 0
        assert response.generation_summary.avg_composite_score == 0.3

    async def test_mixed_pass_fail(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(4)]

        report_pass = _make_quality_report(passed=True, composite_score=0.9)
        report_fail = _make_quality_report(passed=False, composite_score=0.2)

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)
            mock_evaluator.evaluate = AsyncMock(side_effect=[report_pass, report_fail, report_pass, report_fail])

            response = await service.generate(seed, count=4, evaluate_after=True)

        assert response.generation_summary.total_passed == 2
        expected_avg = round((0.9 + 0.2 + 0.9 + 0.2) / 4, 4)
        assert response.generation_summary.avg_composite_score == expected_avg

    async def test_evaluator_called_once_per_conversation(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        convs = [_make_conversation() for _ in range(5)]

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=convs)
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report(passed=True, composite_score=0.85))

            await service.generate(seed, count=5, evaluate_after=True)

        assert mock_evaluator.evaluate.await_count == 5


# ---------------------------------------------------------------------------
# TestGenerateDifferentDomains — domain-related edge cases
# ---------------------------------------------------------------------------


class TestGenerateDifferentDomains:
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
    async def test_generate_across_domains(self, domain: str) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed(dominio=domain)
        mock_conv = _make_conversation(seed_id=seed.seed_id)

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, evaluate_after=False)

        assert response.generation_summary.total_generated == 1


# ---------------------------------------------------------------------------
# TestGenerateResponseSchema — verify response schema compliance
# ---------------------------------------------------------------------------


class TestGenerateResponseSchema:
    async def test_response_serializable(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        mock_conv = _make_conversation()

        with (
            patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls,
            patch.object(service, "_evaluator") as mock_evaluator,
        ):
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])
            mock_evaluator.evaluate = AsyncMock(return_value=_make_quality_report(passed=True, composite_score=0.85))

            response = await service.generate(seed, count=1, evaluate_after=True)

        # Verify the response can be serialized (as it would be in the API)
        dumped = response.model_dump()
        assert "conversations" in dumped
        assert "generation_summary" in dumped
        assert "reports" in dumped

    async def test_response_without_reports_serializable(self) -> None:
        service = GeneratorService(settings=_make_settings())
        seed = _make_seed()
        mock_conv = _make_conversation()

        with patch("uncase.services.generator.LiteLLMGenerator") as mock_gen_cls:
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            response = await service.generate(seed, count=1, evaluate_after=False)

        dumped = response.model_dump()
        assert dumped["reports"] is None
        assert dumped["generation_summary"]["total_passed"] is None
