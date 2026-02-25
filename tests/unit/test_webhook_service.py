"""Tests for the webhook subscription and delivery service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from uncase.db.models.webhook import WebhookDeliveryModel
from uncase.exceptions import UNCASEError
from uncase.schemas.webhook import WebhookSubscriptionCreate, WebhookSubscriptionUpdate
from uncase.services.webhook import MAX_DELIVERY_ATTEMPTS, WebhookService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


ORG_ID = "org-test-wh-001"


def _make_sub_create(**overrides: object) -> WebhookSubscriptionCreate:
    """Build a valid WebhookSubscriptionCreate with fictional defaults."""
    defaults: dict[str, object] = {
        "url": "https://example.test/webhooks/fictitious",
        "events": ["seed_created", "evaluation_completed"],
        "description": "Suscripcion ficticia de prueba",
        "is_active": True,
    }
    defaults.update(overrides)
    return WebhookSubscriptionCreate(**defaults)  # type: ignore[arg-type]


class TestWebhookServiceCreateSubscription:
    async def test_create_subscription(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        resp = await service.create_subscription(ORG_ID, _make_sub_create())

        assert resp.id is not None
        assert resp.organization_id == ORG_ID
        assert resp.url == "https://example.test/webhooks/fictitious"
        assert resp.events == ["seed_created", "evaluation_completed"]
        assert resp.is_active is True

    async def test_create_subscription_returns_secret(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        resp = await service.create_subscription(ORG_ID, _make_sub_create())

        assert resp.secret is not None
        assert len(resp.secret) == 64  # hex(32 bytes) = 64 chars

    async def test_create_subscription_with_description(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        resp = await service.create_subscription(
            ORG_ID, _make_sub_create(description="Webhook de prueba personalizado")
        )

        assert resp.description == "Webhook de prueba personalizado"

    async def test_create_inactive_subscription(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        resp = await service.create_subscription(ORG_ID, _make_sub_create(is_active=False))

        assert resp.is_active is False


class TestWebhookServiceGetSubscription:
    async def test_get_existing_subscription(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        found = await service.get_subscription(created.id, ORG_ID)

        assert found.id == created.id
        assert found.url == created.url

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        with pytest.raises(UNCASEError, match="not found"):
            await service.get_subscription("nonexistent-id", ORG_ID)

    async def test_get_wrong_org_raises(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        with pytest.raises(UNCASEError, match="not found"):
            await service.get_subscription(created.id, "other-org")


class TestWebhookServiceListSubscriptions:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        subs, total = await service.list_subscriptions(ORG_ID)

        assert subs == []
        assert total == 0

    async def test_list_returns_all_for_org(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        await service.create_subscription(ORG_ID, _make_sub_create(url="https://a.test"))
        await service.create_subscription(ORG_ID, _make_sub_create(url="https://b.test"))
        await service.create_subscription("other-org", _make_sub_create(url="https://c.test"))

        subs, total = await service.list_subscriptions(ORG_ID)

        assert total == 2
        assert len(subs) == 2

    async def test_list_filter_active(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        await service.create_subscription(ORG_ID, _make_sub_create(is_active=True))
        await service.create_subscription(ORG_ID, _make_sub_create(is_active=False))

        active, total = await service.list_subscriptions(ORG_ID, is_active=True)
        assert total == 1
        assert active[0].is_active is True

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        for i in range(5):
            await service.create_subscription(ORG_ID, _make_sub_create(url=f"https://test-{i}.test"))

        page1, total = await service.list_subscriptions(ORG_ID, page=1, page_size=2)
        assert len(page1) == 2
        assert total == 5

        page2, _ = await service.list_subscriptions(ORG_ID, page=2, page_size=2)
        assert len(page2) == 2


class TestWebhookServiceUpdateSubscription:
    async def test_update_url(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        updated = await service.update_subscription(
            created.id, ORG_ID, WebhookSubscriptionUpdate(url="https://new.test/hook")
        )

        assert updated.url == "https://new.test/hook"

    async def test_update_events(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        updated = await service.update_subscription(
            created.id, ORG_ID, WebhookSubscriptionUpdate(events=["knowledge_uploaded"])
        )

        assert updated.events == ["knowledge_uploaded"]

    async def test_update_deactivate(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        updated = await service.update_subscription(created.id, ORG_ID, WebhookSubscriptionUpdate(is_active=False))

        assert updated.is_active is False

    async def test_update_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        with pytest.raises(UNCASEError, match="not found"):
            await service.update_subscription("nonexistent-id", ORG_ID, WebhookSubscriptionUpdate(url="https://x.test"))


class TestWebhookServiceDeleteSubscription:
    async def test_delete_existing(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        created = await service.create_subscription(ORG_ID, _make_sub_create())
        await service.delete_subscription(created.id, ORG_ID)

        with pytest.raises(UNCASEError, match="not found"):
            await service.get_subscription(created.id, ORG_ID)

    async def test_delete_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        with pytest.raises(UNCASEError, match="not found"):
            await service.delete_subscription("nonexistent-id", ORG_ID)


class TestWebhookServiceDispatchEvent:
    async def test_dispatch_creates_deliveries(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub = await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"]))

        count = await service.dispatch_event(
            "seed_created",
            organization_id=ORG_ID,
            resource_id="seed-abc",
            resource_type="seed",
            data={"domain": "automotive.sales"},
        )

        assert count == 1

        deliveries, total = await service.list_deliveries(sub.id, ORG_ID)
        assert total == 1
        assert deliveries[0].event_type == "seed_created"
        assert deliveries[0].status == "pending"

    async def test_dispatch_no_org_returns_zero(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        count = await service.dispatch_event("seed_created", organization_id=None)
        assert count == 0

    async def test_dispatch_no_matching_subs(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        await service.create_subscription(ORG_ID, _make_sub_create(events=["evaluation_completed"]))

        count = await service.dispatch_event("seed_created", organization_id=ORG_ID)
        assert count == 0

    async def test_dispatch_multiple_subs(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"], url="https://a.test"))
        await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"], url="https://b.test"))

        count = await service.dispatch_event("seed_created", organization_id=ORG_ID)
        assert count == 2

    async def test_dispatch_ignores_inactive_subs(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"], is_active=False))

        count = await service.dispatch_event("seed_created", organization_id=ORG_ID)
        assert count == 0


class TestWebhookServiceExecuteDeliveries:
    async def _create_pending_delivery(self, service: WebhookService, async_session: AsyncSession) -> tuple[str, str]:
        """Helper: create a subscription and dispatch an event to get a pending delivery."""
        sub = await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"]))
        await service.dispatch_event("seed_created", organization_id=ORG_ID, resource_id="s1")
        await async_session.commit()
        return sub.id, sub.secret

    async def test_execute_successful_delivery(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub_id, _ = await self._create_pending_delivery(service, async_session)

        mock_resp = AsyncMock()
        mock_resp.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            processed = await service.execute_pending_deliveries()

        assert processed >= 1

        deliveries, _ = await service.list_deliveries(sub_id, ORG_ID)
        delivered = [d for d in deliveries if d.status == "delivered"]
        assert len(delivered) >= 1

    async def test_execute_failed_delivery_schedules_retry(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub_id, _ = await self._create_pending_delivery(service, async_session)

        mock_resp = AsyncMock()
        mock_resp.status_code = 500

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            processed = await service.execute_pending_deliveries()

        assert processed >= 1

        deliveries, _ = await service.list_deliveries(sub_id, ORG_ID)
        # Should still be pending (retryable) or have next_retry_at set
        pending = [d for d in deliveries if d.status == "pending"]
        assert len(pending) >= 1

    async def test_execute_timeout_schedules_retry(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        _sub_id, _ = await self._create_pending_delivery(service, async_session)

        import httpx

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            processed = await service.execute_pending_deliveries()

        assert processed >= 1

    async def test_execute_no_pending(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        processed = await service.execute_pending_deliveries()
        assert processed == 0


class TestWebhookServiceListDeliveries:
    async def test_list_deliveries_empty(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub = await service.create_subscription(ORG_ID, _make_sub_create())
        deliveries, total = await service.list_deliveries(sub.id, ORG_ID)

        assert deliveries == []
        assert total == 0

    async def test_list_deliveries_for_subscription(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub = await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"]))

        await service.dispatch_event("seed_created", organization_id=ORG_ID)
        await async_session.commit()
        await service.dispatch_event("seed_created", organization_id=ORG_ID)
        await async_session.commit()

        deliveries, total = await service.list_deliveries(sub.id, ORG_ID)

        assert total == 2
        assert len(deliveries) == 2

    async def test_list_deliveries_filter_by_status(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        sub = await service.create_subscription(ORG_ID, _make_sub_create(events=["seed_created"]))

        await service.dispatch_event("seed_created", organization_id=ORG_ID)
        await async_session.commit()

        _deliveries, total = await service.list_deliveries(sub.id, ORG_ID, status_filter="pending")
        assert total == 1

        _deliveries_d, total_d = await service.list_deliveries(sub.id, ORG_ID, status_filter="delivered")
        assert total_d == 0

    async def test_list_deliveries_nonexistent_sub_raises(self, async_session: AsyncSession) -> None:
        service = WebhookService(async_session)
        with pytest.raises(UNCASEError, match="not found"):
            await service.list_deliveries("nonexistent-id", ORG_ID)


class TestWebhookServiceHelpers:
    def test_sign_payload(self) -> None:
        payload: dict[str, object] = {"event": "test", "data": "fictitious"}
        hmac_key = "test-secret-abc123"
        signature = WebhookService._sign_payload(payload, hmac_key)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 hex digest

    def test_sign_payload_deterministic(self) -> None:
        payload: dict[str, object] = {"event": "test", "value": 42}
        hmac_key = "deterministic-hmac-key"
        sig1 = WebhookService._sign_payload(payload, hmac_key)
        sig2 = WebhookService._sign_payload(payload, hmac_key)

        assert sig1 == sig2

    def test_sign_payload_different_secrets(self) -> None:
        payload: dict[str, object] = {"event": "test"}
        sig1 = WebhookService._sign_payload(payload, "secret-a")
        sig2 = WebhookService._sign_payload(payload, "secret-b")

        assert sig1 != sig2

    def test_schedule_retry_sets_backoff(self) -> None:
        delivery = WebhookDeliveryModel(
            id="test-delivery",
            subscription_id="sub-1",
            event_type="test",
            payload={},
            status="pending",
            attempts=1,
        )
        service = WebhookService.__new__(WebhookService)
        service._schedule_retry(delivery)

        assert delivery.next_retry_at is not None
        assert delivery.status == "pending"

    def test_schedule_retry_marks_failed_at_max(self) -> None:
        delivery = WebhookDeliveryModel(
            id="test-delivery",
            subscription_id="sub-1",
            event_type="test",
            payload={},
            status="pending",
            attempts=MAX_DELIVERY_ATTEMPTS,
        )
        service = WebhookService.__new__(WebhookService)
        service._schedule_retry(delivery)

        assert delivery.status == "failed"
