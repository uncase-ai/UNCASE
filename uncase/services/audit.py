"""Audit logging service — fire-and-forget compliance trail.

Every sensitive operation calls ``audit()`` to record the action.
This is separate from application logs (structlog) and metrics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog

from uncase.db.models.audit import AuditLogModel

if TYPE_CHECKING:
    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


async def audit(
    session: AsyncSession,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor_type: str = "user",
    actor_id: str | None = None,
    organization_id: str | None = None,
    detail: str | None = None,
    status: str = "success",
    extra_data: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    """Record an audit log entry (fire-and-forget safe).

    Args:
        session: Database session.
        action: Action verb (create, read, update, delete, login, export, pipeline_run).
        resource_type: Resource type (seed, conversation, job, organization, api_key).
        resource_id: Resource identifier.
        actor_type: Actor type (user, system, api_key).
        actor_id: Actor identifier.
        organization_id: Organization context.
        detail: Human-readable description.
        status: Outcome (success, denied, error).
        extra_data: Additional structured data.
        request: FastAPI request for IP/UA extraction.
    """
    try:
        ip_address = None
        user_agent = None
        endpoint = None
        http_method = None

        if request is not None:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent", "")[:500]
            endpoint = str(request.url.path)
            http_method = request.method

        entry = AuditLogModel(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_type=actor_type,
            actor_id=actor_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            detail=detail,
            extra_data=extra_data,
            status=status,
        )
        session.add(entry)
        await session.commit()
    except Exception:
        logger.debug("audit_log_write_failed", action=action, resource_type=resource_type)


class AuditService:
    """Query interface for audit logs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_logs(
        self,
        *,
        organization_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        actor_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[AuditLogModel]:
        """Query audit logs with filters.

        Args:
            organization_id: Filter by organization.
            action: Filter by action type.
            resource_type: Filter by resource type.
            actor_id: Filter by actor.
            page: Page number (1-indexed).
            page_size: Results per page.

        Returns:
            List of audit log entries, newest first.
        """
        from sqlalchemy import select

        stmt = select(AuditLogModel).order_by(AuditLogModel.created_at.desc())

        if organization_id is not None:
            stmt = stmt.where(AuditLogModel.organization_id == organization_id)
        if action is not None:
            stmt = stmt.where(AuditLogModel.action == action)
        if resource_type is not None:
            stmt = stmt.where(AuditLogModel.resource_type == resource_type)
        if actor_id is not None:
            stmt = stmt.where(AuditLogModel.actor_id == actor_id)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
