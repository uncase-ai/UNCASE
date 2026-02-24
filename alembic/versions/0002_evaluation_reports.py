"""Add evaluation_reports table for Layer 2 quality persistence.

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-24
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0002"
down_revision: str = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluation_reports",
        sa.Column("id", sa.String(32), primary_key=True),
        # References
        sa.Column("conversation_id", sa.String(64), nullable=False),
        sa.Column(
            "seed_id",
            sa.String(32),
            sa.ForeignKey("seeds.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Individual metrics
        sa.Column("rouge_l", sa.Float, nullable=False),
        sa.Column("fidelidad_factual", sa.Float, nullable=False),
        sa.Column("diversidad_lexica", sa.Float, nullable=False),
        sa.Column("coherencia_dialogica", sa.Float, nullable=False),
        sa.Column("privacy_score", sa.Float, nullable=False),
        sa.Column("memorizacion", sa.Float, nullable=False),
        # Composite result
        sa.Column("composite_score", sa.Float, nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False),
        sa.Column("failures", sa.JSON, nullable=False, server_default="[]"),
        # Context
        sa.Column("dominio", sa.String(100), nullable=True),
        sa.Column("evaluation_context", sa.Text, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_eval_conversation_id", "evaluation_reports", ["conversation_id"])
    op.create_index("ix_eval_seed_id", "evaluation_reports", ["seed_id"])
    op.create_index("ix_eval_organization_id", "evaluation_reports", ["organization_id"])
    op.create_index("ix_eval_seed_org", "evaluation_reports", ["seed_id", "organization_id"])
    op.create_index("ix_eval_passed", "evaluation_reports", ["passed"])


def downgrade() -> None:
    op.drop_table("evaluation_reports")
