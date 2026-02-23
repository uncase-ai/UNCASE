"""Health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from uncase._version import __version__
from uncase.api.deps import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok", "version": __version__}


@router.get("/health/db")
async def health_db(session: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, str]:
    """Health check including database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {"status": "ok", "version": __version__, "database": db_status}
