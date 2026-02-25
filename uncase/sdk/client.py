"""HTTP client for the UNCASE API."""

from __future__ import annotations

from typing import Any

import httpx


class UNCASEClient:
    """HTTP client wrapper for the UNCASE REST API.

    Usage:
        client = UNCASEClient(base_url="http://localhost:8000", api_key="...")
        seeds = client.get("/api/v1/seeds")
    """

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)
        self._async_client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout)

    def get(self, path: str, **params: Any) -> Any:
        """Synchronous GET request."""
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Synchronous POST request."""
        resp = self._client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    async def aget(self, path: str, **params: Any) -> Any:
        """Async GET request."""
        resp = await self._async_client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def apost(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Async POST request."""
        resp = await self._async_client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    async def aclose(self) -> None:
        """Close the async HTTP client."""
        await self._async_client.aclose()
