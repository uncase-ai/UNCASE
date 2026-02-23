"""Pydantic models for the UNCASE tool system.

Defines the data contracts used to declare, invoke, and return results
from tools that are injected into synthetic conversations.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Describes a single parameter accepted by a tool.

    Used for documentation and runtime validation of tool arguments.
    """

    name: str = Field(..., description="Parameter name.")
    type: str = Field(..., description="JSON Schema type (string, number, boolean, object, array, etc.).")
    description: str = Field(..., description="Human-readable description of the parameter.")
    required: bool = Field(default=True, description="Whether the parameter is required.")
    enum: list[str] | None = Field(default=None, description="Allowed values, if restricted to a fixed set.")
    default: Any = Field(default=None, description="Default value when the parameter is optional.")


class ToolDefinition(BaseModel):
    """Declarative specification of a tool available inside the SCSF pipeline.

    Each tool is identified by a unique snake_case *name* and carries its
    input/output JSON Schemas so the generator can produce valid tool-call
    turns and the evaluator can verify them.
    """

    name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Unique snake_case identifier for the tool.",
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Human-readable description of what the tool does.",
    )
    input_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema dict describing the tool's expected input.",
    )
    output_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema dict describing the tool's output structure.",
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Domain namespaces where this tool is applicable (e.g. 'automotive.sales').",
    )
    category: str = Field(
        default="",
        description="Logical category for grouping related tools (e.g. 'crm', 'inventory').",
    )
    requires_auth: bool = Field(
        default=False,
        description="Whether the tool requires authentication to execute.",
    )
    execution_mode: Literal["simulated", "live", "mock"] = Field(
        default="simulated",
        description="How the tool is executed: simulated (default), live, or mock.",
    )
    version: str = Field(
        default="1.0",
        description="Semantic version of the tool definition.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary extra metadata attached to the tool.",
    )


class ToolCall(BaseModel):
    """Represents an invocation of a tool within a conversation turn.

    Each call is assigned a unique *tool_call_id* so the corresponding
    ``ToolResult`` can reference it unambiguously.
    """

    tool_call_id: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        description="Unique identifier for this tool call.",
    )
    tool_name: str = Field(..., description="Name of the tool being invoked.")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool, matching its input_schema.",
    )


class ToolResult(BaseModel):
    """Captures the outcome of a tool invocation.

    Links back to the originating ``ToolCall`` via *tool_call_id* and
    carries the result payload together with execution metadata.
    """

    tool_call_id: str = Field(..., description="Identifier of the ToolCall that produced this result.")
    tool_name: str = Field(..., description="Name of the tool that was invoked.")
    result: dict[str, Any] | str = Field(..., description="Tool output payload or error message.")
    status: Literal["success", "error", "timeout"] = Field(
        default="success",
        description="Outcome status of the tool execution.",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Wall-clock execution time in milliseconds, if measured.",
    )
