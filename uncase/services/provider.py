"""LLM provider management service."""

from __future__ import annotations

import base64
import time
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet
from sqlalchemy import select

from uncase.config import UNCASESettings
from uncase.db.models.provider import LLMProviderModel
from uncase.exceptions import ProviderNotFoundError, ValidationError
from uncase.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from uncase.schemas.provider import (
        ProviderCreateRequest,
        ProviderListResponse,
        ProviderResponse,
        ProviderTestResponse,
        ProviderUpdateRequest,
    )

logger = get_logger(__name__)


def _get_fernet(settings: UNCASESettings) -> Fernet:
    """Build a Fernet cipher from the app secret key."""
    raw = settings.api_secret_key.encode("utf-8")
    # Pad or truncate to exactly 32 bytes for Fernet
    key_bytes = (raw * 3)[:32]
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


class ProviderService:
    """Service for LLM provider CRUD and connection testing."""

    def __init__(self, session: AsyncSession, settings: UNCASESettings | None = None) -> None:
        self.session = session
        self._settings = settings or UNCASESettings()
        self._fernet = _get_fernet(self._settings)

    def _encrypt_key(self, plain_key: str) -> str:
        """Encrypt an API key using Fernet."""
        return self._fernet.encrypt(plain_key.encode("utf-8")).decode("utf-8")

    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key."""
        return self._fernet.decrypt(encrypted_key.encode("utf-8")).decode("utf-8")

    async def create_provider(
        self,
        data: ProviderCreateRequest,
        *,
        organization_id: str | None = None,
    ) -> ProviderResponse:
        """Register a new LLM provider."""
        from uncase.schemas.provider import PROVIDER_TYPES

        if data.provider_type not in PROVIDER_TYPES:
            raise ValidationError(
                f"Invalid provider_type '{data.provider_type}'. Must be one of: {', '.join(PROVIDER_TYPES)}"
            )

        # Local providers require api_base
        if data.provider_type in ("ollama", "vllm", "custom") and not data.api_base:
            raise ValidationError(f"api_base is required for provider_type '{data.provider_type}'")

        # Cloud providers require api_key
        if data.provider_type in ("anthropic", "openai", "google", "groq") and not data.api_key:
            raise ValidationError(f"api_key is required for provider_type '{data.provider_type}'")

        encrypted_key = self._encrypt_key(data.api_key) if data.api_key else None

        # If setting as default, clear other defaults
        if data.is_default:
            await self._clear_defaults(organization_id)

        provider = LLMProviderModel(
            id=uuid.uuid4().hex,
            name=data.name,
            provider_type=data.provider_type,
            api_base=data.api_base,
            api_key_encrypted=encrypted_key,
            default_model=data.default_model,
            max_tokens=data.max_tokens,
            temperature_default=data.temperature_default,
            is_default=data.is_default,
            organization_id=organization_id,
        )
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)

        logger.info(
            "provider_created",
            provider_id=provider.id,
            name=provider.name,
            provider_type=provider.provider_type,
        )
        return self._to_response(provider)

    async def get_provider(self, provider_id: str) -> ProviderResponse:
        """Get a provider by ID."""
        provider = await self._get_or_raise(provider_id)
        return self._to_response(provider)

    async def list_providers(
        self,
        *,
        organization_id: str | None = None,
        active_only: bool = True,
    ) -> ProviderListResponse:
        """List all configured providers."""
        from uncase.schemas.provider import ProviderListResponse

        query = select(LLMProviderModel)

        if organization_id is not None:
            query = query.where(LLMProviderModel.organization_id == organization_id)

        if active_only:
            query = query.where(LLMProviderModel.is_active.is_(True))

        query = query.order_by(LLMProviderModel.is_default.desc(), LLMProviderModel.created_at.desc())
        result = await self.session.execute(query)
        providers = result.scalars().all()

        return ProviderListResponse(
            items=[self._to_response(p) for p in providers],
            total=len(providers),
        )

    async def update_provider(self, provider_id: str, data: ProviderUpdateRequest) -> ProviderResponse:
        """Update a provider configuration."""
        provider = await self._get_or_raise(provider_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("No fields to update")

        # Handle API key encryption
        if "api_key" in update_data:
            new_key = update_data.pop("api_key")
            if new_key:
                provider.api_key_encrypted = self._encrypt_key(new_key)
            else:
                provider.api_key_encrypted = None

        # Handle default flag
        if update_data.get("is_default"):
            await self._clear_defaults(provider.organization_id)

        for field, value in update_data.items():
            setattr(provider, field, value)
        provider.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(provider)

        logger.info("provider_updated", provider_id=provider.id, fields=list(update_data.keys()))
        return self._to_response(provider)

    async def delete_provider(self, provider_id: str) -> None:
        """Delete a provider."""
        provider = await self._get_or_raise(provider_id)
        await self.session.delete(provider)
        await self.session.commit()
        logger.info("provider_deleted", provider_id=provider_id)

    async def test_connection(self, provider_id: str) -> ProviderTestResponse:
        """Test a provider connection by making a minimal LLM call."""
        from uncase.schemas.provider import ProviderTestResponse

        provider = await self._get_or_raise(provider_id)

        api_key: str | None = None
        if provider.api_key_encrypted:
            api_key = self._decrypt_key(provider.api_key_encrypted)

        start = time.monotonic()
        try:
            import litellm

            await litellm.acompletion(
                model=provider.default_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                api_key=api_key,
                api_base=provider.api_base,
            )
            latency = round((time.monotonic() - start) * 1000, 1)

            logger.info(
                "provider_test_ok",
                provider_id=provider.id,
                model=provider.default_model,
                latency_ms=latency,
            )
            return ProviderTestResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status="ok",
                latency_ms=latency,
                model_tested=provider.default_model,
            )
        except Exception as exc:
            latency = round((time.monotonic() - start) * 1000, 1)
            error_msg = str(exc)[:200]

            logger.warning(
                "provider_test_failed",
                provider_id=provider.id,
                model=provider.default_model,
                error=error_msg,
            )
            return ProviderTestResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status="error",
                latency_ms=latency,
                model_tested=provider.default_model,
                error=error_msg,
            )

    async def get_default_provider(
        self,
        *,
        organization_id: str | None = None,
    ) -> LLMProviderModel | None:
        """Get the default active provider for an organization."""
        query = select(LLMProviderModel).where(
            LLMProviderModel.is_default.is_(True),
            LLMProviderModel.is_active.is_(True),
        )
        if organization_id is not None:
            query = query.where(LLMProviderModel.organization_id == organization_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def decrypt_provider_key(self, provider: LLMProviderModel) -> str | None:
        """Decrypt the API key from a provider model. Used by GeneratorService."""
        if provider.api_key_encrypted:
            return self._decrypt_key(provider.api_key_encrypted)
        return None

    # -- Helpers --

    async def _get_or_raise(self, provider_id: str) -> LLMProviderModel:
        """Fetch a provider or raise ProviderNotFoundError."""
        result = await self.session.execute(select(LLMProviderModel).where(LLMProviderModel.id == provider_id))
        provider = result.scalar_one_or_none()
        if provider is None:
            raise ProviderNotFoundError(f"Provider '{provider_id}' not found")
        return provider

    async def _clear_defaults(self, organization_id: str | None) -> None:
        """Clear the is_default flag on all providers for an organization."""
        query = select(LLMProviderModel).where(
            LLMProviderModel.is_default.is_(True),
        )
        if organization_id is not None:
            query = query.where(LLMProviderModel.organization_id == organization_id)

        result = await self.session.execute(query)
        for p in result.scalars().all():
            p.is_default = False

    @staticmethod
    def _to_response(provider: LLMProviderModel) -> ProviderResponse:
        """Convert a model to a response schema."""
        from uncase.schemas.provider import ProviderResponse

        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            provider_type=provider.provider_type,
            api_base=provider.api_base,
            has_api_key=provider.api_key_encrypted is not None,
            default_model=provider.default_model,
            max_tokens=provider.max_tokens,
            temperature_default=provider.temperature_default,
            is_active=provider.is_active,
            is_default=provider.is_default,
            organization_id=provider.organization_id,
            created_at=(
                provider.created_at.isoformat()
                if hasattr(provider.created_at, "isoformat")
                else str(provider.created_at)
            ),
            updated_at=(
                provider.updated_at.isoformat()
                if hasattr(provider.updated_at, "isoformat")
                else str(provider.updated_at)
            ),
        )
