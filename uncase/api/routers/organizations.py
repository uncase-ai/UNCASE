"""Organization management API endpoints."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db
from uncase.schemas.organization import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from uncase.services.organization import OrganizationService

# NOTE: Phase 0 — Organization endpoints are intentionally unauthenticated
# to allow bootstrapping the first organization and API key. Authentication
# guards (require_scopes("admin")) will be added in Phase 1.
router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])

logger = structlog.get_logger(__name__)


def _get_service(session: AsyncSession) -> OrganizationService:
    return OrganizationService(session)


# -- Organization CRUD --


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """Create a new organization."""
    service = _get_service(session)
    result = await service.create_organization(data)
    logger.info("organization_created", org_id=result.id, name=result.name)
    return result


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """Get an organization by ID."""
    service = _get_service(session)
    return await service.get_organization(org_id)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """Update an organization."""
    service = _get_service(session)
    result = await service.update_organization(org_id, data)
    logger.info("organization_updated", org_id=org_id)
    return result


# -- API Key Management --


@router.post(
    "/{org_id}/api-keys",
    response_model=APIKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    org_id: str,
    data: APIKeyCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> APIKeyCreatedResponse:
    """Issue a new API key for an organization.

    The full key is returned exactly once in the response.
    """
    service = _get_service(session)
    result = await service.create_api_key(org_id, data)
    logger.info("api_key_created", org_id=org_id, key_name=data.name)
    return result


@router.get("/{org_id}/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    org_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[APIKeyResponse]:
    """List all API keys for an organization."""
    service = _get_service(session)
    return await service.list_api_keys(org_id)


@router.delete("/{org_id}/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    org_id: str,
    key_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Revoke an API key."""
    service = _get_service(session)
    await service.revoke_api_key(org_id, key_id)
    logger.info("api_key_revoked", org_id=org_id, key_id=key_id)


@router.post("/{org_id}/api-keys/{key_id}/rotate", response_model=APIKeyCreatedResponse)
async def rotate_api_key(
    org_id: str,
    key_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> APIKeyCreatedResponse:
    """Rotate an API key: revoke old and issue new with same name/scopes."""
    service = _get_service(session)
    result = await service.rotate_api_key(org_id, key_id)
    logger.info("api_key_rotated", org_id=org_id, old_key_id=key_id)
    return result
