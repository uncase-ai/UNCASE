"""UNCASE Pydantic schemas — data contracts for the SCSF pipeline."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.import_result import ImportErrorDetail, ImportResult
from uncase.schemas.quality import QualityMetrics, QualityReport, compute_composite_score
from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate
from uncase.schemas.seed import (
    MetricasCalidad,
    ParametrosFactuales,
    PasosTurnos,
    Privacidad,
    SeedSchema,
)
from uncase.schemas.template import RenderRequest, RenderResponse, TemplateInfo
from uncase.schemas.validation import ValidationCheck, ValidationReport
from uncase.tools.schemas import ToolCall, ToolDefinition, ToolParameter, ToolResult

__all__ = [
    "Conversation",
    "ConversationTurn",
    "ImportErrorDetail",
    "ImportResult",
    "MetricasCalidad",
    "ParametrosFactuales",
    "PasosTurnos",
    "Privacidad",
    "QualityMetrics",
    "QualityReport",
    "RenderRequest",
    "RenderResponse",
    "ScenarioPack",
    "ScenarioTemplate",
    "SeedSchema",
    "TemplateInfo",
    "ToolCall",
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "ValidationCheck",
    "ValidationReport",
    "compute_composite_score",
]
