"""Tests for the ToolCallValidatorMetric."""

from __future__ import annotations

import pytest

from tests.factories import make_conversation, make_seed, make_tool_definition
from uncase.core.evaluator.metrics.tool_call import ToolCallValidatorMetric
from uncase.schemas.conversation import ConversationTurn
from uncase.schemas.seed import ParametrosFactuales
from uncase.tools.schemas import ToolCall, ToolResult


@pytest.fixture()
def metric() -> ToolCallValidatorMetric:
    return ToolCallValidatorMetric()


@pytest.fixture()
def seed_with_tools():
    """Seed with fully defined tool schemas."""
    return make_seed(
        parametros_factuales=ParametrosFactuales(
            contexto="Concesionario ficticio de prueba",
            restricciones=["Restriccion de prueba"],
            herramientas=["buscar_inventario", "calcular_precio"],
            herramientas_definidas=[
                make_tool_definition(
                    name="buscar_inventario",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "marca": {"type": "string"},
                            "modelo": {"type": "string"},
                            "precio_maximo": {"type": "number"},
                        },
                        "required": ["marca"],
                    },
                ),
                make_tool_definition(
                    name="calcular_precio",
                    description="Calcular precio de financiamiento ficticio",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "precio_vehiculo": {"type": "number"},
                            "enganche_porcentaje": {"type": "number"},
                            "plazo_meses": {"type": "integer"},
                        },
                        "required": ["precio_vehiculo"],
                    },
                ),
            ],
            metadata={},
        ),
    )


