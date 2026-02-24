"""Evaluator service — business logic for conversation quality assessment."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from uncase.core.evaluator.evaluator import ConversationEvaluator

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


class EvaluatorService:
    """Service layer for quality evaluation operations.

    Wraps the ConversationEvaluator with additional business logic:
    batch statistics, summary reports, and threshold customization.
    """

    def __init__(self) -> None:
        self._evaluator = ConversationEvaluator()

    async def evaluate_single(
        self, conversation: Conversation, seed: SeedSchema
    ) -> QualityReport:
        """Evaluate a single conversation against its origin seed."""
        return await self._evaluator.evaluate(conversation, seed)

    async def evaluate_batch(
        self, conversations: list[Conversation], seeds: list[SeedSchema]
    ) -> BatchEvaluationResult:
        """Evaluate a batch and return summary statistics."""
        reports = await self._evaluator.evaluate_batch(conversations, seeds)

        passed = [r for r in reports if r.passed]
        failed = [r for r in reports if not r.passed]

        avg_composite = (
            sum(r.composite_score for r in reports) / len(reports) if reports else 0.0
        )

        # Aggregate metric averages
        metric_avgs: dict[str, float] = {}
        if reports:
            metric_fields = [
                "rouge_l",
                "fidelidad_factual",
                "diversidad_lexica",
                "coherencia_dialogica",
                "privacy_score",
                "memorizacion",
            ]
            for field in metric_fields:
                values = [getattr(r.metrics, field) for r in reports]
                metric_avgs[field] = sum(values) / len(values)

        # Collect all unique failure reasons
        all_failures: dict[str, int] = {}
        for report in failed:
            for failure in report.failures:
                metric_name = failure.split("=")[0] if "=" in failure else failure
                all_failures[metric_name] = all_failures.get(metric_name, 0) + 1

        logger.info(
            "batch_evaluation_summary",
            total=len(reports),
            passed=len(passed),
            failed=len(failed),
            avg_composite=round(avg_composite, 4),
        )

        return BatchEvaluationResult(
            reports=reports,
            total=len(reports),
            passed_count=len(passed),
            failed_count=len(failed),
            avg_composite_score=round(avg_composite, 4),
            metric_averages=metric_avgs,
            failure_summary=all_failures,
        )


class BatchEvaluationResult:
    """Summary of a batch evaluation run."""

    __slots__ = (
        "avg_composite_score",
        "failed_count",
        "failure_summary",
        "metric_averages",
        "passed_count",
        "reports",
        "total",
    )

    def __init__(
        self,
        *,
        reports: list[QualityReport],
        total: int,
        passed_count: int,
        failed_count: int,
        avg_composite_score: float,
        metric_averages: dict[str, float],
        failure_summary: dict[str, int],
    ) -> None:
        self.reports = reports
        self.total = total
        self.passed_count = passed_count
        self.failed_count = failed_count
        self.avg_composite_score = avg_composite_score
        self.metric_averages = metric_averages
        self.failure_summary = failure_summary

    @property
    def pass_rate(self) -> float:
        """Percentage of conversations that passed all thresholds."""
        return (self.passed_count / self.total * 100) if self.total > 0 else 0.0

    def to_dict(self) -> dict[str, object]:
        """Serialize to a dictionary for API responses."""
        return {
            "total": self.total,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": round(self.pass_rate, 2),
            "avg_composite_score": self.avg_composite_score,
            "metric_averages": self.metric_averages,
            "failure_summary": self.failure_summary,
            "reports": [r.model_dump(mode="json") for r in self.reports],
        }
