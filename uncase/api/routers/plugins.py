"""Plugins API — browse catalog, install, uninstall, and publish plugins."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from uncase.plugins import (
    get_catalog,
    get_plugin,
    get_registry,
    install_plugin,
    list_installed,
    uninstall_plugin,
)
from uncase.plugins.schemas import InstalledPlugin, PluginManifest

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])


# ---------------------------------------------------------------------------
# Catalog endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=list[PluginManifest])
async def list_plugins(
    domain: str | None = Query(None, description="Filter by domain namespace"),
    tag: str | None = Query(None, description="Filter by tag"),
    source: str | None = Query(None, description="Filter by source (official/community)"),
) -> list[PluginManifest]:
    """List all available plugins in the catalog."""
    plugins = get_catalog()

    if domain:
        plugins = [p for p in plugins if domain in p.domains]
    if tag:
        plugins = [p for p in plugins if tag in p.tags]
    if source:
        plugins = [p for p in plugins if p.source == source]

    return plugins


@router.get("/installed", response_model=list[InstalledPlugin])
async def list_installed_plugins() -> list[InstalledPlugin]:
    """List all currently installed plugins."""
    return list_installed()


@router.get("/{plugin_id}", response_model=PluginManifest)
async def get_plugin_detail(plugin_id: str) -> PluginManifest:
    """Get detailed information about a specific plugin."""
    return get_plugin(plugin_id)


# ---------------------------------------------------------------------------
# Installation endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/{plugin_id}/install",
    response_model=InstalledPlugin,
    status_code=status.HTTP_201_CREATED,
)
async def install(plugin_id: str) -> InstalledPlugin:
    """Install a plugin, registering its tools into the pipeline."""
    return install_plugin(plugin_id)


@router.delete("/{plugin_id}/install", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall(plugin_id: str) -> None:
    """Uninstall a plugin, removing its tools from the pipeline."""
    uninstall_plugin(plugin_id)


# ---------------------------------------------------------------------------
# Community publish endpoint
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=PluginManifest,
    status_code=status.HTTP_201_CREATED,
)
async def publish_plugin(manifest: PluginManifest) -> PluginManifest:
    """Publish a community plugin to the catalog."""
    manifest.source = "community"
    manifest.verified = False
    registry = get_registry()
    registry.register_plugin(manifest)
    return manifest
