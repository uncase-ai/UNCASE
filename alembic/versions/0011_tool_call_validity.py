"""Add tool_call_validity column to evaluation_reports.

Revision ID: 0011
Revises: 0010
Create Date: 2026-02-27
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0011"
down_revision: str = "0010"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column(
        "evaluation_reports",
        sa.Column("tool_call_validity", sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("evaluation_reports", "tool_call_validity")
