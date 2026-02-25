"""Webhook subscription and delivery API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

WEBHOOK_EVENTS = [
    "seed_created",
    "conversation_generated",
    "evaluation_completed",
    "knowledge_uploaded",
    "sandbox_completed",
    "gateway_call",
    "test.webhook",
]


class WebhookSubscriptionCreate(BaseModel):
    """Create a new webhook subscription."""

    url: str = Field(..., min_length=1, max_length=2048, description="HTTPS endpoint to receive webhooks")
    events: list[str] = Field(..., min_length=1, description="Event types to subscribe to")
    description: str | None = Field(default=None, max_length=512)
    is_active: bool = Field(default=True)


class WebhookSubscriptionUpdate(BaseModel):
    """Update a webhook subscription."""

    url: str | None = Field(default=None, max_length=2048)
    events: list[str] | None = None
    description: str | None = None
    is_active: bool | None = None


class WebhookSubscriptionResponse(BaseModel):
    """Webhook subscription details (without secret)."""

    id: str
    organization_id: str
    url: str
    events: list[str]
    description: str | None
    is_active: bool
    last_triggered_at: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class WebhookSubscriptionCreatedResponse(WebhookSubscriptionResponse):
    """Full subscription including secret (only returned on creation)."""

    secret: str = Field(description="HMAC-SHA256 secret for verifying webhook signatures")


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery attempt."""

    id: str
    subscription_id: str
    event_type: str
    status: str
    http_status_code: int | None
    error_message: str | None
    attempts: int
    next_retry_at: str | None
    created_at: str
    delivered_at: str | None

    model_config = {"from_attributes": True}


class WebhookEventPayload(BaseModel):
    """Standard webhook event payload structure."""

    id: str = Field(description="Unique event ID")
    event_type: str
    timestamp: str
    organization_id: str
    resource_id: str | None = None
    resource_type: str | None = None
    data: dict[str, object] = Field(default_factory=dict)
