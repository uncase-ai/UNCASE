"""Webhook subscription API endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_current_org, get_db
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.webhook import (
    WEBHOOK_EVENTS,
    WebhookSubscriptionCreate,
    WebhookSubscriptionCreatedResponse,
    WebhookSubscriptionResponse,
    WebhookSubscriptionUpdate,
)
from uncase.services.webhook import WebhookService

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

logger = structlog.get_logger(__name__)


def _get_service(session: AsyncSession) -> WebhookService:
    return WebhookService(session)


@router.post("", response_model=WebhookSubscriptionCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: WebhookSubscriptionCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
) -> WebhookSubscriptionCreatedResponse:
    """Create a webhook subscription. The secret is only returned once."""
    service = _get_service(session)
    result = await service.create_subscription(org.id, data)
    logger.info("webhook_created", subscription_id=result.id, org_id=org.id)
    return result


@router.get("", response_model=dict)
async def list_subscriptions(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> dict[str, object]:
    """List webhook subscriptions for your organization."""
    service = _get_service(session)
    items, total = await service.list_subscriptions(org.id, is_active=is_active, page=page, page_size=page_size)
    return {
        "items": [s.model_dump() for s in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{subscription_id}", response_model=WebhookSubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
) -> WebhookSubscriptionResponse:
    """Get a webhook subscription by ID."""
    service = _get_service(session)
    return await service.get_subscription(subscription_id, org.id)


@router.patch("/{subscription_id}", response_model=WebhookSubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    data: WebhookSubscriptionUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
) -> WebhookSubscriptionResponse:
    """Update a webhook subscription."""
    service = _get_service(session)
    return await service.update_subscription(subscription_id, org.id, data)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
) -> None:
    """Delete a webhook subscription and all its delivery history."""
    service = _get_service(session)
    await service.delete_subscription(subscription_id, org.id)


@router.post("/{subscription_id}/test", status_code=status.HTTP_202_ACCEPTED)
async def send_test_webhook(
    subscription_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
) -> dict[str, str]:
    """Send a test webhook event."""
    service = _get_service(session)
    await service.get_subscription(subscription_id, org.id)
    await service.dispatch_event(
        "test.webhook",
        organization_id=org.id,
        resource_id="test",
        data={"message": "Test webhook delivery"},
    )
    await service.session.commit()
    return {"status": "queued", "message": "Test delivery has been queued"}


@router.get("/{subscription_id}/deliveries", response_model=dict)
async def list_deliveries(
    subscription_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel, Depends(get_current_org)],
    delivery_status: str | None = Query(default=None, alias="status", description="pending, delivered, or failed"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> dict[str, object]:
    """List delivery attempts for a subscription."""
    service = _get_service(session)
    items, total = await service.list_deliveries(
        subscription_id,
        org.id,
        status_filter=delivery_status,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [d.model_dump() for d in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/meta/event-types", response_model=list[str])
async def list_event_types() -> list[str]:
    """List all available webhook event types."""
    return WEBHOOK_EVENTS
