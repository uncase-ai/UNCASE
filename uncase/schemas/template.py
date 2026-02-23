"""Template API schemas — Pydantic models for template rendering endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.schemas.conversation import Conversation  # noqa: TC001


class TemplateInfo(BaseModel):
    """Summary information about a registered chat template."""

    name: str = Field(..., description="Snake_case template identifier.")
    display_name: str = Field(..., description="Human-readable template name.")
    supports_tool_calls: bool = Field(..., description="Whether the template can render tool-call turns.")
    special_tokens: list[str] = Field(default_factory=list, description="Special tokens used by this template.")


class RenderRequest(BaseModel):
    """Request body for rendering conversations through a template."""

    conversations: list[Conversation] = Field(..., min_length=1, description="Conversations to render.")
    template_name: str = Field(..., description="Name of the template to use for rendering.")
    tool_call_mode: str = Field(default="none", description="Tool call handling mode: 'none' or 'inline'.")
    system_prompt: str | None = Field(
        default=None,
        description="Optional system prompt prepended to each conversation.",
    )


class RenderResponse(BaseModel):
    """Response body with rendered conversation strings."""

    rendered: list[str] = Field(..., description="Rendered prompt strings, one per conversation.")
    template_name: str = Field(..., description="Name of the template used.")
    count: int = Field(..., ge=0, description="Number of conversations rendered.")
