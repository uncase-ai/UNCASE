"""User management service — registration, authentication, memberships."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from uncase.db.models.user import OrgMembershipModel, UserModel
from uncase.exceptions import AuthenticationError, EmailAlreadyExistsError, UserNotFoundError
from uncase.log_config import get_logger
from uncase.utils.security import hash_api_key, verify_api_key

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class UserService:
    """Service for user registration, authentication, and membership queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register(self, email: str, password: str, display_name: str) -> UserModel:
        """Register a new user account.

        Args:
            email: User email address.
            password: Plain-text password (will be hashed with argon2id).
            display_name: User display name.

        Returns:
            The created UserModel.

        Raises:
            EmailAlreadyExistsError: If the email is already registered.
        """
        # Check for existing email
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise EmailAlreadyExistsError()

        user = UserModel(
            id=uuid.uuid4().hex,
            email=email.lower(),
            password_hash=hash_api_key(password),
            display_name=display_name,
        )
        self._session.add(user)
        await self._session.flush()

        logger.info("user_registered", user_id=user.id, email=user.email)
        return user

    async def authenticate(self, email: str, password: str) -> UserModel:
        """Authenticate a user with email and password.

        Args:
            email: User email address.
            password: Plain-text password.

        Returns:
            The authenticated UserModel.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Check account lockout
        if user.locked_until is not None and user.locked_until > datetime.now(UTC):
            remaining = int((user.locked_until - datetime.now(UTC)).total_seconds() / 60) + 1
            raise AuthenticationError(f"Account locked. Try again in {remaining} minutes")

        if not verify_api_key(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
                logger.warning("account_locked", user_id=user.id, attempts=user.failed_login_attempts)
            await self._session.flush()
            raise AuthenticationError("Invalid email or password")

        # Reset lockout on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.locked_until = None
        user.last_login_at = datetime.now(UTC)
        await self._session.flush()

        logger.info("user_authenticated", user_id=user.id)
        return user

    async def get_by_id(self, user_id: str) -> UserModel:
        """Fetch a user by ID.

        Args:
            user_id: User UUID hex string.

        Returns:
            The UserModel.

        Raises:
            UserNotFoundError: If user does not exist.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str) -> UserModel:
        """Fetch a user by email.

        Args:
            email: User email address.

        Returns:
            The UserModel.

        Raises:
            UserNotFoundError: If user does not exist.
        """
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        return user

    async def get_memberships(self, user_id: str) -> list[dict[str, str]]:
        """List org memberships for a user.

        Args:
            user_id: User UUID hex string.

        Returns:
            List of dicts with organization_id, org_name, and role.
        """
        stmt = (
            select(OrgMembershipModel)
            .where(OrgMembershipModel.user_id == user_id)
            .options(selectinload(OrgMembershipModel.organization))
        )
        result = await self._session.execute(stmt)
        memberships = result.scalars().all()

        return [
            {
                "organization_id": m.organization_id,
                "org_name": m.organization.name if m.organization else "",
                "role": m.role,
            }
            for m in memberships
        ]

    async def create_membership(self, user_id: str, organization_id: str, role: str = "member") -> OrgMembershipModel:
        """Create an org membership for a user.

        Args:
            user_id: User UUID hex string.
            organization_id: Organization UUID hex string.
            role: Membership role (owner, admin, member, viewer).

        Returns:
            The created OrgMembershipModel.
        """
        membership = OrgMembershipModel(
            id=uuid.uuid4().hex,
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )
        self._session.add(membership)
        await self._session.flush()

        logger.info(
            "membership_created",
            user_id=user_id,
            org_id=organization_id,
            role=role,
        )
        return membership

    async def get_org_members(self, organization_id: str) -> list[dict[str, str]]:
        """List all members of an organization with their user details.

        Args:
            organization_id: Organization UUID hex string.

        Returns:
            List of dicts with user_id, email, display_name, role, and created_at.
        """
        stmt = (
            select(OrgMembershipModel)
            .where(OrgMembershipModel.organization_id == organization_id)
            .options(selectinload(OrgMembershipModel.user))
        )
        result = await self._session.execute(stmt)
        memberships = result.scalars().all()

        return [
            {
                "user_id": m.user_id,
                "email": m.user.email if m.user else "",
                "display_name": m.user.display_name if m.user else "",
                "role": m.role,
                "joined_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in memberships
        ]
