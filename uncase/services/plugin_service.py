"""Plugin service — install/uninstall with DB persistence."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from uncase.db.models.installed_plugin import InstalledPluginModel
from uncase.exceptions import PluginAlreadyInstalledError, PluginNotFoundError
from uncase.logging import get_logger
from uncase.plugins import get_registry as get_plugin_registry
from uncase.schemas.installed_plugin import (
    InstalledPluginListResponse,
    InstalledPluginResponse,
    PluginConfigUpdateRequest,
)
from uncase.tools import get_registry as get_tool_registry

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class PluginService:
    """Service for plugin installation lifecycle with DB persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def install_plugin(
        self,
        plugin_id: str,
        *,
        organization_id: str | None = None,
    ) -> InstalledPluginResponse:
        """Install a plugin: validate it exists, persist to DB, register tools."""
        # Validate plugin exists in catalog
        plugin_registry = get_plugin_registry()
        manifest = plugin_registry.get(plugin_id)

        # Check if already installed for this org
        existing = await self.session.execute(
            select(InstalledPluginModel).where(
                InstalledPluginModel.plugin_id == plugin_id,
                InstalledPluginModel.organization_id == organization_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise PluginAlreadyInstalledError(f"Plugin '{plugin_id}' is already installed")

        # Register tools in-memory
        tool_registry = get_tool_registry()
        registered_names: list[str] = []
        for tool in manifest.tools:
            if tool.name not in tool_registry:
                tool_registry.register(tool)
            registered_names.append(tool.name)

        # Persist to DB
        model = InstalledPluginModel(
            id=uuid.uuid4().hex,
            plugin_id=plugin_id,
            plugin_name=manifest.name,
            plugin_version=manifest.version,
            plugin_source=manifest.source,
            tools_registered=registered_names,
            domains=manifest.domains,
            organization_id=organization_id,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        logger.info(
            "plugin_installed",
            plugin_id=plugin_id,
            org_id=organization_id,
            tools_count=len(registered_names),
        )
        return self._to_response(model)

    async def uninstall_plugin(
        self,
        plugin_id: str,
        *,
        organization_id: str | None = None,
    ) -> None:
        """Uninstall a plugin: remove from DB and de-register tools."""
        model = await self._get_installed_or_raise(plugin_id, organization_id)

        # Remove tools from in-memory registry (only if no other org uses them)
        tool_registry = get_tool_registry()
        other_installs = await self.session.execute(
            select(InstalledPluginModel).where(
                InstalledPluginModel.plugin_id == plugin_id,
                InstalledPluginModel.id != model.id,
                InstalledPluginModel.is_active.is_(True),
            )
        )
        other_count = len(other_installs.scalars().all())

        if other_count == 0:
            for tool_name in model.tools_registered:
                tool_registry._tools.pop(tool_name, None)

        await self.session.delete(model)
        await self.session.commit()

        logger.info("plugin_uninstalled", plugin_id=plugin_id, org_id=organization_id)

    async def list_installed(
        self,
        *,
        organization_id: str | None = None,
    ) -> InstalledPluginListResponse:
        """List installed plugins for an org."""
        query = select(InstalledPluginModel).where(InstalledPluginModel.is_active.is_(True))
        if organization_id is not None:
            query = query.where(InstalledPluginModel.organization_id == organization_id)

        query = query.order_by(InstalledPluginModel.created_at.desc())
        result = await self.session.execute(query)
        models = result.scalars().all()

        return InstalledPluginListResponse(
            items=[self._to_response(m) for m in models],
            total=len(models),
        )

    async def update_plugin_config(
        self,
        plugin_id: str,
        data: PluginConfigUpdateRequest,
        *,
        organization_id: str | None = None,
    ) -> InstalledPluginResponse:
        """Update per-plugin configuration for an org."""
        model = await self._get_installed_or_raise(plugin_id, organization_id)

        if data.config is not None:
            model.config = data.config
        if data.is_active is not None:
            model.is_active = data.is_active

        await self.session.commit()
        await self.session.refresh(model)

        logger.info("plugin_config_updated", plugin_id=plugin_id, org_id=organization_id)
        return self._to_response(model)

    async def is_installed(
        self,
        plugin_id: str,
        *,
        organization_id: str | None = None,
    ) -> bool:
        """Check if a plugin is installed for an org."""
        result = await self.session.execute(
            select(InstalledPluginModel).where(
                InstalledPluginModel.plugin_id == plugin_id,
                InstalledPluginModel.organization_id == organization_id,
                InstalledPluginModel.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None

    # -- Helpers --

    async def _get_installed_or_raise(
        self,
        plugin_id: str,
        organization_id: str | None,
    ) -> InstalledPluginModel:
        result = await self.session.execute(
            select(InstalledPluginModel).where(
                InstalledPluginModel.plugin_id == plugin_id,
                InstalledPluginModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not installed")
        return model

    @staticmethod
    def _to_response(model: InstalledPluginModel) -> InstalledPluginResponse:
        return InstalledPluginResponse(
            id=model.id,
            plugin_id=model.plugin_id,
            plugin_name=model.plugin_name,
            plugin_version=model.plugin_version,
            plugin_source=model.plugin_source,
            tools_registered=model.tools_registered,
            domains=model.domains,
            config=model.config,
            is_active=model.is_active,
            organization_id=model.organization_id,
            created_at=model.created_at.isoformat() if model.created_at else "",
            updated_at=model.updated_at.isoformat() if model.updated_at else "",
        )
