"""Blockchain audit trail — evaluation hashes, Merkle batches, and proofs.

Revision ID: 0014
Revises: 0013
Create Date: 2026-03-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: str = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- merkle_batches (must be created first, referenced by FKs) --
    op.create_table(
        "merkle_batches",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("batch_number", sa.Integer, unique=True, nullable=False),
        sa.Column("leaf_count", sa.Integer, nullable=False),
        sa.Column("tree_depth", sa.Integer, nullable=False),
        sa.Column("merkle_root", sa.String(64), nullable=False),
        sa.Column("tx_hash", sa.String(66), nullable=True),
        sa.Column("block_number", sa.Integer, nullable=True),
        sa.Column("chain_id", sa.Integer, nullable=True),
        sa.Column("contract_address", sa.String(42), nullable=True),
        sa.Column("anchored", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("anchor_error", sa.Text, nullable=True),
        sa.Column(
            "organization_id",
            sa.String(32),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_merkle_batches_batch_number", "merkle_batches", ["batch_number"])
    op.create_index("ix_merkle_batches_anchored", "merkle_batches", ["anchored"])

    # -- evaluation_hashes --
    op.create_table(
        "evaluation_hashes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "evaluation_report_id",
            sa.String(32),
            sa.ForeignKey("evaluation_reports.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("report_hash", sa.String(64), nullable=False),
        sa.Column("canonical_json", sa.Text, nullable=True),
        sa.Column(
            "batch_id",
            sa.String(32),
            sa.ForeignKey("merkle_batches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("leaf_index", sa.Integer, nullable=True),
    )
    op.create_index("ix_evaluation_hashes_report_hash", "evaluation_hashes", ["report_hash"])
    op.create_index("ix_evaluation_hashes_batch_id", "evaluation_hashes", ["batch_id"])
    op.create_index(
        "ix_eval_hash_unbatched",
        "evaluation_hashes",
        ["batch_id"],
        postgresql_where=sa.text("batch_id IS NULL"),
    )

    # -- merkle_proofs --
    op.create_table(
        "merkle_proofs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "evaluation_hash_id",
            sa.String(32),
            sa.ForeignKey("evaluation_hashes.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "batch_id",
            sa.String(32),
            sa.ForeignKey("merkle_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("siblings", sa.JSON, nullable=False),
        sa.Column("directions", sa.JSON, nullable=False),
        sa.Column("leaf_hash", sa.String(64), nullable=False),
        sa.Column("leaf_index", sa.Integer, nullable=False),
        sa.Column("merkle_root", sa.String(64), nullable=False),
    )
    op.create_index("ix_merkle_proofs_batch_id", "merkle_proofs", ["batch_id"])


def downgrade() -> None:
    op.drop_table("merkle_proofs")
    op.drop_table("evaluation_hashes")
    op.drop_table("merkle_batches")
