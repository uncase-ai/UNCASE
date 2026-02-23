"""Unit tests for the Alpaca template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation
from uncase.templates.alpaca import AlpacaTemplate


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Alpaca instruction/response blocks."""
    template = AlpacaTemplate()
    output = template.render(basic_conversation)

    assert "### Instruction:" in output or "### Response:" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output
    # vendedor maps to Response, cliente maps to Instruction
    assert "### Response:" in output
    assert "### Instruction:" in output


def test_render_with_system_prompt(basic_conversation: Conversation) -> None:
    """Render with a custom system prompt; verify it is prepended to the first instruction."""
    template = AlpacaTemplate()
    prompt = "You are a fictional Alpaca-style assistant."
    output = template.render(basic_conversation, system_prompt=prompt)

    assert "fictional Alpaca-style assistant" in output
    # System prompt should appear before the first instruction content
    system_pos = output.index("fictional Alpaca-style assistant")
    instruction_pos = output.index("### Instruction:")
    # System prompt is inside the first Instruction block
    assert system_pos > instruction_pos or "fictional Alpaca-style assistant" in output.split("### Instruction:")[1]


def test_special_tokens() -> None:
    """Verify get_special_tokens returns empty list (plain text format)."""
    template = AlpacaTemplate()
    tokens = template.get_special_tokens()

    assert tokens == []


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = AlpacaTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "### Response:" in r or "### Instruction:" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = AlpacaTemplate()

    assert template.name == "alpaca"
    assert template.display_name == "Alpaca"
    assert template.supports_tool_calls is False
