"""Abstract base class for chat templates.

Defines the contract that every chat template implementation must follow
in order to render ``Conversation`` objects into prompt strings suitable
for LLM fine-tuning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.tools.schemas import ToolDefinition


class ToolCallMode(StrEnum):
    """How to handle tool calls in template rendering."""

    NONE = "none"
    INLINE = "inline"


class BaseChatTemplate(ABC):
    """Abstract base for all UNCASE chat templates.

    Subclasses must implement :pymethod:`render`, :pymethod:`get_special_tokens`,
    and the ``name``, ``display_name``, and ``supports_tool_calls`` properties.

    Usage::

        class ChatMLTemplate(BaseChatTemplate):
            @property
            def name(self) -> str:
                return "chatml"
            ...

        template = ChatMLTemplate()
        text = template.render(conversation)
    """

    # -- Abstract properties ------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique snake_case identifier for this template."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name shown in UI and logs."""

    @property
    @abstractmethod
    def supports_tool_calls(self) -> bool:
        """Whether this template can render tool-call turns."""

    # -- Abstract methods ---------------------------------------------------

    @abstractmethod
    def render(
        self,
        conversation: Conversation,
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> str:
        """Render a single conversation into a prompt string.

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
            The fully rendered prompt string.
        """

    @abstractmethod
    def get_special_tokens(self) -> list[str]:
        """Return all special tokens used by this template.

        Returns
        -------
        list[str]
            Ordered list of special tokens (e.g. ``["<|im_start|>", "<|im_end|>"]``).
        """

    # -- Concrete methods ---------------------------------------------------

    def render_batch(
        self,
        conversations: list[Conversation],
        tool_call_mode: ToolCallMode = ToolCallMode.NONE,
        system_prompt: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
    ) -> list[str]:
        """Render multiple conversations into prompt strings.

        Parameters
        ----------
        conversations:
            List of conversations to render.
        tool_call_mode:
            How to handle tool calls (applied to every conversation).
        system_prompt:
            Optional system prompt prepended to each conversation.
        available_tools:
            Tool definitions to include when *tool_call_mode* is ``INLINE``.

        Returns
        -------
        list[str]
            Rendered prompt strings, one per conversation.
        """
        return [
            self.render(
                conversation=conv,
                tool_call_mode=tool_call_mode,
                system_prompt=system_prompt,
                available_tools=available_tools,
            )
            for conv in conversations
        ]
