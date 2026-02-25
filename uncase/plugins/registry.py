"""Plugin registry for the UNCASE framework.

Manages the lifecycle of plugins: catalog browsing, installation,
uninstallation, and integration with the tool registry.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from uncase.exceptions import DuplicateError, PluginNotFoundError

if TYPE_CHECKING:
    from uncase.plugins.schemas import InstalledPlugin, PluginManifest


class PluginRegistry:
    """Central registry for plugin management.

    Maintains a catalog of available plugins and tracks which ones
    are currently installed.  On install, plugin tools are registered
    into the default ``ToolRegistry``.

    Usage::

        registry = PluginRegistry()
        catalog = registry.get_catalog()
        registry.install("medical-consultation-toolkit")
        installed = registry.list_installed()
    """

    def __init__(self) -> None:
        self._catalog: dict[str, PluginManifest] = {}
        self._installed: dict[str, InstalledPlugin] = {}
        self._load_builtin_catalog()

    # -- Catalog management -------------------------------------------------

    def _load_builtin_catalog(self) -> None:
        """Load official plugin manifests from the built-in catalog."""
        with contextlib.suppress(ImportError):
            from uncase.plugins._catalog import BUILTIN_PLUGINS

            for plugin in BUILTIN_PLUGINS:
                self._catalog[plugin.id] = plugin

    def register_plugin(self, manifest: PluginManifest) -> None:
        """Add a plugin manifest to the catalog.

        Parameters
        ----------
        manifest:
            The plugin manifest to register.

        Raises
        ------
        DuplicateError
            If a plugin with the same ID already exists.
        """
        if manifest.id in self._catalog:
            raise DuplicateError(f"Plugin '{manifest.id}' already exists in catalog")
        self._catalog[manifest.id] = manifest

    def get_catalog(self) -> list[PluginManifest]:
        """Return all available plugins sorted by name."""
        return sorted(self._catalog.values(), key=lambda p: p.name)

    def get(self, plugin_id: str) -> PluginManifest:
        """Return the plugin manifest for *plugin_id*.

        Raises
        ------
        PluginNotFoundError
            If no plugin with the given ID exists.
        """
        try:
            return self._catalog[plugin_id]
        except KeyError:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' not found") from None

    # -- Installation -------------------------------------------------------

    def install(self, plugin_id: str) -> InstalledPlugin:
        """Install a plugin by registering its tools.

        Parameters
        ----------
        plugin_id:
            The ID of the plugin to install.

        Returns
        -------
        InstalledPlugin
            Record of the installation with registered tool names.

        Raises
        ------
        PluginNotFoundError
            If the plugin ID is not in the catalog.
        DuplicateError
            If the plugin is already installed.
        """
        from uncase.plugins.schemas import InstalledPlugin as InstalledPluginModel

        manifest = self.get(plugin_id)

        if plugin_id in self._installed:
            raise DuplicateError(f"Plugin '{plugin_id}' is already installed")

        # Register tools into the default tool registry
        import uncase.tools as tools_pkg

        registry = tools_pkg._default_registry
        registered_names: list[str] = []

        for tool in manifest.tools:
            if tool.name not in registry:
                registry.register(tool)
                registered_names.append(tool.name)

        record = InstalledPluginModel(
            plugin_id=plugin_id,
            name=manifest.name,
            version=manifest.version,
            tools_registered=registered_names,
            domains=manifest.domains,
        )
        self._installed[plugin_id] = record
        return record

    def uninstall(self, plugin_id: str) -> None:
        """Uninstall a plugin by removing its tools from the registry.

        Parameters
        ----------
        plugin_id:
            The ID of the plugin to uninstall.

        Raises
        ------
        PluginNotFoundError
            If the plugin is not currently installed.
        """
        if plugin_id not in self._installed:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not installed")

        record = self._installed[plugin_id]

        # Remove tools from the tool registry
        import uncase.tools as tools_pkg

        registry = tools_pkg._default_registry
        for tool_name in record.tools_registered:
            registry._tools.pop(tool_name, None)

        del self._installed[plugin_id]

    def list_installed(self) -> list[InstalledPlugin]:
        """Return all currently installed plugins."""
        return list(self._installed.values())

    def is_installed(self, plugin_id: str) -> bool:
        """Check if a plugin is currently installed."""
        return plugin_id in self._installed

    # -- Dunder helpers -----------------------------------------------------

    def __contains__(self, plugin_id: str) -> bool:
        return plugin_id in self._catalog

    def __len__(self) -> int:
        return len(self._catalog)
