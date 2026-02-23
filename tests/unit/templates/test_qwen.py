"""Unit tests for the Qwen 3 template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.qwen import QwenChatTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Qwen tokens and content."""
    template = QwenChatTemplate()
    output = template.render(basic_conversation)

    assert "<|im_start|>" in output
    assert "<|im_end|>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output
    assert "<|im_start|>assistant" in output
    assert "<|im_start|>user" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears in output."""
    template = QwenChatTemplate()
    prompt = "You are a fictional sales chatbot."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "<|im_start|>system" in output
    assert "fictional sales chatbot" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = QwenChatTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "<tool_call>" in output
    assert "</tool_call>" in output
    assert "search_inventory" in output
    assert "<tool_response>" in output
    assert "</tool_response>" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected Qwen tokens."""
    template = QwenChatTemplate()
    tokens = template.get_special_tokens()

    assert "<|im_start|>" in tokens
    assert "<|im_end|>" in tokens
    assert "<tool_call>" in tokens
    assert "</tool_call>" in tokens
    assert "<tool_response>" in tokens
    assert "</tool_response>" in tokens
    assert len(tokens) == 6


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = QwenChatTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "<|im_start|>" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = QwenChatTemplate()

    assert template.name == "qwen"
    assert template.display_name == "Qwen 3"
    assert template.supports_tool_calls is True
