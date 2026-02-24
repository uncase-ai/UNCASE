"""Generation API endpoints — Layer 3 synthetic conversation generation."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.schemas.generation import GenerateRequest, GenerateResponse
from uncase.services.generator import GeneratorService

router = APIRouter(prefix="/api/v1/generate", tags=["generation"])

logger = structlog.get_logger(__name__)


@router.post("", response_model=GenerateResponse)
async def generate_conversations(
    request: GenerateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> GenerateResponse:
    """Generate synthetic conversations from a seed.

    Takes a SeedSchema and produces one or more synthetic conversations
    using an LLM. Optionally evaluates each generated conversation
    against quality thresholds.

    Returns the generated conversations, optional quality reports,
    and a generation summary with timing and statistics.
    """
    logger.info(
        "api_generate_request",
        seed_id=request.seed.seed_id,
        domain=request.seed.dominio,
        count=request.count,
        model=request.model,
        evaluate_after=request.evaluate_after,
    )

    service = GeneratorService(session=session, settings=settings)

    return await service.generate(
        seed=request.seed,
        count=request.count,
        temperature=request.temperature,
        model=request.model,
        language_override=request.language_override,
        evaluate_after=request.evaluate_after,
    )
