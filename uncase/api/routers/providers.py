"""LLM Provider management API endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.schemas.provider import (
    ProviderCreateRequest,
    ProviderListResponse,
    ProviderResponse,
    ProviderTestResponse,
    ProviderUpdateRequest,
)
from uncase.services.provider import ProviderService

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])

logger = structlog.get_logger(__name__)


def _get_service(session: AsyncSession, settings: UNCASESettings) -> ProviderService:
    return ProviderService(session=session, settings=settings)


@router.post("", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    data: ProviderCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> ProviderResponse:
    """Register a new LLM provider.

    Configure connection details for a cloud or local LLM provider.
    API keys are encrypted at rest and never returned in responses.
    """
    service = _get_service(session, settings)
    result = await service.create_provider(data)
    logger.info("provider_registered", provider_id=result.id, type=data.provider_type)
    return result


@router.get("", response_model=ProviderListResponse)
async def list_providers(
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    active_only: bool = True,
) -> ProviderListResponse:
    """List all configured LLM providers."""
    service = _get_service(session, settings)
    return await service.list_providers(active_only=active_only)


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> ProviderResponse:
    """Get a provider by ID."""
    service = _get_service(session, settings)
    return await service.get_provider(provider_id)


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    data: ProviderUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> ProviderResponse:
    """Update a provider's configuration.

    To update the API key, include it in the request body.
    Only provided fields are changed.
    """
    service = _get_service(session, settings)
    result = await service.update_provider(provider_id, data)
    logger.info("provider_updated", provider_id=provider_id)
    return result


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> None:
    """Remove a provider configuration."""
    service = _get_service(session, settings)
    await service.delete_provider(provider_id)
    logger.info("provider_deleted", provider_id=provider_id)


@router.post("/{provider_id}/test", response_model=ProviderTestResponse)
async def test_provider(
    provider_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> ProviderTestResponse:
    """Test a provider's connection by making a minimal LLM call.

    Returns status, latency, and any error message.
    """
    service = _get_service(session, settings)
    result = await service.test_connection(provider_id)
    logger.info("provider_tested", provider_id=provider_id, status=result.status)
    return result
