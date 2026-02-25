"""LLM API cost tracking per organization and job.

Records estimated spend on LLM API calls, allowing per-org and per-job
cost visibility. Costs are derived from token counts and provider pricing.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import structlog
from sqlalchemy import func, select

from uncase.db.models.usage import UsageEventModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Approximate per-1K-token pricing (USD). Updated as providers change rates.
# These are input/output averages; real pricing depends on exact model and tier.
PROVIDER_PRICING: dict[str, float] = {
    "anthropic": 0.008,  # Claude average
    "openai": 0.005,  # GPT-4o average
    "google": 0.004,  # Gemini average
    "groq": 0.001,  # Groq fast inference
    "ollama": 0.0,  # Self-hosted, no API cost
    "default": 0.005,
}


def estimate_cost(provider: str, token_count: int) -> float:
    """Estimate cost in USD for a given provider and token count."""
    rate = PROVIDER_PRICING.get(provider.lower(), PROVIDER_PRICING["default"])
    return round(rate * (token_count / 1000), 6)


class CostTrackingService:
    """Aggregate LLM API cost data from usage events.

    Costs are embedded in usage event metadata (``cost_usd``, ``provider``,
    ``tokens``). This service queries and aggregates those events.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_org_cost_summary(
        self,
        organization_id: str,
        *,
        period_days: int = 30,
    ) -> dict[str, Any]:
        """Get cost summary for an organization over a period.

        Returns:
            Dict with total_cost, cost_by_provider, cost_by_event_type,
            total_tokens, and event_count.
        """
        cutoff = datetime.now(UTC) - timedelta(days=period_days)

        # Fetch all gateway/generation events with cost metadata
        stmt = (
            select(UsageEventModel)
            .where(
                UsageEventModel.organization_id == organization_id,
                UsageEventModel.created_at >= cutoff,
                UsageEventModel.event_type.in_(["gateway_call", "conversation_generated"]),
            )
            .order_by(UsageEventModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        events = result.scalars().all()

        total_cost = 0.0
        total_tokens = 0
        cost_by_provider: dict[str, float] = {}
        cost_by_event_type: dict[str, float] = {}

        for event in events:
            meta: dict[str, Any] = dict(event.metadata_) if event.metadata_ else {}
            cost = float(meta.get("cost_usd", 0.0))
            tokens = int(meta.get("tokens", 0))
            provider = str(meta.get("provider", "unknown"))

            total_cost += cost
            total_tokens += tokens
            cost_by_provider[provider] = cost_by_provider.get(provider, 0.0) + cost
            cost_by_event_type[event.event_type] = cost_by_event_type.get(event.event_type, 0.0) + cost

        return {
            "organization_id": organization_id,
            "period_days": period_days,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "event_count": len(events),
            "cost_by_provider": {k: round(v, 4) for k, v in cost_by_provider.items()},
            "cost_by_event_type": {k: round(v, 4) for k, v in cost_by_event_type.items()},
        }

    async def get_job_cost(self, job_id: str) -> dict[str, Any]:
        """Get total cost for a specific job.

        Jobs record usage events with resource_id == job_id in metadata.
        """
        stmt = select(UsageEventModel).where(
            UsageEventModel.resource_id == job_id,
            UsageEventModel.event_type.in_(["gateway_call", "conversation_generated"]),
        )
        result = await self._session.execute(stmt)
        events = result.scalars().all()

        total_cost = 0.0
        total_tokens = 0
        for event in events:
            meta: dict[str, Any] = dict(event.metadata_) if event.metadata_ else {}
            total_cost += float(meta.get("cost_usd", 0.0))
            total_tokens += int(meta.get("tokens", 0))

        return {
            "job_id": job_id,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "event_count": len(events),
        }

    async def get_daily_costs(
        self,
        *,
        organization_id: str | None = None,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Get daily cost breakdown.

        Returns list of {date, cost_usd, tokens, events} dicts.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(
                func.date(UsageEventModel.created_at).label("day"),
                func.count().label("event_count"),
            )
            .where(
                UsageEventModel.created_at >= cutoff,
                UsageEventModel.event_type.in_(["gateway_call", "conversation_generated"]),
            )
            .group_by(func.date(UsageEventModel.created_at))
            .order_by(func.date(UsageEventModel.created_at))
        )

        if organization_id is not None:
            stmt = stmt.where(UsageEventModel.organization_id == organization_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            {
                "date": str(row.day),
                "event_count": row.event_count,
            }
            for row in rows
        ]
