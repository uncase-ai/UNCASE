"""Custom tool definition database model.

Stores user-registered tools that are persisted across restarts.
Built-in tools from _builtin/ remain code-only; this table holds
custom tools created via the API.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class CustomToolModel(TimestampMixin, Base):
    """Database model for custom tool definitions."""

    __tablename__ = "custom_tools"

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Schemas
    input_schema: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    output_schema: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    # Classification
    domains: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    requires_auth: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    execution_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="simulated")
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Multi-tenant
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("ix_custom_tools_name_org", "name", "organization_id", unique=True),
        Index("ix_custom_tools_org_active", "organization_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<CustomToolModel id={self.id} name={self.name}>"
