"""Harmony chat template implementation.

Renders conversations in the Harmony format used by Cohere Command R+.

Format::

    <|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>{system_prompt}<|END_OF_TURN_TOKEN|>
    <|START_OF_TURN_TOKEN|><|USER_TOKEN|>{content}<|END_OF_TURN_TOKEN|>
    <|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>{content}<|END_OF_TURN_TOKEN|>
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

# Harmony turn tokens
_START = "<|START_OF_TURN_TOKEN|>"
_END = "<|END_OF_TURN_TOKEN|>"
_SYSTEM = "<|SYSTEM_TOKEN|>"
_USER = "<|USER_TOKEN|>"
_CHATBOT = "<|CHATBOT_TOKEN|>"

# Role mapping from UNCASE conversation roles to Harmony role tokens
_ROLE_TOKEN_MAP: dict[str, str] = {
    "vendedor": _CHATBOT,
    "asistente": _CHATBOT,
    "cliente": _USER,
    "usuario": _USER,
    "sistema": _SYSTEM,
    "herramienta": _SYSTEM,
}


class HarmonyTemplate(BaseChatTemplate):
    """Harmony template used by Cohere Command R+.

    Supports tool calls via ``Action: ```json`` blocks for invocation and
    ``<results>`` XML blocks for responses.
    """

    @property
    def name(self) -> str:
        return "harmony"

    @property
    def display_name(self) -> str:
        return "Harmony (Cohere)"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return Harmony special tokens."""
        return [_START, _END, _SYSTEM, _USER, _CHATBOT]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in Harmony format.

        Parameters
        ----------
        conversation:
            The conversation to render.
        tool_call_mode:
            How to handle tool calls.  ``NONE`` strips them;
            ``INLINE`` embeds them in the rendered output.
        system_prompt:
            Optional system prompt prepended to the conversation.
        available_tools:
            Tool definitions to include when *tool_call_mode* is ``INLINE``.

        Returns
        -------
        str
            The fully rendered Harmony prompt string.
        """
        parts: list[str] = []

        # -- System prompt --------------------------------------------------
        effective_system = self._build_system_prompt(system_prompt, available_tools, tool_call_mode)
        if effective_system:
            parts.append(self._format_turn(_SYSTEM, effective_system))

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            role_token = _ROLE_TOKEN_MAP.get(turn.rol, _USER)

            # Tool-result turns rendered as system results
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_results and turn.rol in ("herramienta", "sistema"):
                for result in turn.tool_results:
                    parts.append(self._format_tool_result(result))
                continue

            content = turn.contenido

            # Append inline tool calls if enabled
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls and role_token == _CHATBOT:
                content = self._build_tool_call_content(content, turn.tool_calls)

            parts.append(self._format_turn(role_token, content))

        return "\n".join(parts)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _format_turn(role_token: str, content: str) -> str:
        """Format a single Harmony turn block."""
        return f"{_START}{role_token}{content}{_END}"

    @staticmethod
    def _build_tool_call_content(content: str, tool_calls: list[ToolCall]) -> str:
        """Build chatbot content with inline tool-call Action blocks."""
        actions = [{"tool_name": tc.tool_name, "parameters": tc.arguments} for tc in tool_calls]
        action_json = json.dumps(actions, indent=2, ensure_ascii=False)
        parts: list[str] = []
        if content:
            parts.append(content)
        parts.append(f"Action: ```json\n{action_json}\n```")
        return "\n".join(parts)

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Format a tool result as a Harmony system results block."""
        result_payload = json.dumps(
            {"tool_call_id": result.tool_call_id, "result": result.result},
            ensure_ascii=False,
        )
        body = f"\n<results>\n{result_payload}\n</results>"
        return f"{_START}{_SYSTEM}{body}{_END}"

    @staticmethod
    def _build_system_prompt(
        system_prompt: str | None,
        available_tools: list[ToolDefinition] | None,
        tool_call_mode: ToolCallMode,
    ) -> str | None:
        """Compose the system prompt, optionally appending tool signatures."""
        sections: list[str] = []
        if system_prompt:
            sections.append(system_prompt)

        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            tool_sigs = _render_tool_signatures(available_tools)
            sections.append(f"## Available Tools\n{tool_sigs}")

        return "\n\n".join(sections) if sections else None


def _render_tool_signatures(tools: list[ToolDefinition]) -> str:
    """Render tool definitions as TypeScript-style function signatures."""
    signatures: list[str] = []
    for tool in tools:
        params = _schema_to_ts_params(tool.input_schema)
        sig = f"```typescript\n{tool.name}({params}): object\n```"
        desc = f"// {tool.description}"
        signatures.append(f"{desc}\n{sig}")
    return "\n\n".join(signatures)


def _schema_to_ts_params(input_schema: dict[str, Any]) -> str:
    """Convert a JSON Schema properties dict to TypeScript-style parameter list."""
    properties = input_schema.get("properties", {})
    raw_required = input_schema.get("required", [])
    required_fields = set(raw_required) if isinstance(raw_required, list) else set()
    params: list[str] = []
    if not isinstance(properties, dict):
        return ""
    for prop_name, prop_spec in properties.items():
        if not isinstance(prop_spec, dict):
            continue
        ts_type = _json_type_to_ts(prop_spec.get("type", "any"))
        optional = "" if prop_name in required_fields else "?"
        params.append(f"{prop_name}{optional}: {ts_type}")
    return ", ".join(params)


def _json_type_to_ts(json_type: object) -> str:
    """Map JSON Schema type to TypeScript type."""
    type_map: dict[str, str] = {
        "string": "string",
        "number": "number",
        "integer": "number",
        "boolean": "boolean",
        "object": "object",
        "array": "any[]",
        "null": "null",
    }
    if isinstance(json_type, str):
        return type_map.get(json_type, "any")
    return "any"


# -- Auto-register ----------------------------------------------------------
get_template_registry().register(HarmonyTemplate())
