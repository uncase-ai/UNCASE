"""API request/response schemas for the evaluation endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001
from uncase.schemas.quality import QualityReport  # noqa: TC001
from uncase.schemas.seed import SeedSchema  # noqa: TC001

if TYPE_CHECKING:
    from datetime import datetime


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
    tool_call_validity_min: float = Field(default=0.90, description="Minimum tool call validity")
    privacy_score_max: float = Field(default=0.0, description="Maximum PII residual (must be 0.0)")
    memorizacion_max: float = Field(default=0.01, description="Maximum memorization rate")
    formula: str = Field(
        default="Q = min(rouge_l, fidelidad, ttr, coherencia) if privacy=0.0 AND memorization<0.01 else 0.0",
        description="Composite score formula",
    )


class EvaluationReportResponse(BaseModel):
    """Persisted evaluation report from the database."""

    id: str
    conversation_id: str
    seed_id: str | None
    rouge_l: float
    fidelidad_factual: float
    diversidad_lexica: float
    coherencia_dialogica: float
    privacy_score: float
    memorizacion: float
    tool_call_validity: float | None = None
    composite_score: float
    passed: bool
    failures: list[str]
    dominio: str | None
    organization_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationReportListResponse(BaseModel):
    """Paginated list of evaluation reports."""

    items: list[EvaluationReportResponse]
    total: int
    page: int
    page_size: int


# Rebuild models that reference TYPE_CHECKING-only imports (datetime)
def _rebuild_models() -> None:
    from datetime import datetime as _dt

    ns = {"datetime": _dt}
    EvaluationReportResponse.model_rebuild(_types_namespace=ns)
    EvaluationReportListResponse.model_rebuild(_types_namespace=ns)


_rebuild_models()
del _rebuild_models
