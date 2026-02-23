"""UNCASE API — App factory y configuración principal."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uncase._version import __version__


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    application = FastAPI(
        title="UNCASE API",
        description="API del framework SCSF para generación de datos conversacionales sintéticos.",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["sistema"])
    async def health() -> dict[str, str]:
        """Endpoint de health check."""
        return {"status": "ok", "version": __version__}

    return application


app = create_app()
