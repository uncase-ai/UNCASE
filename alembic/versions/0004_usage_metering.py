"""Usage metering events.

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-25
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0004"
down_revision: str = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usage_events",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_usage_events_org_id", "usage_events", ["organization_id"])
    op.create_index("ix_usage_events_org_type", "usage_events", ["organization_id", "event_type"])
    op.create_index("ix_usage_events_created", "usage_events", ["created_at"])
    op.create_index("ix_usage_events_type_created", "usage_events", ["event_type", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_usage_events_type_created", table_name="usage_events")
    op.drop_index("ix_usage_events_created", table_name="usage_events")
    op.drop_index("ix_usage_events_org_type", table_name="usage_events")
    op.drop_index("ix_usage_events_org_id", table_name="usage_events")
    op.drop_table("usage_events")
