"""Conversations table.

Revision ID: 0010
Revises: 0009
Create Date: 2026-02-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0010"
down_revision: str = "0009"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("conversation_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column(
            "seed_id",
            sa.String(32),
            sa.ForeignKey("seeds.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("dominio", sa.String(100), nullable=False, index=True),
        sa.Column("idioma", sa.String(10), nullable=False, server_default="es"),
        sa.Column("es_sintetica", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("turnos", sa.JSON, nullable=False),
        sa.Column("num_turnos", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("metadata_json", sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("rating", sa.Float, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
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
    op.create_index("ix_conv_dominio_org", "conversations", ["dominio", "organization_id"])
    op.create_index("ix_conv_status", "conversations", ["status"])


def downgrade() -> None:
    op.drop_index("ix_conv_status", table_name="conversations")
    op.drop_index("ix_conv_dominio_org", table_name="conversations")
    op.drop_table("conversations")
