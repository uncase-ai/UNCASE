"""Raw conversation format parsers for the Seed Engine.

Supports WhatsApp chat exports, simple transcript formats (Role: message),
numbered turn formats, and structured JSON/JSONL conversations. Each parser
produces a list of ``RawTurn`` dataclass instances that the engine normalises
into SeedSchema fields.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from uncase.logging import get_logger

logger = get_logger(__name__)

# ---------- WhatsApp export patterns ----------
# Matches: [DD/MM/YYYY, HH:MM:SS] Name: message
# Also tolerates the - separator variant: DD/MM/YYYY, HH:MM - Name: message
_WHATSAPP_RE = re.compile(
    r"^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[-\u2013]?\s*(.+?):\s(.+)",
)

# ---------- Numbered turn pattern ----------
# Matches: 1. Role: message  or  1) Role: message
_NUMBERED_RE = re.compile(r"^(\d+)[.)]\s*(.+?):\s(.+)")

# ---------- Simple transcript pattern ----------
# Matches: Role: message  (role is a single capitalised word or short phrase)
_TRANSCRIPT_RE = re.compile(r"^([A-ZÁ-Ú][a-záéíóúñü]*(?:\s[A-ZÁ-Ú][a-záéíóúñü]*)?):\s(.+)")


@dataclass
class RawTurn:
    """A single parsed turn from a raw conversation."""

    role: str
    content: str
    timestamp: str | None = None
    turn_number: int = 0


@dataclass
class ParseResult:
    """Result of parsing a raw conversation."""

    turns: list[RawTurn] = field(default_factory=list)
    format_detected: str = "unknown"
    raw_roles: set[str] = field(default_factory=set)


class WhatsAppParser:
    """Parse WhatsApp chat export format.

    Expected line format::

        [DD/MM/YYYY, HH:MM:SS] Name: message text
    """

    @staticmethod
    def parse(raw: str) -> list[RawTurn]:
        """Parse a WhatsApp export into a list of ``RawTurn``."""
        turns: list[RawTurn] = []
        turn_number = 0

        for line in raw.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            match = _WHATSAPP_RE.match(line)
            if match:
                date_part, time_part, role, content = match.groups()
                turn_number += 1
                turns.append(
                    RawTurn(
                        role=role.strip(),
                        content=content.strip(),
                        timestamp=f"{date_part} {time_part}",
                        turn_number=turn_number,
                    )
                )
            elif turns:
                # Continuation line — append to previous turn
                turns[-1].content += " " + line

        logger.debug("whatsapp_parsed", turn_count=len(turns))
        return turns


class TranscriptParser:
    """Parse simple ``Role: message`` transcript format.

    Each line starting with a recognised role prefix is a new turn.
    Lines that don't match are treated as continuations of the previous turn.
    """

    @staticmethod
    def parse(raw: str) -> list[RawTurn]:
        """Parse a plain transcript into a list of ``RawTurn``."""
        turns: list[RawTurn] = []
        turn_number = 0

        for line in raw.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            # Try numbered format first
            num_match = _NUMBERED_RE.match(line)
            if num_match:
                _num_str, role, content = num_match.groups()
                turn_number += 1
                turns.append(
                    RawTurn(
                        role=role.strip(),
                        content=content.strip(),
                        turn_number=turn_number,
                    )
                )
                continue

            # Then try simple transcript format
            tx_match = _TRANSCRIPT_RE.match(line)
            if tx_match:
                role, content = tx_match.groups()
                turn_number += 1
                turns.append(
                    RawTurn(
                        role=role.strip(),
                        content=content.strip(),
                        turn_number=turn_number,
                    )
                )
            elif turns:
                # Continuation line
                turns[-1].content += " " + line

        logger.debug("transcript_parsed", turn_count=len(turns))
        return turns


class JSONConversationParser:
    """Parse structured JSON/JSONL conversation formats.

    Supports three common structures:

    1. **OpenAI-style messages**::

        {"messages": [{"role": "user", "content": "Hi"}, ...]}

    2. **UNCASE conversation format**::

        {"turnos": [{"rol": "cliente", "contenido": "Hola"}, ...]}

    3. **Flat turn list** (array of objects)::

        [{"role": "user", "content": "Hi"}, ...]

    For JSONL, each line is parsed independently as a separate conversation.
    """

    @staticmethod
    def parse(raw: str) -> list[RawTurn]:
        """Parse a JSON or JSONL string into a list of ``RawTurn``.

        Args:
            raw: JSON object, JSON array, or JSONL (one JSON per line).

        Returns:
            List of parsed turns, empty if parsing fails.
        """
        stripped = raw.strip()
        if not stripped:
            return []

        # Try single JSON object / array first
        try:
            data = json.loads(stripped)
            return JSONConversationParser._parse_json_data(data)
        except json.JSONDecodeError:
            pass

        # Try JSONL (one JSON object per line)
        turns: list[RawTurn] = []
        global_turn = 0
        for line in stripped.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                line_turns = JSONConversationParser._parse_json_data(data, offset=global_turn)
                turns.extend(line_turns)
                global_turn += len(line_turns)
            except json.JSONDecodeError:
                continue

        logger.debug("json_parsed", turn_count=len(turns))
        return turns

    @staticmethod
    def _parse_json_data(data: Any, offset: int = 0) -> list[RawTurn]:
        """Parse a JSON data structure into turns.

        Args:
            data: Parsed JSON (dict or list).
            offset: Turn number offset for JSONL multi-conversation parsing.

        Returns:
            List of ``RawTurn`` objects.
        """
        messages: list[dict[str, Any]] = []

        if isinstance(data, dict):
            # OpenAI-style: {"messages": [...]}
            if "messages" in data:
                messages = data["messages"]
            # UNCASE-style: {"turnos": [...]}
            elif "turnos" in data:
                messages = data["turnos"]
            # Single turn: {"role": "...", "content": "..."}
            elif ("role" in data and "content" in data) or ("rol" in data and "contenido" in data):
                messages = [data]
        elif isinstance(data, list):
            messages = data

        turns: list[RawTurn] = []
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue

            # Extract role (try multiple field names)
            role = msg.get("role") or msg.get("rol") or msg.get("speaker") or msg.get("from", "")
            # Extract content
            content = msg.get("content") or msg.get("contenido") or msg.get("text") or msg.get("message", "")
            # Extract optional timestamp
            timestamp = msg.get("timestamp") or msg.get("time") or msg.get("fecha")

            if not role or not content:
                continue

            turns.append(
                RawTurn(
                    role=str(role).strip(),
                    content=str(content).strip(),
                    timestamp=str(timestamp) if timestamp else None,
                    turn_number=offset + i + 1,
                )
            )

        return turns


def detect_format(raw: str) -> str:
    """Auto-detect the raw conversation format.

    Returns one of ``"whatsapp"``, ``"numbered"``, ``"transcript"``,
    ``"json"``, or ``"unknown"``.
    """
    stripped = raw.strip()
    if not stripped:
        return "unknown"

    # Check for JSON/JSONL first (starts with { or [)
    if stripped[0] in ("{", "["):
        try:
            json.loads(stripped)
            return "json"
        except json.JSONDecodeError:
            # May be JSONL — check first non-empty line
            first_line = stripped.splitlines()[0].strip()
            if first_line and first_line[0] in ("{", "["):
                try:
                    json.loads(first_line)
                    return "json"
                except json.JSONDecodeError:
                    pass

    lines = [ln.strip() for ln in stripped.splitlines() if ln.strip()]

    if not lines:
        return "unknown"

    whatsapp_hits = sum(1 for ln in lines[:10] if _WHATSAPP_RE.match(ln))
    numbered_hits = sum(1 for ln in lines[:10] if _NUMBERED_RE.match(ln))
    transcript_hits = sum(1 for ln in lines[:10] if _TRANSCRIPT_RE.match(ln))

    sample_size = min(len(lines), 10)

    if whatsapp_hits > sample_size * 0.3:
        return "whatsapp"
    if numbered_hits > sample_size * 0.3:
        return "numbered"
    if transcript_hits > sample_size * 0.3:
        return "transcript"

    return "unknown"
