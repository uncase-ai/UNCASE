"""Cost tracking API — LLM API spend visibility per org and job."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.db.models.organization import OrganizationModel
from uncase.services.cost_tracking import CostTrackingService

router = APIRouter(prefix="/api/v1/costs", tags=["costs"])


@router.get("/summary")
async def get_cost_summary(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    period_days: Annotated[int, Query(ge=1, le=365, description="Lookback period in days")] = 30,
) -> dict[str, Any]:
    """Get LLM API cost summary for the organization.

    Returns total spend, breakdown by provider and event type,
    token counts, and event counts for the specified period.
    """
    service = CostTrackingService(session)
    org_id = org.id if org else "global"
    return await service.get_org_cost_summary(org_id, period_days=period_days)


@router.get("/job/{job_id}")
async def get_job_cost(
    job_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get total LLM API cost for a specific job."""
    service = CostTrackingService(session)
    return await service.get_job_cost(job_id)


@router.get("/daily")
async def get_daily_costs(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    days: Annotated[int, Query(ge=1, le=365, description="Number of days")] = 30,
) -> list[dict[str, Any]]:
    """Get daily cost breakdown for charting."""
    service = CostTrackingService(session)
    org_id = org.id if org else None
    return await service.get_daily_costs(organization_id=org_id, days=days)
