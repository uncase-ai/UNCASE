"""Shared fixtures for template unit tests."""

from __future__ import annotations

import pytest

from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult


@pytest.fixture()
def basic_conversation() -> Conversation:
    """A simple 3-turn conversation with fictional data."""
    return Conversation(
        seed_id="seed_fixture_001",
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco informacion sobre vehiculos electricos."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto, tenemos varios modelos disponibles."),
        ],
        es_sintetica=True,
    )


@pytest.fixture()
def conversation_with_tools() -> Conversation:
    """A conversation that includes tool_calls and tool_results (all fictional)."""
    tc = ToolCall(
        tool_call_id="tc_fictional_001",
        tool_name="search_inventory",
        arguments={"category": "sedan", "year": 2025},
    )
    tr = ToolResult(
        tool_call_id="tc_fictional_001",
        tool_name="search_inventory",
        result={"count": 3, "models": ["ModeloX", "ModeloY", "ModeloZ"]},
        status="success",
    )
    return Conversation(
        seed_id="seed_fixture_002",
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="cliente", contenido="Tienen sedanes disponibles?"),
            ConversationTurn(
                turno=2,
                rol="vendedor",
                contenido="Dejeme revisar el inventario.",
                tool_calls=[tc],
            ),
            ConversationTurn(
                turno=3,
                rol="herramienta",
                contenido="Resultado de busqueda.",
                tool_results=[tr],
            ),
            ConversationTurn(turno=4, rol="vendedor", contenido="Tenemos 3 modelos de sedan disponibles."),
        ],
        es_sintetica=True,
    )


@pytest.fixture()
def sample_tool_definitions() -> list[ToolDefinition]:
    """Fictional tool definitions for testing."""
    return [
        ToolDefinition(
            name="search_inventory",
            description="Search the vehicle inventory by category and year",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Vehicle category"},
                    "year": {"type": "integer", "description": "Model year"},
                },
                "required": ["category"],
            },
        ),
    ]


@pytest.fixture()
def batch_conversations(basic_conversation: Conversation) -> list[Conversation]:
    """Three identical conversations for batch rendering tests."""
    return [basic_conversation, basic_conversation, basic_conversation]
