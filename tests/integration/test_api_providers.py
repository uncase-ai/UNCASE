"""Integration tests for the Providers API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.db.models.provider import LLMProviderModel

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


def _provider_create_payload(**overrides: object) -> dict[str, object]:
    """Build a valid ProviderCreateRequest payload with fictional defaults."""
    payload: dict[str, object] = {
        "name": "Test Ollama Provider",
        "provider_type": "ollama",
        "api_base": "http://localhost:11434",
        "default_model": "llama3.1:8b",
        "max_tokens": 4096,
        "temperature_default": 0.7,
        "is_default": False,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
async def sample_provider(async_session: AsyncSession) -> LLMProviderModel:
    """Create a sample provider directly in the DB."""
    provider = LLMProviderModel(
        id="prov-test-001",
        name="Test Ollama",
        provider_type="ollama",
        api_base="http://localhost:11434",
        api_key_encrypted=None,
        default_model="llama3.1:8b",
        max_tokens=4096,
        temperature_default=0.7,
        is_active=True,
        is_default=False,
        organization_id=None,
    )
    async_session.add(provider)
    await async_session.commit()
    await async_session.refresh(provider)
    return provider


@pytest.fixture()
async def inactive_provider(async_session: AsyncSession) -> LLMProviderModel:
    """Create an inactive provider."""
    provider = LLMProviderModel(
        id="prov-test-002",
        name="Inactive Provider",
        provider_type="custom",
        api_base="http://localhost:9999",
        api_key_encrypted=None,
        default_model="custom-model",
        max_tokens=2048,
        temperature_default=0.5,
        is_active=False,
        is_default=False,
        organization_id=None,
    )
    async_session.add(provider)
    await async_session.commit()
    await async_session.refresh(provider)
    return provider


@pytest.mark.integration
class TestListProviders:
    """Test GET /api/v1/providers."""

    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_with_provider(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "prov-test-001"
        assert data["items"][0]["name"] == "Test Ollama"

    async def test_list_active_only_default(
        self,
        client: AsyncClient,
        sample_provider: LLMProviderModel,
        inactive_provider: LLMProviderModel,
    ) -> None:
        """By default, only active providers are returned."""
        response = await client.get("/api/v1/providers")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["is_active"] is True

    async def test_list_include_inactive(
        self,
        client: AsyncClient,
        sample_provider: LLMProviderModel,
        inactive_provider: LLMProviderModel,
    ) -> None:
        response = await client.get("/api/v1/providers", params={"active_only": "false"})
        data = response.json()
        assert data["total"] == 2


@pytest.mark.integration
class TestCreateProvider:
    """Test POST /api/v1/providers."""

    async def test_create_local_provider(self, client: AsyncClient) -> None:
        payload = _provider_create_payload()
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Ollama Provider"
        assert data["provider_type"] == "ollama"
        assert data["has_api_key"] is False
        assert "id" in data

    async def test_create_cloud_provider_with_key(self, client: AsyncClient) -> None:
        payload = _provider_create_payload(
            name="Test Anthropic",
            provider_type="anthropic",
            api_base=None,
            api_key="sk-ant-fictional-key-for-testing-only",
            default_model="claude-sonnet-4-20250514",
        )
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["has_api_key"] is True
        # API key must never be returned
        assert "api_key" not in data

    async def test_create_cloud_provider_without_key_fails(self, client: AsyncClient) -> None:
        payload = _provider_create_payload(
            name="Missing Key Provider",
            provider_type="openai",
            api_base=None,
            default_model="gpt-4o",
        )
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 422

    async def test_create_local_provider_without_api_base_fails(self, client: AsyncClient) -> None:
        payload = _provider_create_payload(api_base=None)
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 422

    async def test_create_invalid_provider_type(self, client: AsyncClient) -> None:
        payload = _provider_create_payload(provider_type="invalid_type")
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 422

    async def test_create_provider_missing_name(self, client: AsyncClient) -> None:
        payload = _provider_create_payload()
        del payload["name"]  # type: ignore[arg-type]
        response = await client.post("/api/v1/providers", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestGetProvider:
    """Test GET /api/v1/providers/{provider_id}."""

    async def test_get_existing(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.get(f"/api/v1/providers/{sample_provider.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_provider.id
        assert data["provider_type"] == "ollama"

    async def test_get_nonexistent(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/providers/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestUpdateProvider:
    """Test PUT /api/v1/providers/{provider_id}."""

    async def test_update_name(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.put(
            f"/api/v1/providers/{sample_provider.id}",
            json={"name": "Updated Ollama Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Ollama Name"

    async def test_update_temperature(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.put(
            f"/api/v1/providers/{sample_provider.id}",
            json={"temperature_default": 0.3},
        )
        assert response.status_code == 200
        assert response.json()["temperature_default"] == 0.3

    async def test_update_nonexistent(self, client: AsyncClient) -> None:
        response = await client.put(
            "/api/v1/providers/no-such-prov",
            json={"name": "Ghost"},
        )
        assert response.status_code == 404

    async def test_update_empty_body(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.put(
            f"/api/v1/providers/{sample_provider.id}",
            json={},
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestDeleteProvider:
    """Test DELETE /api/v1/providers/{provider_id}."""

    async def test_delete_existing(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        response = await client.delete(f"/api/v1/providers/{sample_provider.id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/providers/{sample_provider.id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent(self, client: AsyncClient) -> None:
        response = await client.delete("/api/v1/providers/nonexistent-prov")
        assert response.status_code == 404


@pytest.mark.integration
class TestTestProvider:
    """Test POST /api/v1/providers/{provider_id}/test."""

    async def test_test_nonexistent_provider(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/providers/nonexistent-prov/test")
        assert response.status_code == 404

    async def test_test_provider_returns_result(self, client: AsyncClient, sample_provider: LLMProviderModel) -> None:
        """Test connection returns a result (likely error since ollama isn't running)."""
        response = await client.post(f"/api/v1/providers/{sample_provider.id}/test")
        assert response.status_code == 200
        data = response.json()
        assert data["provider_id"] == sample_provider.id
        assert data["provider_name"] == sample_provider.name
        assert data["model_tested"] == sample_provider.default_model
        # Status will be "error" since no real LLM is running in tests
        assert data["status"] in ("ok", "error", "timeout")
