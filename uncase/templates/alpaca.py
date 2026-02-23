"""Alpaca chat template implementation.

Renders conversations in the Alpaca instruction-response format used
by Stanford Alpaca and many derivative fine-tuned models.

Format::

    ### Instruction:
    {system_prompt}

    {user_content}

    ### Response:
    {assistant_content}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.templates import get_template_registry
from uncase.templates.base import BaseChatTemplate, ToolCallMode

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolDefinition

# Roles that map to assistant / response
_ASSISTANT_ROLES = {"vendedor", "asistente"}
# Roles that map to user / instruction
_USER_ROLES = {"cliente", "usuario"}
# Roles that map to system (prefix for instruction)
_SYSTEM_ROLES = {"sistema"}


class AlpacaTemplate(BaseChatTemplate):
    """Alpaca template for simple instruction-response fine-tuning.

    Produces a straightforward ``### Instruction:`` / ``### Response:``
    format.  Does **not** support tool calls; any tool-related turns are
    rendered as plain text.
    """

    @property
    def name(self) -> str:
        return "alpaca"

    @property
    def display_name(self) -> str:
        return "Alpaca"

    @property
    def supports_tool_calls(self) -> bool:
        return False

    def get_special_tokens(self) -> list[str]:
        """Return Alpaca special tokens (none — plain text format)."""
        return []

    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a conversation in Alpaca format.

        Multi-turn conversations alternate between ``### Instruction:`` and
        ``### Response:`` blocks.  System messages are prepended as a
        prefix to the first ``### Instruction:`` section.

        Parameters
        ----------
        conversation:
            The conversation to render.
        tool_call_mode:
            Ignored — Alpaca does not support tool calls.
        system_prompt:
            Optional system prompt prepended to the instruction section.
        available_tools:
            Ignored — Alpaca does not support tool definitions.

        Returns
        -------
        str
            The fully rendered Alpaca prompt string.
        """
        parts: list[str] = []
        system_prefix: str | None = system_prompt

        for turn in conversation.turnos:
            role = turn.rol

            if role in _SYSTEM_ROLES:
                # Accumulate system content as prefix for next instruction
                system_prefix = f"{system_prefix}\n\n{turn.contenido}" if system_prefix else turn.contenido
                continue

            if role in _USER_ROLES:
                instruction_content = turn.contenido
                if system_prefix:
                    instruction_content = f"{system_prefix}\n\n{instruction_content}"
                    system_prefix = None
                parts.append(f"### Instruction:\n{instruction_content}")

            elif role in _ASSISTANT_ROLES:
                parts.append(f"### Response:\n{turn.contenido}")

            else:
                # Unknown roles rendered as instruction turns
                parts.append(f"### Instruction:\n{turn.contenido}")

        return "\n\n".join(parts)


# -- Auto-register ----------------------------------------------------------
get_template_registry().register(AlpacaTemplate())
