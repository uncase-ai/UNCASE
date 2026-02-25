"""Integration tests for the Knowledge API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.db.models.knowledge import KnowledgeChunkModel, KnowledgeDocumentModel

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


def _knowledge_upload_payload(**overrides: object) -> dict[str, object]:
    """Build a valid KnowledgeUploadRequest payload with fictional content."""
    payload: dict[str, object] = {
        "filename": "fictional-automotive-guide.txt",
        "content": (
            "Guia de ventas de vehiculos ficticios.\n\n"
            "Capitulo 1: Introduccion al inventario ficticio. "
            "En el concesionario ficticio contamos con una amplia gama de vehiculos. "
            "Todos los datos aqui presentados son completamente ficticios.\n\n"
            "Capitulo 2: Proceso de venta ficticio. "
            "El proceso de venta sigue un flujo estandar: saludo, identificacion "
            "de necesidades, presentacion de opciones y cierre."
        ),
        "domain": "automotive.sales",
        "type": "procedures",
        "tags": ["automotive", "sales", "fictional"],
        "chunk_size": 200,
        "chunk_overlap": 50,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
async def sample_document(async_session: AsyncSession) -> KnowledgeDocumentModel:
    """Create a sample knowledge document with chunks directly in the DB."""
    doc = KnowledgeDocumentModel(
        id="doc-test-001",
        filename="fictional-procedures.txt",
        domain="automotive.sales",
        type="procedures",
        chunk_count=2,
        size_bytes=300,
        organization_id=None,
        metadata_={"tags": ["test"]},
    )
    chunk1 = KnowledgeChunkModel(
        id="chunk-001",
        document_id="doc-test-001",
        content="Procedimiento ficticio de saludo al cliente en el concesionario.",
        type="procedures",
        domain="automotive.sales",
        tags=["test"],
        source="fictional-procedures.txt",
        order=0,
    )
    chunk2 = KnowledgeChunkModel(
        id="chunk-002",
        document_id="doc-test-001",
        content="Procedimiento ficticio de cierre de venta de vehiculo.",
        type="procedures",
        domain="automotive.sales",
        tags=["test"],
        source="fictional-procedures.txt",
        order=1,
    )
    async_session.add(doc)
    async_session.add_all([chunk1, chunk2])
    await async_session.commit()
    await async_session.refresh(doc)
    return doc


@pytest.fixture()
async def medical_document(async_session: AsyncSession) -> KnowledgeDocumentModel:
    """Create a second document in the medical domain."""
    doc = KnowledgeDocumentModel(
        id="doc-test-002",
        filename="fictional-medical-terms.txt",
        domain="medical.consultation",
        type="terminology",
        chunk_count=1,
        size_bytes=100,
        organization_id=None,
        metadata_={"tags": ["medical"]},
    )
    chunk = KnowledgeChunkModel(
        id="chunk-003",
        document_id="doc-test-002",
        content="Terminologia medica ficticia para consultas generales.",
        type="terminology",
        domain="medical.consultation",
        tags=["medical"],
        source="fictional-medical-terms.txt",
        order=0,
    )
    async_session.add(doc)
    async_session.add(chunk)
    await async_session.commit()
    await async_session.refresh(doc)
    return doc


@pytest.mark.integration
class TestUploadDocument:
    """Test POST /api/v1/knowledge."""

    async def test_upload_document(self, client: AsyncClient) -> None:
        payload = _knowledge_upload_payload()
        response = await client.post("/api/v1/knowledge", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "fictional-automotive-guide.txt"
        assert data["domain"] == "automotive.sales"
        assert data["type"] == "procedures"
        assert data["chunk_count"] >= 1
        assert "id" in data
        assert isinstance(data["chunks"], list)
        assert len(data["chunks"]) == data["chunk_count"]

    async def test_upload_document_invalid_type(self, client: AsyncClient) -> None:
        payload = _knowledge_upload_payload(type="invalid_type")
        response = await client.post("/api/v1/knowledge", json=payload)
        assert response.status_code == 422

    async def test_upload_document_missing_content(self, client: AsyncClient) -> None:
        payload = _knowledge_upload_payload()
        del payload["content"]  # type: ignore[arg-type]
        response = await client.post("/api/v1/knowledge", json=payload)
        assert response.status_code == 422

    async def test_upload_document_empty_filename(self, client: AsyncClient) -> None:
        payload = _knowledge_upload_payload(filename="")
        response = await client.post("/api/v1/knowledge", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestListDocuments:
    """Test GET /api/v1/knowledge."""

    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_with_document(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.get("/api/v1/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "doc-test-001"

    async def test_filter_by_domain(
        self,
        client: AsyncClient,
        sample_document: KnowledgeDocumentModel,
        medical_document: KnowledgeDocumentModel,
    ) -> None:
        response = await client.get("/api/v1/knowledge", params={"domain": "medical.consultation"})
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["domain"] == "medical.consultation"

    async def test_filter_by_type(
        self,
        client: AsyncClient,
        sample_document: KnowledgeDocumentModel,
        medical_document: KnowledgeDocumentModel,
    ) -> None:
        response = await client.get("/api/v1/knowledge", params={"type": "terminology"})
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["type"] == "terminology"

    async def test_pagination(
        self,
        client: AsyncClient,
        sample_document: KnowledgeDocumentModel,
        medical_document: KnowledgeDocumentModel,
    ) -> None:
        response = await client.get("/api/v1/knowledge", params={"page": 1, "page_size": 1})
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 1


@pytest.mark.integration
class TestGetDocument:
    """Test GET /api/v1/knowledge/{doc_id}."""

    async def test_get_existing(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.get(f"/api/v1/knowledge/{sample_document.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_document.id
        assert data["filename"] == "fictional-procedures.txt"
        assert len(data["chunks"]) == 2
        # Chunks should be ordered
        assert data["chunks"][0]["order"] == 0
        assert data["chunks"][1]["order"] == 1

    async def test_get_nonexistent(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/knowledge/nonexistent-doc-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestDeleteDocument:
    """Test DELETE /api/v1/knowledge/{doc_id}."""

    async def test_delete_existing(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.delete(f"/api/v1/knowledge/{sample_document.id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(f"/api/v1/knowledge/{sample_document.id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent(self, client: AsyncClient) -> None:
        response = await client.delete("/api/v1/knowledge/nonexistent-doc")
        assert response.status_code == 404


@pytest.mark.integration
class TestSearchChunks:
    """Test GET /api/v1/knowledge/search."""

    async def test_search_matching(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.get("/api/v1/knowledge/search", params={"q": "saludo"})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "saludo"
        assert data["total"] >= 1
        assert len(data["results"]) >= 1

    async def test_search_no_results(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.get("/api/v1/knowledge/search", params={"q": "xyznonexistent"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["results"] == []

    async def test_search_filter_by_domain(
        self,
        client: AsyncClient,
        sample_document: KnowledgeDocumentModel,
        medical_document: KnowledgeDocumentModel,
    ) -> None:
        response = await client.get(
            "/api/v1/knowledge/search",
            params={"q": "fictici", "domain": "medical.consultation"},
        )
        data = response.json()
        for result in data["results"]:
            assert result["domain"] == "medical.consultation"

    async def test_search_missing_query(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/knowledge/search")
        assert response.status_code == 422

    async def test_search_with_limit(self, client: AsyncClient, sample_document: KnowledgeDocumentModel) -> None:
        response = await client.get("/api/v1/knowledge/search", params={"q": "fictici", "limit": 1})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 1
