"""Plugins API — browse catalog, install, uninstall, and publish plugins.

Plugin installations are persisted to PostgreSQL and org-scoped.
The in-memory plugin catalog remains the source of truth for available plugins.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.plugins import get_catalog, get_plugin, get_registry
from uncase.plugins.schemas import PluginManifest
from uncase.schemas.installed_plugin import (
    InstalledPluginListResponse,
    InstalledPluginResponse,
    PluginConfigUpdateRequest,
)
from uncase.services.plugin_service import PluginService

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])


# ---------------------------------------------------------------------------
# Catalog endpoints (no persistence needed — these are read-only catalog)
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


@router.get("/installed", response_model=InstalledPluginListResponse)
async def list_installed_plugins(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> InstalledPluginListResponse:
    """List all installed plugins for the current org (persisted)."""
    service = PluginService(session)
    org_id = org.id if org else None
    return await service.list_installed(organization_id=org_id)


@router.get("/{plugin_id}", response_model=PluginManifest)
async def get_plugin_detail(plugin_id: str) -> PluginManifest:
    """Get detailed information about a specific plugin."""
    return get_plugin(plugin_id)


# ---------------------------------------------------------------------------
# Installation endpoints (now DB-persisted)
# ---------------------------------------------------------------------------


@router.post(
    "/{plugin_id}/install",
    response_model=InstalledPluginResponse,
    status_code=status.HTTP_201_CREATED,
)
async def install(
    plugin_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> InstalledPluginResponse:
    """Install a plugin, registering its tools into the pipeline (persisted)."""
    service = PluginService(session)
    org_id = org.id if org else None

    result = await service.install_plugin(plugin_id, organization_id=org_id)

    await meter(
        session,
        "plugin_installed",
        organization_id=org_id,
        resource_id=plugin_id,
        metadata={"tools_count": len(result.tools_registered)},
    )
    return result


@router.delete("/{plugin_id}/install", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall(
    plugin_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> None:
    """Uninstall a plugin, removing its tools from the pipeline (persisted)."""
    service = PluginService(session)
    org_id = org.id if org else None

    await service.uninstall_plugin(plugin_id, organization_id=org_id)

    await meter(session, "plugin_uninstalled", organization_id=org_id, resource_id=plugin_id)


@router.put("/{plugin_id}/config", response_model=InstalledPluginResponse)
async def update_plugin_config(
    plugin_id: str,
    data: PluginConfigUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> InstalledPluginResponse:
    """Update per-plugin configuration for the current org."""
    service = PluginService(session)
    org_id = org.id if org else None
    return await service.update_plugin_config(plugin_id, data, organization_id=org_id)


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
