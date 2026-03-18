"""User management Pydantic schemas for request/response."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic needs runtime access

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 chars)")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")


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


class MembershipInfo(BaseModel):
    """Schema for org membership info."""

    organization_id: str
    org_name: str
    role: str


class UserMeResponse(BaseModel):
    """Schema for GET /me — current user with memberships."""

    user: UserResponse
    memberships: list[MembershipInfo]