class TestToolCallValidatorMetric:
    """Tests for the ToolCallValidatorMetric class."""

    def test_name_and_display_name(self, metric: ToolCallValidatorMetric) -> None:
        assert metric.name == "tool_call_validity"
        assert metric.display_name == "Tool Call Validity"

    def test_no_tools_in_seed_no_tools_in_conv(self, metric: ToolCallValidatorMetric) -> None:
        """When seed has no tools and conversation uses none, score = 1.0."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Test",
                restricciones=[],
                herramientas=[],
                metadata={},
            ),
        )
        conversation = make_conversation(seed_id=seed.seed_id)

        score = metric.compute(conversation, seed)

        assert score == 1.0

    def test_no_tools_in_seed_but_tools_used(self, metric: ToolCallValidatorMetric) -> None:
        """When seed defines no tools but conversation uses them, mild penalty."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Test",
                restricciones=[],
                herramientas=[],
                metadata={},
            ),
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1, rol="vendedor", contenido="Buscando...", herramientas_usadas=["phantom_tool"]
                ),
                ConversationTurn(turno=2, rol="cliente", contenido="Gracias."),
            ],
        )

        score = metric.compute(conversation, seed)

        assert score == 0.8

    def test_all_tool_names_valid(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """All herramientas_usadas match seed tools = full score for name checks."""
        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1, rol="vendedor", contenido="Buscando...", herramientas_usadas=["buscar_inventario"]
                ),
                ConversationTurn(turno=2, rol="cliente", contenido="Gracias."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score == 1.0

    def test_invalid_tool_name_penalized(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Unknown tool name in herramientas_usadas reduces score."""
        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="vendedor",
                    contenido="Buscando...",
                    herramientas_usadas=["buscar_inventario"],
                ),
                ConversationTurn(
                    turno=2,
                    rol="vendedor",
                    contenido="Calculando...",
                    herramientas_usadas=["herramienta_fantasma"],
                ),
                ConversationTurn(turno=3, rol="cliente", contenido="OK."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        # 1 valid name + 1 invalid name = 1/2 = 0.5
        assert score == 0.5

    def test_structured_tool_call_valid(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Valid structured tool_call with correct args passes all checks."""
        tc = ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota", "modelo": "Corolla"})
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="buscar_inventario", result={"vehiculos": []})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="No encontre resultados."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score == 1.0

    def test_structured_tool_call_unknown_name(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Structured tool_call with unknown name fails name check."""
        tc = ToolCall(tool_name="herramienta_fantasma", arguments={"x": 1})
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="herramienta_fantasma", result={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        # Name check fails (0/1), sequence check passes (1/1) = 1/2
        assert score == 0.5

    def test_missing_required_arg(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Missing required argument 'marca' reduces score."""
        tc = ToolCall(tool_name="buscar_inventario", arguments={"modelo": "Corolla"})
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="buscar_inventario", result={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score < 1.0

    def test_unknown_argument_penalized(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Argument not in input_schema.properties reduces score."""
        tc = ToolCall(
            tool_name="buscar_inventario",
            arguments={"marca": "Toyota", "campo_inexistente": "valor"},
        )
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="buscar_inventario", result={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score < 1.0

    def test_wrong_type_penalized(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """String value for a 'number' field reduces score."""
        tc = ToolCall(
            tool_name="buscar_inventario",
            arguments={"marca": "Toyota", "precio_maximo": "$300,000"},  # Should be number
        )
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="buscar_inventario", result={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score < 1.0

    def test_boolean_not_treated_as_integer(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Boolean value should not pass as integer type."""
        tc = ToolCall(
            tool_name="calcular_precio",
            arguments={"precio_vehiculo": 300000, "plazo_meses": True},  # bool, not int
        )
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="calcular_precio", result={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Calculando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score < 1.0

    def test_missing_tool_result_penalized(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Tool call without a matching tool result in subsequent turns."""
        tc = ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota"})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                # No tool_result turn follows
                ConversationTurn(turno=2, rol="vendedor", contenido="Tenemos opciones."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score < 1.0

    def test_tool_result_with_matching_id(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Tool result in non-adjacent turn still counts as valid sequence."""
        tc = ToolCall(tool_name="buscar_inventario", arguments={"marca": "Honda"})
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="buscar_inventario", result={"vehiculos": []})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="cliente", contenido="Espero."),
                ConversationTurn(turno=3, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=4, rol="vendedor", contenido="Encontre opciones."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert score == 1.0

    def test_enum_validation(self, metric: ToolCallValidatorMetric) -> None:
        """Enum constraint violation reduces score."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Test",
                restricciones=[],
                herramientas=["obtener_info"],
                herramientas_definidas=[
                    make_tool_definition(
                        name="obtener_info",
                        description="Obtener informacion de negocio ficticio",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "tema": {
                                    "type": "string",
                                    "enum": ["horarios", "ubicaciones", "garantias"],
                                },
                            },
                            "required": ["tema"],
                        },
                    ),
                ],
                metadata={},
            ),
        )

        tc = ToolCall(tool_name="obtener_info", arguments={"tema": "tema_inventado"})
        tr = ToolResult(tool_call_id=tc.tool_call_id, tool_name="obtener_info", result={})

        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Consultando...", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed)

        assert score < 1.0

    def test_multiple_tool_calls_mixed_validity(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Mix of valid and invalid tool calls produces proportional score."""
        tc_valid = ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota"})
        tr_valid = ToolResult(tool_call_id=tc_valid.tool_call_id, tool_name="buscar_inventario", result={})
        tc_invalid = ToolCall(tool_name="herramienta_fantasma", arguments={})

        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buscando...", tool_calls=[tc_valid]),
                ConversationTurn(turno=2, rol="herramienta", contenido="Resultado", tool_results=[tr_valid]),
                ConversationTurn(turno=3, rol="vendedor", contenido="Ahora otro...", tool_calls=[tc_invalid]),
                ConversationTurn(turno=4, rol="vendedor", contenido="Listo."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert 0.0 < score < 1.0

    def test_tools_from_herramientas_list_only(self, metric: ToolCallValidatorMetric) -> None:
        """Tools listed in herramientas (no definitions) still validate names."""
        seed = make_seed(
            parametros_factuales=ParametrosFactuales(
                contexto="Test",
                restricciones=[],
                herramientas=["crm", "buscar_inventario"],
                metadata={},
            ),
        )

        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Usando CRM.", herramientas_usadas=["crm"]),
                ConversationTurn(turno=2, rol="cliente", contenido="OK."),
            ],
        )

        score = metric.compute(conversation, seed)

        assert score == 1.0

    def test_score_is_between_0_and_1(self, metric: ToolCallValidatorMetric, seed_with_tools) -> None:
        """Score always in [0.0, 1.0] regardless of input."""
        tc = ToolCall(tool_name="fake", arguments={"bad": True})
        conversation = make_conversation(
            seed_id=seed_with_tools.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Test.", tool_calls=[tc]),
                ConversationTurn(turno=2, rol="cliente", contenido="OK."),
            ],
        )

        score = metric.compute(conversation, seed_with_tools)

        assert 0.0 <= score <= 1.0
