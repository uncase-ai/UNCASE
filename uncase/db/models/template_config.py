"""Template configuration persistence model.

Stores per-organization template preferences: default template,
tool call mode, system prompt, and export format.
"""

from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class TemplateConfigModel(TimestampMixin, Base):
    """Database model for per-org template preferences."""

    __tablename__ = "template_configs"

    # Preferences
    default_template: Mapped[str] = mapped_column(String(100), nullable=False, default="chatml")
    default_tool_call_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    default_system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_templates: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    export_format: Mapped[str] = mapped_column(String(50), nullable=False, default="txt")

    # Multi-tenant (one config per org)
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    __table_args__ = (Index("ix_template_configs_org", "organization_id", unique=True),)

    def __repr__(self) -> str:
        return f"<TemplateConfigModel id={self.id} org={self.organization_id}>"
