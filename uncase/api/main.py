"""UNCASE API — App factory and main configuration."""

from __future__ import annotations

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
from uncase.api.routers.costs import router as costs_router
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: init DB engine on startup, close on shutdown."""
    settings = UNCASESettings()
    setup_logging(log_level=settings.uncase_log_level, json_output=settings.is_production)
    init_engine(settings)
    yield
    await close_engine()


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
    application.include_router(generation_router)
    application.include_router(pipeline_router)
    application.include_router(jobs_router)
    application.include_router(plugins_router)
    application.include_router(providers_router)
    application.include_router(sandbox_router)
    application.include_router(connectors_router)
    application.include_router(gateway_router)
    application.include_router(knowledge_router)
    application.include_router(usage_router)
    application.include_router(webhooks_router)
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
