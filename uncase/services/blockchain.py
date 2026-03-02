"""Blockchain certification service — hash, batch, anchor, and verify."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from sqlalchemy import func, select

from uncase.core.blockchain.anchor import get_explorer_url
from uncase.core.blockchain.hasher import canonicalize_report, hash_report
from uncase.core.blockchain.merkle import MerkleTree
from uncase.db.models.blockchain import (
    EvaluationHashModel,
    MerkleBatchModel,
    MerkleProofModel,
)
from uncase.schemas.blockchain import (
    BatchBuildResponse,
    BlockchainStatsResponse,
    MerkleProofResponse,
    VerificationResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from uncase.config import UNCASESettings
    from uncase.core.blockchain.anchor import AnchorClient
    from uncase.schemas.quality import QualityReport

logger = structlog.get_logger(__name__)


class BlockchainService:
    """Orchestrates hashing, Merkle batching, on-chain anchoring, and verification."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: UNCASESettings | None = None,
        anchor_client: AnchorClient | None = None,
    ) -> None:
        self._session = session
        self._settings = settings
        self._anchor_client = anchor_client

    # ------------------------------------------------------------------
    # Hash & store
    # ------------------------------------------------------------------

    async def hash_and_store(
        self,
        report: QualityReport,
        evaluation_report_id: str,
    ) -> EvaluationHashModel:
        """Compute SHA-256 of the canonical report and persist it.

        This is a pure-Python operation with zero external dependencies.
        Called automatically after each evaluation persist.
        """
        canonical = canonicalize_report(report)
        digest = hash_report(report)

        model = EvaluationHashModel(
            evaluation_report_id=evaluation_report_id,
            report_hash=digest,
            canonical_json=canonical,
        )
        self._session.add(model)
        await self._session.flush()

        logger.info(
            "evaluation_hashed",
            evaluation_report_id=evaluation_report_id,
            report_hash=digest[:16] + "...",
        )
        return model

    # ------------------------------------------------------------------
    # Batch build
    # ------------------------------------------------------------------

    async def build_batch(self, organization_id: str | None = None) -> BatchBuildResponse:
        """Collect unbatched hashes, build a Merkle tree, and optionally anchor on-chain."""
        # Fetch unbatched hashes
        stmt = (
            select(EvaluationHashModel)
            .where(EvaluationHashModel.batch_id.is_(None))
            .order_by(EvaluationHashModel.created_at)
        )
        result = await self._session.execute(stmt)
        hashes = list(result.scalars().all())

        if not hashes:
            msg = "No unbatched evaluation hashes available"
            raise ValueError(msg)

        # Determine next batch number
        max_stmt = select(func.coalesce(func.max(MerkleBatchModel.batch_number), 0))
        max_result = await self._session.execute(max_stmt)
        next_batch_number = (max_result.scalar() or 0) + 1

        # Build Merkle tree
        leaves = [h.report_hash for h in hashes]
        tree = MerkleTree(leaves)

        # Create batch record
        batch = MerkleBatchModel(
            batch_number=next_batch_number,
            leaf_count=tree.leaf_count,
            tree_depth=tree.depth,
            merkle_root=tree.root,
            organization_id=organization_id,
        )

        if self._settings:
            batch.chain_id = self._settings.polygon_chain_id
            batch.contract_address = self._settings.polygon_contract_address or None

        self._session.add(batch)
        await self._session.flush()

        # Assign batch_id and leaf_index to each hash, and create proofs
        proofs = tree.get_all_proofs()
        for i, (eval_hash, proof) in enumerate(zip(hashes, proofs, strict=True)):
            eval_hash.batch_id = batch.id
            eval_hash.leaf_index = i

            proof_model = MerkleProofModel(
                evaluation_hash_id=eval_hash.id,
                batch_id=batch.id,
                siblings=proof.siblings,
                directions=proof.directions,
                leaf_hash=proof.leaf_hash,
                leaf_index=proof.leaf_index,
                merkle_root=proof.root,
            )
            self._session.add(proof_model)

        # Attempt on-chain anchoring
        if self._anchor_client:
            try:
                tx_hash = await self._anchor_client.anchor_root(next_batch_number, tree.root)
                batch.tx_hash = tx_hash
                batch.anchored = True
            except Exception as exc:
                batch.anchor_error = str(exc)
                logger.error(
                    "batch_anchor_failed",
                    batch_number=next_batch_number,
                    error=str(exc),
                )

        await self._session.commit()

        logger.info(
            "batch_built",
            batch_number=next_batch_number,
            leaf_count=tree.leaf_count,
            merkle_root=tree.root[:16] + "...",
            anchored=batch.anchored,
        )

        return BatchBuildResponse(
            batch_id=batch.id,
            batch_number=batch.batch_number,
            leaf_count=batch.leaf_count,
            tree_depth=batch.tree_depth,
            merkle_root=batch.merkle_root,
            anchored=batch.anchored,
            tx_hash=batch.tx_hash,
            anchor_error=batch.anchor_error,
        )

    # ------------------------------------------------------------------
    # Retry anchor
    # ------------------------------------------------------------------

    async def retry_anchor(self, batch_id: str) -> BatchBuildResponse:
        """Retry on-chain anchoring for a previously failed batch."""
        stmt = select(MerkleBatchModel).where(MerkleBatchModel.id == batch_id)
        result = await self._session.execute(stmt)
        batch = result.scalar_one_or_none()

        if batch is None:
            msg = f"Batch {batch_id} not found"
            raise ValueError(msg)

        if batch.anchored:
            msg = f"Batch {batch_id} is already anchored (tx={batch.tx_hash})"
            raise ValueError(msg)

        if not self._anchor_client:
            msg = "Anchor client not configured"
            raise ValueError(msg)

        try:
            tx_hash = await self._anchor_client.anchor_root(batch.batch_number, batch.merkle_root)
            batch.tx_hash = tx_hash
            batch.anchored = True
            batch.anchor_error = None
        except Exception as exc:
            batch.anchor_error = str(exc)
            logger.error("retry_anchor_failed", batch_id=batch_id, error=str(exc))

        await self._session.commit()

        return BatchBuildResponse(
            batch_id=batch.id,
            batch_number=batch.batch_number,
            leaf_count=batch.leaf_count,
            tree_depth=batch.tree_depth,
            merkle_root=batch.merkle_root,
            anchored=batch.anchored,
            tx_hash=batch.tx_hash,
            anchor_error=batch.anchor_error,
        )

    # ------------------------------------------------------------------
    # Verify
    # ------------------------------------------------------------------

    async def verify(self, evaluation_report_id: str) -> VerificationResponse:
        """Return the full verification bundle for an evaluation report."""
        stmt = select(EvaluationHashModel).where(
            EvaluationHashModel.evaluation_report_id == evaluation_report_id
        )
        result = await self._session.execute(stmt)
        eval_hash = result.scalar_one_or_none()

        if eval_hash is None:
            msg = f"No hash found for evaluation report {evaluation_report_id}"
            raise ValueError(msg)

        response = VerificationResponse(  # type: ignore[call-arg]
            evaluation_report_id=evaluation_report_id,
            report_hash=eval_hash.report_hash,
            hashed_at=eval_hash.created_at,
        )

        # If batched, include proof and batch info
        if eval_hash.batch_id:
            batch_stmt = select(MerkleBatchModel).where(MerkleBatchModel.id == eval_hash.batch_id)
            batch_result = await self._session.execute(batch_stmt)
            batch = batch_result.scalar_one_or_none()

            proof_stmt = select(MerkleProofModel).where(
                MerkleProofModel.evaluation_hash_id == eval_hash.id
            )
            proof_result = await self._session.execute(proof_stmt)
            proof = proof_result.scalar_one_or_none()

            if batch:
                response.batch_id = batch.id
                response.batch_number = batch.batch_number
                response.tx_hash = batch.tx_hash
                response.block_number = batch.block_number
                response.chain_id = batch.chain_id
                response.anchored = batch.anchored

                if batch.tx_hash and batch.chain_id:
                    response.explorer_url = get_explorer_url(batch.chain_id, batch.tx_hash)

            if proof:
                response.proof = MerkleProofResponse(
                    siblings=proof.siblings,
                    directions=proof.directions,
                    leaf_hash=proof.leaf_hash,
                    leaf_index=proof.leaf_index,
                    merkle_root=proof.merkle_root,
                )

        return response

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    async def get_stats(self) -> BlockchainStatsResponse:
        """Return aggregate statistics for blockchain certification."""
        total_hashed = (await self._session.execute(select(func.count(EvaluationHashModel.id)))).scalar() or 0
        total_batched = (
            await self._session.execute(
                select(func.count(EvaluationHashModel.id)).where(EvaluationHashModel.batch_id.is_not(None))
            )
        ).scalar() or 0
        total_batches = (await self._session.execute(select(func.count(MerkleBatchModel.id)))).scalar() or 0
        total_anchored = (
            await self._session.execute(
                select(func.count(MerkleBatchModel.id)).where(MerkleBatchModel.anchored.is_(True))
            )
        ).scalar() or 0
        total_failed = (
            await self._session.execute(
                select(func.count(MerkleBatchModel.id)).where(
                    MerkleBatchModel.anchored.is_(False),
                    MerkleBatchModel.anchor_error.is_not(None),
                )
            )
        ).scalar() or 0

        return BlockchainStatsResponse(
            total_hashed=total_hashed,
            total_batched=total_batched,
            total_unbatched=total_hashed - total_batched,
            total_batches=total_batches,
            total_anchored=total_anchored,
            total_pending_anchor=total_batches - total_anchored - total_failed,
            total_failed_anchor=total_failed,
        )
