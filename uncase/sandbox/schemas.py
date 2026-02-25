"""Pydantic schemas for E2B sandbox generation, demos, and evaluation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001
from uncase.schemas.quality import QualityReport  # noqa: TC001
from uncase.schemas.seed import SeedSchema  # noqa: TC001

# -- Sandbox template types --


class SandboxTemplate(StrEnum):
    """Sandbox template types for different workloads."""

    GENERATION = "generation"
    DEMO_AUTOMOTIVE = "demo_automotive"
    DEMO_MEDICAL = "demo_medical"
    DEMO_LEGAL = "demo_legal"
    DEMO_FINANCE = "demo_finance"
    DEMO_INDUSTRIAL = "demo_industrial"
    DEMO_EDUCATION = "demo_education"
    EVALUATION_OPIK = "evaluation_opik"
    TRAINING_LORA = "training_lora"

    @property
    def is_demo(self) -> bool:
        """Check if this is a demo template."""
        return self.value.startswith("demo_")

    @property
    def domain(self) -> str | None:
        """Extract domain from demo template name."""
        domain_map = {
            "demo_automotive": "automotive.sales",
            "demo_medical": "medical.consultation",
            "demo_legal": "legal.advisory",
            "demo_finance": "finance.advisory",
            "demo_industrial": "industrial.support",
            "demo_education": "education.tutoring",
        }
        return domain_map.get(self.value)


class SandboxJobStatus(StrEnum):
    """Lifecycle states for a sandbox job."""

    PENDING = "pending"
    BOOTING = "booting"
    RUNNING = "running"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class SandboxJob(BaseModel):
    """Tracks a sandbox job through its lifecycle."""

    job_id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique job identifier")
    template: SandboxTemplate = Field(..., description="Sandbox template type")
    status: SandboxJobStatus = Field(default=SandboxJobStatus.PENDING, description="Current job status")
    organization_id: str | None = Field(default=None, description="Owning organization")
    sandbox_url: str | None = Field(default=None, description="URL to access the sandbox (for demos)")
    api_url: str | None = Field(default=None, description="API URL inside the sandbox")
    opik_url: str | None = Field(default=None, description="Opik UI URL (for evaluation sandboxes)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Job creation time")
    expires_at: datetime | None = Field(default=None, description="When the sandbox auto-destroys")
    error: str | None = Field(default=None, description="Error message if failed")
    metadata: dict[str, str] = Field(default_factory=dict, description="Job-level metadata")


class SandboxConfig(BaseModel):
    """Configuration for a sandbox generation job."""

    max_parallel: int = Field(default=5, ge=1, le=20, description="Max concurrent sandboxes")
    sandbox_timeout: int = Field(default=300, ge=30, le=600, description="Timeout per sandbox in seconds")
    template_id: str = Field(default="base", description="E2B sandbox template ID")


class SandboxGenerateRequest(BaseModel):
    """Request body for sandbox-based parallel generation."""

    seeds: list[SeedSchema] = Field(..., min_length=1, description="Seeds to generate from (one sandbox per seed)")
    count_per_seed: int = Field(default=1, ge=1, le=10, description="Conversations per seed")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM sampling temperature")
    model: str | None = Field(default=None, description="Override default LLM model")
    provider_id: str | None = Field(default=None, description="Provider ID for API key resolution")
    language_override: str | None = Field(default=None, description="Override seed language")
    evaluate_after: bool = Field(default=True, description="Run quality evaluation inside each sandbox")
    max_parallel: int = Field(default=5, ge=1, le=20, description="Max concurrent sandboxes")


class SandboxProgress(BaseModel):
    """Real-time progress update from sandbox execution."""

    seed_id: str = Field(..., description="Seed being processed")
    sandbox_index: int = Field(..., ge=0, description="Sandbox index in the batch")
    total_sandboxes: int = Field(..., ge=1, description="Total sandboxes in the batch")
    status: str = Field(..., description="Status: queued, booting, generating, evaluating, complete, error")
    conversations_completed: int = Field(default=0, ge=0, description="Conversations completed so far")
    conversations_total: int = Field(default=0, ge=1, description="Total conversations for this sandbox")
    error: str | None = Field(default=None, description="Error message if status is 'error'")
    elapsed_seconds: float = Field(default=0.0, ge=0.0, description="Elapsed time in seconds")


class SandboxSeedResult(BaseModel):
    """Result from a single sandbox execution (one seed)."""

    seed_id: str = Field(..., description="Seed that was processed")
    conversations: list[Conversation] = Field(default_factory=list, description="Generated conversations")
    reports: list[QualityReport] | None = Field(default=None, description="Quality reports if evaluation was run")
    passed_count: int = Field(default=0, ge=0, description="Conversations passing quality thresholds")
    error: str | None = Field(default=None, description="Error message if generation failed")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Sandbox execution time")


class SandboxGenerationSummary(BaseModel):
    """Aggregate summary of a sandbox generation batch."""

    total_seeds: int = Field(..., ge=0, description="Total seeds processed")
    total_conversations: int = Field(default=0, ge=0, description="Total conversations generated")
    total_passed: int | None = Field(default=None, description="Total passing quality thresholds")
    avg_composite_score: float | None = Field(default=None, description="Average composite quality score")
    failed_seeds: int = Field(default=0, ge=0, description="Seeds that had errors")
    model_used: str = Field(..., description="LLM model used")
    temperature: float = Field(..., description="Temperature used")
    max_parallel: int = Field(..., description="Max parallel sandboxes used")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Total wall-clock time")
    sandbox_mode: bool = Field(default=True, description="Whether sandboxes were used (vs local fallback)")


class SandboxGenerateResponse(BaseModel):
    """Response body for sandbox-based parallel generation."""

    results: list[SandboxSeedResult] = Field(..., description="Per-seed results")
    summary: SandboxGenerationSummary = Field(..., description="Aggregate summary")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Job start time")


# -- Demo sandbox schemas --


class DemoSandboxRequest(BaseModel):
    """Request to spin up a short-lived demo sandbox for an industry vertical."""

    domain: str = Field(
        ...,
        description="Industry domain (automotive.sales, medical.consultation, etc.)",
    )
    ttl_minutes: int = Field(default=30, ge=5, le=60, description="Time-to-live in minutes before auto-destroy")
    preload_seeds: int = Field(default=3, ge=1, le=10, description="Number of demo seeds to pre-load")
    language: str = Field(default="es", description="Demo language (ISO 639-1)")


class DemoSandboxResponse(BaseModel):
    """Response with demo sandbox access details."""

    job: SandboxJob = Field(..., description="Job tracking info")
    api_url: str = Field(..., description="UNCASE API URL inside the sandbox")
    docs_url: str = Field(..., description="Swagger docs URL")
    expires_at: datetime = Field(..., description="When the sandbox will auto-destroy")
    preloaded_seeds: int = Field(..., ge=0, description="Number of pre-loaded seeds")
    domain: str = Field(..., description="Industry domain of the demo")


# -- Opik evaluation sandbox schemas --


class OpikEvaluationRequest(BaseModel):
    """Request to spin up an Opik evaluation sandbox for a generation run."""

    conversations: list[Conversation] = Field(..., min_length=1, description="Conversations to evaluate in Opik")
    seeds: list[SeedSchema] = Field(..., min_length=1, description="Origin seeds for reference")
    experiment_name: str = Field(default="uncase-eval", description="Opik experiment name")
    model: str | None = Field(default=None, description="LLM model used for LLM-as-judge metrics")
    provider_id: str | None = Field(default=None, description="Provider ID for API key resolution")
    ttl_minutes: int = Field(default=60, ge=10, le=180, description="Sandbox TTL in minutes")
    run_hallucination_check: bool = Field(default=True, description="Run Opik hallucination metric")
    run_coherence_check: bool = Field(default=True, description="Run Opik coherence GEval")
    run_relevance_check: bool = Field(default=True, description="Run Opik answer relevance metric")
    export_before_destroy: bool = Field(default=True, description="Export results before sandbox dies")


class OpikMetricResult(BaseModel):
    """Result from a single Opik metric evaluation."""

    metric_name: str = Field(..., description="Metric name (hallucination, coherence, etc.)")
    value: float = Field(..., ge=0.0, le=1.0, description="Metric score")
    reason: str | None = Field(default=None, description="Explanation from LLM-as-judge")


class OpikConversationResult(BaseModel):
    """Opik evaluation results for a single conversation."""

    conversation_id: str = Field(..., description="Evaluated conversation ID")
    seed_id: str = Field(..., description="Origin seed ID")
    metrics: list[OpikMetricResult] = Field(default_factory=list, description="Per-metric results")
    uncase_composite_score: float = Field(..., ge=0.0, le=1.0, description="UNCASE composite quality score")
    opik_avg_score: float = Field(..., ge=0.0, le=1.0, description="Average Opik metric score")


class OpikEvaluationSummary(BaseModel):
    """Aggregate summary of an Opik evaluation run."""

    total_conversations: int = Field(..., ge=0, description="Total conversations evaluated")
    avg_hallucination: float | None = Field(default=None, description="Average hallucination score (0=clean)")
    avg_coherence: float | None = Field(default=None, description="Average GEval coherence score")
    avg_relevance: float | None = Field(default=None, description="Average answer relevance score")
    avg_uncase_composite: float = Field(..., ge=0.0, le=1.0, description="Average UNCASE composite score")
    avg_opik_score: float = Field(..., ge=0.0, le=1.0, description="Average Opik composite score")
    passed_uncase: int = Field(default=0, ge=0, description="Passing UNCASE thresholds")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Total evaluation time")


class OpikEvaluationResponse(BaseModel):
    """Response from an Opik evaluation sandbox run."""

    job: SandboxJob = Field(..., description="Job tracking info")
    experiment_name: str = Field(..., description="Opik experiment name")
    results: list[OpikConversationResult] = Field(default_factory=list, description="Per-conversation results")
    summary: OpikEvaluationSummary = Field(..., description="Aggregate evaluation summary")
    opik_url: str | None = Field(default=None, description="Opik UI URL (available while sandbox lives)")
    exported: bool = Field(default=False, description="Whether results were exported to persistent storage")


# -- Export schemas --


class ExportArtifact(BaseModel):
    """An artifact exported from a sandbox before destruction."""

    artifact_type: str = Field(
        ..., description="Type: conversations, reports, opik_traces, opik_experiments, lora_adapter"
    )
    format: str = Field(default="json", description="Export format (json, jsonl, csv, safetensors)")
    size_bytes: int = Field(default=0, ge=0, description="Artifact size in bytes")
    path: str | None = Field(default=None, description="Local path where artifact was saved")
    url: str | None = Field(default=None, description="Remote URL if uploaded to cloud storage")
    record_count: int = Field(default=0, ge=0, description="Number of records in the artifact")


class SandboxExportResult(BaseModel):
    """Result of exporting data from a sandbox before destruction."""

    job_id: str = Field(..., description="Sandbox job ID")
    artifacts: list[ExportArtifact] = Field(default_factory=list, description="Exported artifacts")
    total_size_bytes: int = Field(default=0, ge=0, description="Total size of all artifacts")
    exported_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Export timestamp")
    error: str | None = Field(default=None, description="Error if export partially failed")
