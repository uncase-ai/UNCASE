"""Usage metering event model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base


class UsageEventModel(Base):
    """Tracks platform usage events for metering and analytics.

    Each row represents a single usage event (or a batched count).
    Events are non-blocking and informational in Phase 1 (no rate limiting).
    """

    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="seed_created, conversation_generated, evaluation_run, "
        "sandbox_launched, gateway_call, plugin_installed, knowledge_uploaded",
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="ID of the resource involved (seed_id, conversation_id, etc.)",
    )
    count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        comment="Event count (allows batched recording, e.g. 5 conversations generated at once)",
    )
    metadata_: Mapped[dict[str, object] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        comment="Additional context: domain, model, provider, duration_ms, etc.",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_usage_events_org_type", "organization_id", "event_type"),
        Index("ix_usage_events_created", "created_at"),
        Index("ix_usage_events_type_created", "event_type", "created_at"),
    )
