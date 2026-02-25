"""Tests for the usage metering service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.schemas.usage import UsageEventRecord
from uncase.services.usage import UsageMeteringService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_event(**overrides: object) -> UsageEventRecord:
    """Build a valid UsageEventRecord with fictional defaults."""
    defaults: dict[str, object] = {
        "organization_id": "org-test-001",
        "event_type": "seed_created",
        "resource_id": "seed-abc123",
        "count": 1,
        "metadata": {"domain": "automotive.sales"},
        "ip_address": "192.0.2.1",
    }
    defaults.update(overrides)
    return UsageEventRecord(**defaults)  # type: ignore[arg-type]


class TestUsageMeteringRecord:
    async def test_record_event(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        event = _make_event()
        resp = await service.record(event)

        assert resp.id is not None
        assert resp.event_type == "seed_created"
        assert resp.organization_id == "org-test-001"
        assert resp.resource_id == "seed-abc123"
        assert resp.count == 1

    async def test_record_event_with_count(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        event = _make_event(count=5, event_type="conversation_generated")
        resp = await service.record(event)

        assert resp.count == 5
        assert resp.event_type == "conversation_generated"

    async def test_record_event_without_org(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        event = _make_event(organization_id=None)
        resp = await service.record(event)

        assert resp.organization_id is None

    async def test_record_event_without_metadata(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        event = _make_event(metadata=None)
        resp = await service.record(event)

        assert resp.metadata is None

    async def test_record_preserves_ip_address(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        event = _make_event(ip_address="198.51.100.42")
        resp = await service.record(event)

        assert resp.id is not None
        assert resp.created_at != ""


class TestUsageMeteringSummary:
    async def test_summary_empty(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        summary = await service.get_summary()

        assert summary.items == []
        assert summary.total_events == 0

    async def test_summary_aggregates_by_type(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(event_type="seed_created", count=1))
        await service.record(_make_event(event_type="seed_created", count=2))
        await service.record(_make_event(event_type="evaluation_run", count=1))

        summary = await service.get_summary()

        assert summary.total_events == 3
        type_map = {item.event_type: item for item in summary.items}
        assert "seed_created" in type_map
        assert type_map["seed_created"].total_count == 3
        assert type_map["seed_created"].event_count == 2
        assert "evaluation_run" in type_map
        assert type_map["evaluation_run"].total_count == 1

    async def test_summary_filters_by_org(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(organization_id="org-a", event_type="seed_created"))
        await service.record(_make_event(organization_id="org-b", event_type="seed_created"))

        summary = await service.get_summary(organization_id="org-a")

        assert summary.total_events == 1
        assert summary.organization_id == "org-a"

    async def test_summary_includes_period(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        summary = await service.get_summary()

        assert summary.period_start != ""
        assert summary.period_end != ""


class TestUsageMeteringListEvents:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        events, total = await service.list_events()

        assert events == []
        assert total == 0

    async def test_list_returns_all(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(event_type="seed_created"))
        await service.record(_make_event(event_type="evaluation_run"))

        events, total = await service.list_events()

        assert total == 2
        assert len(events) == 2

    async def test_list_filter_by_org(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(organization_id="org-a"))
        await service.record(_make_event(organization_id="org-b"))

        events, total = await service.list_events(organization_id="org-a")

        assert total == 1
        assert events[0].organization_id == "org-a"

    async def test_list_filter_by_event_type(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(event_type="seed_created"))
        await service.record(_make_event(event_type="evaluation_run"))

        events, total = await service.list_events(event_type="seed_created")

        assert total == 1
        assert events[0].event_type == "seed_created"

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        for i in range(5):
            await service.record(_make_event(resource_id=f"res-{i}"))

        events_p1, total = await service.list_events(page=1, page_size=2)
        assert len(events_p1) == 2
        assert total == 5

        events_p2, _ = await service.list_events(page=2, page_size=2)
        assert len(events_p2) == 2

        events_p3, _ = await service.list_events(page=3, page_size=2)
        assert len(events_p3) == 1

    async def test_list_combined_filters(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        await service.record(_make_event(organization_id="org-x", event_type="seed_created"))
        await service.record(_make_event(organization_id="org-x", event_type="evaluation_run"))
        await service.record(_make_event(organization_id="org-y", event_type="seed_created"))

        events, total = await service.list_events(organization_id="org-x", event_type="seed_created")

        assert total == 1
        assert events[0].event_type == "seed_created"
        assert events[0].organization_id == "org-x"


class TestUsageMeteringResponse:
    async def test_response_has_created_at(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        resp = await service.record(_make_event())

        assert resp.created_at != ""

    async def test_response_has_unique_ids(self, async_session: AsyncSession) -> None:
        service = UsageMeteringService(async_session)
        r1 = await service.record(_make_event())
        r2 = await service.record(_make_event())

        assert r1.id != r2.id
