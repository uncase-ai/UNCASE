"""Llama 3/4 chat template implementation.

Renders conversations using the Llama 3/4 special-token format with
support for tool calls via the ``<|python_tag|>`` and ``ipython`` role
conventions.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation, ConversationTurn
    from uncase.tools.schemas import ToolDefinition

# Role mapping: UNCASE Spanish roles → Llama roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "ipython",
    # Pass-through for already-mapped roles
    "assistant": "assistant",
    "user": "user",
    "system": "system",
    "ipython": "ipython",
    "tool": "ipython",
}


def _map_role(rol: str) -> str:
    """Map a ConversationTurn role to a Llama role."""
    return _ROLE_MAP.get(rol.lower(), "user")


def _render_tool_definitions(tools: list[ToolDefinition]) -> str:
    """Render tool definitions as JSON for the system prompt."""
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
    return json.dumps(defs, ensure_ascii=False, indent=2)


class LlamaChatTemplate(BaseChatTemplate):
    """Llama 3/4 chat template.

    Uses Llama's header-based special-token format::

        <|begin_of_text|><|start_header_id|>system<|end_header_id|>

        {system_prompt}<|eot_id|>
        <|start_header_id|>user<|end_header_id|>

        {content}<|eot_id|>
        ...

    Tool calls use ``<|python_tag|>`` and the ``ipython`` role for results.
    """

    @property
    def name(self) -> str:
        return "llama"

    @property
    def display_name(self) -> str:
        return "Llama 3/4"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        return [
            "<|begin_of_text|>",
            "<|start_header_id|>",
            "<|end_header_id|>",
            "<|eot_id|>",
            "<|python_tag|>",
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation into a Llama 3/4 prompt string."""
        parts: list[str] = ["<|begin_of_text|>"]

        # -- System prompt --------------------------------------------------
        effective_system = system_prompt or ""
        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            tool_block = "\n\nAvailable tools:\n" + _render_tool_definitions(available_tools)
            effective_system += tool_block

        if effective_system:
            parts.append(f"<|start_header_id|>system<|end_header_id|>\n\n{effective_system}<|eot_id|>")

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            parts.extend(self._render_turn(turn, tool_call_mode))

        return "\n".join(parts)

    def _render_turn(
        self,
        turn: ConversationTurn,
        tool_call_mode: ToolCallMode,
    ) -> list[str]:
        """Render a single turn into Llama format parts."""
        fragments: list[str] = []
        role = _map_role(turn.rol)

        # Tool calls embedded inside an assistant turn
        if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls:
            for tc in turn.tool_calls:
                call_json = json.dumps(
                    {"name": tc.tool_name, "parameters": tc.arguments},
                    ensure_ascii=False,
                )
                fragments.append(
                    f"<|start_header_id|>assistant<|end_header_id|>\n\n<|python_tag|>{call_json}<|eot_id|>"
                )

        # Tool results rendered as ipython turns
        if tool_call_mode == ToolCallMode.INLINE and turn.tool_results:
            for tr in turn.tool_results:
                result_json = json.dumps(
                    {"tool_call_id": tr.tool_call_id, "result": tr.result},
                    ensure_ascii=False,
                )
                fragments.append(f"<|start_header_id|>ipython<|end_header_id|>\n\n{result_json}<|eot_id|>")

        # Skip the herramienta/tool role content when tool_call_mode is NONE
        # (tool turns have no meaningful text content outside tool results)
        if role == "ipython" and tool_call_mode == ToolCallMode.NONE:
            return fragments

        # Regular content
        if turn.contenido:
            fragments.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{turn.contenido}<|eot_id|>")

        return fragments


# -- Auto-register ---------------------------------------------------------

from uncase.templates import get_template_registry  # noqa: E402

get_template_registry().register(LlamaChatTemplate())
