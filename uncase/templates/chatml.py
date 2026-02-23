"""ChatML chat template implementation.

Renders conversations in the ChatML format used by GPT-4, Qwen base,
and many other instruction-tuned models.

Format::

    <|im_start|>system
    {system_prompt}<|im_end|>
    <|im_start|>user
    {content}<|im_end|>
    <|im_start|>assistant
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

# Role mapping from UNCASE conversation roles to ChatML roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "function",
}

_IM_START = "<|im_start|>"
_IM_END = "<|im_end|>"


class ChatMLTemplate(BaseChatTemplate):
    """ChatML template used by GPT-4, Qwen base, and many other models.

    Supports tool calls via inline ``<tool_call>`` / ``<tool_response>``
    XML blocks within turns.
    """

    @property
    def name(self) -> str:
        return "chatml"

    @property
    def display_name(self) -> str:
        return "ChatML"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return ChatML special tokens."""
        return [_IM_START, _IM_END]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in ChatML format.

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
            The fully rendered ChatML prompt string.
        """
        parts: list[str] = []

        # -- System prompt --------------------------------------------------
        effective_system = self._build_system_prompt(system_prompt, available_tools, tool_call_mode)
        if effective_system:
            parts.append(self._format_message("system", effective_system))

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            role = _ROLE_MAP.get(turn.rol, turn.rol)

            # Tool-result turns rendered as function messages
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_results and role in ("function", "herramienta"):
                for result in turn.tool_results:
                    parts.append(self._format_tool_result(result))
                continue

            # Regular content
            content = turn.contenido

            # Append inline tool calls if enabled
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls and role == "assistant":
                content = self._append_tool_calls(content, turn.tool_calls)

            parts.append(self._format_message(role, content))

        return "\n".join(parts)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _format_message(role: str, content: str) -> str:
        """Format a single ChatML message block."""
        return f"{_IM_START}{role}\n{content}{_IM_END}"

    @staticmethod
    def _append_tool_calls(content: str, tool_calls: list[ToolCall]) -> str:
        """Append tool-call XML blocks to assistant content."""
        parts = [content] if content else []
        for tc in tool_calls:
            call_payload = json.dumps(
                {"name": tc.tool_name, "arguments": tc.arguments},
                ensure_ascii=False,
            )
            parts.append(f"<tool_call>\n{call_payload}\n</tool_call>")
        return "\n".join(parts)

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Format a tool result as a ChatML function message."""
        result_payload = json.dumps(
            {"tool_call_id": result.tool_call_id, "result": result.result},
            ensure_ascii=False,
        )
        body = f"<tool_response>\n{result_payload}\n</tool_response>"
        return f"{_IM_START}function\n{body}{_IM_END}"

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
get_template_registry().register(ChatMLTemplate())
