"""Evaluation API endpoints — Layer 2 quality assessment."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_optional_org
from uncase.db.models.evaluation import EvaluationReportModel
from uncase.db.models.organization import OrganizationModel
from uncase.schemas.evaluation import (
    BatchEvaluationResponse,
    EvaluateBatchRequest,
    EvaluateRequest,
    EvaluationReportListResponse,
    EvaluationReportResponse,
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
    strict: bool = Query(
        default=False,
        description="Raise 422 if the conversation fails quality thresholds",
    ),
) -> QualityReport:
    """Evaluate a single conversation against its origin seed.

    Returns a QualityReport with individual metric scores, composite score,
    and pass/fail determination. The report is persisted to the database.

    When ``strict=true``, a 422 QualityThresholdError is raised if the
    conversation does not pass all quality thresholds.
    """
    service = EvaluatorService(session=session)

    logger.info(
        "api_evaluate_single",
        conversation_id=request.conversation.conversation_id,
        seed_id=request.seed.seed_id,
        strict=strict,
    )

    return await service.evaluate_single(request.conversation, request.seed, strict=strict)


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


@router.get("/reports", response_model=EvaluationReportListResponse)
async def list_evaluation_reports(
    session: Annotated[AsyncSession, Depends(get_db)],
    org: Annotated[OrganizationModel | None, Depends(get_optional_org)],
    domain: Annotated[str | None, Query(description="Filter by domain")] = None,
    passed: Annotated[bool | None, Query(description="Filter by pass/fail")] = None,
    seed_id: Annotated[str | None, Query(description="Filter by seed ID")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> EvaluationReportListResponse:
    """List persisted evaluation reports with optional filters."""
    query = select(EvaluationReportModel)
    count_query = select(func.count()).select_from(EvaluationReportModel)

    org_id = org.id if org else None
    if org_id is not None:
        query = query.where(EvaluationReportModel.organization_id == org_id)
        count_query = count_query.where(EvaluationReportModel.organization_id == org_id)

    if domain is not None:
        query = query.where(EvaluationReportModel.dominio == domain)
        count_query = count_query.where(EvaluationReportModel.dominio == domain)

    if passed is not None:
        query = query.where(EvaluationReportModel.passed == passed)
        count_query = count_query.where(EvaluationReportModel.passed == passed)

    if seed_id is not None:
        query = query.where(EvaluationReportModel.seed_id == seed_id)
        count_query = count_query.where(EvaluationReportModel.seed_id == seed_id)

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(EvaluationReportModel.created_at.desc()).offset(offset).limit(page_size)
    result = await session.execute(query)
    reports = result.scalars().all()

    items = [
        EvaluationReportResponse(
            id=r.id,
            conversation_id=r.conversation_id,
            seed_id=r.seed_id,
            rouge_l=r.rouge_l,
            fidelidad_factual=r.fidelidad_factual,
            diversidad_lexica=r.diversidad_lexica,
            coherencia_dialogica=r.coherencia_dialogica,
            privacy_score=r.privacy_score,
            memorizacion=r.memorizacion,
            tool_call_validity=r.tool_call_validity,
            composite_score=r.composite_score,
            passed=r.passed,
            failures=r.failures,
            dominio=r.dominio,
            organization_id=r.organization_id,
            created_at=r.created_at,
        )
        for r in reports
    ]

    logger.info("evaluation_reports_listed", total=total, page=page)
    return EvaluationReportListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/thresholds", response_model=QualityThresholdsResponse)
async def get_quality_thresholds() -> QualityThresholdsResponse:
    """Return current quality thresholds and the composite score formula."""
    logger.info("thresholds_requested")
    return QualityThresholdsResponse()
