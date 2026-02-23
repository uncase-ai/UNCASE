"""Unit tests for the Harmony template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.base import ToolCallMode
from uncase.templates.harmony import HarmonyTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Harmony tokens and content."""
    template = HarmonyTemplate()
    output = template.render(basic_conversation)

    assert "<|START_OF_TURN_TOKEN|>" in output
    assert "<|END_OF_TURN_TOKEN|>" in output
    assert "<|CHATBOT_TOKEN|>" in output
    assert "<|USER_TOKEN|>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it appears in output."""
    template = HarmonyTemplate()
    prompt = "You are a fictional automotive advisor."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "<|SYSTEM_TOKEN|>" in output
    assert "fictional automotive advisor" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = HarmonyTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "Action:" in output
    assert "search_inventory" in output
    assert "<results>" in output
    assert "tc_fictional_001" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected Harmony tokens."""
    template = HarmonyTemplate()
    tokens = template.get_special_tokens()

    assert "<|START_OF_TURN_TOKEN|>" in tokens
    assert "<|END_OF_TURN_TOKEN|>" in tokens
    assert "<|SYSTEM_TOKEN|>" in tokens
    assert "<|USER_TOKEN|>" in tokens
    assert "<|CHATBOT_TOKEN|>" in tokens
    assert len(tokens) == 5


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = HarmonyTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "<|START_OF_TURN_TOKEN|>" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = HarmonyTemplate()

    assert template.name == "harmony"
    assert template.display_name == "Harmony (Cohere)"
    assert template.supports_tool_calls is True
