"""Unit tests for the OpenAI API template."""

from __future__ import annotations

import json

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.openai_api import OpenAIAPITemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify valid JSON with messages array."""
    template = OpenAIAPITemplate()
    output = template.render(basic_conversation)

    data = json.loads(output)
    assert "messages" in data
    messages = data["messages"]
    assert len(messages) == 3

    roles = [m["role"] for m in messages]
    assert "assistant" in roles
    assert "user" in roles

    contents = " ".join(m["content"] for m in messages)
    assert "Buenos dias" in contents
    assert "vehiculos electricos" in contents


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears as a system message."""
    template = OpenAIAPITemplate()
    prompt = "You are a fictional OpenAI-compatible assistant."
    output = template.render(basic_conversation, system_prompt=prompt)

    data = json.loads(output)
    messages = data["messages"]
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert "fictional OpenAI-compatible assistant" in system_msgs[0]["content"]


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = OpenAIAPITemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    data = json.loads(output)
    assert "tools" in data
    assert data["tools"][0]["function"]["name"] == "search_inventory"

    messages = data["messages"]
    # Find assistant message with tool_calls
    tool_call_msgs = [m for m in messages if "tool_calls" in m]
    assert len(tool_call_msgs) >= 1
    assert tool_call_msgs[0]["tool_calls"][0]["function"]["name"] == "search_inventory"

    # Find tool result message
    tool_result_msgs = [m for m in messages if m["role"] == "tool"]
    assert len(tool_result_msgs) >= 1
    assert tool_result_msgs[0]["tool_call_id"] == "tc_fictional_001"


def test_special_tokens() -> None:
    """Verify get_special_tokens returns empty list (JSON format has no special tokens)."""
    template = OpenAIAPITemplate()
    tokens = template.get_special_tokens()

    assert tokens == []


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches and all are valid JSON."""
    template = OpenAIAPITemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        data = json.loads(r)
        assert "messages" in data


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = OpenAIAPITemplate()

    assert template.name == "openai_api"
    assert template.display_name == "OpenAI API"
    assert template.supports_tool_calls is True
