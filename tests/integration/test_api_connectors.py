"""Integration tests for connector API endpoints (WhatsApp, webhook, PII scan)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Inline test data (fictional only — no real PII)
# ---------------------------------------------------------------------------

VALID_WHATSAPP_EXPORT = (
    "[12/01/2025, 10:00:00] Carlos Lopez: Hola, busco un auto compacto.\n"
    "[12/01/2025, 10:01:00] Vendedor Ana: Buenos dias. Tenemos opciones en sedan y hatchback.\n"
    "[12/01/2025, 10:02:00] Carlos Lopez: Me interesa un hatchback automatico.\n"
    "[12/01/2025, 10:03:00] Vendedor Ana: Tenemos el Modelo X con transmision automatica.\n"
)

EMPTY_WHATSAPP_EXPORT = ""

# A few system messages that should be skipped
SYSTEM_ONLY_WHATSAPP = (
    "[12/01/2025, 09:00:00] Messages and calls are end-to-end encrypted.\n"
    "[12/01/2025, 09:05:00] Carlos Lopez created group Test\n"
)


@pytest.mark.integration
class TestListConnectors:
    """Test GET /api/v1/connectors."""

    async def test_list_connectors(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/connectors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # whatsapp, huggingface, webhook, pii-scanner
        slugs = {c["slug"] for c in data}
        assert "whatsapp" in slugs
        assert "webhook" in slugs


@pytest.mark.integration
class TestWhatsAppImport:
    """Test POST /api/v1/connectors/whatsapp."""

    async def test_import_whatsapp(self, client: AsyncClient) -> None:
        """Upload a valid WhatsApp export and verify conversations are imported."""
        files = {"file": ("chat.txt", VALID_WHATSAPP_EXPORT, "text/plain")}
        response = await client.post("/api/v1/connectors/whatsapp", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["total_imported"] >= 1
        assert isinstance(data["conversations"], list)
        assert data["total_pii_anonymized"] >= 0

    async def test_import_whatsapp_empty_file(self, client: AsyncClient) -> None:
        """Empty file should return 200 with 0 imported or parse gracefully."""
        files = {"file": ("empty.txt", EMPTY_WHATSAPP_EXPORT, "text/plain")}
        response = await client.post("/api/v1/connectors/whatsapp", files=files)
        # Even an empty file should be parseable (0 conversations)
        assert response.status_code == 200
        data = response.json()
        assert data["total_imported"] == 0

    async def test_import_whatsapp_system_only(self, client: AsyncClient) -> None:
        """File with only system messages should import 0 conversations."""
        files = {"file": ("system.txt", SYSTEM_ONLY_WHATSAPP, "text/plain")}
        response = await client.post("/api/v1/connectors/whatsapp", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["total_imported"] == 0

    async def test_import_whatsapp_no_file(self, client: AsyncClient) -> None:
        """Missing file should return 422."""
        response = await client.post("/api/v1/connectors/whatsapp")
        assert response.status_code == 422


@pytest.mark.integration
class TestWebhookImport:
    """Test POST /api/v1/connectors/webhook."""

    async def test_webhook_import(self, client: AsyncClient) -> None:
        """Import conversations via webhook JSON payload."""
        payload = {
            "conversations": [
                {
                    "turns": [
                        {"role": "user", "content": "Necesito cotizar un auto."},
                        {"role": "assistant", "content": "Con gusto. Que modelo le interesa?"},
                    ],
                    "domain": "automotive.sales",
                    "language": "es",
                },
            ],
        }
        response = await client.post("/api/v1/connectors/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_imported"] >= 1

    async def test_webhook_empty_conversations(self, client: AsyncClient) -> None:
        """Empty conversations array should fail validation."""
        payload: dict[str, list[object]] = {"conversations": []}
        response = await client.post("/api/v1/connectors/webhook", json=payload)
        assert response.status_code == 422

    async def test_webhook_missing_body(self, client: AsyncClient) -> None:
        """Missing body should return 422."""
        response = await client.post("/api/v1/connectors/webhook")
        assert response.status_code == 422


@pytest.mark.integration
class TestScanPII:
    """Test POST /api/v1/connectors/scan-pii."""

    async def test_scan_clean_text(self, client: AsyncClient) -> None:
        """Scan text without PII."""
        response = await client.post(
            "/api/v1/connectors/scan-pii",
            params={"text": "Este es un texto ficticio sin datos personales."},
        )
        assert response.status_code == 200
        data = response.json()
        assert "pii_found" in data
        assert "entity_count" in data
        assert "scanner_mode" in data

    async def test_scan_text_with_email(self, client: AsyncClient) -> None:
        """Scan text that contains an email address."""
        response = await client.post(
            "/api/v1/connectors/scan-pii",
            params={"text": "Contactame en ficticio@example.com por favor."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pii_found"] is True
        assert data["entity_count"] >= 1
