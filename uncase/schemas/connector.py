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
