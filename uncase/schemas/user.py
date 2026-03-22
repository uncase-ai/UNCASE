"""User management Pydantic schemas for request/response."""

from __future__ import annotations

import re
from datetime import datetime  # noqa: TC003 — Pydantic needs runtime access

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 chars)")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Enforce OWASP password complexity requirements."""
        errors: list[str] = []
        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", v):
            errors.append("at least one special character")
        if errors:
            msg = "Password must contain: " + ", ".join(errors)
            raise ValueError(msg)
        return v


class UserLoginRequest(BaseModel):
    """Schema for password-based login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user responses."""

    id: str
    email: str
    display_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


VALID_ROLES = {"owner", "admin", "member", "viewer"}


class MembershipInfo(BaseModel):
    """Schema for org membership info."""

    organization_id: str
    org_name: str
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Enforce that role is one of the allowed RBAC roles."""
        if v not in VALID_ROLES:
            msg = f"Invalid role '{v}'. Must be one of: {', '.join(sorted(VALID_ROLES))}"
            raise ValueError(msg)
        return v


class UserMeResponse(BaseModel):
    """Schema for GET /me — current user with memberships."""

    user: UserResponse
    memberships: list[MembershipInfo]


class OrgDetailResponse(BaseModel):
    """Full organization details with user's role."""

    id: str
    name: str
    slug: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: str = Field(..., description="Current user's role in this organization")
    member_count: int = Field(..., description="Total number of members")


class OrgMemberResponse(BaseModel):
    """Organization member info."""

    user_id: str
    email: str
    display_name: str
    role: str
    joined_at: str


class OrgMembersListResponse(BaseModel):
    """Response for listing org members."""

    members: list[OrgMemberResponse]
    total: int
