"""Add scenarios JSON column to seeds table.

Revision ID: 0013
Revises: 0012
Create Date: 2026-02-28
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0013"
down_revision: str = "0012"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column("seeds", sa.Column("scenarios", sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_column("seeds", "scenarios")
