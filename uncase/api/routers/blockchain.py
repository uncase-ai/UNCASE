"""Blockchain certification API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.config import UNCASESettings
from uncase.db.models.blockchain import MerkleBatchModel
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.blockchain import (
    BatchBuildRequest,
    BatchBuildResponse,
    BlockchainStatsResponse,
    MerkleBatchResponse,
    RetryAnchorRequest,
    VerificationResponse,
)
from uncase.services.blockchain import BlockchainService

if TYPE_CHECKING:
    from uncase.core.blockchain.anchor import AnchorClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/blockchain", tags=["blockchain"])


def _get_anchor_client(settings: UNCASESettings) -> AnchorClient | None:
    """Lazily create an AnchorClient if blockchain is enabled and configured."""
    if not settings.blockchain_enabled:
        return None
    if not settings.polygon_rpc_url or not settings.polygon_private_key or not settings.polygon_contract_address:
        return None
    try:
        from uncase.core.blockchain.anchor import AnchorClient

        return AnchorClient(
            rpc_url=settings.polygon_rpc_url,
            private_key=settings.polygon_private_key,
            contract_address=settings.polygon_contract_address,
            chain_id=settings.polygon_chain_id,
        )
    except Exception:
        logger.warning("anchor_client_init_failed")
        return None


@router.get("/verify/{evaluation_report_id}", response_model=VerificationResponse)
async def verify_evaluation(
    evaluation_report_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> VerificationResponse:
    """Return the full verification bundle for an evaluation report.

    Includes the SHA-256 hash, Merkle proof (if batched), transaction hash,
    and Polygonscan explorer URL (if anchored on-chain).
    """
    service = BlockchainService(session)
    try:
        return await service.verify(evaluation_report_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/batch", response_model=BatchBuildResponse)
async def build_batch(
    request: BatchBuildRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> BatchBuildResponse:
    """Build a Merkle tree from unbatched evaluation hashes and anchor on-chain."""
    settings = UNCASESettings()
    anchor_client = _get_anchor_client(settings)

    org_id = request.organization_id or (org.id if org else None)

    service = BlockchainService(session, settings=settings, anchor_client=anchor_client)
    try:
        return await service.build_batch(organization_id=org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/retry-anchor", response_model=BatchBuildResponse)
async def retry_anchor(
    request: RetryAnchorRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BatchBuildResponse:
    """Retry on-chain anchoring for a failed batch."""
    settings = UNCASESettings()
    anchor_client = _get_anchor_client(settings)
    service = BlockchainService(session, settings=settings, anchor_client=anchor_client)
    try:
        return await service.retry_anchor(request.batch_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/batches", response_model=list[MerkleBatchResponse])
async def list_batches(
    session: Annotated[AsyncSession, Depends(get_db)],
    anchored: bool | None = Query(None, description="Filter by anchored status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[MerkleBatchResponse]:
    """List Merkle batches with optional filtering."""
    stmt = select(MerkleBatchModel).order_by(MerkleBatchModel.batch_number.desc())

    if anchored is not None:
        stmt = stmt.where(MerkleBatchModel.anchored == anchored)

    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    batches = result.scalars().all()
    return [MerkleBatchResponse.model_validate(b) for b in batches]


@router.get("/stats", response_model=BlockchainStatsResponse)
async def get_stats(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BlockchainStatsResponse:
    """Return aggregate statistics for blockchain certification."""
    service = BlockchainService(session)
    return await service.get_stats()
