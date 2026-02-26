"""Inbound E2B sandbox webhook receiver.

Receives lifecycle notifications from E2B (or internal orchestration)
when sandboxes start, complete, error, or expire.  Events are logged,
metered, audited, and forwarded to any matching outbound webhook
subscriptions.

Endpoints are NOT org-authenticated — they are called by external
infrastructure.  An optional shared secret (``E2B_WEBHOOK_SECRET``)
can be configured for HMAC-SHA256 signature verification via the
``X-E2B-Signature`` header.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid
from collections import deque
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query, Request, status

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.schemas.e2b_webhook import (
    E2BCompletePayload,
    E2BErrorPayload,
    E2BEventType,
    E2BStartPayload,
    E2BWebhookEventRecord,
    E2BWebhookPayload,
    E2BWebhookResponse,
)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:  # pragma: no cover
    AsyncSession = object  # type: ignore[assignment,misc]

router = APIRouter(prefix="/api/v1/webhooks/e2b", tags=["e2b-webhooks"])

logger = structlog.get_logger(__name__)

# In-memory ring buffer for recent events (lightweight, no DB table needed).
# Production deployments should back this with a proper store.
_MAX_EVENT_HISTORY = 200
_event_log: deque[E2BWebhookEventRecord] = deque(maxlen=_MAX_EVENT_HISTORY)


# ── Helpers ──────────────────────────────────────────────────────────


def _verify_signature(
    body: bytes,
    secret: str,
    signature_header: str | None,
) -> bool:
    """Verify HMAC-SHA256 signature if a shared secret is configured.

    Returns True when:
    - No secret is configured (verification disabled), OR
    - The signature matches.
    """
    if not secret:
        return True  # verification disabled
    if not signature_header:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    # Accept both "sha256=<hex>" and raw hex
    provided = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def _record_event(
    event_type: E2BEventType,
    sandbox_id: str,
    *,
    domain: str | None = None,
    organization_id: str | None = None,
    payload: dict[str, object] | None = None,
) -> str:
    """Append an event to the in-memory ring buffer. Returns the event ID."""
    event_id = uuid.uuid4().hex
    _event_log.append(
        E2BWebhookEventRecord(
            event_id=event_id,
            event_type=event_type,
            sandbox_id=sandbox_id,
            domain=domain,
            organization_id=organization_id,
            payload=payload or {},
        )
    )
    return event_id


async def _dispatch_outbound(
    session: AsyncSession,
    event_type: str,
    *,
    organization_id: str | None,
    resource_id: str | None = None,
    data: dict[str, object] | None = None,
) -> None:
    """Forward the event to matching outbound webhook subscriptions."""
    try:
        from uncase.services.webhook import WebhookService

        service = WebhookService(session)
        await service.dispatch_event(
            event_type,
            organization_id=organization_id,
            resource_id=resource_id,
            data=data,
        )
    except Exception:
        logger.debug("e2b_outbound_dispatch_skipped", event_type=event_type)


async def _meter_event(
    session: AsyncSession,
    event_type: str,
    *,
    organization_id: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    """Record the event in usage metering (fire-and-forget)."""
    try:
        from uncase.api.metering import meter

        await meter(
            session,
            event_type,
            organization_id=organization_id,
            resource_id=resource_id,
            metadata=metadata,
        )
    except Exception:
        logger.debug("e2b_metering_skipped", event_type=event_type)


async def _audit_event(
    session: AsyncSession,
    *,
    action: str,
    sandbox_id: str,
    organization_id: str | None = None,
    detail: str | None = None,
    request: Request | None = None,
) -> None:
    """Record an audit log entry (fire-and-forget)."""
    try:
        from uncase.services.audit import audit

        await audit(
            session,
            action=action,
            resource_type="sandbox",
            resource_id=sandbox_id,
            actor_type="system",
            organization_id=organization_id,
            detail=detail,
            request=request,
        )
    except Exception:
        logger.debug("e2b_audit_skipped", action=action, sandbox_id=sandbox_id)


# ── Endpoints ────────────────────────────────────────────────────────


@router.post("/start", response_model=E2BWebhookResponse, status_code=status.HTTP_200_OK)
async def on_sandbox_start(
    payload: E2BStartPayload,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    x_e2b_signature: str | None = Header(default=None),
) -> E2BWebhookResponse:
    """Receive notification that a new sandbox/demo has started.

    Called by E2B infrastructure or the internal demo orchestrator when
    a sandbox boots successfully.
    """
    body = await request.body()
    if not _verify_signature(body, settings.e2b_webhook_secret, x_e2b_signature):
        from uncase.exceptions import AuthenticationError

        raise AuthenticationError("Invalid E2B webhook signature")

    event_id = _record_event(
        E2BEventType.SANDBOX_STARTED,
        payload.sandbox_id,
        domain=payload.domain,
        organization_id=payload.organization_id,
        payload=payload.model_dump(mode="json"),
    )

    logger.info(
        "e2b_sandbox_started",
        event_id=event_id,
        sandbox_id=payload.sandbox_id,
        domain=payload.domain,
        organization_id=payload.organization_id,
        ttl_minutes=payload.ttl_minutes,
    )

    await _audit_event(
        session,
        action="sandbox_start",
        sandbox_id=payload.sandbox_id,
        organization_id=payload.organization_id,
        detail=f"Sandbox started for domain={payload.domain}, ttl={payload.ttl_minutes}min",
        request=request,
    )

    await _dispatch_outbound(
        session,
        "sandbox_started",
        organization_id=payload.organization_id,
        resource_id=payload.sandbox_id,
        data=payload.model_dump(mode="json"),
    )

    await _meter_event(
        session,
        "sandbox_started",
        organization_id=payload.organization_id,
        resource_id=payload.sandbox_id,
        metadata={"domain": payload.domain, "ttl_minutes": payload.ttl_minutes},
    )

    await session.commit()

    return E2BWebhookResponse(
        event_id=event_id,
        event_type=E2BEventType.SANDBOX_STARTED,
    )


@router.post("/complete", response_model=E2BWebhookResponse, status_code=status.HTTP_200_OK)
async def on_sandbox_complete(
    payload: E2BCompletePayload,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    x_e2b_signature: str | None = Header(default=None),
) -> E2BWebhookResponse:
    """Receive notification that a sandbox has completed successfully."""
    body = await request.body()
    if not _verify_signature(body, settings.e2b_webhook_secret, x_e2b_signature):
        from uncase.exceptions import AuthenticationError

        raise AuthenticationError("Invalid E2B webhook signature")

    event_id = _record_event(
        E2BEventType.SANDBOX_COMPLETED,
        payload.sandbox_id,
        domain=payload.domain,
        organization_id=payload.organization_id,
        payload=payload.model_dump(mode="json"),
    )

    logger.info(
        "e2b_sandbox_completed",
        event_id=event_id,
        sandbox_id=payload.sandbox_id,
        domain=payload.domain,
        conversations_generated=payload.conversations_generated,
        duration_seconds=payload.duration_seconds,
    )

    await _audit_event(
        session,
        action="sandbox_complete",
        sandbox_id=payload.sandbox_id,
        organization_id=payload.organization_id,
        detail=f"Sandbox completed: {payload.conversations_generated} conversations in {payload.duration_seconds}s",
        request=request,
    )

    await _dispatch_outbound(
        session,
        "sandbox_completed",
        organization_id=payload.organization_id,
        resource_id=payload.sandbox_id,
        data=payload.model_dump(mode="json"),
    )

    await _meter_event(
        session,
        "sandbox_completed",
        organization_id=payload.organization_id,
        resource_id=payload.sandbox_id,
        metadata={
            "domain": payload.domain,
            "conversations_generated": payload.conversations_generated,
            "duration_seconds": payload.duration_seconds,
        },
    )

    await session.commit()

    return E2BWebhookResponse(
        event_id=event_id,
        event_type=E2BEventType.SANDBOX_COMPLETED,
    )


@router.post("/error", response_model=E2BWebhookResponse, status_code=status.HTTP_200_OK)
async def on_sandbox_error(
    payload: E2BErrorPayload,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    x_e2b_signature: str | None = Header(default=None),
) -> E2BWebhookResponse:
    """Receive notification that a sandbox has errored."""
    body = await request.body()
    if not _verify_signature(body, settings.e2b_webhook_secret, x_e2b_signature):
        from uncase.exceptions import AuthenticationError

        raise AuthenticationError("Invalid E2B webhook signature")

    event_id = _record_event(
        E2BEventType.SANDBOX_ERROR,
        payload.sandbox_id,
        domain=payload.domain,
        organization_id=payload.organization_id,
        payload=payload.model_dump(mode="json"),
    )

    logger.warning(
        "e2b_sandbox_error",
        event_id=event_id,
        sandbox_id=payload.sandbox_id,
        domain=payload.domain,
        error=payload.error[:200],
        error_code=payload.error_code,
    )

    await _audit_event(
        session,
        action="sandbox_error",
        sandbox_id=payload.sandbox_id,
        organization_id=payload.organization_id,
        detail=f"Sandbox error: {payload.error[:500]}",
        request=request,
    )

    await _dispatch_outbound(
        session,
        "sandbox_error",
        organization_id=payload.organization_id,
        resource_id=payload.sandbox_id,
        data=payload.model_dump(mode="json"),
    )

    await session.commit()

    return E2BWebhookResponse(
        event_id=event_id,
        event_type=E2BEventType.SANDBOX_ERROR,
    )


@router.post("", response_model=E2BWebhookResponse, status_code=status.HTTP_200_OK)
async def on_sandbox_event(
    payload: E2BWebhookPayload,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    x_e2b_signature: str | None = Header(default=None),
) -> E2BWebhookResponse:
    """Generic E2B webhook receiver for any sandbox lifecycle event.

    Use the typed endpoints (/start, /complete, /error) when possible.
    This generic endpoint accepts any event_type from ``E2BEventType``.
    """
    body = await request.body()
    if not _verify_signature(body, settings.e2b_webhook_secret, x_e2b_signature):
        from uncase.exceptions import AuthenticationError

        raise AuthenticationError("Invalid E2B webhook signature")

    event_id = _record_event(
        payload.event_type,
        payload.sandbox_id,
        domain=payload.domain,
        organization_id=payload.organization_id,
        payload=payload.model_dump(mode="json"),
    )

    logger.info(
        "e2b_webhook_received",
        event_id=event_id,
        event_type=payload.event_type,
        sandbox_id=payload.sandbox_id,
        domain=payload.domain,
    )

    # Map E2B event types to outbound webhook event names
    outbound_event_map: dict[E2BEventType, str] = {
        E2BEventType.SANDBOX_STARTED: "sandbox_started",
        E2BEventType.SANDBOX_COMPLETED: "sandbox_completed",
        E2BEventType.SANDBOX_ERROR: "sandbox_error",
        E2BEventType.SANDBOX_EXPIRED: "sandbox_expired",
    }

    outbound_event = outbound_event_map.get(payload.event_type)
    if outbound_event:
        await _dispatch_outbound(
            session,
            outbound_event,
            organization_id=payload.organization_id,
            resource_id=payload.sandbox_id,
            data=payload.model_dump(mode="json"),
        )

    await session.commit()

    return E2BWebhookResponse(
        event_id=event_id,
        event_type=payload.event_type,
    )


@router.get("/events", response_model=dict, status_code=status.HTTP_200_OK)
async def list_recent_events(
    event_type: Annotated[E2BEventType | None, Query(description="Filter by event type")] = None,
    sandbox_id: Annotated[str | None, Query(description="Filter by sandbox ID")] = None,
    limit: Annotated[int, Query(ge=1, le=200, description="Max events to return")] = 50,
) -> dict[str, object]:
    """List recent E2B webhook events (from in-memory ring buffer).

    Useful for debugging and monitoring sandbox activity without
    querying the audit log.
    """
    events = list(_event_log)
    events.reverse()  # newest first

    if event_type is not None:
        events = [e for e in events if e.event_type == event_type]

    if sandbox_id is not None:
        events = [e for e in events if e.sandbox_id == sandbox_id]

    events = events[:limit]

    return {
        "items": [e.model_dump(mode="json") for e in events],
        "total": len(events),
        "buffer_size": len(_event_log),
        "buffer_capacity": _MAX_EVENT_HISTORY,
    }
