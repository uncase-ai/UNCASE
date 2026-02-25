"""Tests for the background job service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.exceptions import JobNotFoundError, UNCASEError
from uncase.services.jobs import JobService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TestJobServiceCreate:
    async def test_create_job(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(
            job_type="pipeline_run",
            config={"domain": "automotive.sales", "count": 10},
        )
        assert job.id is not None
        assert job.job_type == "pipeline_run"
        assert job.status == "pending"
        assert job.progress == 0.0
        assert job.config == {"domain": "automotive.sales", "count": 10}

    async def test_create_job_with_org(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(
            job_type="generation",
            config={},
            organization_id="org-123",
        )
        assert job.organization_id == "org-123"


class TestJobServiceGet:
    async def test_get_existing_job(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        created = await service.create_job(job_type="test", config={})
        found = await service.get_job(created.id)
        assert found.id == created.id

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        with pytest.raises(JobNotFoundError):
            await service.get_job("nonexistent-id")


class TestJobServiceList:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        jobs = await service.list_jobs()
        assert jobs == []

    async def test_list_all(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        await service.create_job(job_type="a", config={})
        await service.create_job(job_type="b", config={})
        jobs = await service.list_jobs()
        assert len(jobs) == 2

    async def test_list_filter_by_type(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        await service.create_job(job_type="pipeline_run", config={})
        await service.create_job(job_type="generation", config={})
        jobs = await service.list_jobs(job_type="pipeline_run")
        assert len(jobs) == 1
        assert jobs[0].job_type == "pipeline_run"

    async def test_list_filter_by_status(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        j1 = await service.create_job(job_type="a", config={})
        await service.create_job(job_type="b", config={})
        await service.mark_running(j1.id)
        jobs = await service.list_jobs(status="running")
        assert len(jobs) == 1

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        for i in range(5):
            await service.create_job(job_type="test", config={"i": i})
        page1 = await service.list_jobs(page=1, page_size=2)
        page2 = await service.list_jobs(page=2, page_size=2)
        assert len(page1) == 2
        assert len(page2) == 2


class TestJobServiceLifecycle:
    async def test_mark_running(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.mark_running(job.id)
        updated = await service.get_job(job.id)
        assert updated.status == "running"

    async def test_mark_completed(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.mark_running(job.id)
        await service.mark_completed(job.id, result={"output": "done"})
        updated = await service.get_job(job.id)
        assert updated.status == "completed"
        assert updated.progress == 1.0
        assert updated.result == {"output": "done"}

    async def test_mark_failed(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.mark_running(job.id)
        await service.mark_failed(job.id, "Something broke")
        updated = await service.get_job(job.id)
        assert updated.status == "failed"
        assert updated.error_message == "Something broke"

    async def test_update_progress(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.update_progress(job.id, progress=0.5, current_stage="generation", status_message="Halfway")
        updated = await service.get_job(job.id)
        assert updated.progress == 0.5
        assert updated.current_stage == "generation"
        assert updated.status_message == "Halfway"

    async def test_progress_clamped(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.update_progress(job.id, progress=1.5)
        updated = await service.get_job(job.id)
        assert updated.progress == 1.0

    async def test_progress_clamped_negative(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.update_progress(job.id, progress=-0.5)
        updated = await service.get_job(job.id)
        assert updated.progress == 0.0


class TestJobServiceCancel:
    async def test_cancel_pending(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        cancelled = await service.cancel_job(job.id)
        assert cancelled.status == "cancelled"

    async def test_cancel_running(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.mark_running(job.id)
        cancelled = await service.cancel_job(job.id)
        assert cancelled.status == "cancelled"

    async def test_cancel_completed_raises(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        job = await service.create_job(job_type="test", config={})
        await service.mark_completed(job.id)
        with pytest.raises(UNCASEError, match="Cannot cancel"):
            await service.cancel_job(job.id)

    async def test_cancel_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = JobService(async_session)
        with pytest.raises(JobNotFoundError):
            await service.cancel_job("no-such-id")
