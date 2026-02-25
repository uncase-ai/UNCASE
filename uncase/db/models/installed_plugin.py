"""Installed plugin persistence model.

Tracks which plugins are installed per organization so that
installations survive server restarts.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class InstalledPluginModel(TimestampMixin, Base):
    """Database model for installed plugin records."""

    __tablename__ = "installed_plugins"

    # Plugin identity (from catalog)
    plugin_id: Mapped[str] = mapped_column(String(255), nullable=False)
    plugin_name: Mapped[str] = mapped_column(String(255), nullable=False)
    plugin_version: Mapped[str] = mapped_column(String(50), nullable=False)
    plugin_source: Mapped[str] = mapped_column(String(20), nullable=False, default="official")

    # Tools that were registered from this plugin
    tools_registered: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    domains: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Per-plugin configuration (future-proofing)
    config: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Multi-tenant
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("ix_installed_plugins_plugin_org", "plugin_id", "organization_id", unique=True),
        Index("ix_installed_plugins_org_active", "organization_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<InstalledPluginModel id={self.id} plugin_id={self.plugin_id}>"
