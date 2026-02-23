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
