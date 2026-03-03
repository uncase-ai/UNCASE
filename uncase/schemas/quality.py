"""Quality metrics schemas and composite score calculation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final

from pydantic import BaseModel, Field

# Neutral score returned by optional metrics when the API is unavailable.
_NEUTRAL_SCORE: Final[float] = 0.5

# Metrics that are optional — they require external API calls and fall back
# to _NEUTRAL_SCORE when unavailable. They are excluded from the composite
# MIN formula when at their neutral value to avoid penalizing environments
# without LLM-judge or embedding APIs configured.
OPTIONAL_METRICS: Final[frozenset[str]] = frozenset({"semantic_fidelity", "embedding_drift"})

# Canonical threshold definitions — single source of truth.
# Referenced by compute_composite_score(), CLI, API, and docs.
QUALITY_THRESHOLDS: Final[dict[str, tuple[float, str, str]]] = {
    # name: (threshold, operator, description)
    "rouge_l": (0.55, ">=", "ROUGE-L structural coherence with seed"),
    "fidelidad_factual": (0.85, ">=", "Factual fidelity (domain constraint adherence)"),
    "diversidad_lexica": (0.55, ">=", "Type-Token Ratio (lexical diversity)"),
    "coherencia_dialogica": (0.80, ">=", "Inter-turn dialog coherence"),
    "tool_call_validity": (0.80, ">=", "Tool call schema validity"),
    "privacy_score": (0.0, "=", "PII residual (MUST be zero)"),
    "memorizacion": (0.01, "<", "Extraction attack success rate"),
    "semantic_fidelity": (0.60, ">=", "Semantic fidelity (LLM-as-Judge)"),
    "embedding_drift": (0.40, ">=", "Semantic drift (embedding cosine similarity)"),
}


class QualityMetrics(BaseModel):
    """Individual quality metrics for a conversation."""

    rouge_l: float = Field(..., ge=0.0, le=1.0, description="ROUGE-L structural coherence score")
    fidelidad_factual: float = Field(..., ge=0.0, le=1.0, description="Factual fidelity score")
    diversidad_lexica: float = Field(..., ge=0.0, le=1.0, description="Type-Token Ratio (TTR)")
    coherencia_dialogica: float = Field(..., ge=0.0, le=1.0, description="Inter-turn dialog coherence")
    tool_call_validity: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Tool call schema validity (1.0 = all valid or no tools)"
    )
    privacy_score: float = Field(..., ge=0.0, le=1.0, description="PII residual score (0.0 = clean)")
    memorizacion: float = Field(..., ge=0.0, le=1.0, description="Extraction attack success rate")
    semantic_fidelity: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Semantic fidelity via LLM-as-Judge (0.5 = neutral/unavailable)"
    )
    embedding_drift: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Semantic drift via embedding cosine similarity"
    )


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

    Formula: Q = min(core_metrics + [optional_metrics if computed])
             if privacy_score == 0.0 AND memorizacion < 0.01
             else Q = 0.0

    Optional metrics (semantic_fidelity, embedding_drift) are only included
    in the composite MIN and threshold checks when they have been actually
    computed (i.e. not at the neutral fallback value of 0.5). This prevents
    environments without LLM-judge or embedding APIs from being penalized.

    Args:
        metrics: Individual quality metrics.

    Returns:
        Tuple of (score, passed, failures).
    """
    failures: list[str] = []

    # Check all thresholds using canonical definitions.
    # Optional metrics at neutral score are skipped — they weren't computed.
    gate_metrics = {"privacy_score", "memorizacion"}
    for name, (threshold, operator, _desc) in QUALITY_THRESHOLDS.items():
        value = getattr(metrics, name)

        # Skip optional metrics that are at neutral (not computed)
        if name in OPTIONAL_METRICS and abs(value - _NEUTRAL_SCORE) < 1e-9:
            continue

        if operator == ">=" and value < threshold:
            failures.append(f"{name}={value} (min {threshold})")
        elif operator == "<" and value >= threshold:
            failures.append(f"{name}={value} (must be < {threshold})")
        elif operator == "=" and abs(value - threshold) > 1e-9:
            failures.append(f"{name}={value} (must be {threshold})")

    # Gate metrics kill the composite score entirely
    gate_failed = any(f.startswith(name) for f in failures for name in gate_metrics)

    if gate_failed:
        return 0.0, False, failures

    # Composite = min of core quality dimensions.
    # Optional metrics are only included when actually computed.
    scores = [
        metrics.rouge_l,
        metrics.fidelidad_factual,
        metrics.diversidad_lexica,
        metrics.coherencia_dialogica,
        metrics.tool_call_validity,
    ]

    # Include optional metrics only when they were computed (not neutral)
    if abs(metrics.semantic_fidelity - _NEUTRAL_SCORE) > 1e-9:
        scores.append(metrics.semantic_fidelity)
    if abs(metrics.embedding_drift - _NEUTRAL_SCORE) > 1e-9:
        scores.append(metrics.embedding_drift)

    score = min(scores)

    passed = len(failures) == 0
    return score, passed, failures
