"""Kimi/Moonshot chat template implementation.

Renders conversations in the Moonshot format used by Kimi models, which
uses unique role-specific start tokens and a ``<|im_middle|>`` separator
before assistant responses.

Format::

    <|im_system|>{system_prompt}<|im_end|>
    <|im_user|>{content}<|im_end|>
    <|im_middle|>
    <|im_assistant|>{content}<|im_end|>
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

# Role mapping from UNCASE conversation roles to Moonshot roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "tool",
}

_IM_SYSTEM = "<|im_system|>"
_IM_USER = "<|im_user|>"
_IM_ASSISTANT = "<|im_assistant|>"
_IM_MIDDLE = "<|im_middle|>"
_IM_TOOL = "<|im_tool|>"
_IM_END = "<|im_end|>"

_TOOL_CALL_OPEN = "<tool_call>"
_TOOL_CALL_CLOSE = "</tool_call>"

# Mapping from abstract role to Moonshot start token
_ROLE_TOKEN_MAP: dict[str, str] = {
    "system": _IM_SYSTEM,
    "user": _IM_USER,
    "assistant": _IM_ASSISTANT,
    "tool": _IM_TOOL,
}


class MoonshotTemplate(BaseChatTemplate):
    """Kimi/Moonshot template with role-specific tokens and middle separator.

    Uses unique start tokens for each role (``<|im_system|>``, ``<|im_user|>``,
    ``<|im_assistant|>``, ``<|im_tool|>``) and inserts ``<|im_middle|>``
    before assistant responses.  Tool calls are rendered inline using
    ``<tool_call>`` XML tags.
    """

    @property
    def name(self) -> str:
        return "moonshot"

    @property
    def display_name(self) -> str:
        return "Kimi (Moonshot)"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return Moonshot special tokens."""
        return [
            _IM_SYSTEM,
            _IM_USER,
            _IM_ASSISTANT,
            _IM_MIDDLE,
            _IM_TOOL,
            _IM_END,
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in Moonshot format.

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
            The fully rendered Moonshot prompt string.
        """
        parts: list[str] = []

        # -- System prompt --------------------------------------------------
        effective_system = self._build_system_prompt(system_prompt, available_tools, tool_call_mode)
        if effective_system:
            parts.append(f"{_IM_SYSTEM}{effective_system}{_IM_END}")

        # -- Conversation turns ---------------------------------------------
        prev_role: str | None = None

        for turn in conversation.turnos:
            role = _ROLE_MAP.get(turn.rol, turn.rol)

            # Tool-result turns rendered as tool messages
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_results and role in ("tool", "herramienta"):
                for result in turn.tool_results:
                    parts.append(self._format_tool_result(result))
                prev_role = "tool"
                continue

            # Insert middle token before assistant turns
            if role == "assistant" and prev_role != "assistant":
                parts.append(_IM_MIDDLE)

            # Build content
            content = turn.contenido
            start_token = _ROLE_TOKEN_MAP.get(role, f"<|im_{role}|>")

            # Append inline tool calls if enabled
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls and role == "assistant":
                content = self._append_tool_calls(content, turn.tool_calls)

            parts.append(f"{start_token}{content}{_IM_END}")
            prev_role = role

        return "\n".join(parts)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _append_tool_calls(content: str, tool_calls: list[ToolCall]) -> str:
        """Append tool-call XML blocks to assistant content."""
        parts: list[str] = []
        if content:
            parts.append(content)
        for tc in tool_calls:
            call_payload = json.dumps(
                {"name": tc.tool_name, "arguments": tc.arguments},
                ensure_ascii=False,
            )
            parts.append(f"{_TOOL_CALL_OPEN}\n{call_payload}\n{_TOOL_CALL_CLOSE}")
        return "\n".join(parts)

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Format a tool result as a Moonshot tool message."""
        result_payload = json.dumps(
            {"result": result.result},
            ensure_ascii=False,
        )
        return f"{_IM_TOOL}\n{result_payload}\n{_IM_END}"

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
get_template_registry().register(MoonshotTemplate())
