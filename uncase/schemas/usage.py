"""API request/response schemas for usage metering."""

from __future__ import annotations

from pydantic import BaseModel, Field

EVENT_TYPES = [
    "seed_created",
    "conversation_generated",
    "evaluation_run",
    "sandbox_launched",
    "gateway_call",
    "plugin_installed",
    "knowledge_uploaded",
]


class UsageEventRecord(BaseModel):
    """Internal schema for recording a usage event."""

    organization_id: str | None = None
    event_type: str = Field(..., description="One of the supported event types")
    resource_id: str | None = None
    count: int = Field(default=1, ge=1)
    metadata: dict[str, object] | None = None
    ip_address: str | None = None


class UsageEventResponse(BaseModel):
    """A single usage event returned by the API."""

    id: str
    organization_id: str | None
    event_type: str
    resource_id: str | None
    count: int
    metadata: dict[str, object] | None
    created_at: str

    model_config = {"from_attributes": True}


class UsageSummaryItem(BaseModel):
    """Aggregated count for a single event type."""

    event_type: str
    total_count: int
    event_count: int = Field(description="Number of individual events (rows)")


class UsageSummaryResponse(BaseModel):
    """Aggregated usage summary for an organization."""

    organization_id: str | None
    period_start: str
    period_end: str
    items: list[UsageSummaryItem]
    total_events: int


class UsageTimelinePoint(BaseModel):
    """A single data point in a time-series."""

    period: str = Field(description="ISO date or datetime for the bucket")
    count: int


class UsageTimelineResponse(BaseModel):
    """Time-series usage data for charting."""

    organization_id: str | None
    event_type: str
    granularity: str
    points: list[UsageTimelinePoint]
