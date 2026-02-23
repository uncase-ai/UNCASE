"""CSV conversation parser — imports conversations from CSV files."""

from __future__ import annotations

import csv
import io
import json
import uuid
from collections import defaultdict
from typing import TYPE_CHECKING, Any

import structlog

from uncase.core.parser.base import BaseParser
from uncase.exceptions import ImportParsingError
from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.tools.schemas import ToolCall, ToolResult

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

_REQUIRED_COLUMNS = {"conversation_id", "turn_number", "role", "content"}
_OPTIONAL_COLUMNS = {
    "tool_calls",
    "tool_results",
    "seed_id",
    "domain",
    "language",
    "metadata",
}


class CSVConversationParser(BaseParser):
    """Parse conversations from CSV format.

    Required columns: ``conversation_id``, ``turn_number``, ``role``,
    ``content``.

    Optional columns: ``tool_calls`` (JSON string), ``tool_results``
    (JSON string), ``seed_id``, ``domain``, ``language``, ``metadata``
    (JSON string).
    """

    # -- BaseParser interface --------------------------------------------------

    async def parse(self, raw_input: str, format: str = "csv") -> list[Conversation]:  # noqa: A002
        """Parse a CSV string into a list of Conversation objects.

        Args:
            raw_input: Full CSV content as a string.
            format: Must be ``"csv"`` (kept for interface compatibility).

        Returns:
            A list of :class:`Conversation` instances.

        Raises:
            ImportParsingError: When required columns are missing or rows
                cannot be parsed.
        """
        reader = csv.DictReader(io.StringIO(raw_input))

        if reader.fieldnames is None:
            raise ImportParsingError("CSV input is empty or has no header row")

        present = {name.strip().lower() for name in reader.fieldnames}
        missing = _REQUIRED_COLUMNS - present
        if missing:
            raise ImportParsingError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        # Group rows by conversation_id.
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for line_no, row in enumerate(reader, start=2):
            try:
                groups[row["conversation_id"].strip()].append(row)
            except KeyError as exc:
                raise ImportParsingError(f"Row {line_no}: missing 'conversation_id' value") from exc

        conversations: list[Conversation] = []
        for conv_id, rows in groups.items():
            try:
                conversations.append(self._build_conversation(conv_id, rows))
            except Exception as exc:
                raise ImportParsingError(f"Failed to build conversation '{conv_id}': {exc}") from exc

        logger.info(
            "csv_parse_complete",
            conversations=len(conversations),
            total_rows=sum(len(r) for r in groups.values()),
        )
        return conversations

    def supported_formats(self) -> list[str]:
        """Return supported formats."""
        return ["csv"]

    # -- File helper -----------------------------------------------------------

    async def parse_file(self, path: Path) -> list[Conversation]:
        """Read a CSV file and parse it into conversations.

        Args:
            path: Path to the CSV file.

        Returns:
            A list of :class:`Conversation` instances.
        """
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ImportParsingError(f"Cannot read file {path}: {exc}") from exc
        return await self.parse(content)

    # -- Internal helpers ------------------------------------------------------

    def _build_conversation(self, conv_id: str, rows: list[dict[str, Any]]) -> Conversation:
        """Build a single Conversation from grouped CSV rows."""
        # Sort by turn_number to guarantee ordering.
        rows.sort(key=lambda r: int(r["turn_number"]))

        # Extract conversation-level fields from the first row.
        first = rows[0]
        seed_id = (first.get("seed_id") or "").strip() or uuid.uuid4().hex
        domain = (first.get("domain") or "").strip() or "general"
        language = (first.get("language") or "").strip() or "es"

        turns: list[ConversationTurn] = []
        for row in rows:
            turns.append(self._build_turn(row))

        return Conversation(
            conversation_id=conv_id,
            seed_id=seed_id,
            dominio=domain,
            idioma=language,
            turnos=turns,
        )

    def _build_turn(self, row: dict[str, Any]) -> ConversationTurn:
        """Build a single ConversationTurn from a CSV row."""
        tool_calls = self._parse_json_field(row.get("tool_calls"), "tool_calls", ToolCall)
        tool_results = self._parse_json_field(row.get("tool_results"), "tool_results", ToolResult)
        metadata = self._parse_json_dict(row.get("metadata"))

        return ConversationTurn(
            turno=int(row["turn_number"]),
            rol=row["role"].strip(),
            contenido=row["content"].strip(),
            tool_calls=tool_calls if tool_calls else None,
            tool_results=tool_results if tool_results else None,
            metadata=metadata,
        )

    @staticmethod
    def _parse_json_field(
        value: str | None,
        field_name: str,
        model_cls: type[ToolCall | ToolResult],
    ) -> list[Any] | None:
        """Parse an optional JSON-string column into a list of Pydantic models."""
        if not value or not value.strip():
            return None
        try:
            data = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ImportParsingError(f"Invalid JSON in column '{field_name}': {exc}") from exc
        if not isinstance(data, list):
            data = [data]
        return [model_cls.model_validate(item) for item in data]

    @staticmethod
    def _parse_json_dict(value: str | None) -> dict[str, str]:
        """Parse an optional JSON-string column into a dict."""
        if not value or not value.strip():
            return {}
        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        return {}
