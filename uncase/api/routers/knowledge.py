"""Knowledge base API endpoints.

Supports document upload (with server-side chunking), listing,
search, and deletion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, status

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.knowledge import (
    KnowledgeDocumentResponse,
    KnowledgeListResponse,
    KnowledgeSearchResponse,
    KnowledgeUploadRequest,
)
from uncase.services.knowledge import KnowledgeService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.post("", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    data: KnowledgeUploadRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> KnowledgeDocumentResponse:
    """Upload a knowledge document. The text is chunked server-side."""
    service = KnowledgeService(session)
    org_id = org.id if org else None
    result = await service.upload_document(data, organization_id=org_id)
    await meter(
        session,
        "knowledge_uploaded",
        organization_id=org_id,
        resource_id=result.id,
        metadata={"domain": data.domain, "type": data.type, "chunk_count": result.chunk_count},
    )
    return result


@router.get("", response_model=KnowledgeListResponse)
async def list_documents(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: str | None = Query(default=None),
    knowledge_type: str | None = Query(default=None, alias="type"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> KnowledgeListResponse:
    """List knowledge documents with optional filters."""
    service = KnowledgeService(session)
    org_id = org.id if org else None
    return await service.list_documents(
        domain=domain,
        type_filter=knowledge_type,
        organization_id=org_id,
        page=page,
        page_size=page_size,
    )


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_chunks(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    q: str = Query(..., min_length=1, description="Search query"),
    domain: str | None = Query(default=None),
    knowledge_type: str | None = Query(default=None, alias="type"),
    limit: int = Query(default=20, ge=1, le=100),
) -> KnowledgeSearchResponse:
    """Search knowledge chunks by content keyword match."""
    service = KnowledgeService(session)
    org_id = org.id if org else None
    return await service.search_chunks(
        query=q,
        domain=domain,
        type_filter=knowledge_type,
        organization_id=org_id,
        limit=limit,
    )


@router.get("/{doc_id}", response_model=KnowledgeDocumentResponse)
async def get_document(
    doc_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> KnowledgeDocumentResponse:
    """Get a knowledge document with all its chunks."""
    service = KnowledgeService(session)
    return await service.get_document(doc_id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a knowledge document and all its chunks."""
    service = KnowledgeService(session)
    await service.delete_document(doc_id)
