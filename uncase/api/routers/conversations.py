"""Conversation CRUD API endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.conversation_api import (
    ConversationBulkCreateRequest,
    ConversationBulkCreateResponse,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdateRequest,
)
from uncase.services.conversation import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

logger = structlog.get_logger(__name__)


def _get_service(session: AsyncSession) -> ConversationService:
    return ConversationService(session)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> ConversationResponse:
    """Persist a conversation to the database."""
    service = _get_service(session)
    org_id = org.id if org else None
    result = await service.create_conversation(data, organization_id=org_id)
    logger.info("conversation_created", conversation_id=result.conversation_id, org_id=org_id)
    await meter(
        session,
        "conversation_created",
        organization_id=org_id,
        resource_id=result.conversation_id,
        metadata={"dominio": result.dominio},
    )
    return result


@router.post("/bulk", response_model=ConversationBulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_conversations(
    data: ConversationBulkCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> ConversationBulkCreateResponse:
    """Bulk-create multiple conversations. Duplicates are skipped."""
    service = _get_service(session)
    org_id = org.id if org else None
    result = await service.bulk_create(data.conversations, organization_id=org_id)
    logger.info("conversations_bulk_created", created=result.created, skipped=result.skipped, org_id=org_id)
    return result


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: Annotated[str | None, Query(description="Filter by domain")] = None,
    language: Annotated[str | None, Query(description="Filter by language")] = None,
    conv_status: Annotated[str | None, Query(alias="status", description="Filter by status")] = None,
    seed_id: Annotated[str | None, Query(description="Filter by seed ID")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> ConversationListResponse:
    """List conversations with optional filters and pagination."""
    service = _get_service(session)
    org_id = org.id if org else None
    return await service.list_conversations(
        domain=domain,
        language=language,
        status=conv_status,
        seed_id=seed_id,
        organization_id=org_id,
        page=page,
        page_size=page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """Get a single conversation by its conversation_id."""
    service = _get_service(session)
    return await service.get_conversation(conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """Update conversation metadata (status, rating, tags, notes)."""
    service = _get_service(session)
    result = await service.update_conversation(conversation_id, data)
    logger.info("conversation_updated", conversation_id=conversation_id)
    return result


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a conversation."""
    service = _get_service(session)
    await service.delete_conversation(conversation_id)
    logger.info("conversation_deleted", conversation_id=conversation_id)
