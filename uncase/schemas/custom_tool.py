"""Pydantic schemas for custom tool CRUD endpoints."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CustomToolCreateRequest(BaseModel):
    """Request body for creating a custom tool."""

    name: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$", description="Unique snake_case tool identifier.")
    description: str = Field(..., min_length=10, description="Human-readable description.")
    input_schema: dict[str, Any] = Field(..., description="JSON Schema for tool input.")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for tool output.")
    domains: list[str] = Field(default_factory=list, description="Applicable domain namespaces.")
    category: str = Field(default="", description="Logical category for grouping.")
    requires_auth: bool = Field(default=False, description="Whether tool requires authentication.")
    execution_mode: Literal["simulated", "live", "mock"] = Field(default="simulated")
    version: str = Field(default="1.0", description="Semantic version.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary extra metadata.")


class CustomToolUpdateRequest(BaseModel):
    """Request body for updating a custom tool (partial)."""

    description: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    domains: list[str] | None = None
    category: str | None = None
    requires_auth: bool | None = None
    execution_mode: Literal["simulated", "live", "mock"] | None = None
    version: str | None = None
    metadata: dict[str, Any] | None = None
    is_active: bool | None = None


class CustomToolResponse(BaseModel):
    """Response for a persisted custom tool."""

    id: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    domains: list[str]
    category: str
    requires_auth: bool
    execution_mode: str
    version: str
    metadata: dict[str, Any] | None
    is_active: bool
    is_builtin: bool = Field(default=False, description="Whether this is a built-in tool.")
    organization_id: str | None
    created_at: str
    updated_at: str


class CustomToolListResponse(BaseModel):
    """Paginated list of custom tools."""

    items: list[CustomToolResponse]
    total: int
    page: int
    page_size: int
