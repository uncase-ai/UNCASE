"""MiniMax chat template implementation.

Renders conversations in the MiniMax format, which uses ChatML-style
tokens for messages and XML-based ``<function_call>`` / ``<function_response>``
tags for tool interactions.

Format::

    <|im_start|>system
    {system_prompt}<|im_end|>
    <|im_start|>user
    {content}<|im_end|>
    <|im_start|>assistant
    {content}<|im_end|>

Tool calls::

    <|im_start|>assistant
    <function_call>
    {"name": "tool_name", "arguments": {...}}
    </function_call><|im_end|>
    <|im_start|>function
    <function_response>
    {"name": "tool_name", "result": ...}
    </function_response><|im_end|>
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

# Role mapping from UNCASE conversation roles to MiniMax roles
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
_FUNC_CALL_OPEN = "<function_call>"
_FUNC_CALL_CLOSE = "</function_call>"
_FUNC_RESPONSE_OPEN = "<function_response>"
_FUNC_RESPONSE_CLOSE = "</function_response>"


class MiniMaxTemplate(BaseChatTemplate):
    """MiniMax template with ChatML base and XML function call tags.

    Uses ``<function_call>`` / ``</function_call>`` for tool invocations and
    ``<function_response>`` / ``</function_response>`` for tool results.
    Available tools are rendered inside ``<functions>`` XML tags in the
    system prompt.
    """

    @property
    def name(self) -> str:
        return "minimax"

    @property
    def display_name(self) -> str:
        return "MiniMax"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return MiniMax special tokens."""
        return [
            _IM_START,
            _IM_END,
            _FUNC_CALL_OPEN,
            _FUNC_CALL_CLOSE,
            _FUNC_RESPONSE_OPEN,
            _FUNC_RESPONSE_CLOSE,
        ]

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in MiniMax format.

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
            The fully rendered MiniMax prompt string.
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
                content = self._build_function_calls(turn.tool_calls)

            parts.append(self._format_message(role, content))

        return "\n".join(parts)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _format_message(role: str, content: str) -> str:
        """Format a single MiniMax message block."""
        return f"{_IM_START}{role}\n{content}{_IM_END}"

    @staticmethod
    def _build_function_calls(tool_calls: list[ToolCall]) -> str:
        """Build function call blocks for assistant content."""
        parts: list[str] = []
        for tc in tool_calls:
            call_payload = json.dumps(
                {"name": tc.tool_name, "arguments": tc.arguments},
                ensure_ascii=False,
            )
            parts.append(f"{_FUNC_CALL_OPEN}\n{call_payload}\n{_FUNC_CALL_CLOSE}")
        return "\n".join(parts)

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Format a tool result as a MiniMax function message."""
        result_payload = json.dumps(
            {"name": result.tool_name, "result": result.result},
            ensure_ascii=False,
        )
        body = f"{_FUNC_RESPONSE_OPEN}\n{result_payload}\n{_FUNC_RESPONSE_CLOSE}"
        return f"{_IM_START}function\n{body}{_IM_END}"

    @staticmethod
    def _build_system_prompt(
        system_prompt: str | None,
        available_tools: list[ToolDefinition] | None,
        tool_call_mode: ToolCallMode,
    ) -> str | None:
        """Compose the system prompt, optionally appending tool definitions in XML."""
        sections: list[str] = []
        if system_prompt:
            sections.append(system_prompt)

        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            functions_xml_parts: list[str] = ["<functions>"]
            for t in available_tools:
                func_def = json.dumps(
                    {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.input_schema,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                functions_xml_parts.append(func_def)
            functions_xml_parts.append("</functions>")
            sections.append("\n".join(functions_xml_parts))

        return "\n\n".join(sections) if sections else None


# -- Auto-register ----------------------------------------------------------
get_template_registry().register(MiniMaxTemplate())
