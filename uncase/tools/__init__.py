"""UNCASE tool framework — schemas, registry, and convenience helpers.

Provides a module-level singleton ``ToolRegistry`` with public accessor
functions so that any part of the codebase can discover registered tools
without managing registry instances manually.

Usage::

    from uncase.tools import get_tool, list_tools, get_registry

    tool = get_tool("lookup_vehicle")
    names = list_tools()
    registry = get_registry()
"""

from __future__ import annotations

import contextlib

from uncase.tools.registry import ToolRegistry
from uncase.tools.schemas import (
    ToolCall,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_default_registry: ToolRegistry = ToolRegistry()

# Auto-register built-in tools when the sub-module is available.
with contextlib.suppress(ImportError):
    import uncase.tools._builtin  # noqa: F401 — side-effect import registers tools


# ---------------------------------------------------------------------------
# Public convenience functions
# ---------------------------------------------------------------------------


def get_tool(name: str) -> ToolDefinition:
    """Retrieve a tool definition from the default registry.

    Parameters
    ----------
    name:
        Snake_case tool identifier.

    Raises
    ------
    ToolNotFoundError
        If the tool is not registered.
    """
    return _default_registry.get(name)


def list_tools() -> list[str]:
    """Return a sorted list of all registered tool names."""
    return _default_registry.list_names()


def get_registry() -> ToolRegistry:
    """Return the module-level singleton ``ToolRegistry`` instance."""
    return _default_registry


__all__ = [
    "ToolCall",
    "ToolDefinition",
    "ToolParameter",
    "ToolRegistry",
    "ToolResult",
    "get_registry",
    "get_tool",
    "list_tools",
]
