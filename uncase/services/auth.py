"""Authentication service — JWT token management and verification."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import structlog
from sqlalchemy import select

from uncase.db.models.organization import APIKeyModel, OrganizationModel
from uncase.exceptions import AuthenticationError, UserNotFoundError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Default token lifetimes
ACCESS_TOKEN_LIFETIME = timedelta(hours=1)
REFRESH_TOKEN_LIFETIME = timedelta(days=30)


def _create_jwt(
    payload: dict[str, Any],
    secret: str,
    expires_delta: timedelta,
) -> str:
    """Create a signed JWT token using PyJWT (HS256).

    Args:
        payload: Token payload data.
        secret: Signing secret key.
        expires_delta: Token expiration duration.

    Returns:
        Encoded JWT string.
    """
    import jwt

    now = datetime.now(UTC)
    token_payload = {
        **payload,
        "iat": now,
        "exp": now + expires_delta,
        "jti": uuid.uuid4().hex,
    }

    return jwt.encode(token_payload, secret, algorithm="HS256")


def _decode_jwt(token: str, secret: str) -> dict[str, Any]:
    """Decode and verify a JWT token using PyJWT (HS256).

    Args:
        token: Encoded JWT string.
        secret: Signing secret key.

    Returns:
        Decoded token payload.

    Raises:
        AuthenticationError: If the token is invalid or expired.
    """
    import jwt

    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(f"Invalid token: {exc}") from exc


class AuthService:
    """JWT authentication and token management service.

    Supports login via API key, returning JWT access + refresh tokens.
    Tokens carry org_id, scopes, and role information.
    """

    def __init__(self, session: AsyncSession, secret: str) -> None:
        self._session = session
        self._secret = secret

    async def login_with_password(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate with email/password and return JWT tokens.

        Args:
            email: User email address.
            password: Plain-text password.

        Returns:
            Dict with ``access_token``, ``refresh_token``, ``token_type``, and ``expires_in``.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        from uncase.services.user import UserService

        user_service = UserService(self._session)
        user = await user_service.authenticate(email, password)
        memberships = await user_service.get_memberships(user.id)

        if not memberships:
            raise AuthenticationError("User has no organization memberships")

        first_org_id = memberships[0]["organization_id"]
        first_role = memberships[0]["role"]

        token_payload = {
            "sub": user.id,
            "type": "user",
            "org_id": first_org_id,
            "role": first_role,
            "email": user.email,
            "display_name": user.display_name,
        }

        access_token = _create_jwt(token_payload, self._secret, ACCESS_TOKEN_LIFETIME)
        refresh_token = _create_jwt(
            {"sub": user.id, "type": "refresh", "token_type": "user", "org_id": first_org_id},
            self._secret,
            REFRESH_TOKEN_LIFETIME,
        )

        logger.info("jwt_user_login_success", user_id=user.id, role=first_role)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            "role": first_role,
            "org_id": first_org_id,
        }

    async def login_with_api_key(self, api_key: str) -> dict[str, Any]:
        """Authenticate with an API key and return JWT tokens.

        Args:
            api_key: Full API key string.

        Returns:
            Dict with ``access_token``, ``refresh_token``, ``token_type``, and ``expires_in``.

        Raises:
            AuthenticationError: If the API key is invalid.
        """
        from uncase.services.organization import OrganizationService

        org_service = OrganizationService(self._session)
        org = await org_service.verify_and_get_org(api_key)
        key_model = org_service.last_verified_key

        if key_model is None:
            raise AuthenticationError("API key verification failed")

        scopes = key_model.scopes or "read"
        role = "admin" if "admin" in scopes else ("developer" if "write" in scopes else "viewer")

        token_payload = {
            "sub": org.id,
            "org_id": org.id,
            "org_name": org.name,
            "key_id": key_model.key_id,
            "scopes": scopes,
            "role": role,
        }

        access_token = _create_jwt(token_payload, self._secret, ACCESS_TOKEN_LIFETIME)
        refresh_token = _create_jwt(
            {"sub": org.id, "org_id": org.id, "type": "refresh"},
            self._secret,
            REFRESH_TOKEN_LIFETIME,
        )

        logger.info("jwt_login_success", org_id=org.id, role=role)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            "role": role,
            "org_id": org.id,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: Encoded refresh JWT.

        Returns:
            New access and refresh token pair.

        Raises:
            AuthenticationError: If the refresh token is invalid.
        """
        payload = _decode_jwt(refresh_token, self._secret)

        if payload.get("type") != "refresh":
            raise AuthenticationError("Not a refresh token")

        org_id = payload.get("org_id")
        if not org_id:
            raise AuthenticationError("Invalid refresh token: missing org_id")

        # Handle user-type refresh tokens
        if payload.get("token_type") == "user":
            return await self._refresh_user_token(payload)

        # Verify org still exists and is active
        stmt = select(OrganizationModel).where(
            OrganizationModel.id == org_id,
            OrganizationModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        org = result.scalar_one_or_none()
        if org is None:
            raise AuthenticationError("Organization not found or deactivated")

        # Get the most recent active API key for scope info
        key_stmt = (
            select(APIKeyModel)
            .where(
                APIKeyModel.organization_id == org_id,
                APIKeyModel.is_active.is_(True),
            )
            .order_by(APIKeyModel.created_at.desc())
            .limit(1)
        )
        key_result = await self._session.execute(key_stmt)
        key_model = key_result.scalar_one_or_none()

        scopes = key_model.scopes if key_model else "read"
        role = "admin" if "admin" in scopes else ("developer" if "write" in scopes else "viewer")

        new_payload = {
            "sub": org.id,
            "org_id": org.id,
            "org_name": org.name,
            "scopes": scopes,
            "role": role,
        }

        new_access = _create_jwt(new_payload, self._secret, ACCESS_TOKEN_LIFETIME)
        new_refresh = _create_jwt(
            {"sub": org.id, "org_id": org.id, "type": "refresh"},
            self._secret,
            REFRESH_TOKEN_LIFETIME,
        )

        logger.info("jwt_refreshed", org_id=org.id)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            "role": role,
            "org_id": org.id,
        }

    async def _refresh_user_token(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Refresh a user-type token.

        Args:
            payload: Decoded refresh token payload.

        Returns:
            New token pair dict.

        Raises:
            AuthenticationError: If the user is not found or deactivated.
        """
        from uncase.services.user import UserService

        user_id = payload["sub"]
        org_id = payload.get("org_id", "")

        user_service = UserService(self._session)
        try:
            user = await user_service.get_by_id(user_id)
        except UserNotFoundError as exc:
            raise AuthenticationError("User not found or deactivated") from exc

        if not user.is_active:
            raise AuthenticationError("User account deactivated")

        memberships = await user_service.get_memberships(user.id)
        # Try to keep the same org, otherwise fall back to first
        current_role = "member"
        for m in memberships:
            if m["organization_id"] == org_id:
                current_role = m["role"]
                break
        else:
            if memberships:
                org_id = memberships[0]["organization_id"]
                current_role = memberships[0]["role"]

        new_access_payload = {
            "sub": user.id,
            "type": "user",
            "org_id": org_id,
            "role": current_role,
            "email": user.email,
            "display_name": user.display_name,
        }

        new_access = _create_jwt(new_access_payload, self._secret, ACCESS_TOKEN_LIFETIME)
        new_refresh = _create_jwt(
            {"sub": user.id, "type": "refresh", "token_type": "user", "org_id": org_id},
            self._secret,
            REFRESH_TOKEN_LIFETIME,
        )

        logger.info("jwt_user_refreshed", user_id=user.id)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            "role": current_role,
            "org_id": org_id,
        }

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode an access token.

        Args:
            token: Encoded JWT access token.

        Returns:
            Decoded payload with org_id, scopes, role.

        Raises:
            AuthenticationError: If the token is invalid or expired.
        """
        payload = _decode_jwt(token, self._secret)
        if payload.get("type") == "refresh":
            raise AuthenticationError("Cannot use refresh token for API access")
        return payload
