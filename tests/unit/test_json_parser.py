"""Tests for the JSON/JSONL conversation parser."""

from __future__ import annotations

import json

import pytest

from uncase.core.seed_engine.parsers import (
    JSONConversationParser,
    detect_format,
)


class TestJSONConversationParser:
    """Test JSONConversationParser with all supported formats."""

    def test_openai_style_messages(self) -> None:
        raw = json.dumps(
            {
                "messages": [
                    {"role": "user", "content": "Hola, necesito ayuda."},
                    {"role": "assistant", "content": "Claro, con gusto le ayudo."},
                    {"role": "user", "content": "Gracias."},
                ]
            }
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 3
        assert turns[0].role == "user"
        assert turns[0].content == "Hola, necesito ayuda."
        assert turns[1].role == "assistant"
        assert turns[2].turn_number == 3

    def test_uncase_style_turnos(self) -> None:
        raw = json.dumps(
            {
                "turnos": [
                    {"rol": "vendedor", "contenido": "Buenos dias."},
                    {"rol": "cliente", "contenido": "Busco un vehiculo."},
                ]
            }
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 2
        assert turns[0].role == "vendedor"
        assert turns[0].content == "Buenos dias."
        assert turns[1].role == "cliente"

    def test_flat_turn_list(self) -> None:
        raw = json.dumps(
            [
                {"role": "agent", "content": "Welcome."},
                {"role": "customer", "content": "Thank you."},
            ]
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 2
        assert turns[0].role == "agent"
        assert turns[1].content == "Thank you."

    def test_single_turn_object(self) -> None:
        raw = json.dumps({"role": "user", "content": "Hello?"})
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "user"

    def test_single_turn_uncase_style(self) -> None:
        raw = json.dumps({"rol": "cliente", "contenido": "Hola"})
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "cliente"

    def test_alternative_field_names(self) -> None:
        raw = json.dumps(
            [
                {"speaker": "Doctor", "text": "How are you feeling?"},
                {"from": "Patient", "message": "Much better."},
            ]
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 2
        assert turns[0].role == "Doctor"
        assert turns[0].content == "How are you feeling?"
        assert turns[1].role == "Patient"
        assert turns[1].content == "Much better."

    def test_with_timestamps(self) -> None:
        raw = json.dumps(
            [
                {"role": "agent", "content": "Hi", "timestamp": "2026-01-01T10:00:00"},
                {"role": "user", "content": "Hello", "time": "2026-01-01T10:01:00"},
            ]
        )
        turns = JSONConversationParser.parse(raw)
        assert turns[0].timestamp == "2026-01-01T10:00:00"
        assert turns[1].timestamp == "2026-01-01T10:01:00"

    def test_jsonl_format(self) -> None:
        lines = [
            json.dumps({"role": "user", "content": "Line 1"}),
            json.dumps({"role": "assistant", "content": "Line 2"}),
        ]
        raw = "\n".join(lines)
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 2
        assert turns[0].content == "Line 1"
        assert turns[1].content == "Line 2"

    def test_jsonl_with_empty_lines(self) -> None:
        lines = [
            json.dumps({"role": "user", "content": "A"}),
            "",
            json.dumps({"role": "bot", "content": "B"}),
        ]
        raw = "\n".join(lines)
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 2

    def test_skips_entries_without_role(self) -> None:
        raw = json.dumps(
            [
                {"content": "No role here"},
                {"role": "user", "content": "Valid"},
            ]
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "user"

    def test_skips_entries_without_content(self) -> None:
        raw = json.dumps(
            [
                {"role": "user"},
                {"role": "bot", "content": "Hello"},
            ]
        )
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1
        assert turns[0].role == "bot"

    def test_skips_non_dict_entries(self) -> None:
        raw = json.dumps([42, "string", {"role": "user", "content": "Valid"}])
        turns = JSONConversationParser.parse(raw)
        assert len(turns) == 1

    def test_empty_string(self) -> None:
        assert JSONConversationParser.parse("") == []
        assert JSONConversationParser.parse("   ") == []

    def test_invalid_json(self) -> None:
        turns = JSONConversationParser.parse("not json at all {{{")
        assert turns == []

    def test_turn_numbering_with_offset(self) -> None:
        data = [
            {"role": "a", "content": "First"},
            {"role": "b", "content": "Second"},
        ]
        turns = JSONConversationParser._parse_json_data(data, offset=5)
        assert turns[0].turn_number == 6
        assert turns[1].turn_number == 7


class TestDetectFormat:
    """Test format auto-detection."""

    def test_detect_json_object(self) -> None:
        raw = json.dumps({"messages": [{"role": "user", "content": "Hi"}]})
        assert detect_format(raw) == "json"

    def test_detect_json_array(self) -> None:
        raw = json.dumps([{"role": "user", "content": "Hi"}])
        assert detect_format(raw) == "json"

    def test_detect_jsonl(self) -> None:
        raw = '{"role": "user", "content": "A"}\n{"role": "bot", "content": "B"}'
        assert detect_format(raw) == "json"

    def test_detect_whatsapp(self) -> None:
        raw = (
            "[01/01/2026, 10:00:00] Juan: Hola\n"
            "[01/01/2026, 10:01:00] Maria: Hola que tal\n"
            "[01/01/2026, 10:02:00] Juan: Bien gracias\n"
            "[01/01/2026, 10:03:00] Maria: Me alegro\n"
        )
        assert detect_format(raw) == "whatsapp"

    def test_detect_transcript(self) -> None:
        raw = "Vendedor: Buenos dias\nCliente: Hola\nVendedor: En que puedo ayudarle\nCliente: Necesito info"
        assert detect_format(raw) == "transcript"

    def test_detect_numbered(self) -> None:
        raw = "1. Vendedor: Hola\n2. Cliente: Buenos dias\n3. Vendedor: En que puedo ayudarle\n4. Cliente: Info"
        assert detect_format(raw) == "numbered"

    def test_detect_empty(self) -> None:
        assert detect_format("") == "unknown"
        assert detect_format("   ") == "unknown"

    def test_detect_unknown(self) -> None:
        assert detect_format("just some random text here") == "unknown"


class TestWhatsAppTimestampVariants:
    """Test WhatsApp parser handles multiple timestamp formats."""

    def test_bracket_format(self) -> None:
        from uncase.core.seed_engine.parsers import WhatsAppParser

        raw = "[25/02/2026, 14:30:00] Ana: Hola\n[25/02/2026, 14:31:00] Pedro: Buenos dias"
        turns = WhatsAppParser.parse(raw)
        assert len(turns) == 2
        assert turns[0].role == "Ana"
        assert turns[0].timestamp == "25/02/2026 14:30:00"

    def test_continuation_lines(self) -> None:
        from uncase.core.seed_engine.parsers import WhatsAppParser

        raw = (
            "[01/01/2026, 10:00:00] Juan: Este es un mensaje\n"
            "que continua en la siguiente linea\n"
            "[01/01/2026, 10:01:00] Maria: Ok"
        )
        turns = WhatsAppParser.parse(raw)
        assert len(turns) == 2
        assert "continua" in turns[0].content


class TestTranscriptParser:
    """Test transcript parser variants."""

    def test_numbered_format(self) -> None:
        from uncase.core.seed_engine.parsers import TranscriptParser

        raw = "1. Vendedor: Hola\n2. Cliente: Buenos dias\n3. Vendedor: En que puedo ayudarle"
        turns = TranscriptParser.parse(raw)
        assert len(turns) == 3
        assert turns[0].role == "Vendedor"

    def test_simple_transcript(self) -> None:
        from uncase.core.seed_engine.parsers import TranscriptParser

        raw = "Agente: Bienvenido\nCliente: Gracias\nAgente: En que puedo ayudarle"
        turns = TranscriptParser.parse(raw)
        assert len(turns) == 3
        assert turns[1].role == "Cliente"

    def test_continuation_line(self) -> None:
        from uncase.core.seed_engine.parsers import TranscriptParser

        raw = "Doctor: Necesita tomar\nel medicamento dos veces al dia\nPaciente: Entendido"
        turns = TranscriptParser.parse(raw)
        assert len(turns) == 2
        assert "dos veces" in turns[0].content
