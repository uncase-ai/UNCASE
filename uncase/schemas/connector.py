"""API request/response schemas for connector endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001


class PIIEntityResponse(BaseModel):
    """A single detected PII entity."""

    category: str = Field(..., description="PII category (email, phone, ssn, etc.)")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    score: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    source: str = Field(..., description="Detection source: regex or presidio")


class ConnectorImportResponse(BaseModel):
    """Response body for connector import operations."""

    conversations: list[Conversation] = Field(..., description="Imported and anonymized conversations")
    total_imported: int = Field(..., ge=0, description="Number of conversations imported")
    total_skipped: int = Field(default=0, ge=0, description="Conversations skipped (too short, etc.)")
    total_pii_anonymized: int = Field(default=0, ge=0, description="Total PII entities found and anonymized")
    errors: list[str] = Field(default_factory=list, description="Parsing errors encountered")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")


class WebhookPayload(BaseModel):
    """Expected webhook JSON structure."""

    conversations: list[dict[str, object]] = Field(
        ...,
        min_length=1,
        description="Array of conversation objects with 'turns' arrays",
    )


class PIIScanResponse(BaseModel):
    """Response showing PII scan results for a text."""

    text_length: int = Field(..., description="Length of scanned text")
    pii_found: bool = Field(..., description="Whether any PII was detected")
    entity_count: int = Field(..., ge=0, description="Number of PII entities found")
    entities: list[PIIEntityResponse] = Field(default_factory=list, description="Detected PII entities")
    anonymized_preview: str = Field(default="", description="Text with PII replaced by tokens")
    scanner_mode: str = Field(..., description="Scanner capabilities: regex_only or regex+presidio")


class HFDatasetInfoResponse(BaseModel):
    """Metadata for a Hugging Face dataset."""

    repo_id: str = Field(..., description="Repository identifier (user/dataset)")
    description: str | None = Field(default=None, description="Dataset description")
    downloads: int = Field(default=0, ge=0, description="Download count")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    tags: list[str] = Field(default_factory=list, description="Dataset tags")
    last_modified: str = Field(default="", description="Last modification timestamp")
    size_bytes: int | None = Field(default=None, description="Dataset size in bytes")


class HFUploadRequest(BaseModel):
    """Request body for uploading conversations to Hugging Face."""

    conversation_ids: list[str] = Field(
        ...,
        min_length=1,
        description="IDs of conversations to upload",
    )
    repo_id: str = Field(..., description="Target HuggingFace dataset repo (user/dataset)")
    token: str = Field(..., description="HuggingFace API token")
    private: bool = Field(default=False, description="Create as private repository")


class HFUploadResponse(BaseModel):
    """Response from uploading to Hugging Face."""

    repo_id: str = Field(..., description="Repository identifier")
    url: str = Field(..., description="URL of the uploaded dataset")
    commit_hash: str = Field(default="", description="Git commit hash of the upload")
    files_uploaded: int = Field(default=0, ge=0, description="Number of files uploaded")
