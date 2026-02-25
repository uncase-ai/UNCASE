"""Pipeline API — end-to-end pipeline orchestration endpoints."""

from __future__ import annotations

import asyncio
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org, get_settings
from uncase.api.metering import meter
from uncase.config import UNCASESettings
from uncase.db.models.organization import OrganizationModel
from uncase.services.jobs import JobService

# Background task references to prevent garbage collection (Python asyncio requirement)
_background_tasks: set[asyncio.Task[None]] = set()

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

logger = structlog.get_logger(__name__)


class PipelineRunRequest(BaseModel):
    """Request to run the full end-to-end pipeline."""

    raw_conversations: list[str] = Field(
        ..., min_length=1, max_length=100, description="Raw conversation texts (any format)"
    )
    domain: str = Field(..., description="Domain namespace (e.g. 'automotive.sales')")
    count: int = Field(default=10, ge=1, le=1000, description="Synthetic conversations per seed")
    model: str | None = Field(default=None, description="LLM model override")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    train_adapter: bool = Field(default=False, description="Train LoRA adapter after generation")
    base_model: str = Field(default="meta-llama/Llama-3.1-8B", description="Base model for LoRA training")
    use_qlora: bool = Field(default=True, description="Use QLoRA 4-bit quantization")
    use_dp_sgd: bool = Field(default=False, description="Enable DP-SGD differential privacy")
    dp_epsilon: float = Field(default=8.0, gt=0.0, description="Privacy budget epsilon")
    async_mode: bool = Field(default=True, description="Run as background job (recommended for large runs)")


class PipelineRunResponse(BaseModel):
    """Response for pipeline run submission."""

    job_id: str = Field(..., description="Background job ID for tracking")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Human-readable message")


class PipelineStatusResponse(BaseModel):
    """Detailed pipeline status with stage-level breakdown."""

    job_id: str
    status: str
    progress: float
    current_stage: str | None = None
    status_message: str | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None


@router.post("/run", response_model=PipelineRunResponse, status_code=202)
async def run_pipeline(
    request: PipelineRunRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> PipelineRunResponse:
    """Submit an end-to-end pipeline run.

    The pipeline chains: Seed Engine -> Generation -> Evaluation -> LoRA Training.
    By default, runs asynchronously as a background job.
    """
    org_id = org.id if org else None

    # Create the background job
    job_service = JobService(session)
    job = await job_service.create_job(
        job_type="pipeline_run",
        config=request.model_dump(),
        organization_id=org_id,
    )

    # Meter the event
    await meter(
        session,
        "pipeline_run_submitted",
        organization_id=org_id,
        resource_id=job.id,
        metadata={"domain": request.domain, "count": request.count, "train": request.train_adapter},
    )

    if request.async_mode:
        # Launch background execution — store reference to prevent GC
        task = asyncio.create_task(_execute_pipeline_job(job.id, request, settings))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

        return PipelineRunResponse(
            job_id=job.id,
            status="pending",
            message=f"Pipeline job {job.id} submitted. Use GET /api/v1/jobs/{job.id} to track progress.",
        )

    # Synchronous mode (for small runs / testing)
    from uncase.core.pipeline_orchestrator import PipelineOrchestrator

    async def _update_progress(stage: str, progress: float, message: str) -> None:
        try:
            await job_service.update_progress(job.id, progress=progress, current_stage=stage, status_message=message)
        except Exception:
            logger.debug("progress_update_failed", job_id=job.id, stage=stage)

    orchestrator = PipelineOrchestrator(
        settings=settings,
        progress_callback=lambda s, p, m: asyncio.create_task(_update_progress(s, p, m)),
    )

    await job_service.mark_running(job.id)

    try:
        result = await orchestrator.run(
            raw_conversations=request.raw_conversations,
            domain=request.domain,
            count=request.count,
            model=request.model,
            temperature=request.temperature,
            train_adapter=request.train_adapter,
            base_model=request.base_model,
            use_qlora=request.use_qlora,
            use_dp_sgd=request.use_dp_sgd,
            dp_epsilon=request.dp_epsilon,
        )

        result_data = {
            "run_id": result.run_id,
            "success": result.success,
            "seeds_created": result.seeds_created,
            "conversations_generated": result.conversations_generated,
            "conversations_passed": result.conversations_passed,
            "avg_quality_score": result.avg_quality_score,
            "pass_rate": result.pass_rate,
            "adapter_path": str(result.adapter_path) if result.adapter_path else None,
            "total_duration_seconds": result.total_duration_seconds,
            "stages": [
                {
                    "stage": s.stage,
                    "success": s.success,
                    "duration_seconds": s.duration_seconds,
                    "error": s.error,
                }
                for s in result.stages
            ],
        }

        await job_service.mark_completed(job.id, result=result_data)

        return PipelineRunResponse(
            job_id=job.id,
            status="completed",
            message=f"Pipeline completed: {result.conversations_generated} conversations, "
            f"{result.conversations_passed} passed ({result.pass_rate:.0%} pass rate)",
        )

    except Exception as exc:
        await job_service.mark_failed(job.id, str(exc))
        return PipelineRunResponse(
            job_id=job.id,
            status="failed",
            message=f"Pipeline failed: {exc}",
        )


async def _execute_pipeline_job(
    job_id: str,
    request: PipelineRunRequest,
    settings: UNCASESettings,
) -> None:
    """Execute a pipeline job in the background.

    Creates its own database session for the background task.
    """
    from uncase.core.pipeline_orchestrator import PipelineOrchestrator
    from uncase.db.engine import get_async_session

    async for session in get_async_session():
        svc = JobService(session)

        try:
            await svc.mark_running(job_id)

            async def _update_progress(
                stage: str, progress: float, message: str, _svc: JobService = svc
            ) -> None:
                try:
                    await _svc.update_progress(job_id, progress=progress, current_stage=stage, status_message=message)
                except Exception:
                    logger.debug("bg_progress_update_failed", job_id=job_id, stage=stage)

            orchestrator = PipelineOrchestrator(
                settings=settings,
                progress_callback=lambda s, p, m: asyncio.ensure_future(_update_progress(s, p, m)),
            )

            result = await orchestrator.run(
                raw_conversations=request.raw_conversations,
                domain=request.domain,
                count=request.count,
                model=request.model,
                temperature=request.temperature,
                train_adapter=request.train_adapter,
                base_model=request.base_model,
                use_qlora=request.use_qlora,
                use_dp_sgd=request.use_dp_sgd,
                dp_epsilon=request.dp_epsilon,
            )

            result_data = {
                "run_id": result.run_id,
                "success": result.success,
                "seeds_created": result.seeds_created,
                "conversations_generated": result.conversations_generated,
                "conversations_passed": result.conversations_passed,
                "avg_quality_score": result.avg_quality_score,
                "pass_rate": result.pass_rate,
                "adapter_path": str(result.adapter_path) if result.adapter_path else None,
                "total_duration_seconds": result.total_duration_seconds,
            }

            await svc.mark_completed(job_id, result=result_data)

        except Exception as exc:
            logger.error("background_pipeline_failed", job_id=job_id, error=str(exc))
            try:
                await svc.mark_failed(job_id, str(exc))
            except Exception:
                logger.error("failed_to_mark_job_failed", job_id=job_id)
