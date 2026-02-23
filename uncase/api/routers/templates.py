"""Template rendering API endpoints."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from uncase.exceptions import TemplateNotFoundError
from uncase.schemas.template import RenderRequest, RenderResponse, TemplateInfo
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
async def render_conversations(body: RenderRequest) -> RenderResponse:
    """Render conversations using a specified template."""
    register_all_templates()
    registry = get_template_registry()

    try:
        template = registry.get(body.template_name)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail) from exc

    tool_mode = ToolCallMode(body.tool_call_mode)
    rendered = template.render_batch(
        conversations=body.conversations,
        tool_call_mode=tool_mode,
        system_prompt=body.system_prompt,
    )

    logger.info(
        "conversations_rendered",
        template=body.template_name,
        count=len(rendered),
    )
    return RenderResponse(
        rendered=rendered,
        template_name=body.template_name,
        count=len(rendered),
    )


@router.post("/export")
async def export_conversations(body: RenderRequest) -> Response:
    """Export rendered conversations as a downloadable text file."""
    register_all_templates()
    registry = get_template_registry()

    try:
        template = registry.get(body.template_name)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail) from exc

    tool_mode = ToolCallMode(body.tool_call_mode)
    rendered = template.render_batch(
        conversations=body.conversations,
        tool_call_mode=tool_mode,
        system_prompt=body.system_prompt,
    )

    content = "\n\n".join(rendered)
    filename = f"uncase_export_{body.template_name}.txt"

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
