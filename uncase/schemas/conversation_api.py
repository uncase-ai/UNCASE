"""Conversation CRUD API request and response schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from uncase.schemas.conversation import ConversationTurn

if TYPE_CHECKING:
    from datetime import datetime


class ConversationCreateRequest(BaseModel):
    """Request body for persisting a conversation."""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    seed_id: str | None = Field(default=None, description="Origin seed ID")
    dominio: str = Field(..., description="Domain namespace")
    idioma: str = Field(default="es", description="Conversation language")
    turnos: list[ConversationTurn] = Field(..., min_length=1, description="Conversation turns")
    es_sintetica: bool = Field(default=False, description="Whether this is synthetic data")
    metadata: dict[str, object] = Field(default_factory=dict, description="Extra metadata")
    status: str | None = Field(default=None, description="Validation status (valid/invalid)")
    rating: float | None = Field(default=None, description="User rating")
    tags: list[str] | None = Field(default=None, description="User-defined tags")
    notes: str | None = Field(default=None, description="User notes")


class ConversationUpdateRequest(BaseModel):
    """Partial update — only provided fields are changed."""

    status: str | None = Field(default=None, description="Validation status")
    rating: float | None = Field(default=None, description="User rating")
    tags: list[str] | None = Field(default=None, description="User-defined tags")
    notes: str | None = Field(default=None, description="User notes")
    metadata: dict[str, object] | None = Field(default=None, description="Extra metadata")


class ConversationResponse(BaseModel):
    """API response for a single conversation."""

    id: str = Field(..., description="Database primary key")
    conversation_id: str
    seed_id: str | None
    dominio: str
    idioma: str
    turnos: list[ConversationTurn]
    es_sintetica: bool
    num_turnos: int
    metadata: dict[str, object] = Field(default_factory=dict, alias="metadata_json")
    status: str | None
    rating: float | None
    tags: list[str] | None
    notes: str | None
    organization_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ConversationListResponse(BaseModel):
    """Paginated list of conversations."""

    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int


class ConversationBulkCreateRequest(BaseModel):
    """Bulk-create multiple conversations at once."""

    conversations: list[ConversationCreateRequest] = Field(..., min_length=1, max_length=100)


class ConversationBulkCreateResponse(BaseModel):
    """Result of a bulk-create operation."""

    created: int
    skipped: int
    errors: list[str]


# Rebuild models that reference TYPE_CHECKING-only imports
def _rebuild_models() -> None:
    from datetime import datetime as _dt

    ns = {"datetime": _dt}
    ConversationResponse.model_rebuild(_types_namespace=ns)
    ConversationListResponse.model_rebuild(_types_namespace=ns)


_rebuild_models()
del _rebuild_models
