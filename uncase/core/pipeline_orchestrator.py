"""End-to-end pipeline orchestrator — chains all 5 SCSF layers.

Supports parallel processing of seeds/conversations with semaphore-based
concurrency control to respect LLM rate limits.

Usage:
    orchestrator = PipelineOrchestrator(settings=settings)
    result = await orchestrator.run(
        raw_conversations=["..."],
        domain="automotive.sales",
        count=100,
    )
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import structlog

from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.core.generator.litellm_generator import GenerationConfig, LiteLLMGenerator
from uncase.core.lora_pipeline.pipeline import LoraPipeline
from uncase.core.seed_engine.engine import SeedEngine
from uncase.exceptions import GenerationError, TrainingError

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from uncase.config import UNCASESettings
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)

# Default concurrency limit — controls how many LLM calls can be in-flight
# simultaneously. Respects typical rate limits (10-50 RPM for most providers).
_DEFAULT_MAX_CONCURRENCY = 10


@dataclass
class PipelineStageResult:
    """Result of a single pipeline stage."""

    stage: str
    success: bool
    duration_seconds: float
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class PipelineResult:
    """Complete result of an end-to-end pipeline run."""

    run_id: str
    domain: str
    success: bool
    total_duration_seconds: float

    # Stage results
    stages: list[PipelineStageResult] = field(default_factory=list)

    # Artifacts
    seeds: list[SeedSchema] = field(default_factory=list)
    conversations: list[Conversation] = field(default_factory=list)
    reports: list[QualityReport] = field(default_factory=list)
    adapter_path: Path | None = None

    # Statistics
    seeds_created: int = 0
    conversations_generated: int = 0
    conversations_passed: int = 0
    avg_quality_score: float = 0.0
    pass_rate: float = 0.0


class PipelineOrchestrator:
    """End-to-end orchestrator for the SCSF pipeline.

    Chains all 5 layers:
        Layer 0 (Seed Engine) → Layer 1 (Parse) → Layer 2 (Evaluate) →
        Layer 3 (Generate) → Layer 2 (Re-evaluate) → Layer 4 (LoRA Train)

    Uses ``asyncio.gather()`` with semaphore-based concurrency control to
    process seeds and conversations in parallel while respecting LLM rate
    limits.

    Args:
        settings: Application settings.
        progress_callback: Optional callback for progress updates.
            Receives (stage_name: str, progress: float, message: str).
        max_concurrency: Max number of concurrent LLM calls (default 10).
    """

    def __init__(
        self,
        *,
        settings: UNCASESettings | None = None,
        progress_callback: Callable[[str, float, str], Any] | None = None,
        max_concurrency: int = _DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        from uncase.config import UNCASESettings as _Settings

        self._settings = settings or _Settings()
        self._progress = progress_callback or (lambda *_args: None)
        self._seed_engine = SeedEngine()
        self._evaluator = ConversationEvaluator()
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._max_concurrency = max_concurrency

    async def run(
        self,
        *,
        raw_conversations: list[str],
        domain: str,
        count: int = 100,
        model: str | None = None,
        temperature: float = 0.7,
        train_adapter: bool = True,
        base_model: str = "meta-llama/Llama-3.1-8B",
        use_qlora: bool = True,
        use_dp_sgd: bool = False,
        dp_epsilon: float = 8.0,
        output_dir: str = "./outputs/pipeline",
        run_id: str | None = None,
    ) -> PipelineResult:
        """Run the full end-to-end pipeline.

        Args:
            raw_conversations: List of raw conversation texts (any format).
            domain: Domain namespace (e.g. ``'automotive.sales'``).
            count: Number of synthetic conversations to generate per seed.
            model: LLM model to use for generation.
            temperature: Generation temperature.
            train_adapter: Whether to train a LoRA adapter (Layer 4).
            base_model: Base model for LoRA fine-tuning.
            use_qlora: Use 4-bit QLoRA quantization.
            use_dp_sgd: Enable DP-SGD differential privacy during training.
            dp_epsilon: Privacy budget epsilon.
            output_dir: Output directory for all artifacts.
            run_id: Optional run identifier. Auto-generated if None.

        Returns:
            PipelineResult with all artifacts and statistics.
        """
        import uuid

        run_id = run_id or uuid.uuid4().hex[:12]
        total_start = time.monotonic()
        stages: list[PipelineStageResult] = []

        logger.info(
            "pipeline_run_started",
            run_id=run_id,
            domain=domain,
            raw_conversation_count=len(raw_conversations),
            generate_count=count,
            train_adapter=train_adapter,
        )

        result = PipelineResult(
            run_id=run_id,
            domain=domain,
            success=False,
            total_duration_seconds=0.0,
        )

        # ── Stage 1: Seed Engine (Layer 0) — parallel ─────────────────
        self._progress("seed_engine", 0.0, "Creating seeds from raw conversations...")
        stage_start = time.monotonic()
        seeds: list[SeedSchema] = []

        try:
            total_raw = len(raw_conversations)

            async def _create_seed(raw: str) -> SeedSchema:
                async with self._semaphore:
                    return await self._seed_engine.create_seed(raw, domain)

            seed_tasks = [_create_seed(raw) for raw in raw_conversations]
            for idx, coro in enumerate(asyncio.as_completed(seed_tasks), 1):
                seed = await coro
                seeds.append(seed)
                self._progress(
                    "seed_engine",
                    idx / total_raw,
                    f"Seed {idx}/{total_raw} created",
                )

            stage_result = PipelineStageResult(
                stage="seed_engine",
                success=True,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                artifacts={"seed_count": len(seeds)},
            )
        except Exception as exc:
            stage_result = PipelineStageResult(
                stage="seed_engine",
                success=False,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                error=str(exc),
            )
            logger.error("pipeline_seed_engine_failed", run_id=run_id, error=str(exc))

        stages.append(stage_result)
        result.seeds = seeds
        result.seeds_created = len(seeds)

        if not seeds:
            result.stages = stages
            result.total_duration_seconds = round(time.monotonic() - total_start, 2)
            return result

        # ── Stage 2: Generation (Layer 3) — parallel ─────────────────
        self._progress("generation", 0.0, "Generating synthetic conversations...")
        stage_start = time.monotonic()
        all_conversations: list[Conversation] = []

        try:
            api_key = self._settings.litellm_api_key or self._settings.anthropic_api_key or None
            config = GenerationConfig(
                model=model or "claude-sonnet-4-20250514",
                temperature=temperature,
            )
            generator = LiteLLMGenerator(config=config, api_key=api_key)

            total_seeds = len(seeds)

            async def _generate_for_seed(seed: SeedSchema) -> list[Conversation]:
                async with self._semaphore:
                    return await generator.generate(seed, count=count)

            gen_tasks = [_generate_for_seed(s) for s in seeds]
            for idx, gen_coro in enumerate(asyncio.as_completed(gen_tasks), 1):
                conversations = await gen_coro
                all_conversations.extend(conversations)
                self._progress(
                    "generation",
                    idx / total_seeds,
                    f"Generated from seed {idx}/{total_seeds} ({len(conversations)} conversations)",
                )

            stage_result = PipelineStageResult(
                stage="generation",
                success=True,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                artifacts={"conversation_count": len(all_conversations)},
            )
        except GenerationError:
            raise
        except Exception as exc:
            stage_result = PipelineStageResult(
                stage="generation",
                success=False,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                error=str(exc),
            )
            logger.error("pipeline_generation_failed", run_id=run_id, error=str(exc))

        stages.append(stage_result)
        result.conversations = all_conversations
        result.conversations_generated = len(all_conversations)

        if not all_conversations:
            result.stages = stages
            result.total_duration_seconds = round(time.monotonic() - total_start, 2)
            return result

        # ── Stage 3: Quality Evaluation (Layer 2) — parallel batches ──
        self._progress("evaluation", 0.0, "Evaluating quality...")
        stage_start = time.monotonic()
        all_reports: list[QualityReport] = []

        try:
            # Pair conversations with their origin seeds (round-robin)
            conv_seed_pairs = [
                (conv, seeds[i % len(seeds)])
                for i, conv in enumerate(all_conversations)
            ]

            completed = 0
            total_convs = len(conv_seed_pairs)

            async def _evaluate_one(conv: Conversation, seed: SeedSchema) -> QualityReport:
                return await self._evaluator.evaluate(conv, seed)

            eval_tasks = [_evaluate_one(conv, seed) for conv, seed in conv_seed_pairs]

            # Process in batches to avoid overwhelming memory with too many
            # concurrent coroutines when there are thousands of conversations.
            batch_size = self._max_concurrency * 2
            for batch_start in range(0, len(eval_tasks), batch_size):
                batch = eval_tasks[batch_start : batch_start + batch_size]
                batch_reports = await asyncio.gather(*batch)
                all_reports.extend(batch_reports)
                completed += len(batch)
                self._progress(
                    "evaluation",
                    completed / total_convs,
                    f"Evaluated {completed}/{total_convs}",
                )

            passed = sum(1 for r in all_reports if r.passed)
            avg_score = round(sum(r.composite_score for r in all_reports) / len(all_reports), 4) if all_reports else 0.0

            stage_result = PipelineStageResult(
                stage="evaluation",
                success=True,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                artifacts={
                    "total_evaluated": len(all_reports),
                    "passed": passed,
                    "failed": len(all_reports) - passed,
                    "avg_score": avg_score,
                    "pass_rate": round(passed / len(all_reports), 4) if all_reports else 0.0,
                },
            )
        except Exception as exc:
            passed = 0
            avg_score = 0.0
            stage_result = PipelineStageResult(
                stage="evaluation",
                success=False,
                duration_seconds=round(time.monotonic() - stage_start, 2),
                error=str(exc),
            )
            logger.error("pipeline_evaluation_failed", run_id=run_id, error=str(exc))

        stages.append(stage_result)
        result.reports = all_reports
        result.conversations_passed = passed
        result.avg_quality_score = avg_score
        result.pass_rate = round(passed / len(all_reports), 4) if all_reports else 0.0

        # ── Stage 4: LoRA Training (Layer 4) ─────────────────────────────
        if train_adapter and all_conversations:
            self._progress("training", 0.0, "Preparing dataset and training LoRA adapter...")
            stage_start = time.monotonic()

            try:
                # Filter to only passing conversations for training
                passing_conversations = (
                    [conv for conv, report in zip(all_conversations, all_reports, strict=False) if report.passed]
                    if all_reports
                    else all_conversations
                )

                if not passing_conversations:
                    logger.warning(
                        "no_passing_conversations",
                        run_id=run_id,
                        message="No conversations passed quality thresholds. Using all conversations.",
                    )
                    passing_conversations = all_conversations

                pipeline = LoraPipeline(
                    base_model=base_model,
                    output_dir=output_dir,
                    use_qlora=use_qlora,
                    use_dp_sgd=use_dp_sgd,
                    dp_epsilon=dp_epsilon,
                )

                self._progress("training", 0.1, "Preparing training dataset...")
                dataset_path = await pipeline.prepare_dataset(passing_conversations)

                self._progress("training", 0.2, "Training LoRA adapter (this may take a while)...")
                adapter_path = await pipeline.train(dataset_path, {"run_id": run_id})

                self._progress("training", 0.9, "Evaluating trained model...")
                model_metrics = await pipeline.evaluate_model(adapter_path)

                result.adapter_path = adapter_path

                stage_result = PipelineStageResult(
                    stage="training",
                    success=True,
                    duration_seconds=round(time.monotonic() - stage_start, 2),
                    artifacts={
                        "adapter_path": str(adapter_path),
                        "dataset_path": str(dataset_path),
                        "training_conversations": len(passing_conversations),
                        **model_metrics,
                    },
                )
            except (TrainingError, Exception) as exc:
                stage_result = PipelineStageResult(
                    stage="training",
                    success=False,
                    duration_seconds=round(time.monotonic() - stage_start, 2),
                    error=str(exc),
                )
                logger.error("pipeline_training_failed", run_id=run_id, error=str(exc))

            stages.append(stage_result)

        # ── Finalize ─────────────────────────────────────────────────────
        result.stages = stages
        result.total_duration_seconds = round(time.monotonic() - total_start, 2)
        result.success = all(s.success for s in stages)

        self._progress("complete", 1.0, "Pipeline complete!")

        logger.info(
            "pipeline_run_complete",
            run_id=run_id,
            success=result.success,
            seeds_created=result.seeds_created,
            conversations_generated=result.conversations_generated,
            conversations_passed=result.conversations_passed,
            pass_rate=result.pass_rate,
            avg_quality_score=result.avg_quality_score,
            adapter_path=str(result.adapter_path) if result.adapter_path else None,
            total_duration=result.total_duration_seconds,
        )

        return result
