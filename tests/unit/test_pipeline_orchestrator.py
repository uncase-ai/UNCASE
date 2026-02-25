"""Tests for the end-to-end pipeline orchestrator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from uncase.core.pipeline_orchestrator import (
    PipelineOrchestrator,
    PipelineResult,
    PipelineStageResult,
)


class TestPipelineStageResult:
    def test_success_stage(self) -> None:
        stage = PipelineStageResult(stage="seed_engine", success=True, duration_seconds=1.5)
        assert stage.stage == "seed_engine"
        assert stage.success is True
        assert stage.error is None

    def test_failed_stage(self) -> None:
        stage = PipelineStageResult(stage="generation", success=False, duration_seconds=0.1, error="LLM timeout")
        assert stage.success is False
        assert stage.error == "LLM timeout"

    def test_artifacts_default_empty(self) -> None:
        stage = PipelineStageResult(stage="test", success=True, duration_seconds=0.0)
        assert stage.artifacts == {}


class TestPipelineResult:
    def test_default_values(self) -> None:
        result = PipelineResult(run_id="test-001", domain="automotive.sales", success=False, total_duration_seconds=0.0)
        assert result.seeds == []
        assert result.conversations == []
        assert result.reports == []
        assert result.adapter_path is None
        assert result.seeds_created == 0
        assert result.conversations_generated == 0
        assert result.pass_rate == 0.0


# Mock objects for pipeline testing
def _make_mock_seed() -> MagicMock:
    seed = MagicMock()
    seed.model_dump.return_value = {"dominio": "automotive.sales"}
    return seed


def _make_mock_conversation() -> MagicMock:
    conv = MagicMock()
    conv.model_dump.return_value = {"turnos": []}
    return conv


def _make_mock_report(passed: bool = True, score: float = 0.85) -> MagicMock:
    report = MagicMock()
    report.passed = passed
    report.composite_score = score
    return report


class TestPipelineOrchestrator:
    """Test orchestrator execution with mocked layers."""

    @pytest.fixture()
    def mock_settings(self) -> MagicMock:
        settings = MagicMock()
        settings.litellm_api_key = "test-key"
        settings.anthropic_api_key = None
        return settings

    async def test_empty_conversations_returns_early(self, mock_settings: MagicMock) -> None:
        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(side_effect=ValueError("Parse failed"))

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["bad data"],
                domain="automotive.sales",
                count=1,
                train_adapter=False,
            )

            assert result.seeds_created == 0
            assert result.success is False
            assert len(result.stages) >= 1

    async def test_seed_engine_stage(self, mock_settings: MagicMock) -> None:
        mock_seed = _make_mock_seed()

        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
            patch("uncase.core.pipeline_orchestrator.LiteLLMGenerator") as mock_gen_cls,
            patch("uncase.core.pipeline_orchestrator.ConversationEvaluator") as mock_eval_cls,
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(return_value=mock_seed)

            mock_conv = _make_mock_conversation()
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])

            mock_report = _make_mock_report(passed=True, score=0.9)
            mock_eval = mock_eval_cls.return_value
            mock_eval.evaluate = AsyncMock(return_value=mock_report)

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["Vendedor: Hola\nCliente: Buenos dias"],
                domain="automotive.sales",
                count=1,
                train_adapter=False,
            )

            assert result.seeds_created == 1
            assert result.conversations_generated == 1
            assert result.conversations_passed == 1
            assert result.pass_rate == 1.0

    async def test_generation_failure(self, mock_settings: MagicMock) -> None:
        mock_seed = _make_mock_seed()

        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
            patch("uncase.core.pipeline_orchestrator.LiteLLMGenerator") as mock_gen_cls,
            patch("uncase.core.pipeline_orchestrator.ConversationEvaluator"),
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(return_value=mock_seed)

            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(side_effect=RuntimeError("LLM unavailable"))

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["Vendedor: Hola\nCliente: Buenos dias"],
                domain="automotive.sales",
                count=1,
                train_adapter=False,
            )

            assert result.seeds_created == 1
            assert result.conversations_generated == 0
            assert result.success is False

    async def test_evaluation_stage(self, mock_settings: MagicMock) -> None:
        mock_seed = _make_mock_seed()
        mock_conv = _make_mock_conversation()

        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
            patch("uncase.core.pipeline_orchestrator.LiteLLMGenerator") as mock_gen_cls,
            patch("uncase.core.pipeline_orchestrator.ConversationEvaluator") as mock_eval_cls,
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(return_value=mock_seed)

            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv, mock_conv, mock_conv])

            report_pass = _make_mock_report(passed=True, score=0.9)
            report_fail = _make_mock_report(passed=False, score=0.3)
            mock_eval = mock_eval_cls.return_value
            mock_eval.evaluate = AsyncMock(side_effect=[report_pass, report_fail, report_pass])

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["Vendedor: Hola\nCliente: Buenos dias"],
                domain="automotive.sales",
                count=3,
                train_adapter=False,
            )

            assert result.conversations_generated == 3
            assert result.conversations_passed == 2
            assert result.pass_rate == pytest.approx(0.6667, rel=1e-2)

    async def test_training_stage(self, mock_settings: MagicMock) -> None:
        mock_seed = _make_mock_seed()
        mock_conv = _make_mock_conversation()
        mock_report = _make_mock_report(passed=True, score=0.9)

        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
            patch("uncase.core.pipeline_orchestrator.LiteLLMGenerator") as mock_gen_cls,
            patch("uncase.core.pipeline_orchestrator.ConversationEvaluator") as mock_eval_cls,
            patch("uncase.core.pipeline_orchestrator.LoraPipeline") as mock_lora_cls,
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(return_value=mock_seed)
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])
            mock_eval = mock_eval_cls.return_value
            mock_eval.evaluate = AsyncMock(return_value=mock_report)

            mock_lora = mock_lora_cls.return_value
            mock_lora.prepare_dataset = AsyncMock(return_value=Path("./outputs/test/dataset.jsonl"))
            mock_lora.train = AsyncMock(return_value=Path("./outputs/test/adapter"))
            mock_lora.evaluate_model = AsyncMock(return_value={"perplexity": 2.5})

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["Vendedor: Hola\nCliente: Buenos dias"],
                domain="automotive.sales",
                count=1,
                train_adapter=True,
                base_model="test-model",
            )

            assert result.adapter_path == Path("./outputs/test/adapter")
            assert result.success is True
            assert len(result.stages) == 4

    async def test_progress_callback(self, mock_settings: MagicMock) -> None:
        mock_seed = _make_mock_seed()
        mock_conv = _make_mock_conversation()
        mock_report = _make_mock_report(passed=True, score=0.9)

        progress_calls: list[tuple[str, float, str]] = []

        def track_progress(stage: str, progress: float, message: str) -> None:
            progress_calls.append((stage, progress, message))

        with (
            patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls,
            patch("uncase.core.pipeline_orchestrator.LiteLLMGenerator") as mock_gen_cls,
            patch("uncase.core.pipeline_orchestrator.ConversationEvaluator") as mock_eval_cls,
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(return_value=mock_seed)
            mock_gen = mock_gen_cls.return_value
            mock_gen.generate = AsyncMock(return_value=[mock_conv])
            mock_eval = mock_eval_cls.return_value
            mock_eval.evaluate = AsyncMock(return_value=mock_report)

            orchestrator = PipelineOrchestrator(settings=mock_settings, progress_callback=track_progress)
            await orchestrator.run(
                raw_conversations=["Vendedor: Hola\nCliente: Buenos dias"],
                domain="automotive.sales",
                count=1,
                train_adapter=False,
            )

        stages_reported = [s for s, _, _ in progress_calls]
        assert "seed_engine" in stages_reported
        assert "generation" in stages_reported
        assert "evaluation" in stages_reported
        assert "complete" in stages_reported

    async def test_custom_run_id(self, mock_settings: MagicMock) -> None:
        with patch("uncase.core.pipeline_orchestrator.SeedEngine") as mock_engine_cls:
            mock_engine = mock_engine_cls.return_value
            mock_engine.create_seed = AsyncMock(side_effect=RuntimeError("fail"))

            orchestrator = PipelineOrchestrator(settings=mock_settings)
            result = await orchestrator.run(
                raw_conversations=["test"],
                domain="automotive.sales",
                count=1,
                train_adapter=False,
                run_id="custom-123",
            )
            assert result.run_id == "custom-123"
