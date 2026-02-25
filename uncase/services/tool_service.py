"""Tool service — CRUD for custom tools + unified tool resolution."""

from __future__ import annotations

import contextlib
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from uncase.db.models.custom_tool import CustomToolModel
from uncase.db.models.installed_plugin import InstalledPluginModel
from uncase.exceptions import CustomToolNotFoundError, DuplicateError, ValidationError
from uncase.logging import get_logger
from uncase.schemas.custom_tool import (
    CustomToolCreateRequest,
    CustomToolListResponse,
    CustomToolResponse,
    CustomToolUpdateRequest,
)
from uncase.tools import get_registry
from uncase.tools.schemas import ToolDefinition

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class ToolService:
    """Service for custom tool CRUD and unified tool resolution."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_custom_tool(
        self,
        data: CustomToolCreateRequest,
        *,
        organization_id: str | None = None,
    ) -> CustomToolResponse:
        """Create a custom tool and persist it to the database."""
        # Check for collisions with built-in tools
        registry = get_registry()
        if data.name in registry:
            raise DuplicateError(f"Tool '{data.name}' conflicts with a built-in tool")

        # Check for duplicates in DB for this org
        existing = await self.session.execute(
            select(CustomToolModel).where(
                CustomToolModel.name == data.name,
                CustomToolModel.organization_id == organization_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise DuplicateError(f"Custom tool '{data.name}' already exists")

        model = CustomToolModel(
            id=uuid.uuid4().hex,
            name=data.name,
            description=data.description,
            input_schema=data.input_schema,
            output_schema=data.output_schema,
            domains=data.domains,
            category=data.category,
            requires_auth=data.requires_auth,
            execution_mode=data.execution_mode,
            version=data.version,
            metadata_=data.metadata,
            organization_id=organization_id,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        # Also register in-memory for immediate availability
        tool_def = self._model_to_tool_definition(model)
        with contextlib.suppress(DuplicateError):
            registry.register(tool_def)

        logger.info("custom_tool_created", tool_name=data.name, org_id=organization_id)
        return self._to_response(model)

    async def get_custom_tool(self, tool_id: str) -> CustomToolResponse:
        """Get a custom tool by ID."""
        model = await self._get_or_raise(tool_id)
        return self._to_response(model)

    async def list_custom_tools(
        self,
        *,
        organization_id: str | None = None,
        domain: str | None = None,
        category: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> CustomToolListResponse:
        """List custom tools with filters and pagination."""
        if page < 1:
            raise ValidationError("Page must be >= 1")

        query = select(CustomToolModel).where(CustomToolModel.is_active.is_(True))
        count_query = select(func.count()).select_from(CustomToolModel).where(CustomToolModel.is_active.is_(True))

        if organization_id is not None:
            query = query.where(CustomToolModel.organization_id == organization_id)
            count_query = count_query.where(CustomToolModel.organization_id == organization_id)

        # JSON array containment for domains filter
        if domain is not None:
            query = query.where(CustomToolModel.domains.contains([domain]))
            count_query = count_query.where(CustomToolModel.domains.contains([domain]))

        if category is not None:
            query = query.where(CustomToolModel.category == category)
            count_query = count_query.where(CustomToolModel.category == category)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(CustomToolModel.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(query)
        models = result.scalars().all()

        return CustomToolListResponse(
            items=[self._to_response(m) for m in models],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_custom_tool(
        self,
        tool_id: str,
        data: CustomToolUpdateRequest,
    ) -> CustomToolResponse:
        """Update a custom tool."""
        model = await self._get_or_raise(tool_id)

        update_data = data.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            update_data["metadata_"] = update_data.pop("metadata")

        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)

        logger.info("custom_tool_updated", tool_id=tool_id)
        return self._to_response(model)

    async def delete_custom_tool(self, tool_id: str) -> None:
        """Hard-delete a custom tool."""
        model = await self._get_or_raise(tool_id)

        # Remove from in-memory registry
        registry = get_registry()
        registry._tools.pop(model.name, None)

        await self.session.delete(model)
        await self.session.commit()
        logger.info("custom_tool_deleted", tool_id=tool_id, tool_name=model.name)

    async def resolve_tools_for_org(
        self,
        *,
        organization_id: str | None = None,
        domain: str | None = None,
    ) -> list[ToolDefinition]:
        """Resolve all available tools for an org: built-in + custom + plugin tools.

        This is the method the generator and pipeline should call to get the
        complete list of tools available for a given org and domain.
        """
        registry = get_registry()

        # 1. Built-in tools for domain
        if domain:
            tools_map: dict[str, ToolDefinition] = {t.name: t for t in registry.list_by_domain(domain)}
        else:
            tools_map = {name: registry.get(name) for name in registry.list_names()}

        # 2. Custom tools from DB
        query = select(CustomToolModel).where(CustomToolModel.is_active.is_(True))
        if organization_id is not None:
            query = query.where(CustomToolModel.organization_id == organization_id)
        if domain is not None:
            query = query.where(CustomToolModel.domains.contains([domain]))

        result = await self.session.execute(query)
        for model in result.scalars():
            tools_map[model.name] = self._model_to_tool_definition(model)

        # 3. Tools from installed plugins
        plugin_query = select(InstalledPluginModel).where(InstalledPluginModel.is_active.is_(True))
        if organization_id is not None:
            plugin_query = plugin_query.where(InstalledPluginModel.organization_id == organization_id)
        if domain is not None:
            plugin_query = plugin_query.where(InstalledPluginModel.domains.contains([domain]))

        plugin_result = await self.session.execute(plugin_query)
        for plugin_model in plugin_result.scalars():
            for tool_name in plugin_model.tools_registered:
                if tool_name not in tools_map and tool_name in registry:
                    tools_map[tool_name] = registry.get(tool_name)

        return sorted(tools_map.values(), key=lambda t: t.name)

    # -- Helpers --

    async def _get_or_raise(self, tool_id: str) -> CustomToolModel:
        result = await self.session.execute(select(CustomToolModel).where(CustomToolModel.id == tool_id))
        model = result.scalar_one_or_none()
        if model is None:
            raise CustomToolNotFoundError(f"Custom tool '{tool_id}' not found")
        return model

    @staticmethod
    def _to_response(model: CustomToolModel) -> CustomToolResponse:
        return CustomToolResponse(
            id=model.id,
            name=model.name,
            description=model.description,
            input_schema=model.input_schema,
            output_schema=model.output_schema,
            domains=model.domains,
            category=model.category,
            requires_auth=model.requires_auth,
            execution_mode=model.execution_mode,
            version=model.version,
            metadata=model.metadata_,
            is_active=model.is_active,
            is_builtin=False,
            organization_id=model.organization_id,
            created_at=model.created_at.isoformat() if model.created_at else "",
            updated_at=model.updated_at.isoformat() if model.updated_at else "",
        )

    @staticmethod
    def _model_to_tool_definition(model: CustomToolModel) -> ToolDefinition:
        exec_mode = model.execution_mode
        if exec_mode not in ("simulated", "live", "mock"):
            exec_mode = "simulated"
        return ToolDefinition(
            name=model.name,
            description=model.description,
            input_schema=model.input_schema,
            output_schema=model.output_schema,
            domains=model.domains,
            category=model.category,
            requires_auth=model.requires_auth,
            execution_mode=exec_mode,  # type: ignore[arg-type]
            version=model.version,
            metadata=model.metadata_ or {},
        )
