"""Quality metrics schemas and composite score calculation."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class QualityMetrics(BaseModel):
    """Individual quality metrics for a conversation."""

    rouge_l: float = Field(..., ge=0.0, le=1.0, description="ROUGE-L structural coherence score")
    fidelidad_factual: float = Field(..., ge=0.0, le=1.0, description="Factual fidelity score")
    diversidad_lexica: float = Field(..., ge=0.0, le=1.0, description="Type-Token Ratio (TTR)")
    coherencia_dialogica: float = Field(..., ge=0.0, le=1.0, description="Inter-turn dialog coherence")
    privacy_score: float = Field(..., ge=0.0, le=1.0, description="PII residual score (0.0 = clean)")
    memorizacion: float = Field(..., ge=0.0, le=1.0, description="Extraction attack success rate")


class QualityReport(BaseModel):
    """Quality evaluation report for a conversation."""

    conversation_id: str = Field(..., description="Evaluated conversation ID")
    seed_id: str = Field(..., description="Origin seed ID")
    metrics: QualityMetrics = Field(..., description="Individual metric scores")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Composite quality score")
    passed: bool = Field(..., description="Whether the conversation meets all thresholds")
    failures: list[str] = Field(default_factory=list, description="List of failed threshold checks")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp")


def compute_composite_score(metrics: QualityMetrics) -> tuple[float, bool, list[str]]:
    """Compute the composite quality score.

    Formula: Q = min(ROUGE-L, Fidelidad, TTR, Coherencia)
             if privacy_score == 0.0 AND memorizacion < 0.01
             else Q = 0.0

    Args:
        metrics: Individual quality metrics.

    Returns:
        Tuple of (score, passed, failures).
    """
    failures: list[str] = []

    # Privacy gate (non-negotiable)
    if metrics.privacy_score != 0.0:
        failures.append(f"privacy_score={metrics.privacy_score} (must be 0.0)")

    # Memorization gate (non-negotiable)
    if metrics.memorizacion >= 0.01:
        failures.append(f"memorizacion={metrics.memorizacion} (must be < 0.01)")

    # If either gate fails, score is zero
    if failures:
        return 0.0, False, failures

    # Composite = min of all quality dimensions
    score = min(
        metrics.rouge_l,
        metrics.fidelidad_factual,
        metrics.diversidad_lexica,
        metrics.coherencia_dialogica,
    )

    # Check individual thresholds
    thresholds = {
        "rouge_l": (metrics.rouge_l, 0.65),
        "fidelidad_factual": (metrics.fidelidad_factual, 0.90),
        "diversidad_lexica": (metrics.diversidad_lexica, 0.55),
        "coherencia_dialogica": (metrics.coherencia_dialogica, 0.85),
    }

    for name, (value, threshold) in thresholds.items():
        if value < threshold:
            failures.append(f"{name}={value} (min {threshold})")

    passed = len(failures) == 0
    return score, passed, failures
