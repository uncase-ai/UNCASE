"""Tool management API endpoints."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, status

from uncase.tools import get_registry, get_tool, list_tools
from uncase.tools.executor import SimulatedToolExecutor
from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])

logger = structlog.get_logger(__name__)


@router.get("", response_model=list[ToolDefinition])
async def list_tool_definitions(
    domain: str | None = None,
    category: str | None = None,
) -> list[ToolDefinition]:
    """List registered tool definitions with optional domain/category filters."""
    registry = get_registry()

    if domain is not None:
        tools = registry.list_by_domain(domain)
    elif category is not None:
        tools = registry.list_by_category(category)
    else:
        tools = [registry.get(name) for name in list_tools()]

    logger.info("tools_listed", count=len(tools), domain=domain, category=category)
    return tools


@router.get("/{tool_name}", response_model=ToolDefinition)
async def get_tool_definition(tool_name: str) -> ToolDefinition:
    """Get a single tool definition by name."""
    # Let ToolNotFoundError bubble to middleware handler
    tool = get_tool(tool_name)
    logger.info("tool_retrieved", tool_name=tool_name)
    return tool


@router.post("", response_model=ToolDefinition, status_code=status.HTTP_201_CREATED)
async def register_tool(tool: ToolDefinition) -> ToolDefinition:
    """Register a custom tool definition."""
    registry = get_registry()
    # Let DuplicateError bubble to middleware handler
    registry.register(tool)
    logger.info("tool_registered", tool_name=tool.name)
    return tool


@router.post("/{tool_name}/simulate", response_model=ToolResult)
async def simulate_tool(tool_name: str, arguments: dict[str, Any]) -> ToolResult:
    """Simulate tool execution and return a mock result."""
    # Let ToolNotFoundError bubble to middleware handler
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
