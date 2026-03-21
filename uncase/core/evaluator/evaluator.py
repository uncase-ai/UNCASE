"""Conversation quality evaluator — Layer 2 implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from uncase.core.evaluator.base import BaseEvaluator
from uncase.core.evaluator.metrics.coherence import DialogCoherenceMetric
from uncase.core.evaluator.metrics.diversity import LexicalDiversityMetric
from uncase.core.evaluator.metrics.fidelity import FactualFidelityMetric
from uncase.core.evaluator.metrics.memorization import MemorizationMetric
from uncase.core.evaluator.metrics.privacy import PrivacyMetric
from uncase.core.evaluator.metrics.rouge import ROUGELMetric
from uncase.core.evaluator.metrics.tool_call import ToolCallValidatorMetric
from uncase.core.evaluator.semantic_judge import EmbeddingDriftMetric, SemanticFidelityMetric
from uncase.schemas.quality import (
    _NEUTRAL_SCORE,
    OPTIONAL_METRICS,
    QualityMetrics,
    QualityReport,
    compute_composite_score,
)

if TYPE_CHECKING:
    from uncase.core.evaluator.metrics.base import BaseMetric
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


class ConversationEvaluator(BaseEvaluator):
    """Concrete evaluator that computes all quality metrics for a conversation.

    This is the primary Layer 2 implementation. It orchestrates all
    individual metrics, computes the composite score, and produces
    a QualityReport with pass/fail determination.

    Usage:
        evaluator = ConversationEvaluator()
        report = await evaluator.evaluate(conversation, seed)
        if report.passed:
            # conversation meets all quality thresholds
            ...
    """

    def __init__(self, *, metrics: list[BaseMetric] | None = None) -> None:
        """Initialize with optional custom metric set.

        Args:
            metrics: Custom list of metrics. If None, uses all built-in metrics.
        """
        self._metrics = metrics or self._default_metrics()

    @staticmethod
    def _default_metrics() -> list[BaseMetric]:
        """Return the standard set of quality metrics.

        Includes both lexical metrics (always available) and semantic
        metrics (EmbeddingDrift with TF-IDF fallback is always available;
        SemanticFidelity requires LLM API access).
        """
        return [
            ROUGELMetric(),
            FactualFidelityMetric(),
            LexicalDiversityMetric(),
            DialogCoherenceMetric(),
            ToolCallValidatorMetric(),
            PrivacyMetric(),
            MemorizationMetric(),
            EmbeddingDriftMetric(),
            SemanticFidelityMetric(),
        ]

    async def evaluate(self, conversation: Conversation, seed: SeedSchema) -> QualityReport:
        """Evaluate a single conversation against its seed.

        Computes all metrics, applies the composite scoring formula
        with privacy/memorization gates, and returns a full report.

        Metrics that provide a ``compute_async()`` method are awaited
        directly so that LLM-backed evaluations (SemanticFidelity,
        EmbeddingDrift) actually execute instead of falling back to
        neutral scores.
        """
        logger.info(
            "evaluating_conversation",
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            domain=conversation.dominio,
        )

        scores: dict[str, float] = {}
        for metric in self._metrics:
            # Prefer the async path when available — avoids the
            # "already in an event loop" fallback that returns 0.5.
            if hasattr(metric, "compute_async"):
                score = await metric.compute_async(conversation, seed)
            else:
                score = metric.compute(conversation, seed)
            scores[metric.name] = max(0.0, min(1.0, score))  # Clamp to [0, 1]

        # Detect which optional metrics came back at neutral (weren't computed)
        skipped: list[str] = [
            name for name in OPTIONAL_METRICS if name in scores and abs(scores[name] - _NEUTRAL_SCORE) < 1e-9
        ]
        if skipped:
            logger.warning(
                "metrics_skipped",
                conversation_id=conversation.conversation_id,
                skipped=skipped,
                reason="LLM API unavailable or returned empty response",
            )

        # Build QualityMetrics from computed scores.
        # Memorization is computed by MemorizationMetric via LCS-based
        # extraction attack simulation against seed text.
        metrics = QualityMetrics(
            rouge_l=scores.get("rouge_l", 0.0),
            fidelidad_factual=scores.get("fidelidad_factual", 0.0),
            diversidad_lexica=scores.get("diversidad_lexica", 0.0),
            coherencia_dialogica=scores.get("coherencia_dialogica", 0.0),
            tool_call_validity=scores.get("tool_call_validity", 1.0),
            privacy_score=scores.get("privacy_score", 0.0),
            memorizacion=scores.get("memorizacion", 0.0),
            semantic_fidelity=scores.get("semantic_fidelity", 0.5),
            embedding_drift=scores.get("embedding_drift", 0.5),
        )

        composite, weighted_mean, passed, failures = compute_composite_score(metrics)

        if skipped:
            logger.info(
                "composite_score_computed_with_skipped_metrics",
                conversation_id=conversation.conversation_id,
                skipped_metrics=skipped,
                composite_score=composite,
                note="Skipped metrics excluded from composite MIN and threshold checks",
            )

        report = QualityReport(
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            metrics=metrics,
            composite_score=composite,
            weighted_mean=weighted_mean,
            passed=passed,
            failures=failures,
            skipped_metrics=skipped,
        )

        logger.info(
            "evaluation_complete",
            conversation_id=conversation.conversation_id,
            composite_score=composite,
            passed=passed,
            failure_count=len(failures),
        )

        return report

    async def evaluate_batch(self, conversations: list[Conversation], seeds: list[SeedSchema]) -> list[QualityReport]:
        """Evaluate a batch of conversations against their seeds.

        Each conversation is paired with the seed at the same index.
        If lengths differ, raises ValueError.
        """
        if len(conversations) != len(seeds):
            msg = f"Mismatched batch sizes: {len(conversations)} conversations vs {len(seeds)} seeds"
            raise ValueError(msg)

        logger.info("evaluating_batch", batch_size=len(conversations))

        reports: list[QualityReport] = []
        for conv, seed in zip(conversations, seeds, strict=True):
            report = await self.evaluate(conv, seed)
            reports.append(report)

        passed_count = sum(1 for r in reports if r.passed)
        logger.info(
            "batch_evaluation_complete",
            total=len(reports),
            passed=passed_count,
            failed=len(reports) - passed_count,
        )

        return reports
