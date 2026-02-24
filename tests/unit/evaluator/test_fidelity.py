"""Tests for factual fidelity metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_conversation_with_tools, make_seed
from uncase.core.evaluator.metrics.fidelity import FactualFidelityMetric
from uncase.schemas.conversation import ConversationTurn
from uncase.schemas.seed import ParametrosFactuales, PasosTurnos


class TestFactualFidelityMetric:
    """Tests for the factual fidelity metric."""

    def test_name(self) -> None:
        metric = FactualFidelityMetric()
        assert metric.name == "fidelidad_factual"

    def test_perfect_role_compliance(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente"])
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola"),
            ],
        )
        metric = FactualFidelityMetric()
        score = metric._role_compliance(conversation, seed)
        assert score == 1.0

    def test_role_compliance_with_unknown_role(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente"])
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="gerente", contenido="Hola"),  # not in seed
            ],
        )
        metric = FactualFidelityMetric()
        score = metric._role_compliance(conversation, seed)
        assert score == 0.5  # 1 of 2 roles valid

    def test_turn_compliance_in_range(self) -> None:
        seed = make_seed(
            pasos_turnos=PasosTurnos(turnos_min=2, turnos_max=10, flujo_esperado=["saludo"]),
        )
        conversation = make_conversation(seed_id=seed.seed_id)  # 3 turns
        metric = FactualFidelityMetric()
        score = metric._turn_compliance(conversation, seed)
        assert score == 1.0

    def test_turn_compliance_out_of_range(self) -> None:
        seed = make_seed(
            pasos_turnos=PasosTurnos(turnos_min=10, turnos_max=20, flujo_esperado=["saludo"]),
        )
        conversation = make_conversation(seed_id=seed.seed_id)  # 3 turns (too few)
        metric = FactualFidelityMetric()
        score = metric._turn_compliance(conversation, seed)
        assert score < 1.0

    def test_flow_adherence_with_matching_steps(self) -> None:
        seed = make_seed(
            pasos_turnos=PasosTurnos(
                turnos_min=2,
                turnos_max=10,
                flujo_esperado=["saludo", "consulta", "resolucion"],
            ),
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, saludo cordial"),
                ConversationTurn(turno=2, rol="cliente", contenido="Tengo una consulta importante"),
                ConversationTurn(turno=3, rol="vendedor", contenido="La resolucion es la siguiente"),
            ],
        )
        metric = FactualFidelityMetric()
        score = metric._flow_adherence(conversation, seed)
        assert score == 1.0

    def test_tool_compliance_when_tools_used(self) -> None:
        seed = make_seed()  # has herramientas=["crm"]
        conversation = make_conversation_with_tools(seed_id=seed.seed_id)
        metric = FactualFidelityMetric()
        # The factory creates buscar_inventario calls, not crm
        score = metric._tool_compliance(conversation, seed)
        assert 0.0 <= score <= 1.0

    def test_tool_compliance_when_no_tools_expected(self) -> None:
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Test context",
                restricciones=[],
                herramientas=[],
                metadata={},
            ),
        )
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = FactualFidelityMetric()
        score = metric._tool_compliance(conversation, seed)
        assert score == 1.0  # No tools expected, none used

    def test_compute_returns_bounded_score(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = FactualFidelityMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0

    def test_context_presence_with_matching_keywords(self) -> None:
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="concesionario vehiculos electricos",
                restricciones=["financiamiento disponible"],
                herramientas=[],
                metadata={},
            ),
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Bienvenido al concesionario de vehiculos electricos",
                ),
                ConversationTurn(
                    turno=2,
                    rol="cliente",
                    contenido="Hay financiamiento disponible para vehiculos?",
                ),
            ],
        )
        metric = FactualFidelityMetric()
        score = metric._context_presence(conversation, seed)
        assert score > 0.5
