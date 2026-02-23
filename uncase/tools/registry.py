"""Tool registry for the UNCASE SCSF pipeline.

Provides a dict-based registry that stores ``ToolDefinition`` instances
and supports lookup by name, domain, or category.  Follows the same
pattern established by ``uncase.domains.DomainRegistry``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.exceptions import DuplicateError, ToolNotFoundError

if TYPE_CHECKING:
    from uncase.tools.schemas import ToolDefinition


class ToolRegistry:
    """Central registry for tool definitions.

    Usage::

        registry = ToolRegistry()
        registry.register(my_tool)
        tool = registry.get("lookup_vehicle")
        names = registry.list_names()
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    # -- Mutation -----------------------------------------------------------

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition.

        Parameters
        ----------
        tool:
            The ``ToolDefinition`` to register.

        Raises
        ------
        DuplicateError
            If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise DuplicateError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    # -- Lookup -------------------------------------------------------------

    def get(self, name: str) -> ToolDefinition:
        """Return the tool definition for *name*.

        Parameters
        ----------
        name:
            Snake_case tool identifier.

        Raises
        ------
        ToolNotFoundError
            If no tool with the given name is registered.
        """
        try:
            return self._tools[name]
        except KeyError:
            raise ToolNotFoundError(f"Tool '{name}' is not registered") from None

    def list_names(self) -> list[str]:
        """Return a sorted list of all registered tool names."""
        return sorted(self._tools.keys())

    def list_by_domain(self, domain: str) -> list[ToolDefinition]:
        """Return all tools whose *domains* list includes *domain*.

        Parameters
        ----------
        domain:
            Domain namespace to filter by, e.g. ``"automotive.sales"``.
        """
        return [tool for tool in self._tools.values() if domain in tool.domains]

    def list_by_category(self, category: str) -> list[ToolDefinition]:
        """Return all tools whose *category* matches *category*.

        Parameters
        ----------
        category:
            Category string to filter by, e.g. ``"crm"``.
        """
        return [tool for tool in self._tools.values() if tool.category == category]

    # -- Dunder helpers -----------------------------------------------------

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)
