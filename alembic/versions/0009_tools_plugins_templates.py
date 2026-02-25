"""Custom tools, installed plugins, and template configs.

Revision ID: 0009
Revises: 0008
Create Date: 2026-02-25
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0009"
down_revision: str = "0008"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    # -- custom_tools --
    op.create_table(
        "custom_tools",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("input_schema", sa.JSON, nullable=False),
        sa.Column("output_schema", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("domains", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("category", sa.String(100), nullable=False, server_default=""),
        sa.Column("requires_auth", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("execution_mode", sa.String(20), nullable=False, server_default="simulated"),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_custom_tools_org", "custom_tools", ["organization_id"])
    op.create_index("ix_custom_tools_name_org", "custom_tools", ["name", "organization_id"], unique=True)
    op.create_index("ix_custom_tools_org_active", "custom_tools", ["organization_id", "is_active"])

    # -- installed_plugins --
    op.create_table(
        "installed_plugins",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("plugin_id", sa.String(255), nullable=False),
        sa.Column("plugin_name", sa.String(255), nullable=False),
        sa.Column("plugin_version", sa.String(50), nullable=False),
        sa.Column("plugin_source", sa.String(20), nullable=False, server_default="official"),
        sa.Column("tools_registered", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("domains", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_installed_plugins_org", "installed_plugins", ["organization_id"])
    op.create_index(
        "ix_installed_plugins_plugin_org", "installed_plugins", ["plugin_id", "organization_id"], unique=True
    )
    op.create_index("ix_installed_plugins_org_active", "installed_plugins", ["organization_id", "is_active"])

    # -- template_configs --
    op.create_table(
        "template_configs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("default_template", sa.String(100), nullable=False, server_default="chatml"),
        sa.Column("default_tool_call_mode", sa.String(20), nullable=False, server_default="none"),
        sa.Column("default_system_prompt", sa.Text, nullable=True),
        sa.Column("preferred_templates", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("export_format", sa.String(50), nullable=False, server_default="txt"),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_template_configs_org", "template_configs", ["organization_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_template_configs_org", table_name="template_configs")
    op.drop_table("template_configs")

    op.drop_index("ix_installed_plugins_org_active", table_name="installed_plugins")
    op.drop_index("ix_installed_plugins_plugin_org", table_name="installed_plugins")
    op.drop_index("ix_installed_plugins_org", table_name="installed_plugins")
    op.drop_table("installed_plugins")

    op.drop_index("ix_custom_tools_org_active", table_name="custom_tools")
    op.drop_index("ix_custom_tools_name_org", table_name="custom_tools")
    op.drop_index("ix_custom_tools_org", table_name="custom_tools")
    op.drop_table("custom_tools")
