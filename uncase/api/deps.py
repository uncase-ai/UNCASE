"""FastAPI dependency injection functions."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.config import UNCASESettings
from uncase.db.engine import get_async_session
from uncase.db.models.organization import OrganizationModel
from uncase.db.models.user import UserModel
from uncase.exceptions import AuthenticationError, AuthorizationError, UserNotFoundError
from uncase.log_config import get_logger
from uncase.services.auth import AuthService
from uncase.services.organization import OrganizationService
from uncase.services.user import UserService

_settings: UNCASESettings | None = None

logger = get_logger(__name__)


def get_settings() -> UNCASESettings:
    """Return cached application settings."""
    global _settings
    if _settings is None:
        _settings = UNCASESettings()
    return _settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async for session in get_async_session():
        yield session


async def get_current_org(
    x_api_key: Annotated[str, Header()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationModel:
    """Authenticate the request via X-API-Key header.

    Returns the organization associated with the API key.

    Raises:
        AuthenticationError: If key is missing, invalid, or revoked.
    """
    if not x_api_key:
        raise AuthenticationError("X-API-Key header is required")

    service = OrganizationService(session)
    return await service.verify_and_get_org(x_api_key)


async def get_optional_org(
    session: Annotated[AsyncSession, Depends(get_db)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> OrganizationModel | None:
    """Optionally authenticate the request via X-API-Key header.

    Returns the organization if a valid API key is provided, or None
    if no key is present. This allows endpoints to work in both
    authenticated and unauthenticated modes during the Phase 0 → 1
    transition.

    Raises:
        AuthenticationError: Only if a key IS provided but is invalid/revoked.
    """
    if not x_api_key:
        return None

    service = OrganizationService(session)
    try:
        return await service.verify_and_get_org(x_api_key)
    except AuthenticationError:
        logger.warning("optional_auth_failed", reason="invalid_key")
        raise


def require_scopes(*required: str) -> Callable[..., object]:
    """Factory that returns a dependency checking that the API key has required scopes.

    Usage:
        @router.post("/seeds", dependencies=[Depends(require_scopes("write"))])
    """

    async def _check_scopes(
        x_api_key: Annotated[str, Header()],
        session: Annotated[AsyncSession, Depends(get_db)],
    ) -> OrganizationModel:
        if not x_api_key:
            raise AuthenticationError("X-API-Key header is required")

        service = OrganizationService(session)
        org = await service.verify_and_get_org(x_api_key)

        # verify_and_get_org already validated the key; now check scopes
        key_model = service.last_verified_key
        if key_model is None:
            raise AuthenticationError("API key not found")

        key_scopes = {s.strip() for s in key_model.scopes.split(",")}

        # admin has all permissions
        if "admin" not in key_scopes:
            for scope in required:
                if scope not in key_scopes:
                    raise AuthorizationError(f"Missing required scope: {scope}")

        return org

    return _check_scopes


# -- Role hierarchy for user-based auth --

_ROLE_HIERARCHY: dict[str, int] = {
    "viewer": 0,
    "member": 1,
    "admin": 2,
    "owner": 3,
}


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> UserModel:
    """Authenticate the request via Bearer token and return the current user.

    Supports both user-type and api_key-type JWT tokens. For api_key tokens,
    the org is resolved but a synthetic user lookup is not performed -- the
    sub claim is used to fetch the user.

    Raises:
        AuthenticationError: If token is missing, invalid, or user not found.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Authorization header with Bearer token is required")

    token = authorization[7:]  # Strip "Bearer "

    auth_service = AuthService(session, settings.api_secret_key)
    payload = auth_service.verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token: missing subject")

    # Fetch the user from DB (works for both user-type and api_key-type tokens)
    user_service = UserService(session)
    try:
        return await user_service.get_by_id(user_id)
    except UserNotFoundError as exc:
        raise AuthenticationError("User not found or deactivated") from exc


def require_role(*roles: str) -> Callable[..., object]:
    """Factory that returns a dependency checking user's membership role for the current org.

    Role hierarchy: owner > admin > member > viewer.
    If the user has a role at or above the minimum required role, access is granted.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    # Determine the minimum required level
    min_level = max(_ROLE_HIERARCHY.get(r, 0) for r in roles)

    async def _check_role(
        session: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[UNCASESettings, Depends(get_settings)],
        authorization: Annotated[str | None, Header()] = None,
    ) -> UserModel:
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationError("Authorization header with Bearer token is required")

        token = authorization[7:]
        auth_service = AuthService(session, settings.api_secret_key)
        payload = auth_service.verify_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token: missing subject")

        user_service = UserService(session)
        try:
            user = await user_service.get_by_id(user_id)
        except UserNotFoundError as exc:
            raise AuthenticationError("User not found") from exc

        # Check role from token payload
        user_role = payload.get("role", "member")
        user_level = _ROLE_HIERARCHY.get(user_role, 0)

        if user_level < min_level:
            raise AuthorizationError(f"Requires role: {', '.join(roles)}. Current role: {user_role}")

        return user

    return _check_role
