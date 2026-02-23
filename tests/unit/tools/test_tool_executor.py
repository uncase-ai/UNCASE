"""Tests for SimulatedToolExecutor — mock tool execution."""

from __future__ import annotations

from tests.factories import make_tool_definition
from uncase.tools.executor import SimulatedToolExecutor
from uncase.tools.registry import ToolRegistry
from uncase.tools.schemas import ToolCall


async def test_execute_success() -> None:
    """Execute a registered tool and verify a success result."""
    registry = ToolRegistry()
    tool = make_tool_definition(
        name="buscar_inventario",
        output_schema={
            "type": "object",
            "properties": {
                "vehiculos": {"type": "array", "items": {"type": "string"}},
                "total_resultados": {"type": "integer"},
            },
        },
    )
    registry.register(tool)

    executor = SimulatedToolExecutor(registry=registry)
    call = ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota"})

    result = await executor.execute(call)

    assert result.status == "success"
    assert result.tool_call_id == call.tool_call_id
    assert result.tool_name == "buscar_inventario"
    assert isinstance(result.result, dict)
    assert result.duration_ms is not None
    assert result.duration_ms > 0


async def test_execute_unknown_tool() -> None:
    """Execute with an unknown tool name and verify error result."""
    registry = ToolRegistry()
    executor = SimulatedToolExecutor(registry=registry)
    call = ToolCall(tool_name="herramienta_inexistente", arguments={})

    result = await executor.execute(call)

    assert result.status == "error"
    assert result.tool_name == "herramienta_inexistente"
    assert "not found" in str(result.result).lower()


async def test_execute_generates_valid_result() -> None:
    """Verify that the result dict has keys matching the output_schema properties."""
    registry = ToolRegistry()
    tool = make_tool_definition(
        name="cotizar_vehiculo",
        output_schema={
            "type": "object",
            "properties": {
                "precio_base": {"type": "number"},
                "descuentos": {"type": "number"},
                "precio_final": {"type": "number"},
                "moneda": {"type": "string"},
            },
        },
    )
    registry.register(tool)

    executor = SimulatedToolExecutor(registry=registry)
    call = ToolCall(tool_name="cotizar_vehiculo", arguments={"vehiculo_id": "VH-001"})

    result = await executor.execute(call)

    assert result.status == "success"
    assert isinstance(result.result, dict)

    expected_keys = {"precio_base", "descuentos", "precio_final", "moneda"}
    assert expected_keys.issubset(result.result.keys())


async def test_execute_no_output_schema() -> None:
    """A tool with empty output_schema returns a default success payload."""
    registry = ToolRegistry()
    tool = make_tool_definition(name="simple_action", output_schema={})
    registry.register(tool)

    executor = SimulatedToolExecutor(registry=registry)
    call = ToolCall(tool_name="simple_action", arguments={})

    result = await executor.execute(call)

    assert result.status == "success"
    assert isinstance(result.result, dict)
    assert "ok" in result.result or "message" in result.result


async def test_execute_context_injection() -> None:
    """Context values are reflected in generated mock strings."""
    registry = ToolRegistry()
    tool = make_tool_definition(
        name="consultar_crm",
        output_schema={
            "type": "object",
            "properties": {
                "nombre": {"type": "string"},
                "marca": {"type": "string"},
            },
        },
    )
    registry.register(tool)

    executor = SimulatedToolExecutor(registry=registry)
    call = ToolCall(
        tool_name="consultar_crm",
        arguments={"marca": "Honda"},
    )

    result = await executor.execute(call)

    assert result.status == "success"
    assert isinstance(result.result, dict)
    # The executor should inject the argument "marca" = "Honda" into the mock.
    assert result.result["marca"] == "Honda"
