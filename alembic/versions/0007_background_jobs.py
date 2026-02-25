"""Background jobs table.

Revision ID: 0007
Revises: 0006
Create Date: 2026-02-25
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0007"
down_revision: str = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create jobs table."""
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("organization_id", sa.String(32), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("current_stage", sa.String(100), nullable=True),
        sa.Column("status_message", sa.String(500), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_org_status", "jobs", ["organization_id", "status"])
    op.create_index("ix_jobs_type_status", "jobs", ["job_type", "status"])
    op.create_index("ix_jobs_created", "jobs", ["created_at"])


def downgrade() -> None:
    """Drop jobs table."""
    op.drop_index("ix_jobs_created", table_name="jobs")
    op.drop_index("ix_jobs_type_status", table_name="jobs")
    op.drop_index("ix_jobs_org_status", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_table("jobs")
