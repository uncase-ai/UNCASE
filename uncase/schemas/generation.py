"""API request/response schemas for the generation endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001
from uncase.schemas.quality import QualityReport  # noqa: TC001
from uncase.schemas.seed import SeedSchema  # noqa: TC001


class GenerateRequest(BaseModel):
    """Request body for synthetic conversation generation."""

    seed: SeedSchema = Field(..., description="Seed to generate conversations from")
    count: int = Field(default=1, ge=1, le=50, description="Number of conversations to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM sampling temperature")
    model: str | None = Field(default=None, description="Override default LLM model")
    provider_id: str | None = Field(default=None, description="Provider ID to use. Falls back to env-based API key.")
    language_override: str | None = Field(default=None, description="Override seed language (ISO 639-1)")
    evaluate_after: bool = Field(default=True, description="Run quality evaluation on generated conversations")


class GenerationProgress(BaseModel):
    """Progress update for streaming generation."""

    completed: int = Field(..., ge=0, description="Number of conversations completed")
    total: int = Field(..., ge=1, description="Total conversations to generate")
    current_conversation_id: str | None = Field(default=None, description="ID of current conversation")
    status: str = Field(..., description="Current status: generating, evaluating, complete, error")


class GenerationSummary(BaseModel):
    """Summary statistics for a generation run."""

    total_generated: int = Field(..., ge=0, description="Total conversations generated")
    total_passed: int | None = Field(default=None, description="Conversations passing quality thresholds")
    avg_composite_score: float | None = Field(default=None, description="Average composite quality score")
    model_used: str = Field(..., description="LLM model used for generation")
    temperature: float = Field(..., description="Temperature used for generation")
    duration_seconds: float = Field(..., ge=0.0, description="Total generation time in seconds")


class GenerateResponse(BaseModel):
    """Response body for synthetic conversation generation."""

    conversations: list[Conversation] = Field(..., description="Generated synthetic conversations")
    reports: list[QualityReport] | None = Field(default=None, description="Quality reports if evaluate_after was True")
    generation_summary: GenerationSummary = Field(..., description="Summary statistics")
