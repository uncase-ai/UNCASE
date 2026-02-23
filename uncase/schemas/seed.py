"""SeedSchema v1 — Central data model for the SCSF pipeline.

A Seed represents a sanitized, structured conversation template that captures
the essential patterns of a real interaction without any PII.
"""

from __future__ import annotations

import uuid
import warnings
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from uncase.tools.schemas import ToolDefinition  # noqa: TC001

SUPPORTED_DOMAINS = frozenset(
    {
        "automotive.sales",
        "medical.consultation",
        "legal.advisory",
        "finance.advisory",
        "industrial.support",
        "education.tutoring",
    }
)


class ParametrosFactuales(BaseModel):
    """Domain-specific factual parameters embedded in the seed."""

    contexto: str = Field(..., description="Contextual description of the scenario")
    restricciones: list[str] = Field(default_factory=list, description="Domain constraints or rules")
    herramientas: list[str] = Field(default_factory=list, description="Tools available in the interaction")
    herramientas_definidas: list[ToolDefinition] | None = Field(
        default=None, description="Structured tool definitions available in the interaction"
    )
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional domain-specific metadata")

    @model_validator(mode="after")
    def warn_mismatched_tools(self) -> ParametrosFactuales:
        """Warn if herramientas names don't match herramientas_definidas."""
        if self.herramientas and self.herramientas_definidas:
            defined_names = {td.name for td in self.herramientas_definidas}
            for name in self.herramientas:
                if name not in defined_names:
                    warnings.warn(
                        f"Tool '{name}' in herramientas does not match any "
                        f"herramientas_definidas entry. Defined: {sorted(defined_names)}",
                        UserWarning,
                        stacklevel=2,
                    )
        return self


class Privacidad(BaseModel):
    """Privacy guarantees for the seed."""

    pii_eliminado: bool = Field(default=True, description="Whether PII has been stripped")
    metodo_anonimizacion: str = Field(default="presidio", description="Anonymization method used")
    nivel_confianza: float = Field(default=0.85, ge=0.0, le=1.0, description="PII detection confidence threshold")
    campos_sensibles_detectados: list[str] = Field(
        default_factory=list, description="Fields where PII was detected and removed"
    )


class PasosTurnos(BaseModel):
    """Turn structure definition for the conversation."""

    turnos_min: int = Field(..., ge=1, description="Minimum number of turns")
    turnos_max: int = Field(..., ge=1, description="Maximum number of turns")
    flujo_esperado: list[str] = Field(..., min_length=1, description="Expected conversation flow steps")

    @model_validator(mode="after")
    def validate_turnos_range(self) -> PasosTurnos:
        """Ensure turnos_min < turnos_max."""
        if self.turnos_min >= self.turnos_max:
            msg = f"turnos_min ({self.turnos_min}) must be less than turnos_max ({self.turnos_max})"
            raise ValueError(msg)
        return self


class MetricasCalidad(BaseModel):
    """Quality metric thresholds for the seed."""

    rouge_l_min: float = Field(default=0.65, ge=0.0, le=1.0, description="Minimum ROUGE-L score")
    fidelidad_min: float = Field(default=0.90, ge=0.0, le=1.0, description="Minimum factual fidelity")
    diversidad_lexica_min: float = Field(default=0.55, ge=0.0, le=1.0, description="Minimum TTR")
    coherencia_dialogica_min: float = Field(default=0.85, ge=0.0, le=1.0, description="Minimum dialog coherence")


class SeedSchema(BaseModel):
    """SeedSchema v1 — The central data model for the SCSF framework.

    Represents a sanitized, structured conversation template ready
    for synthetic data generation.
    """

    # Identity
    seed_id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique seed identifier")
    version: Literal["1.0"] = Field(default="1.0", description="Schema version")

    # Classification
    dominio: str = Field(..., description="Domain namespace (e.g. 'automotive.sales')")
    idioma: str = Field(default="es", description="Conversation language (ISO 639-1)")
    etiquetas: list[str] = Field(default_factory=list, description="Classification tags")

    # Participants
    roles: list[str] = Field(..., min_length=2, description="Participant roles (minimum 2)")
    descripcion_roles: dict[str, str] = Field(default_factory=dict, description="Role descriptions keyed by role name")

    # Structure
    objetivo: str = Field(..., description="Conversation objective")
    tono: str = Field(default="profesional", description="Expected conversation tone")
    pasos_turnos: PasosTurnos = Field(..., description="Turn structure definition")

    # Domain facts
    parametros_factuales: ParametrosFactuales = Field(..., description="Domain-specific factual parameters")

    # Privacy
    privacidad: Privacidad = Field(default_factory=Privacidad, description="Privacy guarantees")

    # Quality
    metricas_calidad: MetricasCalidad = Field(default_factory=MetricasCalidad, description="Quality thresholds")

    # Metadata
    organization_id: str | None = Field(default=None, description="Owning organization ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Last update timestamp")

    @model_validator(mode="after")
    def validate_domain_supported(self) -> SeedSchema:
        """Ensure the domain is in the supported list."""
        if self.dominio not in SUPPORTED_DOMAINS:
            msg = f"Unsupported domain '{self.dominio}'. Supported: {sorted(SUPPORTED_DOMAINS)}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_pii_consistency(self) -> SeedSchema:
        """Cross-field validation: if PII was detected, it must be marked as removed."""
        if self.privacidad.campos_sensibles_detectados and not self.privacidad.pii_eliminado:
            msg = "PII fields were detected but pii_eliminado is False"
            raise ValueError(msg)
        return self


SeedSchemaType = Annotated[SeedSchema, Field(description="SeedSchema v1 instance")]
