"""Audit API — compliance audit trail endpoints."""

from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.db.models.organization import OrganizationModel
from uncase.services.audit import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

logger = structlog.get_logger(__name__)


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    id: str = Field(..., description="Audit log entry ID")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: str | None = Field(default=None, description="Resource ID")
    actor_type: str = Field(..., description="Actor type")
    actor_id: str | None = Field(default=None, description="Actor ID")
    organization_id: str | None = Field(default=None, description="Organization ID")
    ip_address: str | None = Field(default=None, description="Client IP")
    endpoint: str | None = Field(default=None, description="API endpoint")
    http_method: str | None = Field(default=None, description="HTTP method")
    detail: str | None = Field(default=None, description="Description")
    extra_data: dict[str, Any] | None = Field(default=None, description="Additional metadata")
    status: str = Field(..., description="Outcome: success, denied, error")
    created_at: str = Field(..., description="When this occurred")

    model_config = {"from_attributes": True}


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    action: Annotated[str | None, Query(description="Filter by action")] = None,
    resource_type: Annotated[str | None, Query(description="Filter by resource type")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 50,
) -> list[AuditLogResponse]:
    """List audit log entries for the organization.

    Returns compliance audit trail in reverse chronological order.
    Requires organization context (X-API-Key header).
    """
    service = AuditService(session)
    logs = await service.list_logs(
        organization_id=org.id if org else None,
        action=action,
        resource_type=resource_type,
        page=page,
        page_size=page_size,
    )
    return [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            actor_type=log.actor_type,
            actor_id=log.actor_id,
            organization_id=log.organization_id,
            ip_address=log.ip_address,
            endpoint=log.endpoint,
            http_method=log.http_method,
            detail=log.detail,
            extra_data=log.extra_data,
            status=log.status,
            created_at=log.created_at.isoformat() if hasattr(log.created_at, "isoformat") else str(log.created_at),
        )
        for log in logs
    ]
