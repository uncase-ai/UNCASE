"""Generator service — business logic for synthetic conversation generation."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import structlog

from uncase.config import UNCASESettings
from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.core.generator.litellm_generator import GenerationConfig, LiteLLMGenerator
from uncase.exceptions import GenerationError
from uncase.schemas.generation import GenerateResponse, GenerationSummary

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


class GeneratorService:
    """Service layer for synthetic conversation generation.

    Orchestrates the LiteLLM generator with optional quality evaluation
    and database persistence.

    Usage:
        service = GeneratorService(session=db_session, settings=settings)
        response = await service.generate(
            seed=seed,
            count=5,
            evaluate_after=True,
        )
    """

    def __init__(
        self,
        *,
        session: AsyncSession | None = None,
        settings: UNCASESettings | None = None,
    ) -> None:
        self._session = session
        self._settings = settings or UNCASESettings()
        self._evaluator = ConversationEvaluator()

    def _resolve_api_key(self) -> str | None:
        """Resolve the API key from settings.

        Returns the first available key from litellm_api_key or anthropic_api_key.

        Raises:
            LLMConfigurationError: If no API key is configured.
        """
        if self._settings.litellm_api_key:
            return self._settings.litellm_api_key
        if self._settings.anthropic_api_key:
            return self._settings.anthropic_api_key
        return None

    def _build_config(
        self,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        language_override: str | None = None,
    ) -> GenerationConfig:
        """Build a GenerationConfig from request parameters."""
        return GenerationConfig(
            model=model or "claude-sonnet-4-20250514",
            temperature=temperature,
            language_override=language_override,
        )

    async def generate(
        self,
        seed: SeedSchema,
        *,
        count: int = 1,
        temperature: float = 0.7,
        model: str | None = None,
        language_override: str | None = None,
        evaluate_after: bool = True,
    ) -> GenerateResponse:
        """Generate synthetic conversations from a seed.

        Args:
            seed: The seed schema to generate from.
            count: Number of conversations to generate.
            temperature: LLM sampling temperature.
            model: Override default LLM model.
            language_override: Override seed language.
            evaluate_after: Whether to run quality evaluation.

        Returns:
            GenerateResponse with conversations, optional reports, and summary.

        Raises:
            GenerationError: If generation fails.
            LLMConfigurationError: If LLM is not configured.
        """
        logger.info(
            "generation_requested",
            seed_id=seed.seed_id,
            domain=seed.dominio,
            count=count,
            evaluate_after=evaluate_after,
        )

        start_time = time.monotonic()

        # Build generator config
        config = self._build_config(
            model=model,
            temperature=temperature,
            language_override=language_override,
        )

        # Resolve API key
        api_key = self._resolve_api_key()

        # Create generator
        generator = LiteLLMGenerator(config=config, api_key=api_key)

        # Generate conversations
        try:
            conversations = await generator.generate(seed, count=count)
        except GenerationError:
            raise
        except Exception as exc:
            msg = f"Generation failed: {exc}"
            raise GenerationError(msg) from exc

        # Optional quality evaluation
        reports: list[QualityReport] | None = None
        total_passed: int | None = None
        avg_score: float | None = None

        if evaluate_after and conversations:
            logger.info(
                "evaluating_generated_conversations",
                count=len(conversations),
                seed_id=seed.seed_id,
            )

            reports = []
            for conv in conversations:
                report = await self._evaluator.evaluate(conv, seed)
                reports.append(report)

            total_passed = sum(1 for r in reports if r.passed)
            avg_score = round(sum(r.composite_score for r in reports) / len(reports), 4)

            logger.info(
                "evaluation_complete",
                total=len(reports),
                passed=total_passed,
                failed=len(reports) - total_passed,
                avg_composite_score=avg_score,
            )

        duration = round(time.monotonic() - start_time, 2)

        summary = GenerationSummary(
            total_generated=len(conversations),
            total_passed=total_passed,
            avg_composite_score=avg_score,
            model_used=config.model,
            temperature=config.temperature,
            duration_seconds=duration,
        )

        logger.info(
            "generation_service_complete",
            seed_id=seed.seed_id,
            total_generated=summary.total_generated,
            total_passed=summary.total_passed,
            duration_seconds=duration,
        )

        return GenerateResponse(
            conversations=conversations,
            reports=reports,
            generation_summary=summary,
        )

    async def generate_with_feedback(
        self,
        seed: SeedSchema,
        quality_report: QualityReport,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        evaluate_after: bool = True,
    ) -> GenerateResponse:
        """Generate improved conversations using quality feedback.

        Takes a quality report from a previous evaluation and generates
        a new conversation with targeted improvements.

        Args:
            seed: The seed schema to generate from.
            quality_report: Quality report with identified failures.
            model: Override default LLM model.
            temperature: LLM sampling temperature.
            evaluate_after: Whether to evaluate the new conversation.

        Returns:
            GenerateResponse with the improved conversation.
        """
        logger.info(
            "feedback_generation_requested",
            seed_id=seed.seed_id,
            previous_score=quality_report.composite_score,
            failures=quality_report.failures,
        )

        start_time = time.monotonic()

        config = self._build_config(model=model, temperature=temperature)
        api_key = self._resolve_api_key()
        generator = LiteLLMGenerator(config=config, api_key=api_key)

        conversations = await generator.generate_with_feedback(seed, quality_report)

        reports: list[QualityReport] | None = None
        total_passed: int | None = None
        avg_score: float | None = None

        if evaluate_after and conversations:
            reports = []
            for conv in conversations:
                report = await self._evaluator.evaluate(conv, seed)
                reports.append(report)

            total_passed = sum(1 for r in reports if r.passed)
            avg_score = round(sum(r.composite_score for r in reports) / len(reports), 4)

        duration = round(time.monotonic() - start_time, 2)

        summary = GenerationSummary(
            total_generated=len(conversations),
            total_passed=total_passed,
            avg_composite_score=avg_score,
            model_used=config.model,
            temperature=config.temperature,
            duration_seconds=duration,
        )

        return GenerateResponse(
            conversations=conversations,
            reports=reports,
            generation_summary=summary,
        )
