"""Webhook subscriptions and deliveries.

Revision ID: 0006
Revises: 0005
Create Date: 2026-02-25
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0006"
down_revision: str = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create webhook tables."""
    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("events", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("secret", sa.String(64), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_webhooks_org", "webhook_subscriptions", ["organization_id"])
    op.create_index(
        "ix_webhooks_org_active",
        "webhook_subscriptions",
        ["organization_id", "is_active"],
    )

    op.create_table(
        "webhook_deliveries",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "subscription_id",
            sa.String(32),
            sa.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("http_status_code", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_deliveries_subscription", "webhook_deliveries", ["subscription_id"])
    op.create_index("ix_deliveries_status", "webhook_deliveries", ["status"])
    op.create_index("ix_deliveries_event_type", "webhook_deliveries", ["event_type"])
    op.create_index(
        "ix_deliveries_status_retry",
        "webhook_deliveries",
        ["status", "next_retry_at"],
    )


def downgrade() -> None:
    """Drop webhook tables."""
    op.drop_index("ix_deliveries_status_retry", table_name="webhook_deliveries")
    op.drop_index("ix_deliveries_event_type", table_name="webhook_deliveries")
    op.drop_index("ix_deliveries_status", table_name="webhook_deliveries")
    op.drop_index("ix_deliveries_subscription", table_name="webhook_deliveries")
    op.drop_table("webhook_deliveries")
    op.drop_index("ix_webhooks_org_active", table_name="webhook_subscriptions")
    op.drop_index("ix_webhooks_org", table_name="webhook_subscriptions")
    op.drop_table("webhook_subscriptions")
