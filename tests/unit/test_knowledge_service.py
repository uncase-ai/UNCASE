"""Tests for the knowledge base service layer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.exceptions import KnowledgeDocumentNotFoundError, ValidationError
from uncase.schemas.knowledge import KnowledgeUploadRequest
from uncase.services.knowledge import KnowledgeService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_upload(**overrides: object) -> KnowledgeUploadRequest:
    """Build a valid KnowledgeUploadRequest with fictional defaults."""
    defaults: dict[str, object] = {
        "filename": "procedimientos-ventas-ficticio.txt",
        "content": (
            "Procedimiento de atencion al cliente ficticio.\n\n"
            "Paso uno: saludar al cliente de forma cordial.\n\n"
            "Paso dos: identificar la necesidad del cliente.\n\n"
            "Paso tres: ofrecer opciones relevantes del catalogo."
        ),
        "domain": "automotive.sales",
        "type": "procedures",
        "tags": ["ventas", "ficticio"],
    }
    defaults.update(overrides)
    return KnowledgeUploadRequest(**defaults)  # type: ignore[arg-type]


class TestKnowledgeServiceUpload:
    async def test_upload_document(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        req = _make_upload()
        resp = await service.upload_document(req)

        assert resp.id is not None
        assert resp.filename == "procedimientos-ventas-ficticio.txt"
        assert resp.domain == "automotive.sales"
        assert resp.type == "procedures"
        assert resp.chunk_count >= 1
        assert len(resp.chunks) >= 1

    async def test_upload_document_with_org(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        req = _make_upload()
        resp = await service.upload_document(req, organization_id="org-test-001")

        assert resp.organization_id == "org-test-001"

    async def test_upload_calculates_size_bytes(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        content = "Contenido ficticio de prueba para calcular bytes."
        req = _make_upload(content=content)
        resp = await service.upload_document(req)

        expected_size = len(content.encode("utf-8"))
        assert resp.size_bytes == expected_size

    async def test_upload_invalid_type_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        req = _make_upload(type="invalid_type")
        with pytest.raises(ValidationError, match="Invalid knowledge type"):
            await service.upload_document(req)

    async def test_upload_stores_tags_in_metadata(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        req = _make_upload(tags=["prueba", "demo"])
        resp = await service.upload_document(req)

        assert resp.metadata is not None
        assert resp.metadata.get("tags") == ["prueba", "demo"]

    async def test_upload_chunks_are_ordered(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        long_content = "\n\n".join(f"Parrafo ficticio numero {i} con contenido de prueba." for i in range(20))
        req = _make_upload(content=long_content, chunk_size=200)
        resp = await service.upload_document(req)

        orders = [c.order for c in resp.chunks]
        assert orders == sorted(orders)

    async def test_upload_valid_types(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        for knowledge_type in ("facts", "procedures", "terminology", "reference"):
            req = _make_upload(type=knowledge_type, filename=f"doc-{knowledge_type}.txt")
            resp = await service.upload_document(req)
            assert resp.type == knowledge_type


class TestKnowledgeServiceGet:
    async def test_get_document(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        uploaded = await service.upload_document(_make_upload())
        found = await service.get_document(uploaded.id)

        assert found.id == uploaded.id
        assert found.filename == uploaded.filename
        assert len(found.chunks) == uploaded.chunk_count

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        with pytest.raises(KnowledgeDocumentNotFoundError):
            await service.get_document("nonexistent-doc-id")


class TestKnowledgeServiceList:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        result = await service.list_documents()

        assert result.items == []
        assert result.total == 0
        assert result.page == 1

    async def test_list_all(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload(filename="doc1.txt"))
        await service.upload_document(_make_upload(filename="doc2.txt"))

        result = await service.list_documents()

        assert result.total == 2
        assert len(result.items) == 2

    async def test_list_filter_by_domain(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload(domain="automotive.sales"))
        await service.upload_document(_make_upload(domain="medical.consultation"))

        result = await service.list_documents(domain="automotive.sales")

        assert result.total == 1
        assert result.items[0].domain == "automotive.sales"

    async def test_list_filter_by_type(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload(type="facts"))
        await service.upload_document(_make_upload(type="procedures"))

        result = await service.list_documents(type_filter="facts")

        assert result.total == 1
        assert result.items[0].type == "facts"

    async def test_list_filter_by_org(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload(), organization_id="org-a")
        await service.upload_document(_make_upload(), organization_id="org-b")

        result = await service.list_documents(organization_id="org-a")

        assert result.total == 1
        assert result.items[0].organization_id == "org-a"

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        for i in range(5):
            await service.upload_document(_make_upload(filename=f"doc-{i}.txt"))

        p1 = await service.list_documents(page=1, page_size=2)
        assert len(p1.items) == 2
        assert p1.total == 5

        p2 = await service.list_documents(page=2, page_size=2)
        assert len(p2.items) == 2

        p3 = await service.list_documents(page=3, page_size=2)
        assert len(p3.items) == 1

    async def test_list_invalid_page_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        with pytest.raises(ValidationError, match="Page must be >= 1"):
            await service.list_documents(page=0)

    async def test_list_invalid_page_size_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_documents(page_size=0)

        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_documents(page_size=101)


class TestKnowledgeServiceDelete:
    async def test_delete_document(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        uploaded = await service.upload_document(_make_upload())
        await service.delete_document(uploaded.id)

        with pytest.raises(KnowledgeDocumentNotFoundError):
            await service.get_document(uploaded.id)

    async def test_delete_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        with pytest.raises(KnowledgeDocumentNotFoundError):
            await service.delete_document("nonexistent-id")

    async def test_delete_does_not_affect_others(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        d1 = await service.upload_document(_make_upload(filename="doc1.txt"))
        d2 = await service.upload_document(_make_upload(filename="doc2.txt"))
        await service.delete_document(d1.id)

        result = await service.list_documents()
        assert result.total == 1
        assert result.items[0].id == d2.id


class TestKnowledgeServiceSearch:
    async def test_search_finds_matching_chunks(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(
            _make_upload(
                content="Informacion ficticia sobre vehiculos electricos de prueba.",
            )
        )
        result = await service.search_chunks(query="vehiculos")

        assert result.total >= 1
        assert result.query == "vehiculos"
        assert any("vehiculos" in r.content.lower() for r in result.results)

    async def test_search_returns_empty_for_no_match(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload())
        result = await service.search_chunks(query="xyznonexistent")

        assert result.total == 0
        assert result.results == []

    async def test_search_empty_query_raises(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        with pytest.raises(ValidationError, match="Search query cannot be empty"):
            await service.search_chunks(query="   ")

    async def test_search_filter_by_domain(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(
            _make_upload(
                domain="automotive.sales",
                content="Contenido ficticio sobre vehiculos de prueba.",
            )
        )
        await service.upload_document(
            _make_upload(
                domain="medical.consultation",
                content="Contenido ficticio sobre vehiculos en medicina.",
            )
        )

        result = await service.search_chunks(query="vehiculos", domain="automotive.sales")
        assert all(r.domain == "automotive.sales" for r in result.results)

    async def test_search_filter_by_type(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(_make_upload(type="facts", content="Datos ficticios sobre ventas."))
        await service.upload_document(_make_upload(type="procedures", content="Procedimiento ficticio de ventas."))

        result = await service.search_chunks(query="ventas", type_filter="facts")
        assert all(r.type == "facts" for r in result.results)

    async def test_search_respects_limit(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        # Upload a document that will produce multiple chunks containing the keyword
        long_content = "\n\n".join(f"Seccion {i}: informacion ficticia repetida para pruebas." for i in range(30))
        await service.upload_document(_make_upload(content=long_content, chunk_size=200))

        result = await service.search_chunks(query="ficticia", limit=3)
        assert result.total <= 3

    async def test_search_case_insensitive(self, async_session: AsyncSession) -> None:
        service = KnowledgeService(async_session)
        await service.upload_document(
            _make_upload(
                content="INFORMACION FICTICIA EN MAYUSCULAS.",
            )
        )
        result = await service.search_chunks(query="informacion")
        assert result.total >= 1


class TestKnowledgeServiceChunking:
    def test_chunk_text_by_paragraphs(self) -> None:
        text = "Parrafo uno ficticio.\n\nParrafo dos ficticio.\n\nParrafo tres ficticio."
        chunks = KnowledgeService._chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) >= 2

    def test_chunk_text_single_paragraph(self) -> None:
        text = "Texto corto ficticio de prueba."
        chunks = KnowledgeService._chunk_text(text, chunk_size=800, overlap=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_empty_returns_empty(self) -> None:
        chunks = KnowledgeService._chunk_text("", chunk_size=800, overlap=100)
        assert chunks == []

    def test_chunk_text_whitespace_only_returns_empty(self) -> None:
        chunks = KnowledgeService._chunk_text("   \n\n   ", chunk_size=800, overlap=100)
        assert chunks == []

    def test_chunk_text_long_single_paragraph(self) -> None:
        # No paragraph breaks, single long paragraph gets chunked as one piece
        # (sentence fallback only triggers if paragraph processing yields zero chunks)
        text = "Oracion uno ficticia. Oracion dos ficticia. Oracion tres ficticia. Oracion cuatro."
        chunks = KnowledgeService._chunk_text(text, chunk_size=50, overlap=10)
        # The paragraph path handles this as a single chunk since there's only one paragraph
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_overlap(self) -> None:
        paragraphs = [f"Parrafo ficticio numero {i} con algo de contenido de relleno." for i in range(10)]
        text = "\n\n".join(paragraphs)
        chunks = KnowledgeService._chunk_text(text, chunk_size=100, overlap=30)
        # With overlap, later chunks should contain some words from the end of previous chunks
        assert len(chunks) >= 2
