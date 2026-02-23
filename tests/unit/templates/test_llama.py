"""Unit tests for the Llama 3/4 template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.llama import LlamaChatTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Llama tokens and content."""
    template = LlamaChatTemplate()
    output = template.render(basic_conversation)

    assert "<|begin_of_text|>" in output
    assert "<|start_header_id|>" in output
    assert "<|end_header_id|>" in output
    assert "<|eot_id|>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output
    assert "<|start_header_id|>assistant<|end_header_id|>" in output
    assert "<|start_header_id|>user<|end_header_id|>" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears in output."""
    template = LlamaChatTemplate()
    prompt = "You are a fictional vehicle sales assistant."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "<|start_header_id|>system<|end_header_id|>" in output
    assert "fictional vehicle sales assistant" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = LlamaChatTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "<|python_tag|>" in output
    assert "search_inventory" in output
    assert "<|start_header_id|>ipython<|end_header_id|>" in output
    assert "tc_fictional_001" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected Llama tokens."""
    template = LlamaChatTemplate()
    tokens = template.get_special_tokens()

    assert "<|begin_of_text|>" in tokens
    assert "<|start_header_id|>" in tokens
    assert "<|end_header_id|>" in tokens
    assert "<|eot_id|>" in tokens
    assert "<|python_tag|>" in tokens
    assert len(tokens) == 5


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = LlamaChatTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "<|begin_of_text|>" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = LlamaChatTemplate()

    assert template.name == "llama"
    assert template.display_name == "Llama 3/4"
    assert template.supports_tool_calls is True
