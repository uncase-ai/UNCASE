"""Background job persistence model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class JobModel(Base, TimestampMixin):
    """Background job record for long-running pipeline operations.

    Jobs are created when users submit pipeline runs, batch generation,
    batch evaluation, or training tasks. The job record tracks progress,
    status, and results.
    """

    __tablename__ = "jobs"

    # Job identity
    job_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Job type: pipeline_run, generation, evaluation, training, import"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="Job status: pending, running, completed, failed, cancelled",
    )

    # Ownership
    organization_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, index=True, comment="Owning organization"
    )

    # Configuration
    config: Mapped[dict[str, object]] = mapped_column(
        JSON, nullable=False, default=dict, comment="Job configuration parameters"
    )

    # Progress tracking
    progress: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default="0.0", comment="Progress 0.0 to 1.0"
    )
    current_stage: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Current execution stage")
    status_message: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Human-readable status message"
    )

    # Results
    result: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True, comment="Job result data (on completion)"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Error message (on failure)")

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When the job started executing"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When the job finished (success or failure)"
    )

    # Retry
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0", comment="Number of execution attempts"
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default="3", comment="Maximum retry attempts"
    )

    __table_args__ = (
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_org_status", "organization_id", "status"),
        Index("ix_jobs_type_status", "job_type", "status"),
        Index("ix_jobs_created", "created_at"),
    )

    def mark_running(self) -> None:
        """Mark the job as running."""
        self.status = "running"
        self.started_at = datetime.now(UTC)
        self.attempts += 1

    def mark_completed(self, result: dict[str, object] | None = None) -> None:
        """Mark the job as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(UTC)
        self.progress = 1.0
        self.result = result

    def mark_failed(self, error: str) -> None:
        """Mark the job as failed."""
        self.status = "failed"
        self.completed_at = datetime.now(UTC)
        self.error_message = error

    def mark_cancelled(self) -> None:
        """Mark the job as cancelled."""
        self.status = "cancelled"
        self.completed_at = datetime.now(UTC)

    @property
    def is_terminal(self) -> bool:
        """Whether the job is in a terminal state."""
        return self.status in ("completed", "failed", "cancelled")

    @property
    def can_retry(self) -> bool:
        """Whether the job can be retried."""
        return self.status == "failed" and self.attempts < self.max_attempts
