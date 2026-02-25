"""Pydantic schemas for template configuration endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TemplateConfigResponse(BaseModel):
    """Response for per-org template preferences."""

    id: str
    organization_id: str | None
    default_template: str
    default_tool_call_mode: str
    default_system_prompt: str | None
    preferred_templates: list[str]
    export_format: str
    created_at: str
    updated_at: str


class TemplateConfigUpdateRequest(BaseModel):
    """Request body for updating template preferences."""

    default_template: str | None = Field(default=None, description="Default template name.")
    default_tool_call_mode: Literal["none", "inline"] | None = Field(
        default=None, description="Default tool call rendering mode."
    )
    default_system_prompt: str | None = Field(default=None, description="Default system prompt.")
    preferred_templates: list[str] | None = Field(default=None, description="Ordered list of preferred templates.")
    export_format: str | None = Field(default=None, description="Default export format (txt, jsonl, parquet).")
