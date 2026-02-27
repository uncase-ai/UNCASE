"""Scenario template schemas — declarative conversation archetypes.

A ScenarioTemplate captures the *type* of conversation to generate:
the intent, expected tool usage, flow override, skill level, and
distribution weight.  Seeds reference scenarios to guide the
generator toward specific conversation patterns rather than
generic free-form dialogue.

A ScenarioPack groups templates for a domain, making it easy
to ship curated libraries per industry vertical.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScenarioTemplate(BaseModel):
    """Declarative description of a single conversation archetype.

    Instead of hard-coding scenario functions (as in scripts/), this
    model captures the *intent* and *structure* so the LLM generator
    can produce targeted, high-quality conversations.
    """

    name: str = Field(
        ...,
        description="Machine-readable scenario identifier (e.g. 'brand_search', 'frustrated_customer').",
    )

    description: str = Field(
        ...,
        description="Human-readable explanation of the scenario.",
    )

    domain: str = Field(
        ...,
        description="Domain namespace this scenario targets (e.g. 'automotive.sales').",
    )

    intent: str = Field(
        ...,
        description=(
            "Natural-language sentence describing the user's primary intent. "
            "Injected into the system prompt to steer the LLM."
        ),
    )

    skill_level: Literal["basic", "intermediate", "advanced"] = Field(
        default="intermediate",
        description=(
            "Conversation complexity: basic (3-6 turns, single topic), "
            "intermediate (6-12 turns, multi-topic), advanced (10-20+ turns, "
            "multi-step flows with tool chains and edge-case handling)."
        ),
    )

    expected_tool_sequence: list[str] = Field(
        default_factory=list,
        description=(
            "Ordered list of tool names the assistant is expected to call. "
            "Empty for conversations that don't involve tools."
        ),
    )

    flow_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Conversation flow stages that override or refine the seed's "
            "flujo_esperado when this scenario is active. Empty means "
            "use the seed's default flow."
        ),
    )

    edge_case: bool = Field(
        default=False,
        description=(
            "Marks non-happy-path scenarios: frustrated customers, "
            "out-of-scope requests, system errors, boundary enforcement."
        ),
    )

    weight: float = Field(
        default=1.0,
        gt=0.0,
        description=(
            "Relative distribution weight for batch generation. Higher "
            "weight means this scenario is sampled more often."
        ),
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Classification tags for filtering and discovery.",
    )


class ScenarioPack(BaseModel):
    """A curated collection of scenario templates for a domain.

    Scenario packs ship as built-in domain libraries and can be
    extended by users or community plugins.
    """

    id: str = Field(
        ...,
        description="Unique pack identifier (e.g. 'automotive-sales-scenarios').",
    )

    name: str = Field(
        ...,
        description="Human-readable display name.",
    )

    description: str = Field(
        ...,
        description="What this scenario pack covers.",
    )

    domain: str = Field(
        ...,
        description="Target domain namespace.",
    )

    version: str = Field(
        default="1.0.0",
        description="Semantic version.",
    )

    scenarios: list[ScenarioTemplate] = Field(
        ...,
        min_length=1,
        description="Scenario templates included in this pack.",
    )

    @property
    def scenario_names(self) -> list[str]:
        """List of scenario names in this pack."""
        return [s.name for s in self.scenarios]

    @property
    def total_weight(self) -> float:
        """Sum of all scenario weights (for normalization)."""
        return sum(s.weight for s in self.scenarios)
