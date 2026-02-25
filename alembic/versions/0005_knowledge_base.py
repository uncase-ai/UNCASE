"""Knowledge base documents and chunks.

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-25
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0005"
down_revision: str = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("domain", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("chunk_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("size_bytes", sa.Integer, nullable=True),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_docs_domain", "knowledge_documents", ["domain"])
    op.create_index("ix_knowledge_docs_org_domain", "knowledge_documents", ["organization_id", "domain"])

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(32),
            sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("domain", sa.String(100), nullable=False),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("source", sa.String(512), nullable=False),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_chunks_doc", "knowledge_chunks", ["document_id"])
    op.create_index("ix_knowledge_chunks_domain_type", "knowledge_chunks", ["domain", "type"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_domain_type", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_doc", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")

    op.drop_index("ix_knowledge_docs_org_domain", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_docs_domain", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
