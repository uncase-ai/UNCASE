"""Background job service — manages job lifecycle and async execution."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import structlog
from sqlalchemy import select, update

from uncase.db.models.job import JobModel
from uncase.exceptions import JobNotFoundError, UNCASEError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


class JobService:
    """Service for creating, querying, and managing background jobs.

    Jobs are persisted in PostgreSQL for durability. Long-running operations
    are executed via ``asyncio.create_task`` with progress tracking.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_job(
        self,
        *,
        job_type: str,
        config: dict[str, Any],
        organization_id: str | None = None,
    ) -> JobModel:
        """Create a new pending job.

        Args:
            job_type: Job type (pipeline_run, generation, evaluation, training, import).
            config: Job configuration parameters.
            organization_id: Optional owning organization.

        Returns:
            The created JobModel instance.
        """
        job = JobModel(
            id=uuid.uuid4().hex,
            job_type=job_type,
            config=config,
            organization_id=organization_id,
            status="pending",
            progress=0.0,
        )
        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)

        logger.info("job_created", job_id=job.id, job_type=job_type)
        return job

    async def get_job(self, job_id: str) -> JobModel:
        """Get a job by ID.

        Raises:
            JobNotFoundError: If job does not exist.
        """
        stmt = select(JobModel).where(JobModel.id == job_id)
        result = await self._session.execute(stmt)
        job = result.scalar_one_or_none()
        if job is None:
            raise JobNotFoundError(f"Job {job_id} not found")
        return job

    async def list_jobs(
        self,
        *,
        organization_id: str | None = None,
        job_type: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[JobModel]:
        """List jobs with optional filtering.

        Args:
            organization_id: Filter by organization.
            job_type: Filter by job type.
            status: Filter by status.
            page: Page number (1-indexed).
            page_size: Results per page.

        Returns:
            List of matching JobModel instances.
        """
        stmt = select(JobModel).order_by(JobModel.created_at.desc())

        if organization_id is not None:
            stmt = stmt.where(JobModel.organization_id == organization_id)
        if job_type is not None:
            stmt = stmt.where(JobModel.job_type == job_type)
        if status is not None:
            stmt = stmt.where(JobModel.status == status)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_progress(
        self,
        job_id: str,
        *,
        progress: float,
        current_stage: str | None = None,
        status_message: str | None = None,
    ) -> None:
        """Update job progress (fire-and-forget safe).

        Args:
            job_id: Job ID.
            progress: Progress value between 0.0 and 1.0.
            current_stage: Current execution stage name.
            status_message: Human-readable status message.
        """
        values: dict[str, Any] = {"progress": min(max(progress, 0.0), 1.0)}
        if current_stage is not None:
            values["current_stage"] = current_stage
        if status_message is not None:
            values["status_message"] = status_message

        stmt = update(JobModel).where(JobModel.id == job_id).values(**values)
        await self._session.execute(stmt)
        await self._session.commit()

    async def mark_running(self, job_id: str) -> None:
        """Mark a job as running."""
        stmt = (
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(
                status="running",
                started_at=datetime.now(UTC),
                attempts=JobModel.attempts + 1,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def mark_completed(self, job_id: str, result: dict[str, Any] | None = None) -> None:
        """Mark a job as completed with optional result data."""
        stmt = (
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(
                status="completed",
                completed_at=datetime.now(UTC),
                progress=1.0,
                result=result,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
        logger.info("job_completed", job_id=job_id)

    async def mark_failed(self, job_id: str, error: str) -> None:
        """Mark a job as failed with error message."""
        stmt = (
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(
                status="failed",
                completed_at=datetime.now(UTC),
                error_message=error,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
        logger.error("job_failed", job_id=job_id, error=error)

    async def cancel_job(self, job_id: str) -> JobModel:
        """Cancel a job if it's not already in a terminal state.

        Raises:
            JobNotFoundError: If job does not exist.
            UNCASEError: If job is already in a terminal state.
        """
        job = await self.get_job(job_id)
        if job.is_terminal:
            raise UNCASEError(f"Cannot cancel job in '{job.status}' state")

        stmt = (
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(
                status="cancelled",
                completed_at=datetime.now(UTC),
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
        await self._session.refresh(job)

        logger.info("job_cancelled", job_id=job_id)
        return job
