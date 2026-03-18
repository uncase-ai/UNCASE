"""Auth API — JWT authentication endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_current_user, get_db, get_settings
from uncase.config import UNCASESettings
from uncase.db.models.user import UserModel
from uncase.schemas.user import MembershipInfo, UserLoginRequest, UserMeResponse, UserRegisterRequest, UserResponse
from uncase.services.auth import AuthService
from uncase.services.user import UserService

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


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: UserRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> TokenResponse:
    """Register a new user account.

    Creates a user, auto-creates a personal organization, assigns the user as owner,
    and returns JWT tokens.
    """
    import re
    import uuid as _uuid

    from uncase.db.models.organization import OrganizationModel

    user_service = UserService(session)
    user = await user_service.register(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    # Auto-create a personal organization (inline to keep single transaction)
    org_name = f"{request.display_name}'s Org"
    slug = re.sub(r"[^a-z0-9]+", "-", org_name.lower().strip()).strip("-") or "org"
    org = OrganizationModel(id=_uuid.uuid4().hex, name=org_name, slug=f"{slug}-{_uuid.uuid4().hex[:6]}")
    session.add(org)
    await session.flush()

    # Create owner membership
    await user_service.create_membership(user.id, org.id, role="owner")
    await session.commit()

    # Mint JWT tokens
    auth_service = AuthService(session, settings.api_secret_key)
    result = await auth_service.login_with_password(request.email, request.password)
    return TokenResponse(**result)


@router.post("/login/password", response_model=TokenResponse)
async def login_password(
    request: UserLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> TokenResponse:
    """Authenticate with email and password and receive JWT tokens.

    Returns an access token (1h) and refresh token (30d).
    Use the access token in the Authorization header: ``Bearer <token>``.
    """
    auth_service = AuthService(session, settings.api_secret_key)
    result = await auth_service.login_with_password(request.email, request.password)
    return TokenResponse(**result)


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserMeResponse:
    """Return the current authenticated user with their org memberships.

    Requires a valid Bearer token in the Authorization header.
    """
    user_service = UserService(session)
    memberships_raw = await user_service.get_memberships(user.id)

    return UserMeResponse(
        user=UserResponse.model_validate(user),
        memberships=[MembershipInfo(**m) for m in memberships_raw],
    )
