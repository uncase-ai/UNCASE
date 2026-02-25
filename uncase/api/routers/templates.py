"""Template rendering API endpoints.

Supports per-org template preferences stored in PostgreSQL,
with fallback defaults for unauthenticated requests.
"""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.template import RenderRequest, RenderResponse, TemplateInfo
from uncase.schemas.template_config import TemplateConfigResponse, TemplateConfigUpdateRequest
from uncase.services.template_service import TemplateService
from uncase.templates import get_template_registry, register_all_templates
from uncase.templates.base import ToolCallMode

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])

logger = structlog.get_logger(__name__)


@router.get("", response_model=list[TemplateInfo])
async def list_templates() -> list[TemplateInfo]:
    """List all available template formats."""
    register_all_templates()
    registry = get_template_registry()

    templates: list[TemplateInfo] = []
    for name in registry.list_names():
        tpl = registry.get(name)
        templates.append(
            TemplateInfo(
                name=tpl.name,
                display_name=tpl.display_name,
                supports_tool_calls=tpl.supports_tool_calls,
                special_tokens=tpl.get_special_tokens(),
            )
        )

    logger.info("templates_listed", count=len(templates))
    return templates


@router.post("/render", response_model=RenderResponse)
async def render_conversations(
    body: RenderRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> RenderResponse:
    """Render conversations using a specified template.

    Falls back to the org's default template if template_name is not provided.
    """
    register_all_templates()
    registry = get_template_registry()

    template_name = body.template_name
    tool_call_mode_str = body.tool_call_mode
    system_prompt = body.system_prompt

    # Apply org defaults if available
    if org:
        service = TemplateService(session)
        config = await service.get_config(organization_id=org.id)
        if config:
            if not template_name:
                template_name = config.default_template
            if tool_call_mode_str == "none" and config.default_tool_call_mode != "none":
                tool_call_mode_str = config.default_tool_call_mode
            if not system_prompt and config.default_system_prompt:
                system_prompt = config.default_system_prompt

    template = registry.get(template_name)
    tool_mode = ToolCallMode(tool_call_mode_str)
    rendered = template.render_batch(
        conversations=body.conversations,
        tool_call_mode=tool_mode,
        system_prompt=system_prompt,
    )

    org_id = org.id if org else None
    await meter(session, "template_rendered", organization_id=org_id, metadata={"template": template_name})

    logger.info(
        "conversations_rendered",
        template=template_name,
        count=len(rendered),
    )
    return RenderResponse(
        rendered=rendered,
        template_name=template_name,
        count=len(rendered),
    )


@router.post("/export")
async def export_conversations(
    body: RenderRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> Response:
    """Export rendered conversations as a downloadable text file."""
    register_all_templates()
    registry = get_template_registry()

    template = registry.get(body.template_name)
    tool_mode = ToolCallMode(body.tool_call_mode)
    rendered = template.render_batch(
        conversations=body.conversations,
        tool_call_mode=tool_mode,
        system_prompt=body.system_prompt,
    )

    content = "\n\n".join(rendered)
    filename = f"uncase_export_{body.template_name}.txt"

    org_id = org.id if org else None
    await meter(session, "template_exported", organization_id=org_id, metadata={"template": body.template_name})

    logger.info(
        "conversations_exported",
        template=body.template_name,
        count=len(rendered),
    )
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Template config endpoints (per-org preferences)
# ---------------------------------------------------------------------------


@router.get("/config", response_model=TemplateConfigResponse)
async def get_template_config(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> TemplateConfigResponse:
    """Get template preferences for the current org."""
    service = TemplateService(session)
    org_id = org.id if org else None
    return await service.get_or_create_config(organization_id=org_id)


@router.put("/config", response_model=TemplateConfigResponse)
async def update_template_config(
    data: TemplateConfigUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> TemplateConfigResponse:
    """Update template preferences for the current org."""
    service = TemplateService(session)
    org_id = org.id if org else None
    result = await service.update_config(data, organization_id=org_id)

    await meter(session, "template_config_updated", organization_id=org_id)
    return result
