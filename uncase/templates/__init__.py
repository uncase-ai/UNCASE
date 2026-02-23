"""Chat template system — export synthetic conversations for LLM fine-tuning.

Provides a module-level singleton ``TemplateRegistry`` with public accessor
functions so that any part of the codebase can discover registered templates
without managing registry instances manually.

Usage::

    from uncase.templates import get_template, list_templates, get_template_registry

    template = get_template("chatml")
    names = list_templates()
    registry = get_template_registry()
"""

from __future__ import annotations

from uncase.exceptions import DuplicateError, TemplateNotFoundError
from uncase.templates.base import BaseChatTemplate, ToolCallMode


class TemplateRegistry:
    """Central registry for chat template implementations.

    Usage::

        registry = TemplateRegistry()
        registry.register(my_template)
        template = registry.get("chatml")
        names = registry.list_names()
    """

    def __init__(self) -> None:
        self._templates: dict[str, BaseChatTemplate] = {}

    # -- Mutation -----------------------------------------------------------

    def register(self, template: BaseChatTemplate) -> None:
        """Register a chat template.

        Parameters
        ----------
        template:
            The ``BaseChatTemplate`` implementation to register.

        Raises
        ------
        DuplicateError
            If a template with the same name is already registered.
        """
        if template.name in self._templates:
            raise DuplicateError(f"Template '{template.name}' is already registered")
        self._templates[template.name] = template

    # -- Lookup -------------------------------------------------------------

    def get(self, name: str) -> BaseChatTemplate:
        """Return the chat template for *name*.

        Parameters
        ----------
        name:
            Snake_case template identifier.

        Raises
        ------
        TemplateNotFoundError
            If no template with the given name is registered.
        """
        try:
            return self._templates[name]
        except KeyError:
            raise TemplateNotFoundError(f"Template '{name}' is not registered") from None

    def list_names(self) -> list[str]:
        """Return a sorted list of all registered template names."""
        return sorted(self._templates.keys())

    # -- Dunder helpers -----------------------------------------------------

    def __contains__(self, name: str) -> bool:
        return name in self._templates

    def __len__(self) -> int:
        return len(self._templates)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_default_registry: TemplateRegistry = TemplateRegistry()

# Template implementations registered by uncase.templates.{name}


def register_all_templates() -> None:
    """Lazily import and register all built-in template implementations.

    Call this function once before accessing templates to ensure every
    built-in implementation is available in the default registry.

    Each sub-module registers its template(s) as a side-effect on import.
    """
    import uncase.templates.alpaca
    import uncase.templates.chatml
    import uncase.templates.harmony
    import uncase.templates.llama
    import uncase.templates.minimax
    import uncase.templates.mistral
    import uncase.templates.moonshot
    import uncase.templates.nemotron
    import uncase.templates.openai_api
    import uncase.templates.qwen  # noqa: F401


# ---------------------------------------------------------------------------
# Public convenience functions
# ---------------------------------------------------------------------------


def get_template(name: str) -> BaseChatTemplate:
    """Retrieve a chat template from the default registry.

    Parameters
    ----------
    name:
        Snake_case template identifier.

    Raises
    ------
    TemplateNotFoundError
        If the template is not registered.
    """
    return _default_registry.get(name)


def list_templates() -> list[str]:
    """Return a sorted list of all registered template names."""
    return _default_registry.list_names()


def get_template_registry() -> TemplateRegistry:
    """Return the module-level singleton ``TemplateRegistry`` instance."""
    return _default_registry


__all__ = [
    "BaseChatTemplate",
    "TemplateRegistry",
    "ToolCallMode",
    "get_template",
    "get_template_registry",
    "list_templates",
    "register_all_templates",
]
