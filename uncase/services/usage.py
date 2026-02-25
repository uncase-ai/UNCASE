"""Usage metering service layer."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select, text

from uncase.db.models.usage import UsageEventModel
from uncase.logging import get_logger
from uncase.schemas.usage import (
    UsageEventRecord,
    UsageEventResponse,
    UsageSummaryItem,
    UsageSummaryResponse,
    UsageTimelinePoint,
    UsageTimelineResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class UsageMeteringService:
    """Service for recording and querying usage events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(self, event: UsageEventRecord) -> UsageEventResponse:
        """Record a usage event.

        This is the primary entry point for metering. Call this from
        routers or services after a successful operation.
        """
        model = UsageEventModel(
            id=uuid.uuid4().hex,
            organization_id=event.organization_id,
            event_type=event.event_type,
            resource_id=event.resource_id,
            count=event.count,
            metadata_=event.metadata,
            ip_address=event.ip_address,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        logger.info(
            "usage_event_recorded",
            event_type=event.event_type,
            org_id=event.organization_id,
            count=event.count,
        )
        return self._to_response(model)

    async def get_summary(
        self,
        *,
        organization_id: str | None = None,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> UsageSummaryResponse:
        """Get aggregated usage summary grouped by event_type."""
        now = datetime.now(UTC)

        if period_end is None:
            period_end = now
        if period_start is None:
            # Default to current month
            period_start = period_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        query = (
            select(
                UsageEventModel.event_type,
                func.sum(UsageEventModel.count).label("total_count"),
                func.count().label("event_count"),
            )
            .where(
                UsageEventModel.created_at >= period_start,
                UsageEventModel.created_at <= period_end,
            )
            .group_by(UsageEventModel.event_type)
        )

        if organization_id is not None:
            query = query.where(UsageEventModel.organization_id == organization_id)

        result = await self.session.execute(query)
        rows = result.all()

        items = [
            UsageSummaryItem(
                event_type=row.event_type,
                total_count=int(row.total_count),
                event_count=int(row.event_count),
            )
            for row in rows
        ]
        total_events = sum(item.event_count for item in items)

        return UsageSummaryResponse(
            organization_id=organization_id,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            items=items,
            total_events=total_events,
        )

    async def get_timeline(
        self,
        *,
        event_type: str,
        organization_id: str | None = None,
        granularity: str = "day",
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> UsageTimelineResponse:
        """Get time-series usage data for a specific event type."""
        now = datetime.now(UTC)

        if period_end is None:
            period_end = now
        if period_start is None:
            period_start = period_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Truncation expression based on granularity
        trunc_map = {
            "hour": "hour",
            "day": "day",
            "week": "week",
            "month": "month",
        }
        trunc_part = trunc_map.get(granularity, "day")

        query = (
            select(
                func.date_trunc(trunc_part, UsageEventModel.created_at).label("period"),
                func.sum(UsageEventModel.count).label("total_count"),
            )
            .where(
                UsageEventModel.event_type == event_type,
                UsageEventModel.created_at >= period_start,
                UsageEventModel.created_at <= period_end,
            )
            .group_by(text("1"))
            .order_by(text("1"))
        )

        if organization_id is not None:
            query = query.where(UsageEventModel.organization_id == organization_id)

        result = await self.session.execute(query)
        rows = result.all()

        points = [
            UsageTimelinePoint(
                period=row.period.isoformat() if hasattr(row.period, "isoformat") else str(row.period),
                count=int(row.total_count),
            )
            for row in rows
        ]

        return UsageTimelineResponse(
            organization_id=organization_id,
            event_type=event_type,
            granularity=granularity,
            points=points,
        )

    async def list_events(
        self,
        *,
        organization_id: str | None = None,
        event_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[UsageEventResponse], int]:
        """List recent usage events with optional filters."""
        query = select(UsageEventModel)
        count_query = select(func.count()).select_from(UsageEventModel)

        if organization_id is not None:
            query = query.where(UsageEventModel.organization_id == organization_id)
            count_query = count_query.where(UsageEventModel.organization_id == organization_id)

        if event_type is not None:
            query = query.where(UsageEventModel.event_type == event_type)
            count_query = count_query.where(UsageEventModel.event_type == event_type)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(UsageEventModel.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(query)
        events = result.scalars().all()

        return [self._to_response(e) for e in events], total

    @staticmethod
    def _to_response(model: UsageEventModel) -> UsageEventResponse:
        return UsageEventResponse(
            id=model.id,
            organization_id=model.organization_id,
            event_type=model.event_type,
            resource_id=model.resource_id,
            count=model.count,
            metadata=model.metadata_,
            created_at=model.created_at.isoformat() if model.created_at else "",
        )
