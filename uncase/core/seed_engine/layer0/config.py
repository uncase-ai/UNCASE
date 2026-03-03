"""Layer 0 configuration — settings specific to the agentic extraction loop."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Layer0Config(BaseModel):
    """Configuration for the Layer 0 agentic extraction loop.

    Can be instantiated directly or populated from ``UNCASESettings``.
    """

    # ── Loop limits ─────────────────────────────────────────────────
    max_turns: int = Field(
        default=15,
        ge=3,
        le=50,
        description="Maximum number of interview turns before forced completion.",
    )
    min_confidence_required: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for a required field to be considered complete.",
    )

    # ── Extractor settings ──────────────────────────────────────────
    extractor_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Model identifier for the Extractor (Anthropic Claude).",
    )
    extractor_max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of retries for Extractor API calls.",
    )

    # ── Interviewer settings ────────────────────────────────────────
    interviewer_provider: str = Field(
        default="gemini",
        description="LLM provider for the Interviewer. Options: 'gemini', 'claude'.",
    )
    interviewer_model: str = Field(
        default="gemini-2.5-pro",
        description="Model identifier for the Interviewer LLM.",
    )
    interviewer_max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of retries for Interviewer API calls.",
    )
    interviewer_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for the Interviewer LLM (controls creativity).",
    )

    # ── Industry ────────────────────────────────────────────────────
    industry: str = Field(
        default="automotive",
        description="Industry vertical for the extraction schema.",
    )
    default_locale: str = Field(
        default="es",
        description="Default language for the interview (ISO 639-1).",
    )
