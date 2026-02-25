"""Tests for Layer 0 raw conversation parsers — WhatsApp, Transcript, JSON, and format detection."""

from __future__ import annotations

import json

from uncase.core.seed_engine.parsers import (
    JSONConversationParser,
    TranscriptParser,
    WhatsAppParser,
    detect_format,
)

# ---------------------------------------------------------------------------
# Synthetic conversation data — ZERO real PII
# ---------------------------------------------------------------------------

WHATSAPP_MULTI_TURN = """\
[25/02/2026, 10:30:00] Vendedor: Buenos dias, bienvenido al concesionario
[25/02/2026, 10:30:15] Cliente: Hola, busco informacion sobre vehiculos nuevos
[25/02/2026, 10:31:00] Vendedor: Con gusto, que tipo de vehiculo le interesa?
[25/02/2026, 10:32:00] Cliente: Me interesa un sedan familiar
[25/02/2026, 10:33:00] Vendedor: Tenemos excelentes opciones, le muestro nuestro inventario
[25/02/2026, 10:34:00] Cliente: Perfecto, tambien quiero saber sobre financiamiento
"""

WHATSAPP_CONTINUATION = """\
[25/02/2026, 10:30:00] Vendedor: Buenos dias, le comento que tenemos
una promocion especial este mes
[25/02/2026, 10:31:00] Cliente: Que incluye la promocion?
"""

TRANSCRIPT_SIMPLE = """\
Vendedor: Buenos dias, en que puedo ayudarle?
Cliente: Hola, busco un auto nuevo para mi familia
Vendedor: Con gusto, que presupuesto tiene en mente?
Cliente: Alrededor de 400,000 pesos
Vendedor: Tenemos varias opciones en ese rango
"""

TRANSCRIPT_NUMBERED = """\
1. Vendedor: Buenos dias, bienvenido
2. Cliente: Hola, busco un sedan
3. Vendedor: Tenemos varias opciones
4. Cliente: Me puede dar los precios?
"""

TRANSCRIPT_CONTINUATION = """\
Vendedor: Buenos dias, le comento que tenemos varias opciones
disponibles para usted
Cliente: Que modelos tienen?
"""

OPENAI_MESSAGES = json.dumps(
    {
        "messages": [
            {"role": "system", "content": "Eres un asesor de ventas automotrices."},
            {"role": "user", "content": "Busco un auto nuevo."},
            {"role": "assistant", "content": "Con gusto le ayudo. Que presupuesto tiene?"},
        ]
    }
)

UNCASE_TURNOS = json.dumps(
    {
        "turnos": [
            {"rol": "vendedor", "contenido": "Buenos dias, bienvenido."},
            {"rol": "cliente", "contenido": "Hola, busco un vehiculo."},
        ]
    }
)

FLAT_ARRAY = json.dumps(
    [
        {"role": "vendedor", "content": "Buenos dias."},
        {"role": "cliente", "content": "Hola, busco un auto."},
        {"role": "vendedor", "content": "Con gusto."},
    ]
)

JSONL_MULTI = (
    '{"messages": [{"role": "user", "content": "Quiero cotizar un sedan."},'
    ' {"role": "assistant", "content": "Con gusto."}]}\n'
    '{"messages": [{"role": "user", "content": "Tiene disponible?"},'
    ' {"role": "assistant", "content": "Si, tenemos inventario."}]}\n'
)


# ===================================================================
# WhatsAppParser
# ===================================================================


