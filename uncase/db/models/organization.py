"""Organization and API key database models."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — SQLAlchemy needs runtime access for Mapped annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uncase.db.base import Base, TimestampMixin


class OrganizationModel(TimestampMixin, Base):
    """Database model for organizations."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    api_keys: Mapped[list[APIKeyModel]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    seeds: Mapped[list[SeedModel]] = relationship(back_populates="organization")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return f"<OrganizationModel id={self.id} name={self.name}>"


class APIKeyModel(TimestampMixin, Base):
    """Database model for API keys."""

    __tablename__ = "api_keys"

    # Key identity
    key_id: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    key_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)

    # Metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scopes: Mapped[str] = mapped_column(String(255), nullable=False, default="read")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Organization FK
    organization_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    organization: Mapped[OrganizationModel] = relationship(back_populates="api_keys")
    audit_logs: Mapped[list[APIKeyAuditLogModel]] = relationship(back_populates="api_key", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_api_keys_org_active", "organization_id", "is_active"),)

    def __repr__(self) -> str:
        return f"<APIKeyModel key_id={self.key_id} org={self.organization_id}>"


class APIKeyAuditLogModel(TimestampMixin, Base):
    """Audit log for API key operations."""

    __tablename__ = "api_key_audit_logs"

    # Event info
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # API key FK
    api_key_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    api_key: Mapped[APIKeyModel] = relationship(back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<APIKeyAuditLogModel action={self.action} key={self.api_key_id}>"
