"""Knowledge base document and chunk models."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uncase.db.base import Base


class KnowledgeDocumentModel(Base):
    """A knowledge document uploaded to the platform.

    Documents are chunked on upload and stored alongside their chunks.
    Linked to an organization for multi-tenant isolation.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="facts, procedures, terminology, reference",
    )
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_: Mapped[dict[str, object] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    chunks: Mapped[list[KnowledgeChunkModel]] = relationship(
        "KnowledgeChunkModel",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="KnowledgeChunkModel.order",
    )

    __table_args__ = (Index("ix_knowledge_docs_org_domain", "organization_id", "domain"),)


class KnowledgeChunkModel(Base):
    """A text chunk extracted from a knowledge document."""

    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    document_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    # Relationships
    document: Mapped[KnowledgeDocumentModel] = relationship(
        "KnowledgeDocumentModel",
        back_populates="chunks",
    )

    __table_args__ = (
        Index("ix_knowledge_chunks_doc", "document_id"),
        Index("ix_knowledge_chunks_domain_type", "domain", "type"),
    )
