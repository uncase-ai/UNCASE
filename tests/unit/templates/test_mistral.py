"""Unit tests for the Mistral template."""

from __future__ import annotations

from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.templates.base import ToolCallMode
from uncase.templates.mistral import MistralChatTemplate
from uncase.tools.schemas import ToolDefinition


def test_render_basic(basic_conversation: Conversation) -> None:
    """Render a simple conversation; verify Mistral tokens and content."""
    template = MistralChatTemplate()
    output = template.render(basic_conversation)

    assert "[INST]" in output
    assert "[/INST]" in output
    assert "</s>" in output
    assert "Buenos dias" in output
    assert "vehiculos electricos" in output


def test_render_with_system_prompt() -> None:
    """Render with a custom system prompt; verify it appears in output.

    The Mistral template only injects the system prompt into the first
    [INST] block when the conversation starts with a user turn, so we
    use a user-first conversation for this test.
    """
    template = MistralChatTemplate()
    prompt = "You are a fictional dealership assistant."
    conversation = Conversation(
        seed_id="seed_mistral_sys_001",
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="cliente", contenido="Tienen vehiculos electricos?"),
            ConversationTurn(turno=2, rol="vendedor", contenido="Si, tenemos varios modelos."),
        ],
        es_sintetica=True,
    )
    output = template.render(conversation, system_prompt=prompt)

    assert "fictional dealership assistant" in output
    assert "[INST]" in output


def test_render_with_tools(
    conversation_with_tools: Conversation,
    sample_tool_definitions: list[ToolDefinition],
) -> None:
    """Render with tool_calls and tool_results in INLINE mode."""
    template = MistralChatTemplate()
    output = template.render(
        conversation_with_tools,
        tool_call_mode=ToolCallMode.INLINE,
        available_tools=sample_tool_definitions,
    )

    assert "[TOOL_CALLS]" in output
    assert "search_inventory" in output
    assert "[TOOL_RESULTS]" in output
    assert "tc_fictional_001" in output


def test_special_tokens() -> None:
    """Verify get_special_tokens returns expected Mistral tokens."""
    template = MistralChatTemplate()
    tokens = template.get_special_tokens()

    assert "[INST]" in tokens
    assert "[/INST]" in tokens
    assert "[TOOL_CALLS]" in tokens
    assert "[TOOL_RESULTS]" in tokens
    assert "[/TOOL_RESULTS]" in tokens
    assert len(tokens) == 5


def test_render_batch(batch_conversations: list[Conversation]) -> None:
    """Render multiple conversations; verify count matches."""
    template = MistralChatTemplate()
    results = template.render_batch(batch_conversations)

    assert len(results) == 3
    for r in results:
        assert "[INST]" in r


def test_properties() -> None:
    """Check name, display_name, and supports_tool_calls properties."""
    template = MistralChatTemplate()

    assert template.name == "mistral"
    assert template.display_name == "Mistral"
    assert template.supports_tool_calls is True
