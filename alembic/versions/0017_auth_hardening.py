"""Auth hardening — lockout fields, role constraint, missing FKs.

Revision ID: 0017
Revises: 0016
Create Date: 2026-03-20
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0017"
down_revision: str = "0016"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    # 1. User account lockout fields
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    # 2. Role validation constraint on org_memberships
    op.create_check_constraint(
        "ck_org_memberships_role",
        "org_memberships",
        "role IN ('owner', 'admin', 'member', 'viewer')",
    )

    # 3. Missing FK: audit_logs.organization_id → organizations.id
    op.create_foreign_key(
        "fk_audit_logs_organization_id",
        "audit_logs",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_audit_logs_organization_id", "audit_logs", type_="foreignkey")
    op.drop_constraint("ck_org_memberships_role", "org_memberships", type_="check")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
