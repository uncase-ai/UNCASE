"""End-to-end pipeline test — seed → generate → evaluate.

Requires a real LLM API key. Gated behind the 'e2e' marker and the
UNCASE_E2E_MODEL env var (defaults to claude-sonnet-4-20250514).

Run:
    LITELLM_API_KEY=sk-... uv run pytest tests/integration/test_e2e_pipeline.py -m e2e -v
"""

from __future__ import annotations

import os

import pytest

from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.core.generator.litellm_generator import GenerationConfig, LiteLLMGenerator
from uncase.schemas.seed import (
    ParametrosFactuales,
    PasosTurnos,
    SeedSchema,
)

_HAS_API_KEY = bool(os.environ.get("LITELLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))
_E2E_MODEL = os.environ.get("UNCASE_E2E_MODEL", "claude-sonnet-4-20250514")

_skip_reason = "E2E test requires LITELLM_API_KEY or ANTHROPIC_API_KEY in environment"


def _test_seed() -> SeedSchema:
    """Minimal automotive seed for the E2E test."""
    return SeedSchema(
        seed_id="e2e-test-seed-001",
        dominio="automotive.sales",
        idioma="es",
        etiquetas=["e2e", "test"],
        roles=["vendedor", "cliente"],
        descripcion_roles={
            "vendedor": "Asesor de ventas de vehiculos nuevos",
            "cliente": "Cliente interesado en un SUV familiar",
        },
        objetivo="Cliente consulta opciones de SUV con buen espacio y seguridad para familia",
        tono="profesional",
        pasos_turnos=PasosTurnos(
            turnos_min=4,
            turnos_max=8,
            flujo_esperado=[
                "saludo",
                "identificacion_necesidades",
                "presentacion_opciones",
                "resolucion",
            ],
        ),
        parametros_factuales=ParametrosFactuales(
            contexto="Concesionario multi-marca en Ciudad de Mexico",
            restricciones=[
                "Solo vehiculos nuevos del ano en curso",
                "Presupuesto del cliente: 500,000-800,000 MXN",
                "Debe incluir garantia extendida",
            ],
            herramientas=[],
            metadata={"region": "CDMX", "segmento": "SUV"},
        ),
    )


@pytest.mark.e2e
@pytest.mark.skipif(not _HAS_API_KEY, reason=_skip_reason)
async def test_seed_generate_evaluate_roundtrip() -> None:
    """Full roundtrip: create seed → generate conversation → evaluate quality.

    Verifies that the pipeline produces a conversation that passes the
    core quality thresholds (ROUGE-L, fidelity, diversity, coherence).
    """
    seed = _test_seed()

    # --- Layer 3: Generate ---
    config = GenerationConfig(model=_E2E_MODEL, temperature=0.7, max_tokens=4096)
    generator = LiteLLMGenerator(config=config)
    conversations = await generator.generate(seed, count=1)

    assert len(conversations) == 1
    conv = conversations[0]

    # Basic structural checks
    assert conv.seed_id == seed.seed_id
    assert conv.dominio == "automotive.sales"
    assert conv.es_sintetica is True
    assert conv.num_turnos >= 4
    assert len(conv.roles_presentes) >= 2

    # --- Layer 2: Evaluate ---
    evaluator = ConversationEvaluator()
    report = await evaluator.evaluate(conv, seed)

    # The generated conversation should meet core thresholds
    assert report.metrics.rouge_l >= 0.40, f"ROUGE-L too low: {report.metrics.rouge_l}"
    assert report.metrics.fidelidad_factual >= 0.70, f"Fidelity too low: {report.metrics.fidelidad_factual}"
    assert report.metrics.diversidad_lexica >= 0.40, f"Diversity too low: {report.metrics.diversidad_lexica}"
    assert report.metrics.coherencia_dialogica >= 0.60, f"Coherence too low: {report.metrics.coherencia_dialogica}"
    assert report.metrics.privacy_score == 0.0, f"PII detected: {report.metrics.privacy_score}"
    assert report.composite_score > 0.0, f"Composite score is zero (gate failed): {report.failures}"
