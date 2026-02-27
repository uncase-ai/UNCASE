"""Evaluator service — business logic for conversation quality assessment."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.db.models.evaluation import EvaluationReportModel
from uncase.exceptions import QualityThresholdError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


class EvaluatorService:
    """Service layer for quality evaluation operations.

    Wraps the ConversationEvaluator with DB persistence, batch statistics,
    and summary reports.
    """

    def __init__(self, *, session: AsyncSession | None = None) -> None:
        self._evaluator = ConversationEvaluator()
        self._session = session

    async def _persist_report(self, report: QualityReport, dominio: str | None = None) -> None:
        """Persist a quality report to the database if a session is available."""
        if self._session is None:
            return

        model = EvaluationReportModel(
            conversation_id=report.conversation_id,
            seed_id=report.seed_id,
            rouge_l=report.metrics.rouge_l,
            fidelidad_factual=report.metrics.fidelidad_factual,
            diversidad_lexica=report.metrics.diversidad_lexica,
            coherencia_dialogica=report.metrics.coherencia_dialogica,
            privacy_score=report.metrics.privacy_score,
            memorizacion=report.metrics.memorizacion,
            tool_call_validity=report.metrics.tool_call_validity,
            composite_score=report.composite_score,
            passed=report.passed,
            failures=report.failures,
            dominio=dominio,
        )
        self._session.add(model)
        await self._session.flush()

        logger.info(
            "evaluation_persisted",
            report_id=model.id,
            conversation_id=report.conversation_id,
            passed=report.passed,
        )

    async def evaluate_single(
        self, conversation: Conversation, seed: SeedSchema, *, strict: bool = False
    ) -> QualityReport:
        """Evaluate a single conversation against its origin seed.

        Args:
            conversation: The conversation to evaluate.
            seed: The origin seed for comparison.
            strict: If True, raise QualityThresholdError when the
                conversation fails quality thresholds.
        """
        report = await self._evaluator.evaluate(conversation, seed)
        await self._persist_report(report, dominio=conversation.dominio)

        if self._session is not None:
            await self._session.commit()

        if strict and not report.passed:
            failure_detail = ", ".join(report.failures) if report.failures else "composite score below threshold"
            raise QualityThresholdError(
                f"Quality thresholds not met for conversation {report.conversation_id}: {failure_detail}"
            )

        return report

    async def evaluate_batch(self, conversations: list[Conversation], seeds: list[SeedSchema]) -> BatchEvaluationResult:
        """Evaluate a batch and return summary statistics."""
        reports = await self._evaluator.evaluate_batch(conversations, seeds)

        # Persist all reports
        for report, conv in zip(reports, conversations, strict=True):
            await self._persist_report(report, dominio=conv.dominio)

        if self._session is not None:
            await self._session.commit()

        passed = [r for r in reports if r.passed]
        failed = [r for r in reports if not r.passed]

        avg_composite = sum(r.composite_score for r in reports) / len(reports) if reports else 0.0

        # Aggregate metric averages
        metric_avgs: dict[str, float] = {}
        if reports:
            metric_fields = [
                "rouge_l",
                "fidelidad_factual",
                "diversidad_lexica",
                "coherencia_dialogica",
                "tool_call_validity",
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
