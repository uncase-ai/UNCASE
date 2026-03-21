"""Tests for memorization (extraction attack) metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_seed
from uncase.core.evaluator.metrics.memorization import (
    MIN_LCS_LENGTH,
    MemorizationMetric,
    _longest_common_substring_length,
    compute_memorization_score,
)
from uncase.schemas.conversation import ConversationTurn
from uncase.schemas.seed import ParametrosFactuales, PasosTurnos
from uncase.tools.schemas import ToolCall


class TestLongestCommonSubstring:
    """Unit tests for the LCS helper."""

    def test_identical_strings(self) -> None:
        assert _longest_common_substring_length("abcdef", "abcdef") == 6

    def test_no_overlap(self) -> None:
        assert _longest_common_substring_length("abc", "xyz") == 0

    def test_partial_overlap(self) -> None:
        assert _longest_common_substring_length("abcdef", "cde") == 3

    def test_empty_string(self) -> None:
        assert _longest_common_substring_length("", "abc") == 0
        assert _longest_common_substring_length("abc", "") == 0
        assert _longest_common_substring_length("", "") == 0

    def test_single_char_match(self) -> None:
        assert _longest_common_substring_length("a", "a") == 1

    def test_single_char_no_match(self) -> None:
        assert _longest_common_substring_length("a", "b") == 0

    def test_substring_at_end(self) -> None:
        assert _longest_common_substring_length("hello world", "world") == 5


class TestComputeMemorizationScore:
    """Tests for the score computation function."""

    def test_completely_different_content_scores_near_zero(self) -> None:
        """Conversation with original content should score near 0.0."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo",
                restricciones=[
                    "Solo se venden vehiculos nuevos y certificados",
                    "Financiamiento disponible hasta 72 meses",
                    "Garantia extendida de 5 anos obligatoria en vehiculos premium",
                ],
                herramientas=["crm"],
                metadata={"ubicacion": "zona norte metropolitana"},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=[
                    "saludo inicial",
                    "identificacion de necesidades",
                    "presentacion de opciones",
                    "negociacion de precio",
                    "cierre de venta",
                ],
            ),
            objetivo="Asesorar al cliente en la compra de un vehiculo de lujo adecuado a sus necesidades",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Bienvenido a nuestro establecimiento, es un placer atenderle hoy",
                ),
                ConversationTurn(
                    turno=2,
                    rol="cliente",
                    contenido="Gracias, estoy buscando algo comodo para viajes largos por carretera",
                ),
                ConversationTurn(
                    turno=3,
                    rol="vendedor",
                    contenido="Tenemos excelentes alternativas para ese tipo de recorridos",
                ),
            ],
        )
        score = compute_memorization_score(conversation, seed)
        assert score < 0.01, f"Expected < 0.01 but got {score}"

    def test_verbatim_copy_scores_high(self) -> None:
        """Conversation that copies seed text verbatim should score > 0.01."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados",
                restricciones=[
                    "Solo se venden vehiculos nuevos y certificados de fabrica",
                    "Financiamiento disponible hasta 72 meses con tasa preferencial",
                ],
                herramientas=["crm"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente en la compra de un vehiculo",
        )
        # The conversation turn copies the seed contexto verbatim
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados",
                ),
                ConversationTurn(
                    turno=2,
                    rol="cliente",
                    contenido="Entiendo, gracias por la informacion",
                ),
            ],
        )
        score = compute_memorization_score(conversation, seed)
        assert score > 0.01, f"Expected > 0.01 but got {score}"

    def test_partial_copy_scores_proportionally(self) -> None:
        """Partial overlap produces a score proportional to the copied fraction."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados de alta gama",
                restricciones=["Solo vehiculos nuevos certificados"],
                herramientas=["crm"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente",
        )
        # Turn contains a long chunk of seed text (>50 chars) mixed with original content.
        # "concesionario premium motors ubicado en zona norte de la ciudad especializado" = 77 chars
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido=(
                        "Somos un concesionario premium motors ubicado en zona norte de la ciudad especializado "
                        "y ofrecemos excelentes planes de financiamiento y garantia para todos nuestros clientes"
                    ),
                ),
            ],
        )
        score = compute_memorization_score(conversation, seed)
        # Should be between 0 and 1 — partial overlap
        assert 0.0 < score < 1.0, f"Expected partial score but got {score}"

    def test_short_common_substring_ignored(self) -> None:
        """Common substrings shorter than MIN_LCS_LENGTH are treated as incidental."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte",
                restricciones=["Solo vehiculos nuevos"],
                herramientas=["crm"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente",
        )
        # The common substring "vehiculos" (9 chars) is below MIN_LCS_LENGTH
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Tenemos vehiculos disponibles para su revision inmediata",
                ),
            ],
        )
        score = compute_memorization_score(conversation, seed)
        assert score == 0.0, f"Short overlap should be ignored, got {score}"
        assert MIN_LCS_LENGTH == 50, "MIN_LCS_LENGTH should be 50 characters"

    def test_empty_seed_text_returns_zero(self) -> None:
        """If the seed has no text content, score should be 0.0."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="",
                restricciones=[],
                herramientas=[],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=2,
                turnos_max=5,
                flujo_esperado=[""],
            ),
            objetivo="",
        )
        conversation = make_conversation(seed_id=seed.seed_id)
        score = compute_memorization_score(conversation, seed)
        assert score == 0.0

    def test_tool_call_arguments_checked(self) -> None:
        """Tool call arguments that copy seed data should be detected."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados",
                restricciones=["Solo se venden vehiculos nuevos y certificados de fabrica"],
                herramientas=["buscar_inventario"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscare en el inventario."),
                ConversationTurn(
                    turno=2,
                    rol="vendedor",
                    contenido="Ejecutando herramienta.",
                    tool_calls=[
                        ToolCall(
                            tool_name="buscar_inventario",
                            arguments={
                                "query": "concesionario premium motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados"
                            },
                        )
                    ],
                ),
            ],
        )
        score = compute_memorization_score(conversation, seed)
        assert score > 0.01, f"Expected > 0.01 for tool-call memorization but got {score}"


class TestMemorizationMetric:
    """Tests for the MemorizationMetric class (BaseMetric interface)."""

    def test_name(self) -> None:
        metric = MemorizationMetric()
        assert metric.name == "memorizacion"

    def test_display_name(self) -> None:
        metric = MemorizationMetric()
        assert "Memorization" in metric.display_name

    def test_clean_conversation_passes_threshold(self) -> None:
        """A conversation with original content should pass the < 0.01 threshold."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados de alta gama",
                restricciones=[
                    "Solo se venden vehiculos nuevos y certificados de fabrica",
                    "Financiamiento disponible hasta 72 meses",
                ],
                herramientas=["crm"],
                metadata={"ubicacion": "zona norte"},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=[
                    "saludo inicial y bienvenida",
                    "identificacion de necesidades del cliente",
                    "presentacion detallada de opciones",
                    "negociacion y cierre",
                ],
            ),
            objetivo="Asesorar al cliente en la compra de un vehiculo de lujo adecuado a sus necesidades y presupuesto",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Bienvenido, es un placer atenderle en nuestro local el dia de hoy",
                ),
                ConversationTurn(
                    turno=2,
                    rol="cliente",
                    contenido="Estoy interesado en conocer las opciones de sedanes ejecutivos disponibles actualmente",
                ),
                ConversationTurn(
                    turno=3,
                    rol="vendedor",
                    contenido="Por supuesto, permita mostrarle nuestro catalogo actualizado con las mejores alternativas",
                ),
            ],
        )
        metric = MemorizationMetric()
        score = metric.compute(conversation, seed)
        assert score < 0.01, f"Expected < 0.01 for clean conversation but got {score}"

    def test_verbatim_copy_fails_threshold(self) -> None:
        """A conversation that copies seed text verbatim should fail the < 0.01 threshold."""
        seed_context = "Concesionario Premium Motors ubicado en zona norte de la ciudad especializado en vehiculos de lujo importados de alta gama"
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto=seed_context,
                restricciones=["Solo vehiculos nuevos certificados"],
                herramientas=["crm"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido=seed_context),
            ],
        )
        metric = MemorizationMetric()
        score = metric.compute(conversation, seed)
        assert score >= 0.01, f"Expected >= 0.01 for verbatim copy but got {score}"

    def test_score_bounded_zero_one(self) -> None:
        """Score is always in [0.0, 1.0]."""
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = MemorizationMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0

    def test_threshold_boundary(self) -> None:
        """Score exactly at 0.01 should fail (threshold is strict '<')."""
        # We can't produce exact 0.01 deterministically, but we can verify
        # that a score above the threshold is correctly identified as failing.
        # The quality gate checks: memorizacion < 0.01
        from uncase.schemas.quality import compute_composite_score, QualityMetrics

        # Score at exactly 0.01 — should fail
        metrics_at_boundary = QualityMetrics(
            rouge_l=0.80,
            fidelidad_factual=0.90,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.80,
            tool_call_validity=1.0,
            privacy_score=0.0,
            memorizacion=0.01,
        )
        _, _, passed_at, failures_at = compute_composite_score(metrics_at_boundary)
        assert not passed_at, "memorizacion=0.01 should fail (threshold is < 0.01)"
        assert any("memorizacion" in f for f in failures_at)

        # Score just below 0.01 — should pass (assuming other metrics pass)
        metrics_below = QualityMetrics(
            rouge_l=0.80,
            fidelidad_factual=0.90,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.80,
            tool_call_validity=1.0,
            privacy_score=0.0,
            memorizacion=0.009,
        )
        _, _, passed_below, failures_below = compute_composite_score(metrics_below)
        assert not any("memorizacion" in f for f in failures_below), (
            "memorizacion=0.009 should not be in failures"
        )

    def test_restricciones_memorization_detected(self) -> None:
        """Copying restricciones text verbatim should be detected."""
        restriccion = "Solo se venden vehiculos nuevos y certificados de fabrica con garantia extendida obligatoria"
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario de prueba",
                restricciones=[restriccion],
                herramientas=["crm"],
                metadata={},
            ),
            pasos_turnos=PasosTurnos(
                turnos_min=6,
                turnos_max=20,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
            objetivo="Asesorar al cliente",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido=restriccion),
            ],
        )
        metric = MemorizationMetric()
        score = metric.compute(conversation, seed)
        assert score > 0.01, f"Expected > 0.01 for restricciones copy but got {score}"
