"""Pydantic v2 schemas for blockchain-anchored quality certification."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic needs this at runtime

from pydantic import BaseModel, Field


class EvaluationHashResponse(BaseModel):
    """Response for a single evaluation hash."""

    model_config = {"from_attributes": True}

    id: str
    evaluation_report_id: str
    report_hash: str = Field(..., description="SHA-256 hex digest (64 chars)")
    batch_id: str | None = None
    leaf_index: int | None = None
    created_at: datetime


class MerkleBatchResponse(BaseModel):
    """Response for a Merkle batch."""

    model_config = {"from_attributes": True}

    id: str
    batch_number: int
    leaf_count: int
    tree_depth: int
    merkle_root: str
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int | None = None
    contract_address: str | None = None
    anchored: bool
    anchor_error: str | None = None
    organization_id: str | None = None
    created_at: datetime


class MerkleProofResponse(BaseModel):
    """Merkle inclusion proof for verification."""

    siblings: list[str] = Field(..., description="Sibling hashes along the path to root")
    directions: list[str] = Field(..., description="Direction of each sibling (left/right)")
    leaf_hash: str
    leaf_index: int
    merkle_root: str


class VerificationResponse(BaseModel):
    """Full verification bundle for an evaluation report."""

    evaluation_report_id: str
    report_hash: str = Field(..., description="SHA-256 of the canonical QualityReport")
    hashed_at: datetime
    batch_id: str | None = Field(None, description="Merkle batch ID (null if not yet batched)")
    batch_number: int | None = None
    proof: MerkleProofResponse | None = Field(None, description="Merkle inclusion proof")
    tx_hash: str | None = Field(None, description="Polygon transaction hash")
    block_number: int | None = None
    chain_id: int | None = None
    anchored: bool = False
    explorer_url: str | None = Field(None, description="Polygonscan link to the anchoring tx")


class BatchBuildRequest(BaseModel):
    """Request to build a new Merkle batch."""

    organization_id: str | None = Field(None, description="Optional org scope")


class BatchBuildResponse(BaseModel):
    """Response after building a Merkle batch."""

    batch_id: str
    batch_number: int
    leaf_count: int
    tree_depth: int
    merkle_root: str
    anchored: bool
    tx_hash: str | None = None
    anchor_error: str | None = None


class RetryAnchorRequest(BaseModel):
    """Request to retry anchoring a failed batch."""

    batch_id: str


class BlockchainStatsResponse(BaseModel):
    """Aggregate statistics for blockchain certification."""

    total_hashed: int = Field(..., description="Total evaluation hashes stored")
    total_batched: int = Field(..., description="Hashes assigned to a batch")
    total_unbatched: int = Field(..., description="Hashes pending batch assignment")
    total_batches: int = Field(..., description="Total Merkle batches built")
    total_anchored: int = Field(..., description="Batches successfully anchored on-chain")
    total_pending_anchor: int = Field(..., description="Batches awaiting anchor")
    total_failed_anchor: int = Field(..., description="Batches with anchor errors")