class TestWhatsAppParser:
    """Tests for WhatsAppParser."""

    async def test_valid_multi_turn(self) -> None:
        """Parse a valid multi-turn WhatsApp conversation."""
        turns = WhatsAppParser.parse(WHATSAPP_MULTI_TURN)

        assert len(turns) == 6
        assert turns[0].role == "Vendedor"
        assert turns[0].content == "Buenos dias, bienvenido al concesionario"
        assert turns[0].timestamp == "25/02/2026 10:30:00"
        assert turns[0].turn_number == 1
        assert turns[1].role == "Cliente"
        assert turns[5].turn_number == 6

    async def test_continuation_lines(self) -> None:
        """Lines without a WhatsApp prefix are appended to the previous turn."""
        turns = WhatsAppParser.parse(WHATSAPP_CONTINUATION)

        assert len(turns) == 2
        assert "promocion especial este mes" in turns[0].content
        assert "Buenos dias" in turns[0].content

    async def test_empty_input(self) -> None:
        """Empty input returns no turns."""
        turns = WhatsAppParser.parse("")
        assert turns == []

    async def test_whitespace_only(self) -> None:
        """Whitespace-only input returns no turns."""
        turns = WhatsAppParser.parse("   \n  \n  ")
        assert turns == []

    async def test_malformed_lines(self) -> None:
        """Lines that don't match the WhatsApp pattern are ignored when no prior turns exist."""
        raw = "This is not a whatsapp message\nNeither is this one"
        turns = WhatsAppParser.parse(raw)
        assert turns == []

    async def test_timestamps_are_captured(self) -> None:
        """Each turn captures the date and time from the WhatsApp header."""
        turns = WhatsAppParser.parse(WHATSAPP_MULTI_TURN)
        for turn in turns:
            assert turn.timestamp is not None
            assert "25/02/2026" in turn.timestamp

    async def test_turn_numbers_sequential(self) -> None:
        """Turn numbers are assigned sequentially starting from 1."""
        turns = WhatsAppParser.parse(WHATSAPP_MULTI_TURN)
        for i, turn in enumerate(turns, start=1):
            assert turn.turn_number == i


# ===================================================================
# TranscriptParser
# ===================================================================


class TestTranscriptParser:
    """Tests for TranscriptParser."""

    async def test_simple_role_format(self) -> None:
        """Parse a simple 'Role: message' transcript."""
        turns = TranscriptParser.parse(TRANSCRIPT_SIMPLE)

        assert len(turns) == 5
        assert turns[0].role == "Vendedor"
        assert turns[0].content == "Buenos dias, en que puedo ayudarle?"
        assert turns[1].role == "Cliente"
        assert turns[1].content == "Hola, busco un auto nuevo para mi familia"

    async def test_numbered_format(self) -> None:
        """Parse a numbered '1. Role: message' transcript."""
        turns = TranscriptParser.parse(TRANSCRIPT_NUMBERED)

        assert len(turns) == 4
        assert turns[0].role == "Vendedor"
        assert turns[0].content == "Buenos dias, bienvenido"
        assert turns[3].role == "Cliente"
        assert turns[3].content == "Me puede dar los precios?"

    async def test_continuation_lines(self) -> None:
        """Non-matching lines are appended to the previous turn."""
        turns = TranscriptParser.parse(TRANSCRIPT_CONTINUATION)

        assert len(turns) == 2
        assert "disponibles para usted" in turns[0].content
        assert "Buenos dias" in turns[0].content

    async def test_mixed_formats(self) -> None:
        """Numbered and simple transcript lines can coexist."""
        raw = "1. Vendedor: Buenos dias\nCliente: Hola, busco un auto\n2. Vendedor: Con gusto le ayudo\n"
        turns = TranscriptParser.parse(raw)
        assert len(turns) == 3

    async def test_empty_input(self) -> None:
        """Empty input returns no turns."""
        turns = TranscriptParser.parse("")
        assert turns == []

    async def test_turn_numbers_sequential(self) -> None:
        """Turn numbers are assigned sequentially."""
        turns = TranscriptParser.parse(TRANSCRIPT_SIMPLE)
        for i, turn in enumerate(turns, start=1):
            assert turn.turn_number == i

    async def test_no_timestamp(self) -> None:
        """Transcript turns have no timestamp by default."""
        turns = TranscriptParser.parse(TRANSCRIPT_SIMPLE)
        for turn in turns:
            assert turn.timestamp is None


# ===================================================================
# JSONConversationParser
# ===================================================================


