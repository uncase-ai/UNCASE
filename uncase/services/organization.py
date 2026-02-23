"""Organization and API key management service."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from uncase.db.models.organization import APIKeyAuditLogModel, APIKeyModel, OrganizationModel
from uncase.exceptions import (
    APIKeyNotFoundError,
    APIKeyRevokedError,
    AuthenticationError,
    DuplicateError,
    OrganizationNotFoundError,
)
from uncase.logging import get_logger
from uncase.schemas.organization import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from uncase.utils.security import generate_api_key, parse_api_key, verify_api_key

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


def _slugify(name: str) -> str:
    """Generate a URL-friendly slug from a name."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "org"


class OrganizationService:
    """Service for organization and API key management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.last_verified_key: APIKeyModel | None = None

    # -- Organizations --

    async def create_organization(self, data: OrganizationCreate) -> OrganizationResponse:
        """Create a new organization."""
        slug = data.slug or _slugify(data.name)

        # Check for duplicate slug
        existing = await self.session.execute(select(OrganizationModel).where(OrganizationModel.slug == slug))
        if existing.scalar_one_or_none() is not None:
            raise DuplicateError(f"Organization with slug '{slug}' already exists")

        org = OrganizationModel(
            id=uuid.uuid4().hex,
            name=data.name,
            slug=slug,
            description=data.description,
        )
        self.session.add(org)
        await self.session.commit()
        await self.session.refresh(org)

        logger.info("organization_created", org_id=org.id, slug=org.slug)
        return OrganizationResponse.model_validate(org)

    async def get_organization(self, org_id: str) -> OrganizationResponse:
        """Get an organization by ID."""
        org = await self._get_org_or_raise(org_id)
        return OrganizationResponse.model_validate(org)

    async def update_organization(self, org_id: str, data: OrganizationUpdate) -> OrganizationResponse:
        """Update an organization."""
        org = await self._get_org_or_raise(org_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
        org.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(org)

        logger.info("organization_updated", org_id=org.id)
        return OrganizationResponse.model_validate(org)

    # -- API Keys --

    async def create_api_key(
        self, org_id: str, data: APIKeyCreate, *, environment: str = "test"
    ) -> APIKeyCreatedResponse:
        """Create a new API key for an organization.

        Returns the full key exactly once.
        """
        await self._get_org_or_raise(org_id)

        prefix = f"uc_{environment}"
        full_key, key_id, key_hash = generate_api_key(prefix)

        key_model = APIKeyModel(
            id=uuid.uuid4().hex,
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=f"{prefix}_{key_id[:4]}...",
            name=data.name,
            scopes=data.scopes,
            organization_id=org_id,
        )
        self.session.add(key_model)

        # Audit log
        audit = APIKeyAuditLogModel(
            id=uuid.uuid4().hex,
            action="created",
            details=f"Key '{data.name}' created with scopes: {data.scopes}",
            api_key_id=key_model.id,
        )
        self.session.add(audit)

        await self.session.commit()
        await self.session.refresh(key_model)

        logger.info("api_key_created", org_id=org_id, key_id=key_id)
        return APIKeyCreatedResponse(
            id=key_model.id,
            key_id=key_model.key_id,
            key_prefix=key_model.key_prefix,
            name=key_model.name,
            scopes=key_model.scopes,
            plain_key=full_key,
            created_at=key_model.created_at,
        )

    async def list_api_keys(self, org_id: str) -> list[APIKeyResponse]:
        """List all API keys for an organization."""
        await self._get_org_or_raise(org_id)

        result = await self.session.execute(
            select(APIKeyModel).where(APIKeyModel.organization_id == org_id).order_by(APIKeyModel.created_at.desc())
        )
        keys = result.scalars().all()
        return [APIKeyResponse.model_validate(k) for k in keys]

    async def revoke_api_key(self, org_id: str, key_id: str) -> None:
        """Revoke (deactivate) an API key."""
        key_model = await self._get_key_or_raise(org_id, key_id)
        key_model.is_active = False
        key_model.updated_at = datetime.now(UTC)

        audit = APIKeyAuditLogModel(
            id=uuid.uuid4().hex,
            action="revoked",
            details=f"Key '{key_model.name}' revoked",
            api_key_id=key_model.id,
        )
        self.session.add(audit)

        await self.session.commit()
        logger.info("api_key_revoked", org_id=org_id, key_id=key_id)

    async def rotate_api_key(self, org_id: str, key_id: str, *, environment: str = "test") -> APIKeyCreatedResponse:
        """Rotate an API key: revoke old, create new with same name/scopes."""
        old_key = await self._get_key_or_raise(org_id, key_id)

        # Revoke old
        old_key.is_active = False
        old_key.updated_at = datetime.now(UTC)

        audit_revoke = APIKeyAuditLogModel(
            id=uuid.uuid4().hex,
            action="rotated_out",
            details=f"Key rotated — old key '{old_key.name}' deactivated",
            api_key_id=old_key.id,
        )
        self.session.add(audit_revoke)

        # Create new with same metadata
        new_key_data = APIKeyCreate(name=old_key.name, scopes=old_key.scopes)
        await self.session.flush()

        result = await self.create_api_key(org_id, new_key_data, environment=environment)

        logger.info("api_key_rotated", org_id=org_id, old_key_id=key_id, new_key_id=result.key_id)
        return result

    async def verify_and_get_org(self, raw_key: str) -> OrganizationModel:
        """Verify an API key and return the associated organization.

        Args:
            raw_key: The full API key from the request header.

        Returns:
            The organization associated with the key.

        Raises:
            AuthenticationError: If key format is invalid or not found.
            APIKeyRevokedError: If the key has been revoked.
        """
        parsed = parse_api_key(raw_key)
        if parsed is None:
            raise AuthenticationError("Invalid API key format")

        key_id_value, _ = parsed

        result = await self.session.execute(select(APIKeyModel).where(APIKeyModel.key_id == key_id_value))
        key_model = result.scalar_one_or_none()

        if key_model is None:
            raise AuthenticationError("API key not found")

        if not key_model.is_active:
            raise APIKeyRevokedError()

        if not verify_api_key(raw_key, key_model.key_hash):
            raise AuthenticationError("Invalid API key")

        # Store for scope checking without extra DB query
        self.last_verified_key = key_model

        # Update last_used_at
        key_model.last_used_at = datetime.now(UTC)
        await self.session.flush()

        result_org = await self.session.execute(
            select(OrganizationModel).where(OrganizationModel.id == key_model.organization_id)
        )
        org = result_org.scalar_one_or_none()
        if org is None:
            raise OrganizationNotFoundError()

        return org

    # -- Helpers --

    async def _get_org_or_raise(self, org_id: str) -> OrganizationModel:
        """Fetch organization or raise 404."""
        result = await self.session.execute(select(OrganizationModel).where(OrganizationModel.id == org_id))
        org = result.scalar_one_or_none()
        if org is None:
            raise OrganizationNotFoundError(f"Organization '{org_id}' not found")
        return org

    async def _get_key_or_raise(self, org_id: str, key_id: str) -> APIKeyModel:
        """Fetch API key by key_id within an org, or raise 404."""
        result = await self.session.execute(
            select(APIKeyModel).where(
                APIKeyModel.key_id == key_id,
                APIKeyModel.organization_id == org_id,
            )
        )
        key_model = result.scalar_one_or_none()
        if key_model is None:
            raise APIKeyNotFoundError(f"API key '{key_id}' not found in org '{org_id}'")
        return key_model
