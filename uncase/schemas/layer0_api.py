"""Layer 0 extraction API — request and response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StartExtractionRequest(BaseModel):
    """Request to start a new agentic extraction session."""

    industry: str = Field(
        default="automotive",
        description="Industry vertical (e.g. 'automotive').",
    )
    max_turns: int = Field(
        default=15,
        ge=3,
        le=50,
        description="Maximum interview turns.",
    )
    locale: str = Field(
        default="es",
        description="Interview language (ISO 639-1).",
    )


class StartExtractionResponse(BaseModel):
    """Response after starting an extraction session."""

    session_id: str = Field(..., description="Unique session identifier.")
    message: dict[str, Any] = Field(..., description="Initial question message from the engine.")


class TurnRequest(BaseModel):
    """Request for a single conversation turn."""

    session_id: str = Field(..., description="Session identifier.")
    user_message: str = Field(..., min_length=1, description="User's response text.")


class TurnResponse(BaseModel):
    """Response after processing a conversation turn."""

    session_id: str = Field(..., description="Session identifier.")
    message: dict[str, Any] = Field(
        ...,
        description="Engine response: question, clarification, or summary.",
    )
    is_complete: bool = Field(
        default=False,
        description="Whether the extraction session is finished.",
    )


class ProgressResponse(BaseModel):
    """Current extraction progress snapshot."""

    session_id: str
    progress: dict[str, Any]
