"""Qwen 3 chat template implementation.

Renders conversations using the ChatML-based format with Qwen-specific
XML wrapping for tool calls (``<tool_call>``) and tool results
(``<tool_response>``).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation, ConversationTurn
    from uncase.tools.schemas import ToolDefinition

# Role mapping: UNCASE Spanish roles → Qwen/ChatML roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "tool",
    # Pass-through
    "assistant": "assistant",
    "user": "user",
    "system": "system",
    "tool": "tool",
}


def _map_role(rol: str) -> str:
    """Map a ConversationTurn role to a Qwen role."""
    return _ROLE_MAP.get(rol.lower(), "user")


def _render_tool_definitions(tools: list[ToolDefinition]) -> str:
    """Render tool definitions inside ``<tools>`` XML tags for the system prompt."""
    defs = []
    for tool in tools:
        defs.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
        )
    lines = ["\n\n<tools>"]
    for d in defs:
        lines.append(json.dumps(d, ensure_ascii=False))
    lines.append("</tools>")
    return "\n".join(lines)


class QwenChatTemplate(BaseChatTemplate):
    """Qwen 3 chat template (ChatML base with XML tool wrapping).

    Standard messages::

        <|im_start|>system
        {system_prompt}<|im_end|>
        <|im_start|>user
        {content}<|im_end|>
        <|im_start|>assistant
        {content}<|im_end|>

    Tool calls use XML wrappers inside assistant/tool turns::

        <|im_start|>assistant
        <tool_call>
        {"name": "...", "arguments": {...}}
        </tool_call><|im_end|>
        <|im_start|>tool
        <tool_response>
        {"name": "...", "content": ...}
        </tool_response><|im_end|>
    """

    @property
    def name(self) -> str:
        return "qwen"

    @property
    def display_name(self) -> str:
        return "Qwen 3"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        return [
            "<|im_start|>",
            "<|im_end|>",
            "<tool_call>",
            "</tool_call>",
            "<tool_response>",
            "</tool_response>",
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation into a Qwen 3 prompt string."""
        parts: list[str] = []

        # -- System prompt --------------------------------------------------
        effective_system = system_prompt or ""
        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            effective_system += _render_tool_definitions(available_tools)

        if effective_system:
            parts.append(f"<|im_start|>system\n{effective_system}<|im_end|>")

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            parts.extend(self._render_turn(turn, tool_call_mode))

        return "\n".join(parts)

    def _render_turn(
        self,
        turn: ConversationTurn,
        tool_call_mode: ToolCallMode,
    ) -> list[str]:
        """Render a single turn into Qwen format parts."""
        fragments: list[str] = []
        role = _map_role(turn.rol)

        # -- Tool calls inside assistant turn -------------------------------
        if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls:
            for tc in turn.tool_calls:
                call_json = json.dumps(
                    {"name": tc.tool_name, "arguments": tc.arguments},
                    ensure_ascii=False,
                )
                fragments.append(f"<|im_start|>assistant\n<tool_call>\n{call_json}\n</tool_call><|im_end|>")

        # -- Tool results rendered as tool turns ----------------------------
        if tool_call_mode == ToolCallMode.INLINE and turn.tool_results:
            for tr in turn.tool_results:
                result_json = json.dumps(
                    {"name": tr.tool_name, "content": tr.result},
                    ensure_ascii=False,
                )
                fragments.append(f"<|im_start|>tool\n<tool_response>\n{result_json}\n</tool_response><|im_end|>")

        # Skip tool-role turns when mode is NONE
        if role == "tool" and tool_call_mode == ToolCallMode.NONE:
            return fragments

        # Regular content
        if turn.contenido:
            fragments.append(f"<|im_start|>{role}\n{turn.contenido}<|im_end|>")

        return fragments


# -- Auto-register ---------------------------------------------------------

from uncase.templates import get_template_registry  # noqa: E402

get_template_registry().register(QwenChatTemplate())
