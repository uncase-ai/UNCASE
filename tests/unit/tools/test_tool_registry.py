"""Tests for ToolRegistry — registration, lookup, filtering."""

from __future__ import annotations

import pytest

from tests.factories import make_tool_definition
from uncase.exceptions import DuplicateError, ToolNotFoundError
from uncase.tools.registry import ToolRegistry


@pytest.fixture()
def registry() -> ToolRegistry:
    """Return a fresh, empty ToolRegistry."""
    return ToolRegistry()


def test_register_and_get(registry: ToolRegistry) -> None:
    """Register a tool and retrieve it by name."""
    tool = make_tool_definition(name="consultar_crm")
    registry.register(tool)

    result = registry.get("consultar_crm")
    assert result.name == "consultar_crm"
    assert result is tool


def test_register_duplicate_raises(registry: ToolRegistry) -> None:
    """Registering a tool with the same name twice raises DuplicateError."""
    tool = make_tool_definition(name="buscar_inventario")
    registry.register(tool)

    with pytest.raises(DuplicateError, match="buscar_inventario"):
        registry.register(make_tool_definition(name="buscar_inventario"))


def test_get_unknown_raises(registry: ToolRegistry) -> None:
    """Getting an unregistered tool raises ToolNotFoundError."""
    with pytest.raises(ToolNotFoundError, match="no_existe"):
        registry.get("no_existe")


def test_list_names(registry: ToolRegistry) -> None:
    """list_names returns a sorted list of all registered tool names."""
    registry.register(make_tool_definition(name="cotizar_vehiculo"))
    registry.register(make_tool_definition(name="buscar_inventario"))
    registry.register(make_tool_definition(name="consultar_crm"))

    assert registry.list_names() == [
        "buscar_inventario",
        "consultar_crm",
        "cotizar_vehiculo",
    ]


def test_list_names_empty(registry: ToolRegistry) -> None:
    """list_names returns an empty list when no tools are registered."""
    assert registry.list_names() == []


def test_list_by_domain(registry: ToolRegistry) -> None:
    """list_by_domain returns only tools matching the given domain."""
    registry.register(
        make_tool_definition(name="tool_auto", domains=["automotive.sales"]),
    )
    registry.register(
        make_tool_definition(name="tool_medical", domains=["medical.consultation"]),
    )
    registry.register(
        make_tool_definition(name="tool_both", domains=["automotive.sales", "medical.consultation"]),
    )

    auto_tools = registry.list_by_domain("automotive.sales")
    assert len(auto_tools) == 2
    names = {t.name for t in auto_tools}
    assert names == {"tool_auto", "tool_both"}


def test_list_by_domain_no_matches(registry: ToolRegistry) -> None:
    """list_by_domain returns an empty list when no tools match."""
    registry.register(make_tool_definition(name="tool_auto", domains=["automotive.sales"]))
    assert registry.list_by_domain("legal.advisory") == []


def test_list_by_category(registry: ToolRegistry) -> None:
    """list_by_category returns only tools matching the given category."""
    registry.register(make_tool_definition(name="tool_crm", category="crm"))
    registry.register(make_tool_definition(name="tool_inv", category="inventory"))
    registry.register(make_tool_definition(name="tool_crm2", category="crm"))

    crm_tools = registry.list_by_category("crm")
    assert len(crm_tools) == 2
    names = {t.name for t in crm_tools}
    assert names == {"tool_crm", "tool_crm2"}


def test_contains(registry: ToolRegistry) -> None:
    """__contains__ returns True for registered tools, False otherwise."""
    registry.register(make_tool_definition(name="buscar_inventario"))

    assert "buscar_inventario" in registry
    assert "no_existe" not in registry


def test_len(registry: ToolRegistry) -> None:
    """__len__ returns the number of registered tools."""
    assert len(registry) == 0
    registry.register(make_tool_definition(name="tool_a"))
    assert len(registry) == 1
    registry.register(make_tool_definition(name="tool_b"))
    assert len(registry) == 2
