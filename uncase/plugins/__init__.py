"""UNCASE plugin framework — discover, install, and manage tool plugins.

Provides a central plugin catalog and registry so that domain-specific
tool packs can be distributed, discovered, and activated independently
of the core SCSF pipeline.

Usage::

    from uncase.plugins import get_catalog, install_plugin, list_installed

    catalog = get_catalog()
    install_plugin("medical-consultation-toolkit")
    installed = list_installed()
"""

from __future__ import annotations

from uncase.plugins.registry import PluginRegistry
from uncase.plugins.schemas import InstalledPlugin, PluginManifest

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_default_registry: PluginRegistry = PluginRegistry()


# ---------------------------------------------------------------------------
# Public convenience functions
# ---------------------------------------------------------------------------


def get_catalog() -> list[PluginManifest]:
    """Return all available plugins in the catalog."""
    return _default_registry.get_catalog()


def get_plugin(plugin_id: str) -> PluginManifest:
    """Retrieve a plugin manifest by ID."""
    return _default_registry.get(plugin_id)


def install_plugin(plugin_id: str) -> InstalledPlugin:
    """Install a plugin, registering its tools in the tool registry."""
    return _default_registry.install(plugin_id)


def uninstall_plugin(plugin_id: str) -> None:
    """Uninstall a plugin, removing its tools from the tool registry."""
    _default_registry.uninstall(plugin_id)


def list_installed() -> list[InstalledPlugin]:
    """Return all currently installed plugins."""
    return _default_registry.list_installed()


def get_registry() -> PluginRegistry:
    """Return the module-level singleton ``PluginRegistry`` instance."""
    return _default_registry


__all__ = [
    "InstalledPlugin",
    "PluginManifest",
    "PluginRegistry",
    "get_catalog",
    "get_plugin",
    "get_registry",
    "install_plugin",
    "list_installed",
    "uninstall_plugin",
]