class TestJSONConversationParser:
    """Tests for JSONConversationParser."""

    async def test_openai_messages_format(self) -> None:
        """Parse OpenAI-style messages with role/content keys."""
        turns = JSONConversationParser.parse(OPENAI_MESSAGES)

        assert len(turns) == 3
        assert turns[0].role == "system"
        assert turns[0].content == "Eres un asesor de ventas automotrices."
        assert turns[1].role == "user"
        assert turns[2].role == "assistant"

    async def test_uncase_turnos_format(self) -> None:
        """Parse UNCASE-style turnos with rol/contenido keys."""
        turns = JSONConversationParser.parse(UNCASE_TURNOS)

        assert len(turns) == 2
        assert turns[0].role == "vendedor"
        assert turns[0].content == "Buenos dias, bienvenido."
        assert turns[1].role == "cliente"

    async def test_flat_array(self) -> None:
        """Parse a flat JSON array of turn objects."""
        turns = JSONConversationParser.parse(FLAT_ARRAY)

        assert len(turns) == 3
        assert turns[0].role == "vendedor"
        assert turns[2].content == "Con gusto."

    async def test_jsonl_multi_line(self) -> None:
        """Parse JSONL with multiple conversations on separate lines."""
        turns = JSONConversationParser.parse(JSONL_MULTI)

        assert len(turns) == 4
        assert turns[0].role == "user"
        assert turns[0].content == "Quiero cotizar un sedan."
        assert turns[2].role == "user"
        assert turns[3].content == "Si, tenemos inventario."

    async def test_invalid_json(self) -> None:
        """Invalid JSON returns empty list."""
        turns = JSONConversationParser.parse("this is not json {{{")
        assert turns == []

    async def test_empty_input(self) -> None:
        """Empty input returns empty list."""
        turns = JSONConversationParser.parse("")
        assert turns == []

    async def test_missing_role_or_content(self) -> None:
        """Messages missing role or content are skipped."""
        raw = json.dumps({"messages": [{"role": "user"}, {"content": "orphan"}, {"role": "bot", "content": "ok"}]})
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "bot"

    async def test_single_turn_object(self) -> None:
        """A single JSON object with role/content is parsed as one turn."""
        raw = json.dumps({"role": "vendedor", "content": "Bienvenido al concesionario."})
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "vendedor"

    async def test_timestamp_extraction(self) -> None:
        """Timestamps are extracted from the JSON data when present."""
        raw = json.dumps(
            {
                "messages": [
                    {"role": "user", "content": "Hola", "timestamp": "2026-02-25T10:00:00"},
                ]
            }
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].timestamp == "2026-02-25T10:00:00"


# ===================================================================
# detect_format
# ===================================================================


class TestDetectFormat:
    """Tests for the detect_format helper."""

    async def test_whatsapp_format(self) -> None:
        """WhatsApp-style input is detected as 'whatsapp'."""
        assert detect_format(WHATSAPP_MULTI_TURN) == "whatsapp"

    async def test_numbered_format(self) -> None:
        """Numbered transcript input is detected as 'numbered'."""
        assert detect_format(TRANSCRIPT_NUMBERED) == "numbered"

    async def test_transcript_format(self) -> None:
        """Simple Role: format is detected as 'transcript'."""
        assert detect_format(TRANSCRIPT_SIMPLE) == "transcript"

    async def test_json_format(self) -> None:
        """JSON input is detected as 'json'."""
        assert detect_format(OPENAI_MESSAGES) == "json"

    async def test_jsonl_format(self) -> None:
        """JSONL input is detected as 'json'."""
        assert detect_format(JSONL_MULTI) == "json"

    async def test_unknown_format(self) -> None:
        """Unrecognized input returns 'unknown'."""
        assert detect_format("some random text without any structure") == "unknown"

    async def test_empty_string(self) -> None:
        """Empty string returns 'unknown'."""
        assert detect_format("") == "unknown"

    async def test_flat_array_format(self) -> None:
        """A JSON array is detected as 'json'."""
        assert detect_format(FLAT_ARRAY) == "json"
