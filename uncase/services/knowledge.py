"""Knowledge base service layer."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from uncase.db.models.knowledge import KnowledgeChunkModel, KnowledgeDocumentModel
from uncase.exceptions import KnowledgeDocumentNotFoundError, ValidationError
from uncase.logging import get_logger
from uncase.schemas.knowledge import (
    KnowledgeChunkResponse,
    KnowledgeDocumentResponse,
    KnowledgeDocumentSummary,
    KnowledgeListResponse,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeUploadRequest,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

VALID_TYPES = {"facts", "procedures", "terminology", "reference"}


class KnowledgeService:
    """Service for knowledge base CRUD and search."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upload_document(
        self,
        data: KnowledgeUploadRequest,
        *,
        organization_id: str | None = None,
    ) -> KnowledgeDocumentResponse:
        """Upload a document: chunk the text and persist to DB."""
        if data.type not in VALID_TYPES:
            raise ValidationError(f"Invalid knowledge type: {data.type}. Must be one of {VALID_TYPES}")

        raw_chunks = self._chunk_text(data.content, data.chunk_size, data.chunk_overlap)
        doc_id = uuid.uuid4().hex

        doc_model = KnowledgeDocumentModel(
            id=doc_id,
            filename=data.filename,
            domain=data.domain,
            type=data.type,
            chunk_count=len(raw_chunks),
            size_bytes=len(data.content.encode("utf-8")),
            organization_id=organization_id,
            metadata_={"tags": data.tags},
        )

        chunk_models = [
            KnowledgeChunkModel(
                id=uuid.uuid4().hex,
                document_id=doc_id,
                content=content,
                type=data.type,
                domain=data.domain,
                tags=data.tags,
                source=data.filename,
                order=i,
            )
            for i, content in enumerate(raw_chunks)
        ]

        self.session.add(doc_model)
        self.session.add_all(chunk_models)
        await self.session.commit()
        await self.session.refresh(doc_model)

        logger.info(
            "knowledge_document_uploaded",
            doc_id=doc_id,
            filename=data.filename,
            domain=data.domain,
            chunk_count=len(raw_chunks),
        )

        return self._to_doc_response(doc_model, chunk_models)

    async def get_document(self, doc_id: str) -> KnowledgeDocumentResponse:
        """Get a document with all its chunks."""
        doc = await self._get_doc_or_raise(doc_id)
        return self._to_doc_response(doc, list(doc.chunks))

    async def list_documents(
        self,
        *,
        domain: str | None = None,
        type_filter: str | None = None,
        organization_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> KnowledgeListResponse:
        """List knowledge documents with optional filters."""
        if page < 1:
            raise ValidationError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100")

        query = select(KnowledgeDocumentModel)
        count_query = select(func.count()).select_from(KnowledgeDocumentModel)

        if domain is not None:
            query = query.where(KnowledgeDocumentModel.domain == domain)
            count_query = count_query.where(KnowledgeDocumentModel.domain == domain)

        if type_filter is not None:
            query = query.where(KnowledgeDocumentModel.type == type_filter)
            count_query = count_query.where(KnowledgeDocumentModel.type == type_filter)

        if organization_id is not None:
            query = query.where(KnowledgeDocumentModel.organization_id == organization_id)
            count_query = count_query.where(KnowledgeDocumentModel.organization_id == organization_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(KnowledgeDocumentModel.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(query)
        docs = result.scalars().all()

        return KnowledgeListResponse(
            items=[self._to_summary(d) for d in docs],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def delete_document(self, doc_id: str) -> None:
        """Delete a document and all its chunks (CASCADE)."""
        doc = await self._get_doc_or_raise(doc_id)
        await self.session.delete(doc)
        await self.session.commit()

        logger.info("knowledge_document_deleted", doc_id=doc_id)

    async def search_chunks(
        self,
        *,
        query: str,
        domain: str | None = None,
        type_filter: str | None = None,
        organization_id: str | None = None,
        limit: int = 20,
    ) -> KnowledgeSearchResponse:
        """Search chunks by content keyword match."""
        if not query.strip():
            raise ValidationError("Search query cannot be empty")

        search_term = f"%{query.strip().lower()}%"

        stmt = (
            select(KnowledgeChunkModel, KnowledgeDocumentModel.filename)
            .join(KnowledgeDocumentModel, KnowledgeChunkModel.document_id == KnowledgeDocumentModel.id)
            .where(func.lower(KnowledgeChunkModel.content).like(search_term))
        )

        if domain is not None:
            stmt = stmt.where(KnowledgeChunkModel.domain == domain)

        if type_filter is not None:
            stmt = stmt.where(KnowledgeChunkModel.type == type_filter)

        if organization_id is not None:
            stmt = stmt.where(KnowledgeDocumentModel.organization_id == organization_id)

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.all()

        results = [
            KnowledgeSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                filename=filename,
                content=chunk.content,
                type=chunk.type,
                domain=chunk.domain,
                tags=chunk.tags or [],
                order=chunk.order,
            )
            for chunk, filename in rows
        ]

        return KnowledgeSearchResponse(
            query=query.strip(),
            results=results,
            total=len(results),
        )

    # -- Helpers --

    async def _get_doc_or_raise(self, doc_id: str) -> KnowledgeDocumentModel:
        """Fetch a document with chunks or raise KnowledgeDocumentNotFoundError."""
        result = await self.session.execute(
            select(KnowledgeDocumentModel)
            .options(selectinload(KnowledgeDocumentModel.chunks))
            .where(KnowledgeDocumentModel.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            raise KnowledgeDocumentNotFoundError(f"Knowledge document '{doc_id}' not found")
        return doc

    @staticmethod
    def _to_doc_response(
        doc: KnowledgeDocumentModel,
        chunks: list[KnowledgeChunkModel],
    ) -> KnowledgeDocumentResponse:
        return KnowledgeDocumentResponse(
            id=doc.id,
            filename=doc.filename,
            domain=doc.domain,
            type=doc.type,
            chunk_count=doc.chunk_count,
            size_bytes=doc.size_bytes,
            organization_id=doc.organization_id,
            metadata=doc.metadata_,
            chunks=[
                KnowledgeChunkResponse(
                    id=c.id,
                    document_id=c.document_id,
                    content=c.content,
                    type=c.type,
                    domain=c.domain,
                    tags=c.tags or [],
                    source=c.source,
                    order=c.order,
                    created_at=c.created_at.isoformat() if c.created_at else "",
                )
                for c in sorted(chunks, key=lambda x: x.order)
            ],
            created_at=doc.created_at.isoformat() if doc.created_at else "",
            updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        )

    @staticmethod
    def _to_summary(doc: KnowledgeDocumentModel) -> KnowledgeDocumentSummary:
        return KnowledgeDocumentSummary(
            id=doc.id,
            filename=doc.filename,
            domain=doc.domain,
            type=doc.type,
            chunk_count=doc.chunk_count,
            size_bytes=doc.size_bytes,
            organization_id=doc.organization_id,
            metadata=doc.metadata_,
            created_at=doc.created_at.isoformat() if doc.created_at else "",
            updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        )

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
        """Chunk text by paragraphs with overlap, falling back to sentences."""
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            trimmed = para.strip()
            if not trimmed:
                continue

            if len(current) + len(trimmed) > chunk_size and current:
                chunks.append(current.strip())
                # Keep tail for overlap
                words = current.split()
                overlap_words = max(1, overlap // 5)
                current = " ".join(words[-overlap_words:]) + "\n\n" + trimmed
            else:
                current += ("\n\n" if current else "") + trimmed

        if current.strip():
            chunks.append(current.strip())

        # Fallback: if no paragraph breaks, chunk by sentences
        if not chunks and text.strip():
            import re

            sentences = re.split(r"(?<=[.!?])\s+", text)
            buf = ""
            for s in sentences:
                if len(buf) + len(s) > chunk_size and buf:
                    chunks.append(buf.strip())
                    buf = s
                else:
                    buf += (" " if buf else "") + s
            if buf.strip():
                chunks.append(buf.strip())

        return chunks
