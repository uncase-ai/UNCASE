"""UNCASE Pydantic schemas — data contracts for the SCSF pipeline."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.quality import QualityMetrics, QualityReport, compute_composite_score
from uncase.schemas.seed import (
    MetricasCalidad,
    ParametrosFactuales,
    PasosTurnos,
    Privacidad,
    SeedSchema,
)
from uncase.schemas.validation import ValidationCheck, ValidationReport

__all__ = [
    "Conversation",
    "ConversationTurn",
    "MetricasCalidad",
    "ParametrosFactuales",
    "PasosTurnos",
    "Privacidad",
    "QualityMetrics",
    "QualityReport",
    "SeedSchema",
    "ValidationCheck",
    "ValidationReport",
    "compute_composite_score",
]
