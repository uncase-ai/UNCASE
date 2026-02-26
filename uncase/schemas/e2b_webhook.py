"""Schemas for inbound E2B sandbox webhook notifications."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class E2BEventType(StrEnum):
    """Lifecycle events that E2B can notify us about."""

    SANDBOX_STARTED = "sandbox.started"
    SANDBOX_COMPLETED = "sandbox.completed"
    SANDBOX_ERROR = "sandbox.error"
    SANDBOX_EXPIRED = "sandbox.expired"


class E2BWebhookPayload(BaseModel):
    """Inbound payload from E2B or internal sandbox orchestrator."""

    sandbox_id: str = Field(..., description="E2B sandbox identifier")
    template_id: str | None = Field(default=None, description="E2B template used to boot the sandbox")
    domain: str | None = Field(default=None, description="Industry domain (e.g. automotive.sales)")
    organization_id: str | None = Field(default=None, description="Owning organization if applicable")
    event_type: E2BEventType = Field(..., description="Lifecycle event type")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event timestamp")
    sandbox_url: str | None = Field(default=None, description="URL to access the sandbox")
    api_url: str | None = Field(default=None, description="API URL inside the sandbox")
    ttl_minutes: int | None = Field(default=None, ge=1, description="Sandbox time-to-live")
    metadata: dict[str, object] = Field(default_factory=dict, description="Additional context")


class E2BStartPayload(BaseModel):
    """Payload specific to demo/sandbox start events."""

    sandbox_id: str = Field(..., description="E2B sandbox identifier")
    template_id: str | None = Field(default=None, description="E2B template used")
    domain: str | None = Field(default=None, description="Industry domain (e.g. automotive.sales)")
    organization_id: str | None = Field(default=None, description="Owning organization")
    sandbox_url: str | None = Field(default=None, description="URL to access the sandbox")
    api_url: str | None = Field(default=None, description="API URL inside the sandbox")
    ttl_minutes: int | None = Field(default=None, ge=1, description="Sandbox time-to-live in minutes")
    preloaded_seeds: int = Field(default=0, ge=0, description="Number of pre-loaded seeds")
    language: str = Field(default="es", description="Sandbox language (ISO 639-1)")
    metadata: dict[str, object] = Field(default_factory=dict, description="Additional context")


class E2BCompletePayload(BaseModel):
    """Payload specific to sandbox completion events."""

    sandbox_id: str = Field(..., description="E2B sandbox identifier")
    domain: str | None = Field(default=None, description="Industry domain")
    organization_id: str | None = Field(default=None, description="Owning organization")
    conversations_generated: int = Field(default=0, ge=0, description="Total conversations generated")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Total sandbox runtime")
    metadata: dict[str, object] = Field(default_factory=dict)


class E2BErrorPayload(BaseModel):
    """Payload specific to sandbox error events."""

    sandbox_id: str = Field(..., description="E2B sandbox identifier")
    domain: str | None = Field(default=None, description="Industry domain")
    organization_id: str | None = Field(default=None, description="Owning organization")
    error: str = Field(..., max_length=2000, description="Error message")
    error_code: str | None = Field(default=None, description="Machine-readable error code")
    metadata: dict[str, object] = Field(default_factory=dict)


class E2BWebhookResponse(BaseModel):
    """Acknowledgement returned to the caller."""

    received: bool = Field(default=True, description="Whether the event was accepted")
    event_id: str = Field(..., description="Internal event ID for tracking")
    event_type: str = Field(..., description="Echo of the event type received")


class E2BWebhookEventRecord(BaseModel):
    """Stored record of an inbound E2B webhook event."""

    event_id: str = Field(..., description="Internal event ID")
    event_type: E2BEventType = Field(..., description="Lifecycle event type")
    sandbox_id: str = Field(..., description="E2B sandbox identifier")
    domain: str | None = None
    organization_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
