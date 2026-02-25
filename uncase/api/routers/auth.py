"""Auth API — JWT authentication endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

logger = structlog.get_logger(__name__)


class LoginRequest(BaseModel):
    """Login with an API key to receive JWT tokens."""

    api_key: str = Field(..., description="Full API key string")


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in seconds")
    role: str = Field(..., description="User role: admin, developer, or viewer")
    org_id: str = Field(..., description="Organization ID")


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class TokenVerifyResponse(BaseModel):
    """Token verification result."""

    valid: bool = Field(..., description="Whether the token is valid")
    org_id: str | None = Field(default=None, description="Organization ID from token")
    role: str | None = Field(default=None, description="User role from token")
    scopes: str | None = Field(default=None, description="Scopes from token")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> TokenResponse:
    """Authenticate with an API key and receive JWT tokens.

    Returns an access token (1h) and refresh token (30d).
    Use the access token in the Authorization header: ``Bearer <token>``.
    """
    service = AuthService(session, settings.api_secret_key)
    result = await service.login_with_api_key(request.api_key)
    return TokenResponse(**result)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> TokenResponse:
    """Refresh an access token using a refresh token.

    Returns a new access + refresh token pair. The old refresh token is invalidated.
    """
    service = AuthService(session, settings.api_secret_key)
    result = await service.refresh_access_token(request.refresh_token)
    return TokenResponse(**result)


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> TokenVerifyResponse:
    """Verify an access token from the Authorization header.

    Expects: ``Authorization: Bearer <token>``
    """
    if not authorization or not authorization.startswith("Bearer "):
        return TokenVerifyResponse(valid=False)

    token = authorization[7:]  # Strip "Bearer "

    try:
        from uncase.services.auth import _decode_jwt

        payload = _decode_jwt(token, settings.api_secret_key)
        return TokenVerifyResponse(
            valid=True,
            org_id=payload.get("org_id"),
            role=payload.get("role"),
            scopes=payload.get("scopes"),
        )
    except Exception:
        return TokenVerifyResponse(valid=False)
