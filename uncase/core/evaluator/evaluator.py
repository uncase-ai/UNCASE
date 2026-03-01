"""Conversation quality evaluator — Layer 2 implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from uncase.core.evaluator.base import BaseEvaluator
from uncase.core.evaluator.metrics.coherence import DialogCoherenceMetric
from uncase.core.evaluator.metrics.diversity import LexicalDiversityMetric
from uncase.core.evaluator.metrics.fidelity import FactualFidelityMetric
from uncase.core.evaluator.metrics.privacy import PrivacyMetric
from uncase.core.evaluator.metrics.rouge import ROUGELMetric
from uncase.core.evaluator.metrics.tool_call import ToolCallValidatorMetric
from uncase.core.evaluator.semantic_judge import EmbeddingDriftMetric, SemanticFidelityMetric
from uncase.schemas.quality import QualityMetrics, QualityReport, compute_composite_score

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
            EmbeddingDriftMetric(),
            SemanticFidelityMetric(),
        ]

    async def evaluate(self, conversation: Conversation, seed: SeedSchema) -> QualityReport:
        """Evaluate a single conversation against its seed.

        Computes all metrics, applies the composite scoring formula
        with privacy/memorization gates, and returns a full report.
        """
        logger.info(
            "evaluating_conversation",
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            domain=conversation.dominio,
        )

        scores: dict[str, float] = {}
        for metric in self._metrics:
            score = metric.compute(conversation, seed)
            scores[metric.name] = max(0.0, min(1.0, score))  # Clamp to [0, 1]

        # Build QualityMetrics from computed scores.
        # Memorization is set to 0.0 by default — it requires a trained
        # model to test extraction attacks, which is a Layer 4 concern.
        # The evaluator accepts an override if one is provided.
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

        composite, passed, failures = compute_composite_score(metrics)

        report = QualityReport(
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            metrics=metrics,
            composite_score=composite,
            passed=passed,
            failures=failures,
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
