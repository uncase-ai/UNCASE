"""Unit tests for the TemplateRegistry class."""

from __future__ import annotations

import pytest

from uncase.exceptions import DuplicateError, TemplateNotFoundError
from uncase.templates import TemplateRegistry, register_all_templates
from uncase.templates.base import BaseChatTemplate, ToolCallMode


class DummyTemplate(BaseChatTemplate):
    """Minimal concrete template for registry testing."""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def display_name(self) -> str:
        return "Dummy Template"

    @property
    def supports_tool_calls(self) -> bool:
        return False

    def render(
        self,
        conversation,
        tool_call_mode=ToolCallMode.NONE,
        system_prompt=None,
        available_tools=None,
    ) -> str:
        return "dummy"

    def get_special_tokens(self) -> list[str]:
        return ["<dummy>"]


class AnotherDummyTemplate(BaseChatTemplate):
    """Second dummy template with a different name."""

    @property
    def name(self) -> str:
        return "another_dummy"

    @property
    def display_name(self) -> str:
        return "Another Dummy"

    @property
    def supports_tool_calls(self) -> bool:
        return False

    def render(
        self,
        conversation,
        tool_call_mode=ToolCallMode.NONE,
        system_prompt=None,
        available_tools=None,
    ) -> str:
        return "another"

    def get_special_tokens(self) -> list[str]:
        return []


def test_register_and_get() -> None:
    """Register a template and retrieve it by name."""
    registry = TemplateRegistry()
    template = DummyTemplate()
    registry.register(template)

    result = registry.get("dummy")

    assert result is template
    assert result.name == "dummy"
    assert result.display_name == "Dummy Template"


def test_register_duplicate_raises() -> None:
    """Registering two templates with the same name raises DuplicateError."""
    registry = TemplateRegistry()
    registry.register(DummyTemplate())

    with pytest.raises(DuplicateError, match="dummy"):
        registry.register(DummyTemplate())


def test_get_unknown_raises() -> None:
    """Requesting an unregistered name raises TemplateNotFoundError."""
    registry = TemplateRegistry()

    with pytest.raises(TemplateNotFoundError, match="nonexistent"):
        registry.get("nonexistent")


def test_list_names() -> None:
    """list_names returns a sorted list of all registered template names."""
    registry = TemplateRegistry()
    registry.register(DummyTemplate())
    registry.register(AnotherDummyTemplate())

    names = registry.list_names()

    assert names == ["another_dummy", "dummy"]


def test_contains() -> None:
    """__contains__ returns True for registered names, False otherwise."""
    registry = TemplateRegistry()
    registry.register(DummyTemplate())

    assert "dummy" in registry
    assert "nonexistent" not in registry


def test_len() -> None:
    """__len__ returns the number of registered templates."""
    registry = TemplateRegistry()

    assert len(registry) == 0

    registry.register(DummyTemplate())
    assert len(registry) == 1

    registry.register(AnotherDummyTemplate())
    assert len(registry) == 2


def test_register_all_templates() -> None:
    """After register_all_templates(), all 10 built-in templates are registered."""
    # register_all_templates() works on the module-level singleton.
    # We call it and then inspect the default registry.
    register_all_templates()

    from uncase.templates import get_template_registry

    registry = get_template_registry()

    expected_names = sorted([
        "alpaca",
        "chatml",
        "harmony",
        "llama",
        "minimax",
        "mistral",
        "moonshot",
        "nemotron",
        "openai_api",
        "qwen",
    ])

    registered = registry.list_names()

    for name in expected_names:
        assert name in registered, f"Template '{name}' not found in registry"

    assert len(registered) >= 10
