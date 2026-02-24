"""Lexical diversity metric — Type-Token Ratio (TTR)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema


def _extract_tokens(text: str) -> list[str]:
    """Extract word tokens from text, normalizing to lowercase."""
    return [w.lower() for w in re.findall(r"\b\w+\b", text) if len(w) > 1]


def type_token_ratio(tokens: list[str]) -> float:
    """Compute the Type-Token Ratio (unique types / total tokens).

    For long texts, TTR tends to decrease naturally (Heaps' law).
    We use a windowed approach: compute TTR over windows of 50 tokens
    and average them. This gives a length-independent measure.

    Args:
        tokens: List of word tokens.

    Returns:
        TTR score in [0.0, 1.0].
    """
    if not tokens:
        return 0.0

    total = len(tokens)

    # For short texts, use plain TTR
    if total <= 50:
        unique = len(set(tokens))
        return unique / total

    # Windowed TTR (MATTR - Moving Average Type-Token Ratio)
    window_size = 50
    ratios: list[float] = []

    for i in range(total - window_size + 1):
        window = tokens[i : i + window_size]
        unique = len(set(window))
        ratios.append(unique / window_size)

    return sum(ratios) / len(ratios)


class LexicalDiversityMetric(BaseMetric):
    """Lexical diversity via Type-Token Ratio (TTR).

    Measures vocabulary richness in the conversation. A higher TTR
    indicates more diverse word usage, which is desirable for training
    data to avoid repetitive patterns.

    Uses Moving Average TTR (MATTR) for length independence.
    """

    @property
    def name(self) -> str:
        return "diversidad_lexica"

    @property
    def display_name(self) -> str:
        return "Lexical Diversity (TTR)"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute lexical diversity of the conversation content."""
        # Concatenate all turn content (excluding tool results which are
        # structured data, not natural language)
        text_parts = [t.contenido for t in conversation.turnos if t.rol != "herramienta"]

        full_text = " ".join(text_parts)
        tokens = _extract_tokens(full_text)

        return type_token_ratio(tokens)
