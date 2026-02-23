"""Base domain configuration model."""

from __future__ import annotations

from pydantic import BaseModel, Field

from uncase.tools.schemas import ToolDefinition  # noqa: TC001


class DomainConfig(BaseModel):
    """Configuration for a specific industry domain.

    Each domain defines the namespace, display metadata, typical conversation
    roles and tools, turn-count constraints, and any domain-specific required
    parameters that seeds must provide.
    """

    namespace: str = Field(
        ...,
        description="Dot-separated domain namespace, e.g. 'automotive.sales'.",
    )

    display_name: dict[str, str] = Field(
        ...,
        description="Localized display names keyed by ISO-639-1 locale code.",
    )

    description: dict[str, str] = Field(
        ...,
        description="Localized descriptions keyed by ISO-639-1 locale code.",
    )

    typical_roles: list[str] = Field(
        default_factory=list,
        description="Common participant roles in conversations for this domain.",
    )

    typical_tools: list[str] = Field(
        default_factory=list,
        description="Common tools or systems referenced in conversations for this domain.",
    )

    turnos_min: int = Field(
        default=6,
        ge=1,
        description="Minimum number of turns expected in a conversation.",
    )

    turnos_max: int = Field(
        default=30,
        ge=1,
        description="Maximum number of turns expected in a conversation.",
    )

    required_parametros: list[str] = Field(
        default_factory=list,
        description="Domain-specific parameters that every seed must include.",
    )

    tool_definitions: list[ToolDefinition] | None = Field(
        default=None,
        description="Structured tool definitions for this domain.",
    )
