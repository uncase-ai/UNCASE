"""Import result schemas — Pydantic models for file import endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001


class ImportErrorDetail(BaseModel):
    """Describes a single error encountered during file import."""

    line: int = Field(..., ge=1, description="Line number where the error occurred.")
    error: str = Field(..., min_length=1, description="Human-readable error description.")


class ImportResult(BaseModel):
    """Aggregate result of a file import operation."""

    conversations_imported: int = Field(..., ge=0, description="Number of conversations successfully imported.")
    conversations_failed: int = Field(..., ge=0, description="Number of conversations that failed to import.")
    errors: list[ImportErrorDetail] = Field(default_factory=list, description="Details of individual import errors.")
    conversations: list[Conversation] = Field(
        default_factory=list,
        description="Successfully imported conversations.",
    )
