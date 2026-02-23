"""Tests for CSVConversationParser — CSV parsing and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from uncase.core.parser.csv_parser import CSVConversationParser
from uncase.exceptions import ImportParsingError

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


@pytest.fixture()
def parser() -> CSVConversationParser:
    """Return a fresh CSVConversationParser."""
    return CSVConversationParser()


async def test_parse_valid_csv(parser: CSVConversationParser) -> None:
    """Parse a valid CSV string and verify conversations and turns."""
    csv_data = (
        "conversation_id,turn_number,role,content,seed_id,domain\n"
        "conv_001,1,vendedor,Buenos dias,seed_001,automotive.sales\n"
        "conv_001,2,cliente,Busco un auto,seed_001,automotive.sales\n"
        "conv_001,3,vendedor,Con gusto le ayudo,seed_001,automotive.sales\n"
    )

    conversations = await parser.parse(csv_data)

    assert len(conversations) == 1
    conv = conversations[0]
    assert conv.conversation_id == "conv_001"
    assert conv.seed_id == "seed_001"
    assert conv.dominio == "automotive.sales"
    assert len(conv.turnos) == 3
    assert conv.turnos[0].rol == "vendedor"
    assert conv.turnos[0].contenido == "Buenos dias"
    assert conv.turnos[1].rol == "cliente"
    assert conv.turnos[2].turno == 3


async def test_parse_file(parser: CSVConversationParser) -> None:
    """Parse from the sample.csv fixture file."""
    fixture_path = FIXTURES_DIR / "sample.csv"
    if not fixture_path.exists():
        pytest.skip("Fixture file tests/fixtures/sample.csv not found")

    conversations = await parser.parse_file(fixture_path)

    assert len(conversations) >= 1
    # The fixture has conv_001 (3 turns) and conv_002 (2 turns).
    ids = {c.conversation_id for c in conversations}
    assert "conv_001" in ids
    assert "conv_002" in ids


async def test_parse_missing_columns(parser: CSVConversationParser) -> None:
    """CSV missing required columns raises ImportParsingError."""
    csv_data = "id,text\n1,hello\n"

    with pytest.raises(ImportParsingError, match="missing required columns"):
        await parser.parse(csv_data)


async def test_parse_groups_by_conversation_id(parser: CSVConversationParser) -> None:
    """Multiple conversation IDs produce multiple Conversation objects."""
    csv_data = (
        "conversation_id,turn_number,role,content\n"
        "conv_a,1,vendedor,Hola\n"
        "conv_a,2,cliente,Hola\n"
        "conv_b,1,vendedor,Bienvenido\n"
        "conv_b,2,cliente,Gracias\n"
        "conv_c,1,vendedor,Buenos dias\n"
    )

    conversations = await parser.parse(csv_data)

    assert len(conversations) == 3
    ids = {c.conversation_id for c in conversations}
    assert ids == {"conv_a", "conv_b", "conv_c"}

    # Verify turn counts per conversation.
    turn_counts = {c.conversation_id: len(c.turnos) for c in conversations}
    assert turn_counts["conv_a"] == 2
    assert turn_counts["conv_b"] == 2
    assert turn_counts["conv_c"] == 1


async def test_parse_empty_csv(parser: CSVConversationParser) -> None:
    """An empty CSV with only headers produces no conversations."""
    csv_data = "conversation_id,turn_number,role,content\n"

    conversations = await parser.parse(csv_data)
    assert conversations == []


async def test_parse_no_header(parser: CSVConversationParser) -> None:
    """A completely empty CSV raises ImportParsingError."""
    with pytest.raises(ImportParsingError, match="empty|no header"):
        await parser.parse("")


async def test_parse_csv_with_tool_calls(parser: CSVConversationParser) -> None:
    """CSV with tool_calls JSON column is parsed correctly."""
    csv_data = (
        "conversation_id,turn_number,role,content,tool_calls\n"
        'conv_t,1,vendedor,Voy a buscar,"[{""tool_name"": ""buscar_inventario"", ""arguments"": {""marca"": ""Toyota""}}]"\n'
        "conv_t,2,cliente,Gracias,\n"
    )

    conversations = await parser.parse(csv_data)

    assert len(conversations) == 1
    turn1 = conversations[0].turnos[0]
    assert turn1.tool_calls is not None
    assert len(turn1.tool_calls) == 1
    assert turn1.tool_calls[0].tool_name == "buscar_inventario"
