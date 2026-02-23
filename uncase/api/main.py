"""UNCASE API — App factory and main configuration."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uncase._version import __version__
from uncase.api.middleware import register_exception_handlers
from uncase.api.routers.health import router as health_router
from uncase.api.routers.organizations import router as organizations_router
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
    application.include_router(organizations_router)

    # Mount MCP server (lazy import to avoid hard dependency at module level)
    try:
        from uncase.mcp.server import create_mcp_app

        mcp_app = create_mcp_app()
        application.mount("/mcp", mcp_app)
    except ImportError:
        pass

    return application


app = create_app()
