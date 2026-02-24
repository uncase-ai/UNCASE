"""Tests for lexical diversity (TTR) metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_seed
from uncase.core.evaluator.metrics.diversity import (
    LexicalDiversityMetric,
    _extract_tokens,
    type_token_ratio,
)
from uncase.schemas.conversation import ConversationTurn


class TestTypeTokenRatio:
    """Tests for the TTR calculation."""

    def test_all_unique_tokens(self) -> None:
        tokens = ["alpha", "beta", "gamma", "delta", "epsilon"]
        assert type_token_ratio(tokens) == 1.0

    def test_all_identical_tokens(self) -> None:
        tokens = ["repeat"] * 10
        ratio = type_token_ratio(tokens)
        assert ratio == 0.1  # 1 unique / 10 total

    def test_empty_tokens(self) -> None:
        assert type_token_ratio([]) == 0.0

    def test_mixed_tokens(self) -> None:
        tokens = ["hello", "world", "hello", "there", "world"]
        ratio = type_token_ratio(tokens)
        assert ratio == 3 / 5  # 3 unique / 5 total

    def test_long_text_uses_windowed_ttr(self) -> None:
        # > 50 tokens triggers MATTR
        tokens = [f"word_{i}" for i in range(100)]
        ratio = type_token_ratio(tokens)
        assert ratio == 1.0  # All unique, so MATTR = 1.0

    def test_long_repetitive_text(self) -> None:
        tokens = ["the", "quick", "brown", "fox"] * 20  # 80 tokens, 4 unique
        ratio = type_token_ratio(tokens)
        assert ratio < 0.3  # Very repetitive


class TestExtractTokens:
    """Tests for token extraction."""

    def test_basic_extraction(self) -> None:
        tokens = _extract_tokens("Hello World Test")
        assert tokens == ["hello", "world", "test"]

    def test_filters_single_chars(self) -> None:
        tokens = _extract_tokens("a b c hello world")
        assert "hello" in tokens
        assert "world" in tokens
        # Single chars may be included since min length is > 1
        assert "a" not in tokens

    def test_handles_punctuation(self) -> None:
        tokens = _extract_tokens("hello, world! how are you?")
        assert "hello" in tokens
        assert "world" in tokens


class TestLexicalDiversityMetric:
    """Tests for the LexicalDiversityMetric class."""

    def test_name(self) -> None:
        metric = LexicalDiversityMetric()
        assert metric.name == "diversidad_lexica"

    def test_high_diversity_conversation(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Bienvenido al concesionario de vehiculos premium"),
                ConversationTurn(turno=2, rol="cliente", contenido="Busco informacion sobre financiamiento automotriz"),
                ConversationTurn(
                    turno=3, rol="vendedor", contenido="Ofrecemos diferentes planes crediticios con tasas competitivas"
                ),
            ],
        )
        metric = LexicalDiversityMetric()
        score = metric.compute(conversation, seed)
        assert score > 0.5

    def test_low_diversity_conversation(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="hola hola hola hola hola hola"),
                ConversationTurn(turno=2, rol="cliente", contenido="hola hola hola hola hola hola"),
                ConversationTurn(turno=3, rol="vendedor", contenido="hola hola hola hola hola hola"),
            ],
        )
        metric = LexicalDiversityMetric()
        score = metric.compute(conversation, seed)
        assert score < 0.3

    def test_excludes_tool_turns(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Diverso vocabulario aqui"),
                ConversationTurn(turno=2, rol="herramienta", contenido="resultado resultado resultado"),
                ConversationTurn(turno=3, rol="vendedor", contenido="Gracias por la informacion"),
            ],
        )
        metric = LexicalDiversityMetric()
        score = metric.compute(conversation, seed)
        # Tool turn should be excluded, so diversity is based only on vendedor turns
        assert score > 0.3

    def test_returns_bounded_score(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = LexicalDiversityMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0
