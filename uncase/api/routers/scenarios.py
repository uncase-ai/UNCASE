"""Scenario pack browsing API endpoints.

Exposes the built-in domain scenario packs as a read-only catalog.
Scenario packs are code-defined (not DB-persisted) and loaded lazily.
"""

from __future__ import annotations

from typing import Literal

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from uncase.domains.scenario_packs import get_scenario_pack, list_scenario_packs
from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])

logger = structlog.get_logger(__name__)


# ─── Response schemas ───


class ScenarioPackSummary(BaseModel):
    """Lightweight summary for pack listing."""

    id: str
    name: str
    description: str
    domain: str
    version: str
    scenario_count: int = Field(..., description="Total number of scenario templates in this pack")
    edge_case_count: int = Field(..., description="Number of edge-case scenarios")
    skill_levels: list[str] = Field(..., description="Distinct skill levels available")
    tags: list[str] = Field(..., description="Aggregated unique tags from all scenarios")


class ScenarioPackListResponse(BaseModel):
    """Response for listing all available scenario packs."""

    packs: list[ScenarioPackSummary]
    total: int


class ScenarioPackDetailResponse(BaseModel):
    """Full scenario pack with all templates."""

    id: str
    name: str
    description: str
    domain: str
    version: str
    scenarios: list[ScenarioTemplate]
    scenario_count: int
    edge_case_count: int
    skill_levels: list[str]
    tags: list[str]


class ScenarioListResponse(BaseModel):
    """Filtered list of scenarios from a pack."""

    domain: str
    scenarios: list[ScenarioTemplate]
    total: int
    filters_applied: dict[str, str]


# ─── Helpers ───


def _summarize_pack(pack: ScenarioPack) -> ScenarioPackSummary:
    """Build a summary from a full scenario pack."""
    edge_cases = [s for s in pack.scenarios if s.edge_case]
    levels: list[str] = sorted({s.skill_level for s in pack.scenarios})
    all_tags: list[str] = sorted({tag for s in pack.scenarios for tag in s.tags})

    return ScenarioPackSummary(
        id=pack.id,
        name=pack.name,
        description=pack.description,
        domain=pack.domain,
        version=pack.version,
        scenario_count=len(pack.scenarios),
        edge_case_count=len(edge_cases),
        skill_levels=levels,
        tags=all_tags,
    )


def _detail_from_pack(pack: ScenarioPack) -> ScenarioPackDetailResponse:
    """Build a detailed response from a full scenario pack."""
    edge_cases = [s for s in pack.scenarios if s.edge_case]
    levels: list[str] = sorted({s.skill_level for s in pack.scenarios})
    all_tags: list[str] = sorted({tag for s in pack.scenarios for tag in s.tags})

    return ScenarioPackDetailResponse(
        id=pack.id,
        name=pack.name,
        description=pack.description,
        domain=pack.domain,
        version=pack.version,
        scenarios=pack.scenarios,
        scenario_count=len(pack.scenarios),
        edge_case_count=len(edge_cases),
        skill_levels=levels,
        tags=all_tags,
    )


# ─── Endpoints ───


@router.get("/packs", response_model=ScenarioPackListResponse)
async def list_packs() -> ScenarioPackListResponse:
    """List all available scenario packs with summary metadata.

    Returns a lightweight overview of each pack — no individual scenario
    details. Use ``GET /packs/{domain}`` for full scenario templates.
    """
    packs = list_scenario_packs()
    summaries = [_summarize_pack(p) for p in packs]
    summaries.sort(key=lambda s: s.domain)

    logger.info("scenario_packs_listed", count=len(summaries))
    return ScenarioPackListResponse(packs=summaries, total=len(summaries))


@router.get("/packs/{domain}", response_model=ScenarioPackDetailResponse)
async def get_pack(domain: str) -> ScenarioPackDetailResponse:
    """Get a scenario pack by domain with all scenario templates.

    The domain must be a fully qualified domain namespace
    (e.g. ``automotive.sales``, ``medical.consultation``).
    """
    pack = get_scenario_pack(domain)

    if pack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scenario pack found for domain '{domain}'",
        )

    logger.info("scenario_pack_retrieved", domain=domain, scenario_count=len(pack.scenarios))
    return _detail_from_pack(pack)


@router.get("/packs/{domain}/scenarios", response_model=ScenarioListResponse)
async def list_scenarios(
    domain: str,
    skill_level: Literal["basic", "intermediate", "advanced"] | None = Query(None, description="Filter by skill level"),
    edge_case: bool | None = Query(None, description="Filter by edge-case flag"),
    tag: str | None = Query(None, description="Filter by tag (exact match)"),
) -> ScenarioListResponse:
    """List scenarios from a pack with optional filters.

    Supports filtering by skill level, edge-case flag, and tag.
    Useful for building filtered scenario selectors in the UI.
    """
    pack = get_scenario_pack(domain)

    if pack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scenario pack found for domain '{domain}'",
        )

    scenarios = list(pack.scenarios)

    filters: dict[str, str] = {}

    if skill_level is not None:
        scenarios = [s for s in scenarios if s.skill_level == skill_level]
        filters["skill_level"] = skill_level

    if edge_case is not None:
        scenarios = [s for s in scenarios if s.edge_case == edge_case]
        filters["edge_case"] = str(edge_case)

    if tag is not None:
        scenarios = [s for s in scenarios if tag in s.tags]
        filters["tag"] = tag

    logger.info(
        "scenarios_listed",
        domain=domain,
        total=len(scenarios),
        filters=filters,
    )

    return ScenarioListResponse(
        domain=domain,
        scenarios=scenarios,
        total=len(scenarios),
        filters_applied=filters,
    )
