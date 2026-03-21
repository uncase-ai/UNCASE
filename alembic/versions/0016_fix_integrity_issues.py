"""Fix database integrity issues.

- audit_logs.updated_at: change from nullable to non-nullable with server_default
- jobs.organization_id: add ForeignKey constraint to organizations.id
- merkle_batches.organization_id: add index for query performance

Revision ID: a3f8e1c09b72
Revises: 0015
Create Date: 2026-03-20
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0016"
down_revision: str = "0015"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    # 1. Fix audit_logs.updated_at nullable mismatch
    # First backfill any NULL values with created_at
    op.execute("UPDATE audit_logs SET updated_at = created_at WHERE updated_at IS NULL")
    # Then alter to non-nullable with server_default
    op.alter_column(
        "audit_logs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # 2. Add ForeignKey on jobs.organization_id
    op.create_foreign_key(
        "fk_jobs_organization_id",
        "jobs",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 3. Add index on merkle_batches.organization_id
    op.create_index(
        "ix_merkle_batches_organization_id",
        "merkle_batches",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_merkle_batches_organization_id", table_name="merkle_batches")
    op.drop_constraint("fk_jobs_organization_id", "jobs", type_="foreignkey")
    op.alter_column(
        "audit_logs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None,
    )
