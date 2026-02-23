"""OpenAI API JSON chat template implementation.

Renders conversations as valid JSON matching the OpenAI Chat Completions
API message format, suitable for fine-tuning datasets and API-compatible
tooling.

Format::

    {"messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]}

Tool calls follow the full OpenAI API format with ``tool_calls`` arrays
and ``tool`` role messages.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolCall, ToolDefinition, ToolResult

# Role mapping from UNCASE conversation roles to OpenAI API roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "tool",
}


class OpenAIAPITemplate(BaseChatTemplate):
    """OpenAI API JSON template for Chat Completions format.

    Outputs valid JSON using ``json.dumps()`` with ``ensure_ascii=False``
    and ``indent=2``.  Tool calls are rendered in the full OpenAI API format
    with ``tool_calls`` arrays on assistant messages and ``tool`` role messages
    for results.  Available tools are placed in a top-level ``tools`` key.
    """

    @property
    def name(self) -> str:
        return "openai_api"

    @property
    def display_name(self) -> str:
        return "OpenAI API"

    @property
    def supports_tool_calls(self) -> bool:
        return True

    def get_special_tokens(self) -> list[str]:
        """Return special tokens (none for JSON format)."""
        return []

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in OpenAI API JSON format.

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
            A valid JSON string representing the conversation.
        """
        messages: list[dict[str, Any]] = []

        # -- System prompt --------------------------------------------------
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # -- Conversation turns ---------------------------------------------
        for turn in conversation.turnos:
            role = _ROLE_MAP.get(turn.rol, turn.rol)

            # Tool-result turns rendered as tool messages
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_results and role in ("tool", "herramienta"):
                for result in turn.tool_results:
                    messages.append(self._build_tool_result_message(result))
                continue

            # Assistant turn with tool calls
            if tool_call_mode == ToolCallMode.INLINE and turn.tool_calls and role == "assistant":
                messages.append(self._build_assistant_tool_call_message(turn.tool_calls))
                continue

            # Regular message
            messages.append({"role": role, "content": turn.contenido})

        # -- Build output object --------------------------------------------
        output: dict[str, Any] = {"messages": messages}

        # Add tools definitions at top level when available
        if tool_call_mode == ToolCallMode.INLINE and available_tools:
            output["tools"] = [self._build_tool_definition(t) for t in available_tools]

        return json.dumps(output, ensure_ascii=False, indent=2)

    # -- Private helpers ----------------------------------------------------

    @staticmethod
    def _build_assistant_tool_call_message(
        tool_calls: list[ToolCall],
    ) -> dict[str, Any]:
        """Build an assistant message with OpenAI-format tool calls."""
        formatted_calls: list[dict[str, Any]] = []
        for tc in tool_calls:
            formatted_calls.append(
                {
                    "id": tc.tool_call_id,
                    "type": "function",
                    "function": {
                        "name": tc.tool_name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                    },
                }
            )
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": formatted_calls,
        }

    @staticmethod
    def _build_tool_result_message(result: ToolResult) -> dict[str, Any]:
        """Build a tool result message in OpenAI API format."""
        content = result.result if isinstance(result.result, str) else json.dumps(result.result, ensure_ascii=False)
        return {
            "role": "tool",
            "tool_call_id": result.tool_call_id,
            "content": content,
        }

    @staticmethod
    def _build_tool_definition(tool: ToolDefinition) -> dict[str, Any]:
        """Build an OpenAI API tool definition object."""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            },
        }


# -- Auto-register ----------------------------------------------------------
get_template_registry().register(OpenAIAPITemplate())
