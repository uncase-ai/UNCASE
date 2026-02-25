"""Integration tests for the Jobs API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.db.models.job import JobModel

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture()
async def sample_job(async_session: AsyncSession) -> JobModel:
    """Create a sample job for tests."""
    job = JobModel(
        id="test-job-100",
        job_type="pipeline_run",
        status="pending",
        config={"domain": "automotive.sales", "count": 10},
        progress=0.0,
        attempts=0,
        max_attempts=3,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)
    return job


@pytest.fixture()
async def running_job(async_session: AsyncSession) -> JobModel:
    """Create a running job for cancel tests."""
    job = JobModel(
        id="test-job-200",
        job_type="generation",
        status="running",
        config={"model": "test"},
        progress=0.5,
        current_stage="generation",
        status_message="Generating...",
        attempts=1,
        max_attempts=3,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)
    return job


@pytest.fixture()
async def completed_job(async_session: AsyncSession) -> JobModel:
    """Create a completed job."""
    job = JobModel(
        id="test-job-300",
        job_type="evaluation",
        status="completed",
        config={},
        progress=1.0,
        result={"passed": 10, "failed": 2},
        attempts=1,
        max_attempts=3,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)
    return job


@pytest.mark.integration
class TestListJobs:
    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_with_job(self, client: AsyncClient, sample_job: JobModel) -> None:
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-job-100"
        assert data[0]["job_type"] == "pipeline_run"
        assert data[0]["status"] == "pending"

    async def test_filter_by_status(self, client: AsyncClient, sample_job: JobModel, running_job: JobModel) -> None:
        response = await client.get("/api/v1/jobs", params={"status": "running"})
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "running"

    async def test_filter_by_type(self, client: AsyncClient, sample_job: JobModel, completed_job: JobModel) -> None:
        response = await client.get("/api/v1/jobs", params={"job_type": "evaluation"})
        data = response.json()
        assert len(data) == 1
        assert data[0]["job_type"] == "evaluation"

    async def test_pagination(self, client: AsyncClient, sample_job: JobModel) -> None:
        response = await client.get("/api/v1/jobs", params={"page": 1, "page_size": 1})
        assert response.status_code == 200


@pytest.mark.integration
class TestGetJob:
    async def test_get_existing_job(self, client: AsyncClient, sample_job: JobModel) -> None:
        response = await client.get(f"/api/v1/jobs/{sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_job.id
        assert data["progress"] == 0.0

    async def test_get_nonexistent_job(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/jobs/nonexistent-id")
        assert response.status_code == 404

    async def test_get_completed_job_has_result(self, client: AsyncClient, completed_job: JobModel) -> None:
        response = await client.get(f"/api/v1/jobs/{completed_job.id}")
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"] is not None
        assert data["result"]["passed"] == 10


@pytest.mark.integration
class TestCancelJob:
    async def test_cancel_running_job(self, client: AsyncClient, running_job: JobModel) -> None:
        response = await client.post(f"/api/v1/jobs/{running_job.id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    async def test_cancel_pending_job(self, client: AsyncClient, sample_job: JobModel) -> None:
        response = await client.post(f"/api/v1/jobs/{sample_job.id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    async def test_cancel_completed_job_fails(self, client: AsyncClient, completed_job: JobModel) -> None:
        response = await client.post(f"/api/v1/jobs/{completed_job.id}/cancel")
        assert response.status_code == 500  # UNCASEError maps to 500

    async def test_cancel_nonexistent_job(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/jobs/no-such-job/cancel")
        assert response.status_code == 404
