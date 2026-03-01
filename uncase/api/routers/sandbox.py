"""Sandbox API endpoints — E2B parallel generation."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.exceptions import SandboxNotConfiguredError
from uncase.sandbox.schemas import (
    DemoSandboxRequest,
    DemoSandboxResponse,
    OpikEvaluationRequest,
    OpikEvaluationResponse,
    SandboxGenerateRequest,
    SandboxGenerateResponse,
    SandboxJob,
    SandboxJobStatus,
    SandboxProgress,
    SandboxTemplate,
)
from uncase.schemas.generation import SandboxStatusResponse

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

logger = structlog.get_logger(__name__)


async def _resolve_api_key(
    settings: UNCASESettings,
    session: AsyncSession | None = None,
    provider_id: str | None = None,
) -> tuple[str | None, str | None]:
    """Resolve API key and api_base from settings or provider.

    Returns:
        Tuple of (api_key, api_base).
    """
    if provider_id and session:
        from uncase.services.provider import ProviderService

        provider_service = ProviderService(session=session, settings=settings)
        provider = await provider_service._get_or_raise(provider_id)
        api_key = provider_service.decrypt_provider_key(provider)
        return api_key, provider.api_base

    if settings.litellm_api_key:
        return settings.litellm_api_key, None
    if settings.anthropic_api_key:
        return settings.anthropic_api_key, None
    return None, None


@router.get("/status", response_model=SandboxStatusResponse)
async def sandbox_status(
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> SandboxStatusResponse:
    """Check E2B sandbox availability and configuration."""
    return SandboxStatusResponse(
        enabled=settings.sandbox_available,
        max_parallel=settings.e2b_max_parallel,
        template_id=settings.e2b_template_id,
    )


@router.post("", response_model=SandboxGenerateResponse)
async def sandbox_generate(
    request: SandboxGenerateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> SandboxGenerateResponse:
    """Generate conversations in parallel using E2B sandboxes.

    Each seed gets its own isolated sandbox running the generation
    pipeline independently. Results are collected after all sandboxes
    complete.

    Falls back to sequential local generation if E2B is not configured.
    """
    logger.info(
        "api_sandbox_generate",
        total_seeds=len(request.seeds),
        count_per_seed=request.count_per_seed,
        model=request.model,
        max_parallel=request.max_parallel,
    )

    # Resolve API key
    api_key, api_base = await _resolve_api_key(settings, session, request.provider_id)

    if not settings.sandbox_available:
        # Fallback to local sequential generation
        return await _local_fallback(
            request=request,
            session=session,
            settings=settings,
            api_key=api_key,
            api_base=api_base,
        )

    from uncase.sandbox.e2b_client import E2BSandboxOrchestrator

    orchestrator = E2BSandboxOrchestrator(settings=settings)

    seed_dicts = [seed.model_dump(mode="json") for seed in request.seeds]

    return await orchestrator.fan_out_generate(
        seeds=seed_dicts,
        count_per_seed=request.count_per_seed,
        model=request.model or "claude-sonnet-4-20250514",
        temperature=request.temperature,
        api_key=api_key,
        api_base=api_base,
        language_override=request.language_override,
        evaluate_after=request.evaluate_after,
        max_parallel=request.max_parallel,
    )


@router.post("/stream")
async def sandbox_generate_stream(
    request: SandboxGenerateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> StreamingResponse:
    """Stream progress events during parallel sandbox generation (SSE).

    Returns a Server-Sent Events stream with:
    - `data:` events for SandboxProgress updates
    - `event: complete` with the final SandboxGenerateResponse
    """
    if not settings.sandbox_available:
        raise SandboxNotConfiguredError("Streaming requires E2B sandboxes. Set E2B_API_KEY and E2B_ENABLED=true.")

    api_key, api_base = await _resolve_api_key(settings, session, request.provider_id)

    from uncase.sandbox.e2b_client import E2BSandboxOrchestrator

    orchestrator = E2BSandboxOrchestrator(settings=settings)
    seed_dicts = [seed.model_dump(mode="json") for seed in request.seeds]

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in orchestrator.fan_out_generate_stream(
            seeds=seed_dicts,
            count_per_seed=request.count_per_seed,
            model=request.model or "claude-sonnet-4-20250514",
            temperature=request.temperature,
            api_key=api_key,
            api_base=api_base,
            language_override=request.language_override,
            evaluate_after=request.evaluate_after,
            max_parallel=request.max_parallel,
        ):
            if isinstance(event, SandboxProgress):
                yield f"data: {event.model_dump_json()}\n\n"
            else:
                # Final response
                yield f"event: complete\ndata: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _local_fallback(
    *,
    request: SandboxGenerateRequest,
    session: AsyncSession,
    settings: UNCASESettings,
    api_key: str | None,
    api_base: str | None,
) -> SandboxGenerateResponse:
    """Fall back to sequential local generation when E2B is not available."""
    import time

    from uncase.sandbox.schemas import (
        SandboxGenerateResponse,
        SandboxGenerationSummary,
        SandboxSeedResult,
    )
    from uncase.services.generator import GeneratorService

    logger.warning("sandbox_fallback_local", reason="E2B not configured, using local generation")

    start_time = time.monotonic()
    service = GeneratorService(session=session, settings=settings)
    results: list[SandboxSeedResult] = []

    for seed in request.seeds:
        seed_start = time.monotonic()
        try:
            response = await service.generate(
                seed=seed,
                count=request.count_per_seed,
                temperature=request.temperature,
                model=request.model,
                provider_id=request.provider_id,
                language_override=request.language_override,
                evaluate_after=request.evaluate_after,
            )

            passed_count = 0
            if response.reports:
                passed_count = sum(1 for r in response.reports if r.passed)

            results.append(
                SandboxSeedResult(
                    seed_id=seed.seed_id,
                    conversations=response.conversations,
                    reports=response.reports,
                    passed_count=passed_count,
                    duration_seconds=round(time.monotonic() - seed_start, 2),
                )
            )
        except Exception as exc:
            results.append(
                SandboxSeedResult(
                    seed_id=seed.seed_id,
                    error=str(exc),
                    duration_seconds=round(time.monotonic() - seed_start, 2),
                )
            )

    total_conversations = sum(len(r.conversations) for r in results)
    total_passed: int | None = None
    avg_score: float | None = None

    if request.evaluate_after:
        all_reports = [r for result in results if result.reports for r in result.reports]
        if all_reports:
            total_passed = sum(1 for r in all_reports if r.passed)
            avg_score = round(sum(r.composite_score for r in all_reports) / len(all_reports), 4)

    failed_seeds = sum(1 for r in results if r.error is not None)
    duration = round(time.monotonic() - start_time, 2)

    summary = SandboxGenerationSummary(
        total_seeds=len(request.seeds),
        total_conversations=total_conversations,
        total_passed=total_passed,
        avg_composite_score=avg_score,
        failed_seeds=failed_seeds,
        model_used=request.model or "claude-sonnet-4-20250514",
        temperature=request.temperature,
        max_parallel=1,
        duration_seconds=duration,
        sandbox_mode=False,
    )

    return SandboxGenerateResponse(results=results, summary=summary)


# -- Demo sandbox endpoints --


@router.post("/demo", response_model=DemoSandboxResponse)
async def create_demo_sandbox(
    demo_request: DemoSandboxRequest,
    http_request: Request,
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> DemoSandboxResponse:
    """Spin up a short-lived demo sandbox for an industry vertical.

    Creates a fully configured UNCASE instance with pre-loaded seeds
    for the specified domain. The sandbox auto-destroys after the TTL
    expires.

    Falls back to the main API's Swagger docs when E2B is unavailable,
    so users always get a working demo experience.
    """
    logger.info(
        "api_demo_sandbox",
        domain=demo_request.domain,
        ttl_minutes=demo_request.ttl_minutes,
        preload_seeds=demo_request.preload_seeds,
        e2b_available=settings.sandbox_available,
    )

    # Try E2B sandbox first
    if settings.sandbox_available:
        try:
            from uncase.sandbox.demo import DemoSandboxOrchestrator

            demo = DemoSandboxOrchestrator(settings=settings)
            return await demo.create_demo(demo_request)
        except Exception as exc:
            logger.warning(
                "demo_sandbox_e2b_failed",
                domain=demo_request.domain,
                error=str(exc),
            )

    # Graceful fallback — point to main API docs with static seed data
    logger.info("demo_sandbox_fallback", domain=demo_request.domain)
    return _build_demo_fallback(demo_request, http_request)


def _build_demo_fallback(req: DemoSandboxRequest, http_req: Request) -> DemoSandboxResponse:
    """Build a fallback demo response pointing to the main API's Swagger docs.

    Includes static demo seeds so the frontend can show them inline.
    """
    from uncase.sandbox.demo import _DEMO_SEEDS

    base_url = str(http_req.base_url).rstrip("/")

    # Build demo seed list
    demo_seed = _DEMO_SEEDS.get(req.domain, next(iter(_DEMO_SEEDS.values())))
    seeds_data: list[dict[str, object]] = []
    for i in range(req.preload_seeds):
        seed = dict(demo_seed)
        seed["seed_id"] = f"demo-{req.domain.replace('.', '-')}-{i + 1}"
        if req.language != "es":
            seed["idioma"] = req.language
        seeds_data.append(seed)

    # Resolve template
    template_map: dict[str, SandboxTemplate] = {
        "automotive.sales": SandboxTemplate.DEMO_AUTOMOTIVE,
        "medical.consultation": SandboxTemplate.DEMO_MEDICAL,
        "legal.advisory": SandboxTemplate.DEMO_LEGAL,
        "finance.advisory": SandboxTemplate.DEMO_FINANCE,
        "industrial.support": SandboxTemplate.DEMO_INDUSTRIAL,
        "education.tutoring": SandboxTemplate.DEMO_EDUCATION,
    }
    template = template_map.get(req.domain, SandboxTemplate.DEMO_AUTOMOTIVE)

    job = SandboxJob(
        template=template,
        status=SandboxJobStatus.RUNNING,
        api_url=base_url,
        sandbox_url=base_url,
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )

    return DemoSandboxResponse(
        job=job,
        api_url=base_url,
        docs_url=f"{base_url}/docs",
        expires_at=datetime.now(UTC) + timedelta(hours=24),
        preloaded_seeds=len(seeds_data),
        domain=req.domain,
        fallback=True,
        demo_seeds=seeds_data,
    )


# -- Opik evaluation endpoints --


@router.post("/evaluate", response_model=OpikEvaluationResponse)
async def run_opik_evaluation(
    request: OpikEvaluationRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> OpikEvaluationResponse:
    """Run LLM-as-judge evaluation using Opik in an ephemeral sandbox.

    Spins up a sandbox with Opik installed, runs hallucination detection,
    coherence evaluation, and relevance scoring on the provided conversations.
    Results are exported to persistent storage before the sandbox is destroyed.

    This gives each evaluation run its own isolated Opik instance without
    requiring permanent infrastructure.
    """
    if not settings.sandbox_available:
        raise SandboxNotConfiguredError("Opik evaluation requires E2B. Set E2B_API_KEY and E2B_ENABLED=true.")

    logger.info(
        "api_opik_evaluation",
        experiment_name=request.experiment_name,
        total_conversations=len(request.conversations),
        ttl_minutes=request.ttl_minutes,
    )

    api_key, _api_base = await _resolve_api_key(settings, session, request.provider_id)

    from uncase.sandbox.opik_runner import OpikSandboxRunner

    runner = OpikSandboxRunner(settings=settings)
    return await runner.run_evaluation(request, api_key=api_key)
