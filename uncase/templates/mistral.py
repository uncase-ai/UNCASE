"""Mistral v3 chat template implementation.

Renders conversations using the Mistral instruction format with
``[INST]``/``[/INST]`` delimiters and ``[TOOL_CALLS]``/``[TOOL_RESULTS]``
blocks for tool interactions.
"""

from __future__ import annotations

import json
import random
from typing import TYPE_CHECKING

from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation, ConversationTurn
    from uncase.tools.schemas import ToolDefinition

# Role mapping: UNCASE Spanish roles → Mistral logical roles
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
    """Map a ConversationTurn role to a Mistral logical role."""
    return _ROLE_MAP.get(rol.lower(), "user")


def _generate_tool_call_id() -> str:
    """Generate a 9-digit random ID string for Mistral tool calls."""
    return str(random.randint(100000000, 999999999))  # noqa: S311


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


class MistralChatTemplate(BaseChatTemplate):
    """Mistral v3 chat template.

    Uses the Mistral instruction format::

        <s>[INST] {system}

        {user} [/INST]{assistant}</s>[INST] {user2} [/INST]{assistant2}</s>

    Tool calls use ``[TOOL_CALLS]`` / ``[TOOL_RESULTS]`` blocks with
    9-digit random identifiers.
    """

    @property
    def name(self) -> str:
        return "mistral"

    @property
    def display_name(self) -> str:
        return "Mistral"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        return [
            "[INST]",
            "[/INST]",
            "[TOOL_CALLS]",
            "[TOOL_RESULTS]",
            "[/TOOL_RESULTS]",
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation into a Mistral v3 prompt string."""
        # Build effective system prompt
        effective_system = system_prompt or ""
        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            tool_block = "\n\nAvailable tools:\n" + _render_tool_definitions(available_tools)
            effective_system += tool_block

        # Categorise turns into logical pairs
        turns = conversation.turnos
        parts: list[str] = []
        idx = 0

        # First exchange must start with <s> and may include the system prompt
        while idx < len(turns):
            role = _map_role(turns[idx].rol)

            # Skip tool-only turns when mode is NONE
            if role == "tool" and tool_call_mode == ToolCallMode.NONE:
                idx += 1
                continue

            # -- User turn (opens an [INST] block) -------------------------
            if role in ("user", "system"):
                inst_content = self._build_inst_content(
                    turns[idx],
                    effective_system if idx == 0 else None,
                )
                idx += 1

                # Look ahead for assistant response
                assistant_content = ""
                while idx < len(turns):
                    next_role = _map_role(turns[idx].rol)
                    if next_role == "assistant":
                        assistant_content = self._build_assistant_content(turns[idx], tool_call_mode)
                        idx += 1
                        break
                    if next_role == "tool" and tool_call_mode == ToolCallMode.INLINE:
                        # Tool result after an implicit assistant tool call
                        break
                    if next_role == "tool" and tool_call_mode == ToolCallMode.NONE:
                        idx += 1
                        continue
                    break

                if not parts:
                    parts.append(f"<s>[INST] {inst_content} [/INST]{assistant_content}</s>")
                else:
                    parts.append(f"[INST] {inst_content} [/INST]{assistant_content}</s>")

            # -- Assistant turn (tool call or standalone) -------------------
            elif role == "assistant":
                content = self._build_assistant_content(turns[idx], tool_call_mode)
                idx += 1

                # Handle tool results following the assistant turn
                tool_result_parts: list[str] = []
                while idx < len(turns) and _map_role(turns[idx].rol) == "tool":
                    if tool_call_mode == ToolCallMode.INLINE:
                        tool_result_parts.append(self._build_tool_result_content(turns[idx]))
                    idx += 1

                if tool_result_parts:
                    parts.append(content)
                    parts.extend(tool_result_parts)
                else:
                    # Standalone assistant in non-first position — unusual but handled
                    if not parts:
                        parts.append(f"<s>{content}</s>")
                    else:
                        parts.append(f"{content}</s>")

            # -- Tool turn (when INLINE, outside of user/assistant flow) ----
            elif role == "tool" and tool_call_mode == ToolCallMode.INLINE:
                parts.append(self._build_tool_result_content(turns[idx]))
                idx += 1

            else:
                idx += 1

        return "".join(parts)

    # -- Helpers ------------------------------------------------------------

    def _build_inst_content(
        self,
        turn: ConversationTurn,
        system_prompt: str | None,
    ) -> str:
        """Build the content inside an [INST] block."""
        if system_prompt:
            return f"{system_prompt}\n\n{turn.contenido}"
        return turn.contenido

    def _build_assistant_content(
        self,
        turn: ConversationTurn,
        tool_call_mode: ToolCallMode,
    ) -> str:
        """Build assistant content, including tool calls when inline."""
        if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls:
            calls = []
            for tc in turn.tool_calls:
                calls.append(
                    {
                        "name": tc.tool_name,
                        "arguments": tc.arguments,
                        "id": _generate_tool_call_id(),
                    }
                )
            return f"[TOOL_CALLS]{json.dumps(calls, ensure_ascii=False)}</s>"
        return turn.contenido

    def _build_tool_result_content(self, turn: ConversationTurn) -> str:
        """Build a [TOOL_RESULTS] block from a tool turn."""
        if turn.tool_results:
            # Render the first result (Mistral format uses one result block)
            tr = turn.tool_results[0]
            result_obj = {"call_id": tr.tool_call_id, "content": tr.result}
            return f"[TOOL_RESULTS]{json.dumps(result_obj, ensure_ascii=False)}[/TOOL_RESULTS]"
        # Fallback: use turn content
        return f"[TOOL_RESULTS]{turn.contenido}[/TOOL_RESULTS]"


# -- Auto-register ---------------------------------------------------------

from uncase.templates import get_template_registry  # noqa: E402

get_template_registry().register(MistralChatTemplate())
