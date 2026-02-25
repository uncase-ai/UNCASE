"""Data retention policy — automatic cleanup of expired data.

Configurable per-organization retention periods. Resources older than
the retention period are automatically purged via a scheduled task.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import structlog
from sqlalchemy import delete

from uncase.db.models.audit import AuditLogModel
from uncase.db.models.job import JobModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Default retention periods (days). Override per org in config.
DEFAULT_RETENTION = {
    "audit_logs": 365,  # 1 year
    "completed_jobs": 90,  # 3 months
    "failed_jobs": 30,  # 1 month
    "cancelled_jobs": 7,  # 1 week
}


class RetentionService:
    """Apply data retention policies by deleting expired records.

    Usage:
        service = RetentionService(session)
        stats = await service.apply_policies()
    """

    def __init__(
        self,
        session: AsyncSession,
        overrides: dict[str, int] | None = None,
    ) -> None:
        self._session = session
        self._retention = {**DEFAULT_RETENTION, **(overrides or {})}

    async def apply_policies(self) -> dict[str, Any]:
        """Apply all retention policies and return deletion statistics.

        Returns:
            Dict with keys for each policy and counts of deleted records.
        """
        stats: dict[str, Any] = {}
        now = datetime.now(UTC)

        # Audit logs
        audit_cutoff = now - timedelta(days=self._retention["audit_logs"])
        audit_deleted = await self._delete_audit_logs(audit_cutoff)
        stats["audit_logs_deleted"] = audit_deleted

        # Completed jobs
        completed_cutoff = now - timedelta(days=self._retention["completed_jobs"])
        completed_deleted = await self._delete_jobs("completed", completed_cutoff)
        stats["completed_jobs_deleted"] = completed_deleted

        # Failed jobs
        failed_cutoff = now - timedelta(days=self._retention["failed_jobs"])
        failed_deleted = await self._delete_jobs("failed", failed_cutoff)
        stats["failed_jobs_deleted"] = failed_deleted

        # Cancelled jobs
        cancelled_cutoff = now - timedelta(days=self._retention["cancelled_jobs"])
        cancelled_deleted = await self._delete_jobs("cancelled", cancelled_cutoff)
        stats["cancelled_jobs_deleted"] = cancelled_deleted

        total = sum(stats.values())
        stats["total_deleted"] = total

        if total > 0:
            logger.info("retention_applied", **stats)

        return stats

    async def _delete_audit_logs(self, cutoff: datetime) -> int:
        """Delete audit log records older than cutoff."""
        stmt = delete(AuditLogModel).where(AuditLogModel.created_at < cutoff)
        cursor = await self._session.execute(stmt)
        await self._session.commit()
        return int(cursor.rowcount)  # type: ignore[attr-defined]

    async def _delete_jobs(self, status: str, cutoff: datetime) -> int:
        """Delete jobs with given status older than cutoff."""
        stmt = delete(JobModel).where(
            JobModel.status == status,
            JobModel.completed_at < cutoff,
        )
        cursor = await self._session.execute(stmt)
        await self._session.commit()
        return int(cursor.rowcount)  # type: ignore[attr-defined]

    async def get_retention_config(self) -> dict[str, int]:
        """Return the current retention configuration."""
        return dict(self._retention)
