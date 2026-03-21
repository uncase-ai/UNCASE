"""Integration tests for gateway API endpoints (LLM chat proxy).

The gateway depends on get_current_org (mandatory auth) and litellm.acompletion,
so we mock litellm and bootstrap an org with an API key.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _bootstrap_org(client: AsyncClient, name: str = "Gateway Test Org") -> tuple[str, str]:
    """Create an org and return (org_id, plain_api_key)."""
    create_resp = await client.post("/api/v1/organizations", json={"name": name})
    assert create_resp.status_code == 201
    org_id = create_resp.json()["id"]

    key_resp = await client.post(
        f"/api/v1/organizations/{org_id}/api-keys",
        json={"name": "admin-key", "scopes": "admin"},
    )
    assert key_resp.status_code == 201
    return org_id, key_resp.json()["plain_key"]


async def _create_provider_via_api(client: AsyncClient) -> str:
    """Create a provider through the API so the key is properly encrypted.

    Returns the provider ID.
    """
    payload = {
        "name": "Test Gateway Anthropic",
        "provider_type": "anthropic",
        "api_key": "sk-ant-fictional-key-for-gateway-testing",
        "default_model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "temperature_default": 0.7,
        "is_default": True,
    }
    resp = await client.post("/api/v1/providers", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def _mock_litellm_response(content: str = "Respuesta ficticia del modelo.") -> MagicMock:
    """Build a mock litellm response object."""
    message = MagicMock()
    message.content = content
    message.tool_calls = None

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = "stop"

    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.mark.integration
class TestChatProxy:
    """Test POST /api/v1/gateway/chat."""

    async def test_chat_requires_auth(self, client: AsyncClient) -> None:
        """Request without X-API-Key should return 422 (missing header)."""
        body = {
            "messages": [{"role": "user", "content": "Hola, necesito ayuda."}],
        }
        response = await client.post("/api/v1/gateway/chat", json=body)
        assert response.status_code == 422

    async def test_chat_invalid_api_key(self, client: AsyncClient) -> None:
        """Invalid API key should return 401."""
        body = {
            "messages": [{"role": "user", "content": "Hola."}],
        }
        response = await client.post(
            "/api/v1/gateway/chat",
            json=body,
            headers={"X-API-Key": "uc_test_invalid_key_that_does_not_exist"},
        )
        assert response.status_code == 401

    @patch("litellm.acompletion", new_callable=AsyncMock)
    async def test_chat_happy_path(
        self,
        mock_acompletion: AsyncMock,
        client: AsyncClient,
    ) -> None:
        """Successful chat with mocked LLM response."""
        mock_acompletion.return_value = _mock_litellm_response()

        # Create a provider via the API so the key is properly encrypted
        await _create_provider_via_api(client)

        _, api_key = await _bootstrap_org(client, "Chat Happy Org")

        body = {
            "messages": [{"role": "user", "content": "Hola, necesito cotizar un vehiculo ficticio."}],
            "temperature": 0.5,
            "max_tokens": 256,
        }
        response = await client.post(
            "/api/v1/gateway/chat",
            json=body,
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert "privacy" in data
        assert "model" in data

    async def test_chat_empty_messages(self, client: AsyncClient) -> None:
        """Empty messages array should return 422."""
        _, api_key = await _bootstrap_org(client, "Chat Empty Org")
        body: dict[str, list[object]] = {"messages": []}
        response = await client.post(
            "/api/v1/gateway/chat",
            json=body,
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 422

    async def test_chat_missing_message_content(self, client: AsyncClient) -> None:
        """Message without content should return 422."""
        _, api_key = await _bootstrap_org(client, "Chat Missing Content Org")
        body = {"messages": [{"role": "user"}]}
        response = await client.post(
            "/api/v1/gateway/chat",
            json=body,
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 422
