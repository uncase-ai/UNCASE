"""Jobs API — background job management endpoints."""

from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.db.models.organization import OrganizationModel
from uncase.services.jobs import JobService

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

logger = structlog.get_logger(__name__)


class JobResponse(BaseModel):
    """Job status response."""

    id: str = Field(..., description="Job ID")
    job_type: str = Field(..., description="Job type")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., description="Progress 0.0 to 1.0")
    current_stage: str | None = Field(default=None, description="Current stage")
    status_message: str | None = Field(default=None, description="Status message")
    config: dict[str, Any] = Field(default_factory=dict, description="Job configuration")
    result: dict[str, Any] | None = Field(default=None, description="Job result")
    error_message: str | None = Field(default=None, description="Error message")
    organization_id: str | None = Field(default=None, description="Organization ID")
    started_at: str | None = Field(default=None, description="Start timestamp")
    completed_at: str | None = Field(default=None, description="Completion timestamp")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


def _to_response(job: Any) -> JobResponse:
    """Convert a JobModel to JobResponse."""
    return JobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        current_stage=job.current_stage,
        status_message=job.status_message,
        config=job.config or {},
        result=job.result,
        error_message=job.error_message,
        organization_id=job.organization_id,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        created_at=job.created_at.isoformat(),
    )


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    job_type: Annotated[str | None, Query(description="Filter by job type")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 20,
) -> list[JobResponse]:
    """List background jobs with optional filters."""
    service = JobService(session)
    jobs = await service.list_jobs(
        organization_id=org.id if org else None,
        job_type=job_type,
        status=status,
        page=page,
        page_size=page_size,
    )
    return [_to_response(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """Get the status and result of a specific job."""
    service = JobService(session)
    job = await service.get_job(job_id)
    return _to_response(job)


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """Cancel a running or pending job."""
    service = JobService(session)
    job = await service.cancel_job(job_id)
    return _to_response(job)
