"""Integration tests for file import API endpoints (CSV and JSONL)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Inline test data (fictional only — no real PII)
# ---------------------------------------------------------------------------

VALID_CSV = (
    "conversation_id,turn_number,role,content,seed_id,domain\n"
    "conv-001,1,usuario,Busco un auto compacto para ciudad.,seed-csv-001,automotive.sales\n"
    "conv-001,2,asistente,Tenemos varias opciones. ¿Prefiere alguna marca?,seed-csv-001,automotive.sales\n"
    "conv-002,1,usuario,¿Tienen financiamiento a 36 meses?,seed-csv-002,automotive.sales\n"
    "conv-002,2,asistente,Sí contamos con planes desde 12 hasta 72 meses.,seed-csv-002,automotive.sales\n"
)

VALID_JSONL_OPENAI = (
    '{"messages": [{"role": "user", "content": "¿Qué modelos de SUV tienen?"}, '
    '{"role": "assistant", "content": "Contamos con RAV4, CR-V y CX-5."}]}\n'
    '{"messages": [{"role": "user", "content": "¿Cuál es el precio del Civic?"}, '
    '{"role": "assistant", "content": "El Honda Civic tiene un precio base de $420,000 MXN."}]}\n'
)

VALID_JSONL_SHAREGPT = (
    '{"conversations": [{"from": "human", "value": "Necesito cotizar un sedán."}, '
    '{"from": "gpt", "value": "Con gusto. ¿Tiene preferencia de marca?"}]}\n'
)

INVALID_CSV_MISSING_COLUMNS = "id,text\n1,This CSV is missing required columns\n"

INVALID_CSV_EMPTY = ""


@pytest.mark.integration
class TestImportCSV:
    async def test_import_csv(self, client: AsyncClient) -> None:
        """Upload a valid CSV and verify conversations are imported."""
        files = {"file": ("test_conversations.csv", VALID_CSV, "text/csv")}

        response = await client.post("/api/v1/import/csv", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["conversations_imported"] == 2
        assert data["conversations_failed"] == 0
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) == 0
        assert isinstance(data["conversations"], list)
        assert len(data["conversations"]) == 2

        # Verify structure of imported conversations
        conv = data["conversations"][0]
        assert "conversation_id" in conv
        assert "seed_id" in conv
        assert "dominio" in conv
        assert "turnos" in conv
        assert len(conv["turnos"]) >= 1

    async def test_import_csv_invalid_missing_columns(self, client: AsyncClient) -> None:
        """CSV missing required columns returns 422."""
        files = {"file": ("bad.csv", INVALID_CSV_MISSING_COLUMNS, "text/csv")}

        response = await client.post("/api/v1/import/csv", files=files)
        assert response.status_code == 422

    async def test_import_csv_empty(self, client: AsyncClient) -> None:
        """Empty CSV content returns 422."""
        files = {"file": ("empty.csv", INVALID_CSV_EMPTY, "text/csv")}

        response = await client.post("/api/v1/import/csv", files=files)
        assert response.status_code == 422


@pytest.mark.integration
class TestImportJSONL:
    async def test_import_jsonl_openai(self, client: AsyncClient) -> None:
        """Upload a valid OpenAI-format JSONL and verify import."""
        files = {"file": ("openai_data.jsonl", VALID_JSONL_OPENAI, "application/jsonlines")}

        response = await client.post("/api/v1/import/jsonl", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["conversations_imported"] == 2
        assert data["conversations_failed"] == 0
        assert isinstance(data["conversations"], list)
        assert len(data["conversations"]) == 2

    async def test_import_jsonl_sharegpt(self, client: AsyncClient) -> None:
        """Upload a valid ShareGPT-format JSONL and verify import."""
        files = {"file": ("sharegpt_data.jsonl", VALID_JSONL_SHAREGPT, "application/jsonlines")}

        response = await client.post("/api/v1/import/jsonl", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["conversations_imported"] == 1

    async def test_import_jsonl_with_source_format(self, client: AsyncClient) -> None:
        """Pass explicit source_format query parameter."""
        files = {"file": ("data.jsonl", VALID_JSONL_OPENAI, "application/jsonlines")}

        response = await client.post(
            "/api/v1/import/jsonl",
            files=files,
            params={"source_format": "openai"},
        )
        assert response.status_code == 200
        assert response.json()["conversations_imported"] == 2

    async def test_import_jsonl_invalid_json(self, client: AsyncClient) -> None:
        """JSONL with broken JSON returns 422."""
        broken = "this is not valid json\n{also broken\n"
        files = {"file": ("broken.jsonl", broken, "application/jsonlines")}

        response = await client.post("/api/v1/import/jsonl", files=files)
        assert response.status_code == 422

    async def test_import_jsonl_unsupported_format(self, client: AsyncClient) -> None:
        """JSONL with an unsupported explicit format returns 422."""
        files = {"file": ("data.jsonl", VALID_JSONL_OPENAI, "application/jsonlines")}

        response = await client.post(
            "/api/v1/import/jsonl",
            files=files,
            params={"source_format": "unsupported_format"},
        )
        assert response.status_code == 422
