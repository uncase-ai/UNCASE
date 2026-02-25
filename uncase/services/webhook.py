"""Webhook subscription and event delivery service."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import and_, func, or_, select

from uncase.db.models.webhook import WebhookDeliveryModel, WebhookSubscriptionModel
from uncase.logging import get_logger
from uncase.schemas.webhook import (
    WebhookDeliveryResponse,
    WebhookEventPayload,
    WebhookSubscriptionCreate,
    WebhookSubscriptionCreatedResponse,
    WebhookSubscriptionResponse,
    WebhookSubscriptionUpdate,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

MAX_DELIVERY_ATTEMPTS = 5
RETRY_BASE_SECONDS = 300  # 5 minutes, exponential backoff


class WebhookService:
    """Manage webhook subscriptions and event deliveries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -- Subscription CRUD --

    async def create_subscription(
        self, organization_id: str, data: WebhookSubscriptionCreate
    ) -> WebhookSubscriptionCreatedResponse:
        """Create a webhook subscription. Returns secret only on creation."""
        secret = secrets.token_hex(32)
        model = WebhookSubscriptionModel(
            id=uuid.uuid4().hex,
            organization_id=organization_id,
            url=data.url,
            events=data.events,
            secret=secret,
            description=data.description,
            is_active=data.is_active,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        logger.info(
            "webhook_subscription_created",
            subscription_id=model.id,
            org_id=organization_id,
            events=data.events,
        )
        resp = self._to_response(model)
        return WebhookSubscriptionCreatedResponse(**resp.model_dump(), secret=secret)

    async def list_subscriptions(
        self,
        organization_id: str,
        *,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[WebhookSubscriptionResponse], int]:
        """List subscriptions for an organization."""
        base = select(WebhookSubscriptionModel).where(WebhookSubscriptionModel.organization_id == organization_id)
        count_base = (
            select(func.count())
            .select_from(WebhookSubscriptionModel)
            .where(WebhookSubscriptionModel.organization_id == organization_id)
        )

        if is_active is not None:
            base = base.where(WebhookSubscriptionModel.is_active == is_active)
            count_base = count_base.where(WebhookSubscriptionModel.is_active == is_active)

        total = (await self.session.execute(count_base)).scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            base.order_by(WebhookSubscriptionModel.created_at.desc()).offset(offset).limit(page_size)
        )
        return [self._to_response(m) for m in result.scalars().all()], total

    async def get_subscription(self, subscription_id: str, organization_id: str) -> WebhookSubscriptionResponse:
        """Get a single subscription."""
        model = await self._get_or_raise(subscription_id, organization_id)
        return self._to_response(model)

    async def update_subscription(
        self,
        subscription_id: str,
        organization_id: str,
        data: WebhookSubscriptionUpdate,
    ) -> WebhookSubscriptionResponse:
        """Update a subscription."""
        model = await self._get_or_raise(subscription_id, organization_id)
        update = data.model_dump(exclude_unset=True)
        for field, value in update.items():
            setattr(model, field, value)
        model.updated_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(model)
        logger.info("webhook_subscription_updated", subscription_id=subscription_id)
        return self._to_response(model)

    async def delete_subscription(self, subscription_id: str, organization_id: str) -> None:
        """Delete a subscription and all its deliveries."""
        model = await self._get_or_raise(subscription_id, organization_id)
        await self.session.delete(model)
        await self.session.commit()
        logger.info("webhook_subscription_deleted", subscription_id=subscription_id)

    # -- Event Dispatch (fire-and-forget) --

    async def dispatch_event(
        self,
        event_type: str,
        *,
        organization_id: str | None = None,
        resource_id: str | None = None,
        resource_type: str | None = None,
        data: dict[str, object] | None = None,
    ) -> int:
        """Dispatch an event to matching subscriptions. Returns count of deliveries created."""
        if organization_id is None:
            return 0

        try:
            result = await self.session.execute(
                select(WebhookSubscriptionModel).where(
                    and_(
                        WebhookSubscriptionModel.organization_id == organization_id,
                        WebhookSubscriptionModel.is_active.is_(True),
                    )
                )
            )
            subscriptions = result.scalars().all()
            matching = [s for s in subscriptions if event_type in (s.events or [])]

            if not matching:
                return 0

            payload = WebhookEventPayload(
                id=uuid.uuid4().hex,
                event_type=event_type,
                timestamp=datetime.now(UTC).isoformat(),
                organization_id=organization_id,
                resource_id=resource_id,
                resource_type=resource_type,
                data=data or {},
            )

            for sub in matching:
                self.session.add(
                    WebhookDeliveryModel(
                        id=uuid.uuid4().hex,
                        subscription_id=sub.id,
                        event_type=event_type,
                        payload=payload.model_dump(),
                    )
                )

            await self.session.flush()
            logger.info(
                "webhook_event_dispatched",
                event_type=event_type,
                delivery_count=len(matching),
            )
            return len(matching)
        except Exception:
            logger.warning("webhook_dispatch_failed", event_type=event_type, exc_info=True)
            return 0

    # -- Delivery execution --

    async def execute_pending_deliveries(self, batch_size: int = 100) -> int:
        """Process pending deliveries. Called by background scheduler."""
        import httpx

        now = datetime.now(UTC)
        result = await self.session.execute(
            select(WebhookDeliveryModel)
            .where(
                and_(
                    WebhookDeliveryModel.status == "pending",
                    or_(
                        WebhookDeliveryModel.next_retry_at.is_(None),
                        WebhookDeliveryModel.next_retry_at <= now,
                    ),
                    WebhookDeliveryModel.attempts < MAX_DELIVERY_ATTEMPTS,
                )
            )
            .order_by(WebhookDeliveryModel.created_at.asc())
            .limit(batch_size)
        )
        deliveries = result.scalars().all()
        processed = 0

        for delivery in deliveries:
            sub = await self.session.get(WebhookSubscriptionModel, delivery.subscription_id)
            if sub is None:
                delivery.status = "failed"
                delivery.error_message = "Subscription deleted"
                processed += 1
                continue

            delivery.attempts += 1
            signature = self._sign_payload(delivery.payload, sub.secret)

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        sub.url,
                        json=delivery.payload,
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Signature": f"sha256={signature}",
                            "X-Webhook-ID": delivery.id,
                            "X-Webhook-Event": delivery.event_type,
                        },
                    )
                delivery.http_status_code = resp.status_code

                if 200 <= resp.status_code < 300:
                    delivery.status = "delivered"
                    delivery.delivered_at = datetime.now(UTC)
                    sub.last_triggered_at = datetime.now(UTC)
                else:
                    delivery.error_message = f"HTTP {resp.status_code}"
                    self._schedule_retry(delivery)
            except httpx.TimeoutException:
                delivery.error_message = "Request timeout"
                self._schedule_retry(delivery)
            except Exception as exc:
                delivery.error_message = str(exc)[:500]
                self._schedule_retry(delivery)
                logger.error(
                    "webhook_delivery_error",
                    delivery_id=delivery.id,
                    error=str(exc)[:200],
                )

            processed += 1

        await self.session.commit()
        if processed:
            logger.info("webhook_deliveries_processed", count=processed)
        return processed

    # -- Delivery history --

    async def list_deliveries(
        self,
        subscription_id: str,
        organization_id: str,
        *,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[WebhookDeliveryResponse], int]:
        """List deliveries for a subscription."""
        await self._get_or_raise(subscription_id, organization_id)

        base = select(WebhookDeliveryModel).where(WebhookDeliveryModel.subscription_id == subscription_id)
        count_base = (
            select(func.count())
            .select_from(WebhookDeliveryModel)
            .where(WebhookDeliveryModel.subscription_id == subscription_id)
        )

        if status_filter:
            base = base.where(WebhookDeliveryModel.status == status_filter)
            count_base = count_base.where(WebhookDeliveryModel.status == status_filter)

        total = (await self.session.execute(count_base)).scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            base.order_by(WebhookDeliveryModel.created_at.desc()).offset(offset).limit(page_size)
        )

        return [self._to_delivery_response(d) for d in result.scalars().all()], total

    # -- Helpers --

    async def _get_or_raise(self, subscription_id: str, organization_id: str) -> WebhookSubscriptionModel:
        result = await self.session.execute(
            select(WebhookSubscriptionModel).where(
                and_(
                    WebhookSubscriptionModel.id == subscription_id,
                    WebhookSubscriptionModel.organization_id == organization_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            from uncase.exceptions import UNCASEError

            raise UNCASEError(f"Webhook subscription '{subscription_id}' not found")
        return model

    @staticmethod
    def _sign_payload(payload: dict[str, object], secret: str) -> str:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

    def _schedule_retry(self, delivery: WebhookDeliveryModel) -> None:
        if delivery.attempts >= MAX_DELIVERY_ATTEMPTS:
            delivery.status = "failed"
        else:
            backoff = RETRY_BASE_SECONDS * (2 ** (delivery.attempts - 1))
            delivery.next_retry_at = datetime.now(UTC) + timedelta(seconds=backoff)

    @staticmethod
    def _to_response(model: WebhookSubscriptionModel) -> WebhookSubscriptionResponse:
        return WebhookSubscriptionResponse(
            id=model.id,
            organization_id=model.organization_id,
            url=model.url,
            events=model.events or [],
            description=model.description,
            is_active=model.is_active,
            last_triggered_at=model.last_triggered_at.isoformat() if model.last_triggered_at else None,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat(),
        )

    @staticmethod
    def _to_delivery_response(model: WebhookDeliveryModel) -> WebhookDeliveryResponse:
        return WebhookDeliveryResponse(
            id=model.id,
            subscription_id=model.subscription_id,
            event_type=model.event_type,
            status=model.status,
            http_status_code=model.http_status_code,
            error_message=model.error_message,
            attempts=model.attempts,
            next_retry_at=model.next_retry_at.isoformat() if model.next_retry_at else None,
            created_at=model.created_at.isoformat(),
            delivered_at=model.delivered_at.isoformat() if model.delivered_at else None,
        )
