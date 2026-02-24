"""Evaluation API endpoints — Layer 2 quality assessment."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db
from uncase.schemas.evaluation import (
    BatchEvaluationResponse,
    EvaluateBatchRequest,
    EvaluateRequest,
    QualityThresholdsResponse,
)
from uncase.schemas.quality import QualityReport
from uncase.services.evaluator import EvaluatorService

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])

logger = structlog.get_logger(__name__)


@router.post("", response_model=QualityReport)
async def evaluate_conversation(
    request: EvaluateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> QualityReport:
    """Evaluate a single conversation against its origin seed.

    Returns a QualityReport with individual metric scores, composite score,
    and pass/fail determination. The report is persisted to the database.
    """
    service = EvaluatorService(session=session)

    logger.info(
        "api_evaluate_single",
        conversation_id=request.conversation.conversation_id,
        seed_id=request.seed.seed_id,
    )

    return await service.evaluate_single(request.conversation, request.seed)


@router.post("/batch", response_model=BatchEvaluationResponse)
async def evaluate_batch(
    request: EvaluateBatchRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BatchEvaluationResponse:
    """Evaluate a batch of conversation-seed pairs.

    Returns individual reports plus aggregate statistics.
    All reports are persisted to the database.
    """
    service = EvaluatorService(session=session)

    conversations = [pair.conversation for pair in request.pairs]
    seeds = [pair.seed for pair in request.pairs]

    logger.info("api_evaluate_batch", batch_size=len(request.pairs))

    result = await service.evaluate_batch(conversations, seeds)

    return BatchEvaluationResponse(
        total=result.total,
        passed=result.passed_count,
        failed=result.failed_count,
        pass_rate=round(result.pass_rate, 2),
        avg_composite_score=result.avg_composite_score,
        metric_averages=result.metric_averages,
        failure_summary=result.failure_summary,
        reports=result.reports,
    )


@router.get("/thresholds", response_model=QualityThresholdsResponse)
async def get_quality_thresholds() -> QualityThresholdsResponse:
    """Return current quality thresholds and the composite score formula."""
    logger.info("thresholds_requested")
    return QualityThresholdsResponse()
