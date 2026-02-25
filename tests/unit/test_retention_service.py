"""Tests for the data retention service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from uncase.db.models.job import JobModel
from uncase.services.retention import DEFAULT_RETENTION, RetentionService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TestDefaultRetention:
    def test_audit_logs_default(self) -> None:
        assert DEFAULT_RETENTION["audit_logs"] == 365

    def test_completed_jobs_default(self) -> None:
        assert DEFAULT_RETENTION["completed_jobs"] == 90

    def test_failed_jobs_default(self) -> None:
        assert DEFAULT_RETENTION["failed_jobs"] == 30

    def test_cancelled_jobs_default(self) -> None:
        assert DEFAULT_RETENTION["cancelled_jobs"] == 7


class TestRetentionService:
    async def test_no_data_returns_zeros(self, async_session: AsyncSession) -> None:
        service = RetentionService(async_session)
        stats = await service.apply_policies()
        assert stats["total_deleted"] == 0

    async def test_deletes_old_completed_jobs(self, async_session: AsyncSession) -> None:
        old_date = datetime.now(UTC) - timedelta(days=100)
        job = JobModel(
            id="old-completed",
            job_type="test",
            status="completed",
            config={},
            progress=1.0,
            completed_at=old_date,
            attempts=1,
            max_attempts=3,
        )
        async_session.add(job)
        await async_session.commit()

        service = RetentionService(async_session)
        stats = await service.apply_policies()
        assert stats["completed_jobs_deleted"] == 1

    async def test_keeps_recent_completed_jobs(self, async_session: AsyncSession) -> None:
        recent_date = datetime.now(UTC) - timedelta(days=10)
        job = JobModel(
            id="recent-completed",
            job_type="test",
            status="completed",
            config={},
            progress=1.0,
            completed_at=recent_date,
            attempts=1,
            max_attempts=3,
        )
        async_session.add(job)
        await async_session.commit()

        service = RetentionService(async_session)
        stats = await service.apply_policies()
        assert stats["completed_jobs_deleted"] == 0

    async def test_deletes_old_failed_jobs(self, async_session: AsyncSession) -> None:
        old_date = datetime.now(UTC) - timedelta(days=40)
        job = JobModel(
            id="old-failed",
            job_type="test",
            status="failed",
            config={},
            progress=0.5,
            completed_at=old_date,
            error_message="Boom",
            attempts=1,
            max_attempts=3,
        )
        async_session.add(job)
        await async_session.commit()

        service = RetentionService(async_session)
        stats = await service.apply_policies()
        assert stats["failed_jobs_deleted"] == 1

    async def test_custom_retention_override(self, async_session: AsyncSession) -> None:
        old_date = datetime.now(UTC) - timedelta(days=5)
        job = JobModel(
            id="short-retention",
            job_type="test",
            status="completed",
            config={},
            progress=1.0,
            completed_at=old_date,
            attempts=1,
            max_attempts=3,
        )
        async_session.add(job)
        await async_session.commit()

        # Override to 3 days
        service = RetentionService(async_session, overrides={"completed_jobs": 3})
        stats = await service.apply_policies()
        assert stats["completed_jobs_deleted"] == 1

    async def test_get_retention_config(self, async_session: AsyncSession) -> None:
        service = RetentionService(async_session)
        config = await service.get_retention_config()
        assert "audit_logs" in config
        assert "completed_jobs" in config

    async def test_get_retention_config_with_overrides(self, async_session: AsyncSession) -> None:
        service = RetentionService(async_session, overrides={"audit_logs": 30})
        config = await service.get_retention_config()
        assert config["audit_logs"] == 30
