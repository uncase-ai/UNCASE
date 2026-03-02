"""Database models for blockchain-anchored quality certification."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class EvaluationHashModel(TimestampMixin, Base):
    """SHA-256 hash of a canonicalized QualityReport."""

    __tablename__ = "evaluation_hashes"

    evaluation_report_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("evaluation_reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    report_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    canonical_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("merkle_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    leaf_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_eval_hash_unbatched", "batch_id", postgresql_where=batch_id.is_(None)),
    )


class MerkleBatchModel(TimestampMixin, Base):
    """A batch of evaluation hashes grouped into a Merkle tree."""

    __tablename__ = "merkle_batches"

    batch_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    leaf_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tree_depth: Mapped[int] = mapped_column(Integer, nullable=False)
    merkle_root: Mapped[str] = mapped_column(String(64), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(66), nullable=True)
    block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chain_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contract_address: Mapped[str | None] = mapped_column(String(42), nullable=True)
    anchored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    anchor_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )


class MerkleProofModel(TimestampMixin, Base):
    """Pre-computed Merkle inclusion proof for a single evaluation hash."""

    __tablename__ = "merkle_proofs"

    evaluation_hash_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("evaluation_hashes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    batch_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("merkle_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    siblings: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    directions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    leaf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    leaf_index: Mapped[int] = mapped_column(Integer, nullable=False)
    merkle_root: Mapped[str] = mapped_column(String(64), nullable=False)
