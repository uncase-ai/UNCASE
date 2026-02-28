"""Seed API request and response schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from uncase.schemas.scenario import ScenarioTemplate  # noqa: TC001
from uncase.schemas.seed import MetricasCalidad, ParametrosFactuales, PasosTurnos, Privacidad

if TYPE_CHECKING:
    from datetime import datetime


class SeedCreateRequest(BaseModel):
    """Request body for creating a new seed.

    All fields that the client must provide. Server-side fields
    (id, seed_id, created_at, updated_at, organization_id) are set automatically.
    """

    dominio: str = Field(..., description="Domain namespace (e.g. 'automotive.sales')")
    idioma: str = Field(default="es", description="Conversation language (ISO 639-1)")
    version: str = Field(default="1.0", description="Schema version")
    etiquetas: list[str] = Field(default_factory=list, description="Classification tags")
    objetivo: str = Field(..., description="Conversation objective")
    tono: str = Field(default="profesional", description="Expected conversation tone")
    roles: list[str] = Field(..., min_length=2, description="Participant roles (minimum 2)")
    descripcion_roles: dict[str, str] = Field(default_factory=dict, description="Role descriptions keyed by role name")
    pasos_turnos: PasosTurnos = Field(..., description="Turn structure definition")
    parametros_factuales: ParametrosFactuales = Field(..., description="Domain-specific factual parameters")
    privacidad: Privacidad = Field(default_factory=Privacidad, description="Privacy guarantees")
    metricas_calidad: MetricasCalidad = Field(default_factory=MetricasCalidad, description="Quality thresholds")
    scenarios: list[ScenarioTemplate] | None = Field(
        default=None, description="Optional scenario templates for targeted generation"
    )


class SeedUpdateRequest(BaseModel):
    """Partial update request — all fields optional."""

    dominio: str | None = Field(default=None, description="Domain namespace")
    idioma: str | None = Field(default=None, description="Conversation language")
    version: str | None = Field(default=None, description="Schema version")
    etiquetas: list[str] | None = Field(default=None, description="Classification tags")
    objetivo: str | None = Field(default=None, description="Conversation objective")
    tono: str | None = Field(default=None, description="Expected conversation tone")
    roles: list[str] | None = Field(default=None, min_length=2, description="Participant roles")
    descripcion_roles: dict[str, str] | None = Field(default=None, description="Role descriptions")
    pasos_turnos: PasosTurnos | None = Field(default=None, description="Turn structure definition")
    parametros_factuales: ParametrosFactuales | None = Field(default=None, description="Domain-specific parameters")
    privacidad: Privacidad | None = Field(default=None, description="Privacy guarantees")
    metricas_calidad: MetricasCalidad | None = Field(default=None, description="Quality thresholds")
    scenarios: list[ScenarioTemplate] | None = Field(
        default=None, description="Scenario templates for targeted generation"
    )


class SeedRatingRequest(BaseModel):
    """Request body for rating a seed."""

    rating: float = Field(..., ge=0.0, le=5.0, description="User rating (0-5)")


class SeedResponse(BaseModel):
    """API response for a single seed."""

    id: str = Field(..., description="Database primary key")
    dominio: str
    idioma: str
    version: str
    etiquetas: list[str]
    objetivo: str
    tono: str
    roles: list[str]
    descripcion_roles: dict[str, str]
    pasos_turnos: PasosTurnos
    parametros_factuales: ParametrosFactuales
    privacidad: Privacidad
    metricas_calidad: MetricasCalidad
    scenarios: list[ScenarioTemplate] | None = Field(default=None, description="Scenario templates")
    rating: float | None = Field(default=None, description="Average user rating (0-5)")
    rating_count: int = Field(default=0, description="Number of ratings received")
    run_count: int = Field(default=0, description="Number of generation runs")
    avg_quality_score: float | None = Field(default=None, description="Average composite quality score across runs")
    organization_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SeedListResponse(BaseModel):
    """Paginated list of seeds."""

    items: list[SeedResponse]
    total: int
    page: int
    page_size: int


# Rebuild models that reference TYPE_CHECKING-only imports (datetime)
# so Pydantic can resolve forward references at runtime.
def _rebuild_models() -> None:
    from datetime import datetime as _dt

    ns = {"datetime": _dt}
    SeedResponse.model_rebuild(_types_namespace=ns)
    SeedListResponse.model_rebuild(_types_namespace=ns)


_rebuild_models()
del _rebuild_models
