"""Audit logs table for compliance trail.

Revision ID: 0008
Revises: 0007
Create Date: 2026-02-25
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str = "0007"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("actor_type", sa.String(20), nullable=False, server_default="user"),
        sa.Column("actor_id", sa.String(64), nullable=True),
        sa.Column("organization_id", sa.String(32), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("endpoint", sa.String(200), nullable=True),
        sa.Column("http_method", sa.String(10), nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("extra_data", sa.JSON, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_audit_action", "audit_logs", ["action"])
    op.create_index("ix_audit_resource", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_audit_actor", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_org", "audit_logs", ["organization_id"])
    op.create_index("ix_audit_created", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_created", table_name="audit_logs")
    op.drop_index("ix_audit_org", table_name="audit_logs")
    op.drop_index("ix_audit_actor", table_name="audit_logs")
    op.drop_index("ix_audit_resource", table_name="audit_logs")
    op.drop_index("ix_audit_action", table_name="audit_logs")
    op.drop_table("audit_logs")
