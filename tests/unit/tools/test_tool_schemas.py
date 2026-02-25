"""Tests for tool Pydantic schemas — validation, defaults, constraints."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from uncase.tools.schemas import ToolCall, ToolDefinition, ToolParameter, ToolResult


def test_tool_definition_valid() -> None:
    """A ToolDefinition with all required fields is created successfully."""
    td = ToolDefinition(
        name="lookup_vehicle",
        description="Search the dealership inventory for available vehicles.",
        input_schema={
            "type": "object",
            "properties": {"marca": {"type": "string"}},
        },
    )

    assert td.name == "lookup_vehicle"
    assert td.description.startswith("Search")
    assert td.input_schema["type"] == "object"
    # Defaults
    assert td.output_schema == {}
    assert td.domains == []
    assert td.category == ""
    assert td.requires_auth is False
    assert td.execution_mode == "simulated"
    assert td.version == "1.0"
    assert td.metadata == {}


@pytest.mark.parametrize(
    "bad_name",
    [
        "LookupVehicle",  # uppercase
        "Lookup",  # starts with uppercase
        "lookup vehicle",  # space
        "1lookup",  # starts with digit
        "lookup-vehicle",  # hyphen
    ],
)
def test_tool_definition_invalid_name(bad_name: str) -> None:
    """Names that violate the ^[a-z][a-z0-9_]*$ pattern must be rejected."""
    with pytest.raises(ValidationError):
        ToolDefinition(
            name=bad_name,
            description="A valid description that is long enough.",
            input_schema={"type": "object"},
        )


def test_tool_definition_short_description() -> None:
    """Descriptions shorter than 10 characters must be rejected."""
    with pytest.raises(ValidationError):
        ToolDefinition(
            name="some_tool",
            description="Too short",
            input_schema={"type": "object"},
        )


def test_tool_call_auto_id() -> None:
    """ToolCall auto-generates a unique tool_call_id when not provided."""
    tc1 = ToolCall(tool_name="buscar_inventario")
    tc2 = ToolCall(tool_name="buscar_inventario")

    assert tc1.tool_call_id  # not empty
    assert tc2.tool_call_id  # not empty
    assert tc1.tool_call_id != tc2.tool_call_id  # unique


def test_tool_call_explicit_id() -> None:
    """ToolCall preserves an explicit tool_call_id."""
    tc = ToolCall(tool_call_id="custom_id_123", tool_name="buscar_inventario")
    assert tc.tool_call_id == "custom_id_123"


@pytest.mark.parametrize("status", ["success", "error", "timeout"])
def test_tool_result_statuses(status: str) -> None:
    """All three ToolResult status values are accepted."""
    tr = ToolResult(
        tool_call_id="call_001",
        tool_name="buscar_inventario",
        result={"ok": True},
        status=status,
    )
    assert tr.status == status


def test_tool_result_invalid_status() -> None:
    """An invalid status value must be rejected."""
    with pytest.raises(ValidationError):
        ToolResult(
            tool_call_id="call_001",
            tool_name="buscar_inventario",
            result={"ok": True},
            status="pending",  # type: ignore[arg-type]
        )


def test_tool_parameter_defaults() -> None:
    """ToolParameter defaults: required=True, enum=None, default=None."""
    tp = ToolParameter(
        name="marca",
        type="string",
        description="Vehicle brand name.",
    )
    assert tp.required is True
    assert tp.enum is None
    assert tp.default is None


def test_tool_parameter_optional_with_enum() -> None:
    """ToolParameter can be optional and constrained to an enum."""
    tp = ToolParameter(
        name="tipo",
        type="string",
        description="Vehicle type filter.",
        required=False,
        enum=["sedan", "SUV", "pickup"],
        default="sedan",
    )
    assert tp.required is False
    assert tp.enum == ["sedan", "SUV", "pickup"]
    assert tp.default == "sedan"
