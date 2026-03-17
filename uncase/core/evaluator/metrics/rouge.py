"""ROUGE-L metric — structural coherence between conversation and seed flow."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics._stopwords import content_tokens
from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema

_TOKEN_RE = re.compile(r"\b\w+\b")


def _lcs_length(seq_a: list[str], seq_b: list[str]) -> int:
    """Compute the length of the Longest Common Subsequence between two sequences.

    Uses O(min(m,n)) space with the standard DP approach.
    """
    if not seq_a or not seq_b:
        return 0

    # Ensure seq_b is the shorter one for space optimization
    if len(seq_a) < len(seq_b):
        seq_a, seq_b = seq_b, seq_a

    m, n = len(seq_a), len(seq_b)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq_a[i - 1] == seq_b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)

    return prev[n]


def _tokenize(text: str) -> list[str]:
    """Tokenize text stripping punctuation via word-boundary regex."""
    return _TOKEN_RE.findall(text.lower())


def rouge_l_score(hypothesis: str, reference: str) -> float:
    """Compute ROUGE-L F1 score between hypothesis and reference texts.

    Tokenizes with ``\\b\\w+\\b`` (punctuation-safe), filters stopwords via
    :func:`content_tokens`, computes LCS-based F1, and applies a length
    normalization penalty when hypothesis and reference differ significantly
    in length.

    Args:
        hypothesis: Generated/candidate text.
        reference: Reference/seed text.

    Returns:
        ROUGE-L F1 score in [0.0, 1.0].
    """
    hyp_tokens = content_tokens(hypothesis)
    ref_tokens = content_tokens(reference)

    if not hyp_tokens or not ref_tokens:
        return 0.0

    lcs = _lcs_length(hyp_tokens, ref_tokens)

    precision = lcs / len(hyp_tokens)
    recall = lcs / len(ref_tokens)

    if precision + recall == 0:
        return 0.0

    # Use recall-weighted F-beta (β=2) instead of standard F1.
    # For seed-conversation comparison, recall (how much of the seed's
    # content appears in the conversation) matters more than precision
    # (what fraction of the conversation matches the seed).
    beta = 2.0
    beta_sq = beta * beta
    f_beta = ((1 + beta_sq) * precision * recall) / (beta_sq * precision + recall)

    return f_beta


class ROUGELMetric(BaseMetric):
    """ROUGE-L structural coherence metric.

    Measures how well the conversation's content preserves the structural
    patterns defined in the seed's expected flow and factual parameters.

    Builds a rich reference from the seed including role descriptions, full
    objective, context, constraints, expanded flow steps, and tone. Then
    compares it against the conversation content using content-token filtered
    ROUGE-L with length normalization.

    A high ROUGE-L means the conversation follows the seed's structure
    closely. Too high (>0.95) may indicate memorization.
    """

    @property
    def name(self) -> str:
        return "rouge_l"

    @property
    def display_name(self) -> str:
        return "ROUGE-L Structural Coherence"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute ROUGE-L between conversation and seed reference text.

        Builds a rich reference from the seed's roles, objective, context,
        constraints, expanded flow steps, and tone, then compares it against
        the concatenated conversation content.
        """
        # Build a rich reference from all available seed metadata
        reference_parts: list[str] = []

        # Role descriptions — richer than bare role names
        for role, description in seed.descripcion_roles.items():
            reference_parts.append(f"{role} {description}")

        # Full objective text
        reference_parts.append(seed.objetivo)

        # Context text
        reference_parts.append(seed.parametros_factuales.contexto)

        # All constraints
        reference_parts.extend(seed.parametros_factuales.restricciones)

        # Flow steps — expanded with spaces replacing underscores
        for step in seed.pasos_turnos.flujo_esperado:
            reference_parts.append(step.replace("_", " "))

        # Tone description
        reference_parts.append(f"tono {seed.tono}")

        reference = " ".join(reference_parts)

        # Build hypothesis from conversation turns
        hypothesis_parts = [t.contenido for t in conversation.turnos if t.rol != "herramienta"]
        hypothesis = " ".join(hypothesis_parts)

        if not reference.strip() or not hypothesis.strip():
            return 0.0

        return rouge_l_score(hypothesis, reference)
