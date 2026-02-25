"""Seed CRUD API endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.seed_api import SeedCreateRequest, SeedListResponse, SeedResponse, SeedUpdateRequest
from uncase.services.seed import SeedService

# NOTE: Phase 0→1 — Uses optional auth via get_optional_org. If an API key
# is provided, the org is derived from it. Otherwise, endpoints work
# unauthenticated (query params / no org filtering).
router = APIRouter(prefix="/api/v1/seeds", tags=["seeds"])

logger = structlog.get_logger(__name__)


def _get_service(session: AsyncSession) -> SeedService:
    return SeedService(session)


@router.post("", response_model=SeedResponse, status_code=status.HTTP_201_CREATED)
async def create_seed(
    data: SeedCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> SeedResponse:
    """Create a new seed."""
    service = _get_service(session)
    org_id = org.id if org else None
    result = await service.create_seed(data, organization_id=org_id)
    logger.info("seed_created", seed_id=result.id, dominio=result.dominio, org_id=org_id)
    await meter(
        session, "seed_created", organization_id=org_id, resource_id=result.id, metadata={"dominio": result.dominio}
    )
    return result


@router.get("", response_model=SeedListResponse)
async def list_seeds(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: Annotated[str | None, Query(description="Filter by domain namespace")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> SeedListResponse:
    """List seeds with optional domain filter and pagination."""
    service = _get_service(session)
    org_id = org.id if org else None
    return await service.list_seeds(domain=domain, organization_id=org_id, page=page, page_size=page_size)


@router.get("/{seed_id}", response_model=SeedResponse)
async def get_seed(
    seed_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SeedResponse:
    """Get a single seed by ID."""
    service = _get_service(session)
    return await service.get_seed(seed_id)


@router.put("/{seed_id}", response_model=SeedResponse)
async def update_seed(
    seed_id: str,
    data: SeedUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SeedResponse:
    """Update a seed (partial update — only provided fields are changed)."""
    service = _get_service(session)
    result = await service.update_seed(seed_id, data)
    logger.info("seed_updated", seed_id=seed_id)
    return result


@router.delete("/{seed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seed(
    seed_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a seed."""
    service = _get_service(session)
    await service.delete_seed(seed_id)
    logger.info("seed_deleted", seed_id=seed_id)
