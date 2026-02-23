"""Initial schema: organizations, api_keys, seeds.

Revision ID: 0001
Revises: None
Create Date: 2026-02-23
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # API Keys
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("key_id", sa.String(16), nullable=False, unique=True),
        sa.Column("key_hash", sa.String(512), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("scopes", sa.String(255), nullable=False, server_default="read"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_api_keys_key_id", "api_keys", ["key_id"])
    op.create_index("ix_api_keys_organization_id", "api_keys", ["organization_id"])
    op.create_index("ix_api_keys_org_active", "api_keys", ["organization_id", "is_active"])

    # API Key Audit Logs
    op.create_table(
        "api_key_audit_logs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "api_key_id",
            sa.String(32),
            sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_api_key_audit_logs_api_key_id", "api_key_audit_logs", ["api_key_id"])

    # Seeds
    op.create_table(
        "seeds",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("dominio", sa.String(100), nullable=False),
        sa.Column("idioma", sa.String(10), nullable=False, server_default="es"),
        sa.Column("version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("etiquetas", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("objetivo", sa.Text, nullable=False),
        sa.Column("tono", sa.String(50), nullable=False, server_default="profesional"),
        sa.Column("roles", sa.JSON, nullable=False),
        sa.Column("descripcion_roles", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("pasos_turnos", sa.JSON, nullable=False),
        sa.Column("parametros_factuales", sa.JSON, nullable=False),
        sa.Column("privacidad", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("metricas_calidad", sa.JSON, nullable=False, server_default="{}"),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_seeds_dominio", "seeds", ["dominio"])
    op.create_index("ix_seeds_organization_id", "seeds", ["organization_id"])
    op.create_index("ix_seeds_dominio_org", "seeds", ["dominio", "organization_id"])


def downgrade() -> None:
    op.drop_table("seeds")
    op.drop_table("api_key_audit_logs")
    op.drop_table("api_keys")
    op.drop_table("organizations")
