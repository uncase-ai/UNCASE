"""Usage metering API endpoints.

Phase 1: Read-only dashboard endpoints. Events are recorded by other
routers/services via ``UsageMeteringService.record()``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.usage import (
    EVENT_TYPES,
    UsageSummaryResponse,
    UsageTimelineResponse,
)
from uncase.services.usage import UsageMeteringService

router = APIRouter(prefix="/api/v1/usage", tags=["usage"])


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    period_start: str | None = Query(default=None, description="ISO datetime"),
    period_end: str | None = Query(default=None, description="ISO datetime"),
) -> UsageSummaryResponse:
    """Get aggregated usage counts by event type for a period."""
    service = UsageMeteringService(session)

    start = datetime.fromisoformat(period_start) if period_start else None
    end = datetime.fromisoformat(period_end) if period_end else None

    org_id = org.id if org else None
    return await service.get_summary(
        organization_id=org_id,
        period_start=start,
        period_end=end,
    )


@router.get("/timeline", response_model=UsageTimelineResponse)
async def get_usage_timeline(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    event_type: str = Query(..., description=f"One of: {', '.join(EVENT_TYPES)}"),
    granularity: str = Query(default="day", description="hour, day, week, month"),
    period_start: str | None = Query(default=None),
    period_end: str | None = Query(default=None),
) -> UsageTimelineResponse:
    """Get time-series usage data for a specific event type."""
    service = UsageMeteringService(session)

    start = datetime.fromisoformat(period_start) if period_start else None
    end = datetime.fromisoformat(period_end) if period_end else None

    org_id = org.id if org else None
    return await service.get_timeline(
        event_type=event_type,
        organization_id=org_id,
        granularity=granularity,
        period_start=start,
        period_end=end,
    )


@router.get("/events", response_model=dict)
async def list_usage_events(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    event_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> dict[str, object]:
    """List recent usage events with pagination."""
    service = UsageMeteringService(session)
    org_id = org.id if org else None
    events, total = await service.list_events(
        organization_id=org_id,
        event_type=event_type,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [e.model_dump() for e in events],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/event-types", response_model=list[str])
async def list_event_types() -> list[str]:
    """Return the list of supported usage event types."""
    return EVENT_TYPES
