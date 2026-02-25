"""Tests for the LLM cost tracking service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from uncase.db.models.usage import UsageEventModel
from uncase.services.cost_tracking import (
    PROVIDER_PRICING,
    CostTrackingService,
    estimate_cost,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_usage_event(
    *,
    event_type: str = "gateway_call",
    organization_id: str | None = "org-1",
    resource_id: str | None = None,
    cost_usd: float = 0.0,
    provider: str = "anthropic",
    tokens: int = 0,
    created_at: datetime | None = None,
) -> UsageEventModel:
    return UsageEventModel(
        id=uuid.uuid4().hex,
        event_type=event_type,
        organization_id=organization_id,
        resource_id=resource_id,
        count=1,
        metadata_={"cost_usd": cost_usd, "provider": provider, "tokens": tokens},
        created_at=created_at or datetime.now(UTC),
    )


class TestEstimateCost:
    def test_known_provider(self) -> None:
        cost = estimate_cost("anthropic", 1000)
        assert cost == PROVIDER_PRICING["anthropic"]

    def test_unknown_provider_uses_default(self) -> None:
        cost = estimate_cost("acme-llm", 1000)
        assert cost == PROVIDER_PRICING["default"]

    def test_zero_tokens(self) -> None:
        assert estimate_cost("openai", 0) == 0.0

    def test_ollama_free(self) -> None:
        assert estimate_cost("ollama", 10000) == 0.0

    def test_case_insensitive(self) -> None:
        assert estimate_cost("Anthropic", 1000) == estimate_cost("anthropic", 1000)


class TestCostTrackingService:
    async def test_org_summary_empty(self, async_session: AsyncSession) -> None:
        service = CostTrackingService(async_session)
        summary = await service.get_org_cost_summary("org-1")
        assert summary["total_cost_usd"] == 0.0
        assert summary["total_tokens"] == 0
        assert summary["event_count"] == 0

    async def test_org_summary_with_events(self, async_session: AsyncSession) -> None:
        async_session.add(_make_usage_event(cost_usd=0.05, tokens=5000, provider="anthropic"))
        async_session.add(_make_usage_event(cost_usd=0.03, tokens=3000, provider="openai"))
        await async_session.commit()

        service = CostTrackingService(async_session)
        summary = await service.get_org_cost_summary("org-1")
        assert summary["total_cost_usd"] == 0.08
        assert summary["total_tokens"] == 8000
        assert summary["event_count"] == 2
        assert "anthropic" in summary["cost_by_provider"]
        assert "openai" in summary["cost_by_provider"]

    async def test_org_summary_excludes_old_events(self, async_session: AsyncSession) -> None:
        old_date = datetime.now(UTC) - timedelta(days=60)
        async_session.add(_make_usage_event(cost_usd=1.00, tokens=10000, created_at=old_date))
        await async_session.commit()

        service = CostTrackingService(async_session)
        summary = await service.get_org_cost_summary("org-1", period_days=30)
        assert summary["total_cost_usd"] == 0.0

    async def test_org_summary_filters_by_org(self, async_session: AsyncSession) -> None:
        async_session.add(_make_usage_event(organization_id="org-1", cost_usd=0.05, tokens=1000))
        async_session.add(_make_usage_event(organization_id="org-2", cost_usd=0.10, tokens=2000))
        await async_session.commit()

        service = CostTrackingService(async_session)
        summary = await service.get_org_cost_summary("org-1")
        assert summary["total_cost_usd"] == 0.05

    async def test_job_cost_empty(self, async_session: AsyncSession) -> None:
        service = CostTrackingService(async_session)
        result = await service.get_job_cost("job-999")
        assert result["total_cost_usd"] == 0.0
        assert result["job_id"] == "job-999"

    async def test_job_cost_with_events(self, async_session: AsyncSession) -> None:
        async_session.add(_make_usage_event(resource_id="job-100", cost_usd=0.02, tokens=2000))
        async_session.add(_make_usage_event(resource_id="job-100", cost_usd=0.03, tokens=3000))
        async_session.add(_make_usage_event(resource_id="job-200", cost_usd=0.10, tokens=10000))
        await async_session.commit()

        service = CostTrackingService(async_session)
        result = await service.get_job_cost("job-100")
        assert result["total_cost_usd"] == 0.05
        assert result["total_tokens"] == 5000
        assert result["event_count"] == 2

    async def test_daily_costs_empty(self, async_session: AsyncSession) -> None:
        service = CostTrackingService(async_session)
        daily = await service.get_daily_costs()
        assert daily == []

    async def test_daily_costs_with_events(self, async_session: AsyncSession) -> None:
        async_session.add(_make_usage_event(cost_usd=0.01, tokens=100))
        await async_session.commit()

        service = CostTrackingService(async_session)
        daily = await service.get_daily_costs()
        assert len(daily) >= 1
        assert daily[0]["event_count"] >= 1

    async def test_daily_costs_org_filter(self, async_session: AsyncSession) -> None:
        async_session.add(_make_usage_event(organization_id="org-A", cost_usd=0.01, tokens=100))
        async_session.add(_make_usage_event(organization_id="org-B", cost_usd=0.02, tokens=200))
        await async_session.commit()

        service = CostTrackingService(async_session)
        daily = await service.get_daily_costs(organization_id="org-A")
        total_events = sum(d["event_count"] for d in daily)
        assert total_events == 1
