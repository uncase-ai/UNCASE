"""Health check endpoints."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from uncase._version import __version__
from uncase.api.deps import get_db
from uncase.config import get_settings

router = APIRouter(tags=["system"])

logger = structlog.get_logger(__name__)


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to health check."""
    return RedirectResponse(url="/health")


@router.get("/health")
async def health() -> dict[str, object]:
    """Basic health check with LLM availability."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": __version__,
        "llm_configured": settings.llm_available,
    }


@router.get("/health/db")
async def health_db(session: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Health check including database connectivity."""
    settings = get_settings()
    try:
        await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        logger.warning("health_db_check_failed", version=__version__)
        db_status = "disconnected"

    return {
        "status": "ok",
        "version": __version__,
        "database": db_status,
        "llm_configured": settings.llm_available,
    }


@router.get("/health/setup")
async def health_setup(session: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Check whether the system has been set up (any users/orgs exist).

    Used by the frontend to decide whether to show the login screen
    or the initial setup/onboarding flow.
    """
    from uncase.db.models.organization import OrganizationModel
    from uncase.db.models.user import UserModel

    try:
        user_count = (await session.execute(select(func.count(UserModel.id)))).scalar_one()
        org_count = (await session.execute(select(func.count(OrganizationModel.id)))).scalar_one()
    except Exception:
        logger.warning("health_setup_check_failed", version=__version__)
        return {
            "has_users": False,
            "has_organizations": False,
            "setup_complete": False,
        }

    return {
        "has_users": user_count > 0,
        "has_organizations": org_count > 0,
        "setup_complete": user_count > 0 and org_count > 0,
    }
