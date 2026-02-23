"""JSONL conversation parser — imports conversations from JSONL files.

Supports three source formats auto-detected from the first line:

- **openai**: ``{"messages": [{"role": "...", "content": "...", ...}]}``
- **sharegpt**: ``{"conversations": [{"from": "human|gpt", "value": "..."}]}``
- **uncase**: Native Conversation JSON (has ``"turnos"`` field)
"""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any, Literal

import structlog

from uncase.core.parser.base import BaseParser
from uncase.exceptions import ImportFormatError, ImportParsingError
from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.tools.schemas import ToolCall, ToolResult

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

# Mapping from ShareGPT role names to UNCASE internal roles.
_SHAREGPT_ROLE_MAP: dict[str, str] = {
    "human": "usuario",
    "gpt": "asistente",
    "system": "sistema",
}

# Mapping from OpenAI role names to UNCASE internal roles.
_OPENAI_ROLE_MAP: dict[str, str] = {
    "user": "usuario",
    "assistant": "asistente",
    "system": "sistema",
    "tool": "herramienta",
}


class JSONLConversationParser(BaseParser):
    """Parse conversations from JSONL (JSON Lines) format.

    Each line in the input must be a valid JSON object representing one
    conversation. The parser auto-detects whether the source is in
    OpenAI, ShareGPT, or native UNCASE format.
    """

    # -- BaseParser interface --------------------------------------------------

    async def parse(self, raw_input: str, format: str = "auto") -> list[Conversation]:  # noqa: A002
        """Parse a JSONL string into a list of Conversation objects.

        Args:
            raw_input: JSONL content (one JSON object per line).
            format: Source format hint — ``"auto"``, ``"openai"``,
                ``"sharegpt"``, or ``"uncase"``.

        Returns:
            A list of :class:`Conversation` instances.

        Raises:
            ImportParsingError: When a line cannot be parsed as JSON.
            ImportFormatError: When the source format is unrecognised.
        """
        lines = [ln.strip() for ln in raw_input.splitlines() if ln.strip()]
        if not lines:
            raise ImportParsingError("JSONL input is empty")

        # Parse every line into dicts first.
        records: list[dict[str, Any]] = []
        for line_no, line in enumerate(lines, start=1):
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ImportParsingError(f"Line {line_no}: invalid JSON — {exc}") from exc
            if not isinstance(data, dict):
                raise ImportParsingError(f"Line {line_no}: expected a JSON object, got {type(data).__name__}")
            records.append(data)

        # Detect source format from the first record when auto.
        source_format: Literal["openai", "sharegpt", "uncase"]
        if format == "auto":
            source_format = self._detect_source_format(records[0])
            logger.info("jsonl_format_detected", source_format=source_format)
        else:
            if format not in ("openai", "sharegpt", "uncase"):
                raise ImportFormatError(f"Unsupported JSONL source format: {format}")
            source_format = format  # type: ignore[assignment]

        # Dispatch each record to the appropriate handler.
        dispatch = {
            "openai": self._parse_openai,
            "sharegpt": self._parse_sharegpt,
            "uncase": self._parse_uncase,
        }
        handler = dispatch[source_format]

        conversations: list[Conversation] = []
        for line_no, record in enumerate(records, start=1):
            try:
                conversations.append(handler(record))
            except (ImportFormatError, ImportParsingError):
                raise
            except Exception as exc:
                raise ImportParsingError(f"Line {line_no}: failed to convert record — {exc}") from exc

        logger.info(
            "jsonl_parse_complete",
            conversations=len(conversations),
            source_format=source_format,
        )
        return conversations

    def supported_formats(self) -> list[str]:
        """Return supported formats."""
        return ["jsonl"]

    # -- File helper -----------------------------------------------------------

    async def parse_file(self, path: Path, source_format: str = "auto") -> list[Conversation]:
        """Read a JSONL file and parse it into conversations.

        Args:
            path: Path to the JSONL file.
            source_format: Source format hint (``"auto"`` by default).

        Returns:
            A list of :class:`Conversation` instances.
        """
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ImportParsingError(f"Cannot read file {path}: {exc}") from exc
        return await self.parse(content, format=source_format)

    # -- Format detection ------------------------------------------------------

    def _detect_source_format(self, data: dict[str, Any]) -> Literal["openai", "sharegpt", "uncase"]:
        """Detect the source format from the keys in a JSON object.

        Args:
            data: The first parsed JSON object from the file.

        Returns:
            The detected format string.

        Raises:
            ImportFormatError: When the format cannot be determined.
        """
        if "messages" in data:
            return "openai"
        if "conversations" in data:
            return "sharegpt"
        if "turnos" in data:
            return "uncase"
        raise ImportFormatError(
            "Cannot detect JSONL source format — expected 'messages' (OpenAI), "
            "'conversations' (ShareGPT), or 'turnos' (UNCASE) key in the first line"
        )

    # -- Format-specific parsers -----------------------------------------------

    def _parse_openai(self, data: dict[str, Any]) -> Conversation:
        """Convert an OpenAI-format record to a Conversation.

        Expected shape::

            {
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "...", "tool_calls": [...]},
                ]
            }
        """
        messages = data.get("messages")
        if not messages or not isinstance(messages, list):
            raise ImportParsingError("OpenAI record missing 'messages' list")

        turns: list[ConversationTurn] = []
        for idx, msg in enumerate(messages, start=1):
            role = _OPENAI_ROLE_MAP.get(msg.get("role", ""), msg.get("role", "unknown"))
            content = msg.get("content") or ""

            tool_calls: list[ToolCall] | None = None
            if msg.get("tool_calls"):
                tool_calls = [self._convert_openai_tool_call(tc) for tc in msg["tool_calls"]]

            tool_results: list[ToolResult] | None = None
            if msg.get("role") == "tool" and "tool_call_id" in msg:
                tool_results = [
                    ToolResult(
                        tool_call_id=msg["tool_call_id"],
                        tool_name=msg.get("name", "unknown"),
                        result=content,
                        status="success",
                    )
                ]
                # For tool-role messages the content is the result; keep it
                # as the turn content as well for readability.

            turns.append(
                ConversationTurn(
                    turno=idx,
                    rol=role,
                    contenido=content if content else "(tool result)",
                    tool_calls=tool_calls,
                    tool_results=tool_results,
                )
            )

        return Conversation(
            conversation_id=data.get("conversation_id", uuid.uuid4().hex),
            seed_id=data.get("seed_id", uuid.uuid4().hex),
            dominio=data.get("domain", "general"),
            idioma=data.get("language", "en"),
            turnos=turns,
        )

    def _parse_sharegpt(self, data: dict[str, Any]) -> Conversation:
        """Convert a ShareGPT-format record to a Conversation.

        Expected shape::

            {
                "conversations": [
                    {"from": "human", "value": "..."},
                    {"from": "gpt", "value": "..."},
                ]
            }
        """
        convs = data.get("conversations")
        if not convs or not isinstance(convs, list):
            raise ImportParsingError("ShareGPT record missing 'conversations' list")

        turns: list[ConversationTurn] = []
        for idx, msg in enumerate(convs, start=1):
            raw_role = msg.get("from", "unknown")
            role = _SHAREGPT_ROLE_MAP.get(raw_role, raw_role)
            content = msg.get("value", "")

            turns.append(
                ConversationTurn(
                    turno=idx,
                    rol=role,
                    contenido=content,
                )
            )

        return Conversation(
            conversation_id=data.get("id", uuid.uuid4().hex),
            seed_id=data.get("seed_id", uuid.uuid4().hex),
            dominio=data.get("domain", "general"),
            idioma=data.get("language", "en"),
            turnos=turns,
        )

    def _parse_uncase(self, data: dict[str, Any]) -> Conversation:
        """Convert a native UNCASE record to a Conversation.

        Uses Pydantic's ``model_validate`` for full validation.
        """
        try:
            return Conversation.model_validate(data)
        except Exception as exc:
            raise ImportParsingError(f"Failed to validate native UNCASE record: {exc}") from exc

    # -- Utility ---------------------------------------------------------------

    @staticmethod
    def _convert_openai_tool_call(tc: dict[str, Any]) -> ToolCall:
        """Convert an OpenAI tool_call dict to a ToolCall model."""
        # OpenAI nests arguments inside a "function" key.
        func = tc.get("function", {})
        arguments = func.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw": arguments}

        return ToolCall(
            tool_call_id=tc.get("id", uuid.uuid4().hex),
            tool_name=func.get("name", "unknown"),
            arguments=arguments,
        )
