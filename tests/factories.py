"""Test data factories — only synthetic/fictional data, never real PII."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.quality import QualityMetrics
from uncase.schemas.seed import (
    MetricasCalidad,
    ParametrosFactuales,
    PasosTurnos,
    Privacidad,
    SeedSchema,
)
from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult


def make_seed(**overrides: object) -> SeedSchema:
    """Create a valid SeedSchema with sensible defaults.

    All data is fictional — no real PII.
    """
    defaults: dict[str, object] = {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["vendedor", "cliente"],
        "descripcion_roles": {
            "vendedor": "Asesor de ventas ficticio",
            "cliente": "Cliente ficticio",
        },
        "objetivo": "Consulta ficticia sobre vehiculos de prueba",
        "tono": "profesional",
        "pasos_turnos": PasosTurnos(
            turnos_min=6,
            turnos_max=20,
            flujo_esperado=["saludo", "consulta", "resolucion"],
        ),
        "parametros_factuales": ParametrosFactuales(
            contexto="Concesionario ficticio de prueba",
            restricciones=["Restriccion de prueba"],
            herramientas=["crm"],
            metadata={},
        ),
        "privacidad": Privacidad(),
        "metricas_calidad": MetricasCalidad(),
    }
    defaults.update(overrides)
    return SeedSchema(**defaults)  # type: ignore[arg-type]


def make_conversation(seed_id: str = "test_seed_001", **overrides: object) -> Conversation:
    """Create a valid Conversation with fictional data."""
    defaults: dict[str, object] = {
        "seed_id": seed_id,
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco informacion sobre vehiculos."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto, que tipo de vehiculo le interesa?"),
        ],
        "es_sintetica": True,
    }
    defaults.update(overrides)
    return Conversation(**defaults)  # type: ignore[arg-type]


def make_quality_metrics(**overrides: object) -> QualityMetrics:
    """Create quality metrics with passing defaults."""
    defaults: dict[str, object] = {
        "rouge_l": 0.75,
        "fidelidad_factual": 0.95,
        "diversidad_lexica": 0.65,
        "coherencia_dialogica": 0.90,
        "privacy_score": 0.0,
        "memorizacion": 0.005,
    }
    defaults.update(overrides)
    return QualityMetrics(**defaults)  # type: ignore[arg-type]


def make_tool_definition(**overrides: object) -> ToolDefinition:
    """Create a valid ToolDefinition with fictional automotive defaults."""
    defaults: dict[str, object] = {
        "name": "buscar_inventario",
        "description": "Buscar vehiculos en el inventario del concesionario ficticio",
        "input_schema": {
            "type": "object",
            "properties": {
                "marca": {"type": "string", "description": "Marca del vehiculo"},
                "modelo": {"type": "string", "description": "Modelo del vehiculo"},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "vehiculos": {"type": "array", "items": {"type": "object"}},
                "total_resultados": {"type": "integer"},
            },
        },
        "domains": ["automotive.sales"],
        "category": "automotive",
        "execution_mode": "simulated",
    }
    defaults.update(overrides)
    return ToolDefinition(**defaults)  # type: ignore[arg-type]


def make_tool_call(**overrides: object) -> ToolCall:
    """Create a valid ToolCall with fictional automotive defaults."""
    defaults: dict[str, object] = {
        "tool_name": "buscar_inventario",
        "arguments": {"marca": "Toyota", "modelo": "Corolla"},
    }
    defaults.update(overrides)
    return ToolCall(**defaults)  # type: ignore[arg-type]


def make_tool_result(**overrides: object) -> ToolResult:
    """Create a valid ToolResult with fictional automotive defaults."""
    defaults: dict[str, object] = {
        "tool_call_id": "test_call_001",
        "tool_name": "buscar_inventario",
        "result": {"vehiculos": [{"id": "v001", "marca": "Toyota", "modelo": "Corolla"}], "total_resultados": 1},
        "status": "success",
        "duration_ms": 150,
    }
    defaults.update(overrides)
    return ToolResult(**defaults)  # type: ignore[arg-type]


def make_conversation_with_tools(seed_id: str = "test_seed_001", **overrides: object) -> Conversation:
    """Create a valid Conversation with tool calls and results using fictional data."""
    defaults: dict[str, object] = {
        "seed_id": seed_id,
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco un Toyota Corolla."),
            ConversationTurn(
                turno=3,
                rol="vendedor",
                contenido="Permita buscar en nuestro inventario.",
                tool_calls=[
                    ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota", "modelo": "Corolla"})
                ],
            ),
            ConversationTurn(
                turno=4,
                rol="herramienta",
                contenido="Resultado de busqueda.",
                tool_results=[
                    ToolResult(
                        tool_call_id="test_001",
                        tool_name="buscar_inventario",
                        result={"vehiculos": [{"id": "v001"}], "total": 1},
                        status="success",
                        duration_ms=120,
                    )
                ],
            ),
            ConversationTurn(turno=5, rol="vendedor", contenido="Tenemos un Toyota Corolla disponible."),
        ],
        "es_sintetica": True,
    }
    defaults.update(overrides)
    return Conversation(**defaults)  # type: ignore[arg-type]
