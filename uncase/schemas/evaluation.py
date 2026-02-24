"""API request/response schemas for the evaluation endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001
from uncase.schemas.quality import QualityReport  # noqa: TC001
from uncase.schemas.seed import SeedSchema  # noqa: TC001


class EvaluatePair(BaseModel):
    """A single conversation-seed pair for batch evaluation."""

    conversation: Conversation = Field(..., description="Conversation to evaluate")
    seed: SeedSchema = Field(..., description="Origin seed for comparison")


class EvaluateRequest(BaseModel):
    """Request body for single conversation evaluation."""

    conversation: Conversation = Field(..., description="Conversation to evaluate")
    seed: SeedSchema = Field(..., description="Origin seed for comparison")


class EvaluateBatchRequest(BaseModel):
    """Request body for batch conversation evaluation."""

    pairs: list[EvaluatePair] = Field(..., min_length=1, description="Conversation-seed pairs to evaluate")


class BatchEvaluationResponse(BaseModel):
    """Response body for batch evaluation."""

    total: int = Field(..., description="Total conversations evaluated")
    passed: int = Field(..., description="Number passing all thresholds")
    failed: int = Field(..., description="Number failing one or more thresholds")
    pass_rate: float = Field(..., description="Pass rate percentage")
    avg_composite_score: float = Field(..., description="Average composite quality score")
    metric_averages: dict[str, float] = Field(default_factory=dict, description="Per-metric averages")
    failure_summary: dict[str, int] = Field(default_factory=dict, description="Failure counts by metric")
    reports: list[QualityReport] = Field(default_factory=list, description="Individual evaluation reports")


class QualityThresholdsResponse(BaseModel):
    """Response showing current quality thresholds."""

    rouge_l_min: float = Field(default=0.65, description="Minimum ROUGE-L score")
    fidelidad_min: float = Field(default=0.90, description="Minimum factual fidelity")
    diversidad_lexica_min: float = Field(default=0.55, description="Minimum TTR")
    coherencia_dialogica_min: float = Field(default=0.85, description="Minimum dialog coherence")
    privacy_score_max: float = Field(default=0.0, description="Maximum PII residual (must be 0.0)")
    memorizacion_max: float = Field(default=0.01, description="Maximum memorization rate")
    formula: str = Field(
        default="Q = min(rouge_l, fidelidad, ttr, coherencia) if privacy=0.0 AND memorization<0.01 else 0.0",
        description="Composite score formula",
    )
