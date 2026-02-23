"""FastAPI dependency injection functions."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.config import UNCASESettings
from uncase.db.engine import get_async_session
from uncase.db.models.organization import OrganizationModel
from uncase.exceptions import AuthenticationError, AuthorizationError
from uncase.services.organization import OrganizationService

_settings: UNCASESettings | None = None


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
