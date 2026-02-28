"""Add rating, rating_count, run_count, avg_quality_score to seeds.

Revision ID: 0012
Revises: 0011
Create Date: 2026-02-27
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0012"
down_revision: str = "0011"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column("seeds", sa.Column("rating", sa.Float, nullable=True))
    op.add_column("seeds", sa.Column("rating_count", sa.Integer, nullable=False, server_default="0"))
    op.add_column("seeds", sa.Column("run_count", sa.Integer, nullable=False, server_default="0"))
    op.add_column("seeds", sa.Column("avg_quality_score", sa.Float, nullable=True))


def downgrade() -> None:
    op.drop_column("seeds", "avg_quality_score")
    op.drop_column("seeds", "run_count")
    op.drop_column("seeds", "rating_count")
    op.drop_column("seeds", "rating")
