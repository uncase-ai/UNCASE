"""Tests for JSONLConversationParser — JSONL parsing with format auto-detection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from uncase.core.parser.jsonl_parser import JSONLConversationParser
from uncase.exceptions import ImportFormatError, ImportParsingError

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


@pytest.fixture()
def parser() -> JSONLConversationParser:
    """Return a fresh JSONLConversationParser."""
    return JSONLConversationParser()


# -- OpenAI format ----------------------------------------------------------


async def test_parse_openai_format(parser: JSONLConversationParser) -> None:
    """Parse OpenAI-style JSONL and verify role mapping."""
    data = json.dumps({
        "messages": [
            {"role": "system", "content": "Eres un asesor de ventas."},
            {"role": "user", "content": "Busco un auto nuevo."},
            {"role": "assistant", "content": "Con gusto le ayudo."},
        ]
    })

    conversations = await parser.parse(data, format="openai")

    assert len(conversations) == 1
    conv = conversations[0]
    assert len(conv.turnos) == 3
    assert conv.turnos[0].rol == "sistema"
    assert conv.turnos[1].rol == "usuario"
    assert conv.turnos[2].rol == "asistente"
    assert conv.turnos[1].contenido == "Busco un auto nuevo."


# -- ShareGPT format -------------------------------------------------------


async def test_parse_sharegpt_format(parser: JSONLConversationParser) -> None:
    """Parse ShareGPT-style JSONL and verify role mapping."""
    data = json.dumps({
        "conversations": [
            {"from": "human", "value": "Busco un vehiculo familiar."},
            {"from": "gpt", "value": "Le recomiendo ver nuestras SUVs."},
        ]
    })

    conversations = await parser.parse(data, format="sharegpt")

    assert len(conversations) == 1
    conv = conversations[0]
    assert len(conv.turnos) == 2
    assert conv.turnos[0].rol == "usuario"
    assert conv.turnos[1].rol == "asistente"
    assert conv.turnos[0].contenido == "Busco un vehiculo familiar."


# -- Native UNCASE format --------------------------------------------------


async def test_parse_uncase_format(parser: JSONLConversationParser) -> None:
    """Parse native UNCASE JSONL."""
    record = {
        "conversation_id": "conv_native",
        "seed_id": "seed_001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            {"turno": 1, "rol": "vendedor", "contenido": "Buenos dias."},
            {"turno": 2, "rol": "cliente", "contenido": "Hola."},
        ],
    }
    data = json.dumps(record)

    conversations = await parser.parse(data, format="uncase")

    assert len(conversations) == 1
    conv = conversations[0]
    assert conv.conversation_id == "conv_native"
    assert conv.seed_id == "seed_001"
    assert conv.dominio == "automotive.sales"
    assert len(conv.turnos) == 2


# -- File-based parsing -----------------------------------------------------


async def test_parse_file_openai(parser: JSONLConversationParser) -> None:
    """Parse from the sample_openai.jsonl fixture file."""
    fixture_path = FIXTURES_DIR / "sample_openai.jsonl"
    if not fixture_path.exists():
        pytest.skip("Fixture file tests/fixtures/sample_openai.jsonl not found")

    conversations = await parser.parse_file(fixture_path, source_format="openai")

    assert len(conversations) == 2
    # First conversation has system + user + assistant = 3 turns.
    assert len(conversations[0].turnos) == 3
    # Second has user + assistant = 2 turns.
    assert len(conversations[1].turnos) == 2


async def test_parse_file_sharegpt(parser: JSONLConversationParser) -> None:
    """Parse from the sample_sharegpt.jsonl fixture file."""
    fixture_path = FIXTURES_DIR / "sample_sharegpt.jsonl"
    if not fixture_path.exists():
        pytest.skip("Fixture file tests/fixtures/sample_sharegpt.jsonl not found")

    conversations = await parser.parse_file(fixture_path, source_format="sharegpt")

    assert len(conversations) == 2
    # Each conversation has 2 turns (human + gpt).
    for conv in conversations:
        assert len(conv.turnos) == 2


# -- Auto-detection ---------------------------------------------------------


async def test_auto_detect_format_openai(parser: JSONLConversationParser) -> None:
    """Auto-detection recognises OpenAI format from 'messages' key."""
    data = json.dumps({"messages": [{"role": "user", "content": "Hola"}]})

    conversations = await parser.parse(data, format="auto")

    assert len(conversations) == 1
    assert conversations[0].turnos[0].rol == "usuario"


async def test_auto_detect_format_sharegpt(parser: JSONLConversationParser) -> None:
    """Auto-detection recognises ShareGPT format from 'conversations' key."""
    data = json.dumps({"conversations": [{"from": "human", "value": "Hola"}]})

    conversations = await parser.parse(data, format="auto")

    assert len(conversations) == 1
    assert conversations[0].turnos[0].rol == "usuario"


async def test_auto_detect_format_uncase(parser: JSONLConversationParser) -> None:
    """Auto-detection recognises UNCASE format from 'turnos' key."""
    record = {
        "conversation_id": "c1",
        "seed_id": "s1",
        "dominio": "general",
        "turnos": [{"turno": 1, "rol": "user", "contenido": "Hola"}],
    }
    data = json.dumps(record)

    conversations = await parser.parse(data, format="auto")

    assert len(conversations) == 1


async def test_auto_detect_unrecognised_raises(parser: JSONLConversationParser) -> None:
    """Auto-detection with unrecognised keys raises ImportFormatError."""
    data = json.dumps({"unknown_key": [1, 2, 3]})

    with pytest.raises(ImportFormatError, match="Cannot detect"):
        await parser.parse(data, format="auto")


# -- Error cases ------------------------------------------------------------


async def test_parse_invalid_json(parser: JSONLConversationParser) -> None:
    """Malformed JSON lines raise ImportParsingError."""
    data = '{"messages": [{"role": "user", "content": "ok"}]}\nNOT VALID JSON\n'

    with pytest.raises(ImportParsingError, match="invalid JSON"):
        await parser.parse(data, format="auto")


async def test_parse_empty_input(parser: JSONLConversationParser) -> None:
    """Empty input raises ImportParsingError."""
    with pytest.raises(ImportParsingError, match="empty"):
        await parser.parse("", format="auto")


async def test_parse_unsupported_format(parser: JSONLConversationParser) -> None:
    """Explicitly requesting an unsupported format raises ImportFormatError."""
    data = json.dumps({"messages": [{"role": "user", "content": "Hola"}]})

    with pytest.raises(ImportFormatError, match="Unsupported"):
        await parser.parse(data, format="xml")


async def test_parse_openai_with_tool_calls(parser: JSONLConversationParser) -> None:
    """OpenAI format with tool_calls is parsed correctly."""
    data = json.dumps({
        "messages": [
            {"role": "user", "content": "Busca un Toyota."},
            {
                "role": "assistant",
                "content": "Buscando...",
                "tool_calls": [
                    {
                        "id": "tc_001",
                        "function": {
                            "name": "buscar_inventario",
                            "arguments": '{"marca": "Toyota"}',
                        },
                    }
                ],
            },
        ]
    })

    conversations = await parser.parse(data, format="openai")

    assert len(conversations) == 1
    assistant_turn = conversations[0].turnos[1]
    assert assistant_turn.tool_calls is not None
    assert len(assistant_turn.tool_calls) == 1
    assert assistant_turn.tool_calls[0].tool_name == "buscar_inventario"
    assert assistant_turn.tool_calls[0].arguments == {"marca": "Toyota"}


async def test_parse_multiple_lines(parser: JSONLConversationParser) -> None:
    """Multiple JSONL lines produce multiple Conversation objects."""
    lines = [
        json.dumps({"messages": [{"role": "user", "content": "Linea 1"}]}),
        json.dumps({"messages": [{"role": "user", "content": "Linea 2"}]}),
        json.dumps({"messages": [{"role": "user", "content": "Linea 3"}]}),
    ]
    data = "\n".join(lines)

    conversations = await parser.parse(data, format="openai")

    assert len(conversations) == 3
