"""Template service — per-org template preferences."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from uncase.db.models.template_config import TemplateConfigModel
from uncase.logging import get_logger
from uncase.schemas.template_config import TemplateConfigResponse, TemplateConfigUpdateRequest
from uncase.templates import get_template_registry, register_all_templates

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from uncase.templates.base import BaseChatTemplate

logger = get_logger(__name__)


class TemplateService:
    """Service for per-org template configuration."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_config(
        self,
        *,
        organization_id: str | None = None,
    ) -> TemplateConfigResponse | None:
        """Get template config for an org, or None if not set."""
        result = await self.session.execute(
            select(TemplateConfigModel).where(TemplateConfigModel.organization_id == organization_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_response(model)

    async def get_or_create_config(
        self,
        *,
        organization_id: str | None = None,
    ) -> TemplateConfigResponse:
        """Get or lazily create default template config for an org."""
        result = await self.session.execute(
            select(TemplateConfigModel).where(TemplateConfigModel.organization_id == organization_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            model = TemplateConfigModel(
                id=uuid.uuid4().hex,
                organization_id=organization_id,
            )
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            logger.info("template_config_created", org_id=organization_id)

        return self._to_response(model)

    async def update_config(
        self,
        data: TemplateConfigUpdateRequest,
        *,
        organization_id: str | None = None,
    ) -> TemplateConfigResponse:
        """Update template config for an org (upsert)."""
        result = await self.session.execute(
            select(TemplateConfigModel).where(TemplateConfigModel.organization_id == organization_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            model = TemplateConfigModel(
                id=uuid.uuid4().hex,
                organization_id=organization_id,
            )
            self.session.add(model)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)

        logger.info("template_config_updated", org_id=organization_id)
        return self._to_response(model)

    def resolve_template_for_org(
        self,
        config: TemplateConfigResponse | None,
    ) -> BaseChatTemplate:
        """Resolve the default template for an org from its config."""
        register_all_templates()
        registry = get_template_registry()

        template_name = config.default_template if config else "chatml"

        try:
            return registry.get(template_name)
        except Exception:
            logger.warning("template_fallback", requested=template_name, fallback="chatml")
            return registry.get("chatml")

    @staticmethod
    def _to_response(model: TemplateConfigModel) -> TemplateConfigResponse:
        return TemplateConfigResponse(
            id=model.id,
            organization_id=model.organization_id,
            default_template=model.default_template,
            default_tool_call_mode=model.default_tool_call_mode,
            default_system_prompt=model.default_system_prompt,
            preferred_templates=model.preferred_templates,
            export_format=model.export_format,
            created_at=model.created_at.isoformat() if model.created_at else "",
            updated_at=model.updated_at.isoformat() if model.updated_at else "",
        )
