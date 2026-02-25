"""Tests for the LLM provider management service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from uncase.config import UNCASESettings
from uncase.exceptions import ProviderNotFoundError, ValidationError
from uncase.schemas.provider import ProviderCreateRequest, ProviderUpdateRequest
from uncase.services.provider import ProviderService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _settings() -> UNCASESettings:
    return UNCASESettings(
        uncase_env="development",
        uncase_log_level="DEBUG",
        database_url="sqlite+aiosqlite://",
        api_secret_key="test-secret-key-abc",
    )


def _make_create(**overrides: object) -> ProviderCreateRequest:
    """Build a valid ProviderCreateRequest with fictional defaults."""
    defaults: dict[str, object] = {
        "name": "Proveedor ficticio de prueba",
        "provider_type": "anthropic",
        "api_key": "sk-test-fictitious-key-abc123",
        "default_model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "temperature_default": 0.7,
        "is_default": False,
    }
    defaults.update(overrides)
    return ProviderCreateRequest(**defaults)  # type: ignore[arg-type]


class TestProviderServiceCreate:
    async def test_create_provider(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        req = _make_create()
        resp = await service.create_provider(req)

        assert resp.id is not None
        assert resp.name == "Proveedor ficticio de prueba"
        assert resp.provider_type == "anthropic"
        assert resp.default_model == "claude-sonnet-4-20250514"
        assert resp.has_api_key is True
        assert resp.is_active is True
        assert resp.is_default is False

    async def test_create_provider_with_org(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        req = _make_create()
        resp = await service.create_provider(req, organization_id="org-test-001")

        assert resp.organization_id == "org-test-001"

    async def test_create_invalid_provider_type_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        req = _make_create(provider_type="unsupported_llm")
        with pytest.raises(ValidationError, match="Invalid provider_type"):
            await service.create_provider(req)

    async def test_create_local_provider_requires_api_base(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        for provider_type in ("ollama", "vllm", "custom"):
            req = _make_create(provider_type=provider_type, api_key=None, api_base=None)
            with pytest.raises(ValidationError, match="api_base is required"):
                await service.create_provider(req)

    async def test_create_cloud_provider_requires_api_key(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        for provider_type in ("anthropic", "openai", "google", "groq"):
            req = _make_create(provider_type=provider_type, api_key=None)
            with pytest.raises(ValidationError, match="api_key is required"):
                await service.create_provider(req)

    async def test_create_local_provider_without_key(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        req = _make_create(
            provider_type="ollama",
            api_key=None,
            api_base="http://localhost:11434",
            default_model="llama3.1:8b",
        )
        resp = await service.create_provider(req)

        assert resp.has_api_key is False
        assert resp.provider_type == "ollama"

    async def test_create_default_provider_clears_others(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        r1 = await service.create_provider(_make_create(name="Provider A", is_default=True))
        assert r1.is_default is True

        r2 = await service.create_provider(_make_create(name="Provider B", is_default=True))
        assert r2.is_default is True

        # First provider should no longer be default
        fetched_r1 = await service.get_provider(r1.id)
        assert fetched_r1.is_default is False


class TestProviderServiceGet:
    async def test_get_existing_provider(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        found = await service.get_provider(created.id)

        assert found.id == created.id
        assert found.name == created.name

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        with pytest.raises(ProviderNotFoundError):
            await service.get_provider("nonexistent-id")


class TestProviderServiceList:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        result = await service.list_providers()

        assert result.items == []
        assert result.total == 0

    async def test_list_returns_all_active(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(_make_create(name="A"))
        await service.create_provider(_make_create(name="B"))

        result = await service.list_providers()

        assert result.total == 2

    async def test_list_filters_by_org(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(_make_create(name="A"), organization_id="org-a")
        await service.create_provider(_make_create(name="B"), organization_id="org-b")

        result = await service.list_providers(organization_id="org-a")

        assert result.total == 1
        assert result.items[0].name == "A"

    async def test_list_active_only(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create(name="Active"))
        inactive = await service.create_provider(_make_create(name="Inactive"))
        # Deactivate the second one
        await service.update_provider(inactive.id, ProviderUpdateRequest(is_active=False))

        result = await service.list_providers(active_only=True)
        assert result.total == 1
        assert result.items[0].id == created.id

    async def test_list_include_inactive(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(_make_create(name="Active"))
        inactive = await service.create_provider(_make_create(name="Inactive"))
        await service.update_provider(inactive.id, ProviderUpdateRequest(is_active=False))

        result = await service.list_providers(active_only=False)
        assert result.total == 2


class TestProviderServiceUpdate:
    async def test_update_name(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        updated = await service.update_provider(created.id, ProviderUpdateRequest(name="Nombre actualizado"))

        assert updated.name == "Nombre actualizado"

    async def test_update_api_key(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        updated = await service.update_provider(created.id, ProviderUpdateRequest(api_key="sk-new-fictitious-key"))

        assert updated.has_api_key is True

    async def test_update_clear_api_key(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        updated = await service.update_provider(created.id, ProviderUpdateRequest(api_key=""))

        assert updated.has_api_key is False

    async def test_update_no_fields_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        with pytest.raises(ValidationError, match="No fields to update"):
            await service.update_provider(created.id, ProviderUpdateRequest())

    async def test_update_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        with pytest.raises(ProviderNotFoundError):
            await service.update_provider("nonexistent-id", ProviderUpdateRequest(name="test"))

    async def test_update_set_default_clears_others(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        p1 = await service.create_provider(_make_create(name="P1", is_default=True))
        p2 = await service.create_provider(_make_create(name="P2"))
        await service.update_provider(p2.id, ProviderUpdateRequest(is_default=True))

        refreshed_p1 = await service.get_provider(p1.id)
        refreshed_p2 = await service.get_provider(p2.id)
        assert refreshed_p1.is_default is False
        assert refreshed_p2.is_default is True


class TestProviderServiceDelete:
    async def test_delete_existing(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())
        await service.delete_provider(created.id)

        with pytest.raises(ProviderNotFoundError):
            await service.get_provider(created.id)

    async def test_delete_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        with pytest.raises(ProviderNotFoundError):
            await service.delete_provider("nonexistent-id")


class TestProviderServiceEncryption:
    async def test_encrypt_decrypt_roundtrip(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        original = "sk-test-fictitious-secret-key"
        encrypted = service._encrypt_key(original)
        decrypted = service._decrypt_key(encrypted)

        assert decrypted == original
        assert encrypted != original

    async def test_decrypt_provider_key(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create(api_key="sk-decrypt-test-key"))
        provider_model = await service._get_or_raise(created.id)

        decrypted = service.decrypt_provider_key(provider_model)
        assert decrypted == "sk-decrypt-test-key"

    async def test_decrypt_provider_key_none(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(
            _make_create(
                provider_type="ollama",
                api_key=None,
                api_base="http://localhost:11434",
                default_model="llama3.1:8b",
            )
        )
        provider_model = await service._get_or_raise(created.id)

        result = service.decrypt_provider_key(provider_model)
        assert result is None


class TestProviderServiceTestConnection:
    async def test_connection_success(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())

        mock_response = AsyncMock()
        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response):
            result = await service.test_connection(created.id)

        assert result.status == "ok"
        assert result.provider_id == created.id
        assert result.model_tested == "claude-sonnet-4-20250514"
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    async def test_connection_failure(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        created = await service.create_provider(_make_create())

        with patch("litellm.acompletion", new_callable=AsyncMock, side_effect=Exception("Connection refused")):
            result = await service.test_connection(created.id)

        assert result.status == "error"
        assert result.error is not None
        assert "Connection refused" in result.error

    async def test_connection_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        with pytest.raises(ProviderNotFoundError):
            await service.test_connection("nonexistent-id")


class TestProviderServiceGetDefault:
    async def test_get_default_provider(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(_make_create(name="Default", is_default=True))
        await service.create_provider(_make_create(name="Other", is_default=False))

        default = await service.get_default_provider()
        assert default is not None
        assert default.name == "Default"
        assert default.is_default is True

    async def test_get_default_provider_none(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(_make_create(is_default=False))

        default = await service.get_default_provider()
        assert default is None

    async def test_get_default_provider_by_org(self, async_session: AsyncSession) -> None:
        service = ProviderService(async_session, _settings())
        await service.create_provider(
            _make_create(name="Org A default", is_default=True),
            organization_id="org-a",
        )
        await service.create_provider(
            _make_create(name="Org B default", is_default=True),
            organization_id="org-b",
        )

        default_a = await service.get_default_provider(organization_id="org-a")
        assert default_a is not None
        assert default_a.name == "Org A default"
