"""Nemotron chat template implementation.

Renders conversations in the Nemotron format, which uses ChatML base tokens
with additional ``<think>`` tags for chain-of-thought reasoning and
``<tool_call>`` / ``<tool_response>`` XML tags for tool interactions.

Format::

    <|im_start|>system
    {system_prompt}<|im_end|>
    <|im_start|>user
    {content}<|im_end|>
    <|im_start|>assistant
    <think>
    </think>
    {content}<|im_end|>
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

# Role mapping from UNCASE conversation roles to Nemotron roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "tool",
}

_IM_START = "<|im_start|>"
_IM_END = "<|im_end|>"
_THINK_OPEN = "<think>"
_THINK_CLOSE = "</think>"
_TOOL_CALL_OPEN = "<tool_call>"
_TOOL_CALL_CLOSE = "</tool_call>"
_TOOL_RESPONSE_OPEN = "<tool_response>"
_TOOL_RESPONSE_CLOSE = "</tool_response>"


class NemotronTemplate(BaseChatTemplate):
    """Nemotron template with ChatML base, thinking tags, and tool support.

    Uses ``<think>`` / ``</think>`` tags to wrap chain-of-thought reasoning
    in assistant turns, and ``<tool_call>`` / ``<tool_response>`` XML tags
    for tool interactions.
    """

    @property
    def name(self) -> str:
        return "nemotron"

    @property
    def display_name(self) -> str:
        return "Nemotron"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return Nemotron special tokens."""
        return [
            _IM_START,
            _IM_END,
            _THINK_OPEN,
            _THINK_CLOSE,
            _TOOL_CALL_OPEN,
            _TOOL_CALL_CLOSE,
            _TOOL_RESPONSE_OPEN,
            _TOOL_RESPONSE_CLOSE,
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in Nemotron format.

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
            The fully rendered Nemotron prompt string.
        """
        parts: list[str] = []

        # -- System prompt --------------------------------------------------
        effective_system = self._build_system_prompt(system_prompt, available_tools, tool_call_mode)
        if effective_system:
            parts.append(self._format_message("system", effective_system))

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            role = _ROLE_MAP.get(turn.rol, turn.rol)

            # Tool-result turns rendered as tool messages
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_results and role in ("tool", "herramienta"):
                for result in turn.tool_results:
                    parts.append(self._format_tool_result(result))
                continue

            # Assistant turns get thinking tags
            if role == "assistant":
                content = turn.contenido

                # Append inline tool calls if enabled
                if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls:
                    content = self._build_assistant_tool_calls(turn.tool_calls)
                else:
                    content = f"{_THINK_OPEN}\n{_THINK_CLOSE}\n{content}"

                parts.append(self._format_message(role, content))
            else:
                parts.append(self._format_message(role, turn.contenido))

        return "\n".join(parts)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _format_message(role: str, content: str) -> str:
        """Format a single Nemotron message block."""
        return f"{_IM_START}{role}\n{content}{_IM_END}"

    @staticmethod
    def _build_assistant_tool_calls(tool_calls: list[ToolCall]) -> str:
        """Build assistant content with thinking tags and tool call blocks."""
        parts: list[str] = [f"{_THINK_OPEN}\n{_THINK_CLOSE}"]
        for tc in tool_calls:
            call_payload = json.dumps(
                {"name": tc.tool_name, "arguments": tc.arguments},
                ensure_ascii=False,
            )
            parts.append(f"{_TOOL_CALL_OPEN}\n{call_payload}\n{_TOOL_CALL_CLOSE}")
        return "\n".join(parts)

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Format a tool result as a Nemotron tool message."""
        result_payload = json.dumps(
            {"tool_call_id": result.tool_call_id, "result": result.result},
            ensure_ascii=False,
        )
        body = f"{_TOOL_RESPONSE_OPEN}\n{result_payload}\n{_TOOL_RESPONSE_CLOSE}"
        return f"{_IM_START}tool\n{body}{_IM_END}"

    @staticmethod
    def _build_system_prompt(
        system_prompt: str | None,
        available_tools: list[ToolDefinition] | None,
        tool_call_mode: ToolCallMode,
    ) -> str | None:
        """Compose the system prompt, optionally appending tool definitions."""
        sections: list[str] = []
        if system_prompt:
            sections.append(system_prompt)

        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            tool_defs = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.input_schema,
                    },
                }
                for t in available_tools
            ]
            tool_json = json.dumps(tool_defs, indent=2, ensure_ascii=False)
            sections.append(f"# Available tools\n{tool_json}")

        return "\n\n".join(sections) if sections else None


# -- Auto-register ----------------------------------------------------------
get_template_registry().register(NemotronTemplate())
