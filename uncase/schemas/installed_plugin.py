"""Pydantic schemas for installed plugin endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InstalledPluginResponse(BaseModel):
    """Response for a persisted plugin installation."""

    id: str
    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_source: str
    tools_registered: list[str]
    domains: list[str]
    config: dict[str, object] | None = None
    is_active: bool
    organization_id: str | None
    created_at: str
    updated_at: str


class InstalledPluginListResponse(BaseModel):
    """List of installed plugins."""

    items: list[InstalledPluginResponse]
    total: int


class PluginConfigUpdateRequest(BaseModel):
    """Request body for updating per-plugin configuration."""

    config: dict[str, object] = Field(default_factory=dict, description="Plugin configuration overrides.")
    is_active: bool | None = Field(default=None, description="Toggle plugin active state.")
