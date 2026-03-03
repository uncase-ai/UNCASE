"""Layer 0 — Agentic extraction API endpoints.

Exposes the AgenticExtractionEngine as a stateful, turn-by-turn REST API.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException, status

from uncase.api.session_store import extraction_sessions
from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.engine import AgenticExtractionEngine
from uncase.schemas.layer0_api import (
    ProgressResponse,
    StartExtractionRequest,
    StartExtractionResponse,
    TurnRequest,
    TurnResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/seeds/extract", tags=["layer0"])


@router.post(
    "/start",
    response_model=StartExtractionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_extraction(body: StartExtractionRequest) -> StartExtractionResponse:
    """Create a new extraction session and return the initial question."""
    config = Layer0Config(
        industry=body.industry,
        max_turns=body.max_turns,
        default_locale=body.locale,
    )
    engine = AgenticExtractionEngine(config=config)
    session_id = extraction_sessions.create(engine)

    initial = await engine.get_initial_question()

    logger.info(
        "extraction_started",
        session_id=session_id,
        industry=body.industry,
    )

    return StartExtractionResponse(session_id=session_id, message=initial)


@router.post("/turn", response_model=TurnResponse)
async def process_turn(body: TurnRequest) -> TurnResponse:
    """Process a single conversation turn."""
    engine = extraction_sessions.get(body.session_id)
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{body.session_id}' not found or expired.",
        )

    result = await engine.process_turn(body.user_message)
    is_complete = result.get("type") == "summary"

    logger.info(
        "extraction_turn",
        session_id=body.session_id,
        type=result.get("type"),
        turn=engine.state.turn_count,
    )

    if is_complete:
        extraction_sessions.delete(body.session_id)

    return TurnResponse(
        session_id=body.session_id,
        message=result,
        is_complete=is_complete,
    )


@router.get("/{session_id}/progress", response_model=ProgressResponse)
async def get_progress(session_id: str) -> ProgressResponse:
    """Get the current progress of an extraction session."""
    engine = extraction_sessions.get(session_id)
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found or expired.",
        )

    return ProgressResponse(
        session_id=session_id,
        progress=engine.state.get_progress(),
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(session_id: str) -> None:
    """Delete an extraction session."""
    removed = extraction_sessions.delete(session_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
