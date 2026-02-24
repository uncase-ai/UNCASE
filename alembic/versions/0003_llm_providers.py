"""LLM provider configurations.

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-24
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0003"
down_revision: str = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_providers",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider_type", sa.String(50), nullable=False),
        sa.Column("api_base", sa.String(512), nullable=True),
        sa.Column("api_key_encrypted", sa.Text, nullable=True),
        sa.Column("default_model", sa.String(255), nullable=False),
        sa.Column("max_tokens", sa.Integer, nullable=False, server_default="4096"),
        sa.Column("temperature_default", sa.Float, nullable=False, server_default="0.7"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_llm_providers_org_active", "llm_providers", ["organization_id", "is_active"])
    op.create_index("ix_llm_providers_type", "llm_providers", ["provider_type"])


def downgrade() -> None:
    op.drop_index("ix_llm_providers_type", table_name="llm_providers")
    op.drop_index("ix_llm_providers_org_active", table_name="llm_providers")
    op.drop_table("llm_providers")
