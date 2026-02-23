"""Unit tests for the ChatML template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.chatml import ChatMLTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation without tools; verify ChatML tokens and content."""
    template = ChatMLTemplate()
    output = template.render(basic_conversation)

    assert "<|im_start|>" in output
    assert "<|im_end|>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output
    assert "<|im_start|>assistant" in output
    assert "<|im_start|>user" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears in output."""
    template = ChatMLTemplate()
    prompt = "You are a fictional automotive assistant."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "<|im_start|>system" in output
    assert "fictional automotive assistant" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = ChatMLTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "<tool_call>" in output
    assert "search_inventory" in output
    assert "<tool_response>" in output
    assert "tc_fictional_001" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected ChatML tokens."""
    template = ChatMLTemplate()
    tokens = template.get_special_tokens()

    assert "<|im_start|>" in tokens
    assert "<|im_end|>" in tokens
    assert len(tokens) == 2


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = ChatMLTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "<|im_start|>" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = ChatMLTemplate()

    assert template.name == "chatml"
    assert template.display_name == "ChatML"
    assert template.supports_tool_calls is True
