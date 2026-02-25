"""API request/response schemas for the knowledge base."""

from __future__ import annotations

from pydantic import BaseModel, Field

KNOWLEDGE_TYPES = ["facts", "procedures", "terminology", "reference"]


class KnowledgeUploadRequest(BaseModel):
    """Request body for uploading a knowledge document (JSON mode)."""

    filename: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=1, description="Plain text content to chunk and store")
    domain: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., description="facts, procedures, terminology, reference")
    tags: list[str] = Field(default_factory=list, description="Tags for chunk classification")
    chunk_size: int = Field(default=800, ge=100, le=4000, description="Target chunk size in characters")
    chunk_overlap: int = Field(default=100, ge=0, le=500, description="Overlap between consecutive chunks")


class KnowledgeChunkResponse(BaseModel):
    """A single text chunk from a knowledge document."""

    id: str
    document_id: str
    content: str
    type: str
    domain: str
    tags: list[str]
    source: str
    order: int
    created_at: str

    model_config = {"from_attributes": True}


class KnowledgeDocumentResponse(BaseModel):
    """A knowledge document with its chunks."""

    id: str
    filename: str
    domain: str
    type: str
    chunk_count: int
    size_bytes: int | None
    organization_id: str | None
    metadata: dict[str, object] | None
    chunks: list[KnowledgeChunkResponse] = Field(default_factory=list)
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class KnowledgeDocumentSummary(BaseModel):
    """Document summary without chunks (for list endpoints)."""

    id: str
    filename: str
    domain: str
    type: str
    chunk_count: int
    size_bytes: int | None
    organization_id: str | None
    metadata: dict[str, object] | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class KnowledgeListResponse(BaseModel):
    """Paginated list of knowledge documents."""

    items: list[KnowledgeDocumentSummary]
    total: int
    page: int
    page_size: int


class KnowledgeSearchResult(BaseModel):
    """A chunk matching a search query."""

    chunk_id: str
    document_id: str
    filename: str
    content: str
    type: str
    domain: str
    tags: list[str]
    order: int
    relevance: str = Field(default="keyword", description="Match method: keyword")


class KnowledgeSearchResponse(BaseModel):
    """Search results across knowledge chunks."""

    query: str
    results: list[KnowledgeSearchResult]
    total: int
