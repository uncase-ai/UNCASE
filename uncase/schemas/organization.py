"""Organization and API key Pydantic schemas for request/response."""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    slug: str | None = Field(default=None, max_length=255, description="URL-friendly slug (auto-generated if omitted)")
    description: str | None = Field(default=None, description="Organization description")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", v):
            msg = "Slug must be lowercase alphanumeric with hyphens, not starting/ending with hyphen"
            raise ValueError(msg)
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class OrganizationResponse(BaseModel):
    """Schema for organization responses."""

    id: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(..., min_length=1, max_length=255, description="Key display name")
    scopes: str = Field(default="read", description="Comma-separated scopes: read, write, admin")

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, v: str) -> str:
        valid_scopes = {"read", "write", "admin"}
        scopes = {s.strip() for s in v.split(",")}
        invalid = scopes - valid_scopes
        if invalid:
            msg = f"Invalid scopes: {invalid}. Valid: {valid_scopes}"
            raise ValueError(msg)
        return ",".join(sorted(scopes))


class APIKeyResponse(BaseModel):
    """Schema for API key list/detail responses (never includes the raw key)."""

    id: str
    key_id: str
    key_prefix: str
    name: str
    scopes: str
    is_active: bool
    expires_at: datetime | None
    last_used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class APIKeyCreatedResponse(BaseModel):
    """Schema returned exactly once when a key is created — includes the plain key."""

    id: str
    key_id: str
    key_prefix: str
    name: str
    scopes: str
    plain_key: str = Field(..., description="Full API key — shown only once, store securely")
    created_at: datetime


class APIKeyAuditLogResponse(BaseModel):
    """Schema for API key audit log entries."""

    id: str
    action: str
    details: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
