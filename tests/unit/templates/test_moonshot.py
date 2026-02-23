"""Unit tests for the Kimi/Moonshot template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.moonshot import MoonshotTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Moonshot tokens and content."""
    template = MoonshotTemplate()
    output = template.render(basic_conversation)

    assert "<|im_assistant|>" in output
    assert "<|im_user|>" in output
    assert "<|im_end|>" in output
    assert "<|im_middle|>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears in output."""
    template = MoonshotTemplate()
    prompt = "You are a fictional Kimi-powered assistant."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "<|im_system|>" in output
    assert "fictional Kimi-powered assistant" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = MoonshotTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "<tool_call>" in output
    assert "</tool_call>" in output
    assert "search_inventory" in output
    assert "<|im_tool|>" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected Moonshot tokens."""
    template = MoonshotTemplate()
    tokens = template.get_special_tokens()

    assert "<|im_system|>" in tokens
    assert "<|im_user|>" in tokens
    assert "<|im_assistant|>" in tokens
    assert "<|im_middle|>" in tokens
    assert "<|im_tool|>" in tokens
    assert "<|im_end|>" in tokens
    assert len(tokens) == 6


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = MoonshotTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "<|im_assistant|>" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = MoonshotTemplate()

    assert template.name == "moonshot"
    assert template.display_name == "Kimi (Moonshot)"
    assert template.supports_tool_calls is True
