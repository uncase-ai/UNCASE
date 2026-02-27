"""UNCASE API — App factory and main configuration."""

from __future__ import annotations

import asyncio
import contextlib
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uncase._version import __version__
from uncase.api.metrics import MetricsMiddleware
from uncase.api.metrics import router as metrics_router
from uncase.api.middleware import register_exception_handlers
from uncase.api.rate_limit import RateLimitMiddleware
from uncase.api.routers.audit import router as audit_router
from uncase.api.routers.auth import router as auth_router
from uncase.api.routers.connectors import router as connectors_router
from uncase.api.routers.conversations import router as conversations_router
from uncase.api.routers.costs import router as costs_router
from uncase.api.routers.e2b_webhooks import router as e2b_webhooks_router
from uncase.api.routers.evaluations import router as evaluations_router
from uncase.api.routers.gateway import router as gateway_router
from uncase.api.routers.generation import router as generation_router
from uncase.api.routers.health import router as health_router
from uncase.api.routers.imports import router as imports_router
from uncase.api.routers.jobs import router as jobs_router
from uncase.api.routers.knowledge import router as knowledge_router
from uncase.api.routers.organizations import router as organizations_router
from uncase.api.routers.pipeline import router as pipeline_router
from uncase.api.routers.plugins import router as plugins_router
from uncase.api.routers.providers import router as providers_router
from uncase.api.routers.sandbox import router as sandbox_router
from uncase.api.routers.scenarios import router as scenarios_router
from uncase.api.routers.seeds import router as seeds_router
from uncase.api.routers.templates import router as templates_router
from uncase.api.routers.tools import router as tools_router
from uncase.api.routers.usage import router as usage_router
from uncase.api.routers.webhooks import router as webhooks_router
from uncase.config import UNCASESettings
from uncase.db.engine import close_engine, init_engine
from uncase.logging import setup_logging

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

_WEBHOOK_INTERVAL_SECONDS = 30


def _validate_secret_key(settings: UNCASESettings) -> None:
    """Abort startup if the API secret key is still the default in production."""
    from uncase.logging import get_logger

    _logger = get_logger("uncase.startup")

    if settings.api_secret_key == "cambiar-en-produccion":  # noqa: S105
        if settings.is_production:
            msg = (
                "FATAL: api_secret_key is still the default value. "
                "Set API_SECRET_KEY to a strong random secret before running in production."
            )
            _logger.error("insecure_secret_key", env=settings.uncase_env)
            raise SystemExit(msg)

        _logger.warning(
            "insecure_secret_key",
            message="Using default api_secret_key. Set API_SECRET_KEY for non-development environments.",
        )


async def _webhook_scheduler() -> None:
    """Background loop that processes pending webhook deliveries."""
    from uncase.db.engine import get_async_session
    from uncase.logging import get_logger
    from uncase.services.webhook import WebhookService

    _logger = get_logger("uncase.webhook_scheduler")

    while True:
        await asyncio.sleep(_WEBHOOK_INTERVAL_SECONDS)

        with contextlib.suppress(Exception):
            async for session in get_async_session():
                service = WebhookService(session)
                processed = await service.execute_pending_deliveries()

                if processed:
                    _logger.debug("webhook_scheduler_tick", processed=processed)

                break


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: init DB engine on startup, close on shutdown."""
    settings = UNCASESettings()
    _validate_secret_key(settings)
    setup_logging(log_level=settings.uncase_log_level, json_output=settings.is_production)
    init_engine(settings)
    await _hydrate_tools_from_db()

    webhook_task = asyncio.create_task(_webhook_scheduler())
    yield
    webhook_task.cancel()

    with contextlib.suppress(asyncio.CancelledError):
        await webhook_task

    await close_engine()


async def _hydrate_tools_from_db() -> None:
    """Restore persisted custom tools and plugin installations on startup.

    This ensures the in-memory registries are consistent with database state
    after a server restart. Non-fatal: logs but never crashes the app.
    """
    import contextlib

    from uncase.logging import get_logger

    _logger = get_logger("uncase.hydration")

    with contextlib.suppress(Exception):
        from sqlalchemy import select

        from uncase.db.engine import get_async_session
        from uncase.db.models.custom_tool import CustomToolModel
        from uncase.db.models.installed_plugin import InstalledPluginModel
        from uncase.plugins import get_registry as get_plugin_registry
        from uncase.tools import get_registry as get_tool_registry
        from uncase.tools.schemas import ToolDefinition

        tool_registry = get_tool_registry()
        plugin_registry = get_plugin_registry()

        async for session in get_async_session():
            # Hydrate installed plugins
            result = await session.execute(select(InstalledPluginModel).where(InstalledPluginModel.is_active.is_(True)))
            plugin_count = 0
            for row in result.scalars():
                try:
                    if not plugin_registry.is_installed(row.plugin_id):
                        plugin_registry.install(row.plugin_id)
                        plugin_count += 1
                except Exception:
                    _logger.debug("plugin_hydration_skipped", plugin_id=row.plugin_id)

            # Hydrate custom tools
            result = await session.execute(select(CustomToolModel).where(CustomToolModel.is_active.is_(True)))
            tool_count = 0
            for row in result.scalars():
                if row.name not in tool_registry:
                    tool_def = ToolDefinition(
                        name=row.name,
                        description=row.description,
                        input_schema=row.input_schema,
                        output_schema=row.output_schema,
                        domains=row.domains,
                        category=row.category,
                        requires_auth=row.requires_auth,
                        execution_mode=row.execution_mode,
                        version=row.version,
                        metadata=row.metadata_ or {},
                    )
                    tool_registry.register(tool_def)
                    tool_count += 1

            _logger.info("hydration_complete", plugins=plugin_count, custom_tools=tool_count)
            break  # Only need one session


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = UNCASESettings()

    application = FastAPI(
        title="UNCASE API",
        description="SCSF framework API for synthetic conversational data generation.",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware (applied in reverse order — last added = first executed)
    # Security headers (outermost)
    from uncase.api.security_headers import SecurityHeadersMiddleware

    application.add_middleware(SecurityHeadersMiddleware)

    # Metrics instrumentation
    application.add_middleware(MetricsMiddleware)

    # Rate limiting
    application.add_middleware(RateLimitMiddleware)

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(application)

    # Routers
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(organizations_router)
    application.include_router(templates_router)
    application.include_router(tools_router)
    application.include_router(imports_router)
    application.include_router(evaluations_router)
    application.include_router(seeds_router)
    application.include_router(scenarios_router)
    application.include_router(generation_router)
    application.include_router(pipeline_router)
    application.include_router(jobs_router)
    application.include_router(plugins_router)
    application.include_router(providers_router)
    application.include_router(sandbox_router)
    application.include_router(connectors_router)
    application.include_router(conversations_router)
    application.include_router(gateway_router)
    application.include_router(knowledge_router)
    application.include_router(usage_router)
    application.include_router(webhooks_router)
    application.include_router(e2b_webhooks_router)
    application.include_router(audit_router)
    application.include_router(costs_router)
    application.include_router(metrics_router)

    # Mount MCP server (lazy import to avoid hard dependency at module level)
    try:
        from uncase.mcp.server import create_mcp_app

        mcp_app = create_mcp_app()
        application.mount("/mcp", mcp_app)
    except ImportError:
        pass

    return application


app = create_app()
