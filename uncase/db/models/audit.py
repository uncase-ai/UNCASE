"""Audit log persistence model.

Records who accessed what data, when, and from where. Separate from
application logs — this is the compliance audit trail.
"""

from __future__ import annotations

from sqlalchemy import JSON, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class AuditLogModel(Base, TimestampMixin):
    """Immutable audit log entry for compliance tracking.

    Every sensitive operation (create, update, delete, access) is recorded
    here with the actor, resource, action, and context.
    """

    __tablename__ = "audit_logs"

    # Action
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Action: create, read, update, delete, login, export, pipeline_run"
    )
    resource_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Resource type: seed, conversation, job, organization, api_key"
    )
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="Resource identifier")

    # Actor
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user", server_default="user", comment="Actor type: user, system, api_key"
    )
    actor_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="Actor identifier (org_id, key_id, or 'system')"
    )
    organization_id: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="Organization context")

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="Client IP address")
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="Client user agent")
    endpoint: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="API endpoint path")
    http_method: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="HTTP method")

    # Details
    detail: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Human-readable description")
    extra_data: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True, comment="Additional structured metadata"
    )

    # Outcome
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        server_default="success",
        comment="Outcome: success, denied, error",
    )

    __table_args__ = (
        Index("ix_audit_action", "action"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_actor", "actor_id"),
        Index("ix_audit_org", "organization_id"),
        Index("ix_audit_created", "created_at"),
    )
