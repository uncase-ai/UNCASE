"""Tool management API endpoints.

Provides unified access to built-in tools, custom tools, and plugin tools.
Custom tools are persisted to PostgreSQL and org-scoped.
"""

from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.api.metering import meter
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.custom_tool import (
    CustomToolCreateRequest,
    CustomToolListResponse,
    CustomToolResponse,
    CustomToolUpdateRequest,
)
from uncase.services.tool_service import ToolService
from uncase.tools import get_tool
from uncase.tools.executor import SimulatedToolExecutor
from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])

logger = structlog.get_logger(__name__)


@router.get("", response_model=list[ToolDefinition])
async def list_tool_definitions(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: str | None = None,
    category: str | None = None,
) -> list[ToolDefinition]:
    """List all available tools (built-in + custom + plugin) for the org."""
    service = ToolService(session)
    org_id = org.id if org else None

    tools = await service.resolve_tools_for_org(organization_id=org_id, domain=domain)

    if category is not None:
        tools = [t for t in tools if t.category == category]

    logger.info("tools_listed", count=len(tools), domain=domain, category=category, org_id=org_id)
    return tools


@router.get("/custom", response_model=CustomToolListResponse)
async def list_custom_tools(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: str | None = Query(None, description="Filter by domain namespace"),
    category: str | None = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> CustomToolListResponse:
    """List only custom (user-created) tools for the org."""
    service = ToolService(session)
    org_id = org.id if org else None

    return await service.list_custom_tools(
        organization_id=org_id,
        domain=domain,
        category=category,
        page=page,
        page_size=page_size,
    )


@router.get("/resolve/{domain}", response_model=list[ToolDefinition])
async def resolve_tools_for_domain(
    domain: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> list[ToolDefinition]:
    """Resolve all available tools for a specific org + domain."""
    service = ToolService(session)
    org_id = org.id if org else None
    return await service.resolve_tools_for_org(organization_id=org_id, domain=domain)


@router.get("/{tool_name}", response_model=ToolDefinition)
async def get_tool_definition(tool_name: str) -> ToolDefinition:
    """Get a single tool definition by name."""
    tool = get_tool(tool_name)
    logger.info("tool_retrieved", tool_name=tool_name)
    return tool


@router.post("", response_model=CustomToolResponse, status_code=status.HTTP_201_CREATED)
async def register_tool(
    data: CustomToolCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> CustomToolResponse:
    """Register a custom tool definition (persisted to DB)."""
    service = ToolService(session)
    org_id = org.id if org else None

    result = await service.create_custom_tool(data, organization_id=org_id)

    await meter(session, "custom_tool_created", organization_id=org_id, resource_id=result.id)
    return result


@router.put("/{tool_id}", response_model=CustomToolResponse)
async def update_tool(
    tool_id: str,
    data: CustomToolUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> CustomToolResponse:
    """Update a custom tool definition."""
    service = ToolService(session)
    result = await service.update_custom_tool(tool_id, data)

    org_id = org.id if org else None
    await meter(session, "custom_tool_updated", organization_id=org_id, resource_id=tool_id)
    return result


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
) -> None:
    """Delete a custom tool."""
    service = ToolService(session)
    await service.delete_custom_tool(tool_id)

    org_id = org.id if org else None
    await meter(session, "custom_tool_deleted", organization_id=org_id, resource_id=tool_id)


@router.post("/{tool_name}/simulate", response_model=ToolResult)
async def simulate_tool(tool_name: str, arguments: dict[str, Any]) -> ToolResult:
    """Simulate tool execution and return a mock result."""
    get_tool(tool_name)

    tool_call = ToolCall(tool_name=tool_name, arguments=arguments)
    executor = SimulatedToolExecutor()
    result = await executor.execute(tool_call)

    logger.info(
        "tool_simulated",
        tool_name=tool_name,
        status=result.status,
        duration_ms=result.duration_ms,
    )
    return result
