"""Tests for the UNCASE SDK HTTP client."""

from __future__ import annotations

from uncase.sdk.client import UNCASEClient


class TestUNCASEClient:
    """Test UNCASEClient initialization and configuration."""

    def test_default_base_url(self) -> None:
        client = UNCASEClient()
        assert client._client.base_url == "http://localhost:8000"
        client.close()

    def test_custom_base_url(self) -> None:
        client = UNCASEClient(base_url="http://api.example.com")
        assert "api.example.com" in str(client._client.base_url)
        client.close()

    def test_api_key_in_headers(self) -> None:
        client = UNCASEClient(api_key="test-key-123")
        assert client._client.headers["x-api-key"] == "test-key-123"
        client.close()

    def test_no_api_key(self) -> None:
        client = UNCASEClient()
        assert "x-api-key" not in client._client.headers
        client.close()

    def test_content_type_header(self) -> None:
        client = UNCASEClient()
        assert client._client.headers["content-type"] == "application/json"
        client.close()

    def test_custom_timeout(self) -> None:
        client = UNCASEClient(timeout=30.0)
        assert client._client.timeout.read == 30.0
        client.close()

    def test_async_client_created(self) -> None:
        client = UNCASEClient(api_key="key")
        assert client._async_client is not None
        assert client._async_client.headers["x-api-key"] == "key"
        client.close()
