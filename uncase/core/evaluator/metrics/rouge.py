"""ROUGE-L metric — structural coherence between conversation and seed flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema


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
    """Simple whitespace + punctuation tokenizer."""
    return text.lower().split()


def rouge_l_score(hypothesis: str, reference: str) -> float:
    """Compute ROUGE-L F1 score between hypothesis and reference texts.

    ROUGE-L uses the Longest Common Subsequence to measure structural
    similarity. F1 combines precision and recall with equal weight.

    Args:
        hypothesis: Generated/candidate text.
        reference: Reference/seed text.

    Returns:
        ROUGE-L F1 score in [0.0, 1.0].
    """
    hyp_tokens = _tokenize(hypothesis)
    ref_tokens = _tokenize(reference)

    if not hyp_tokens or not ref_tokens:
        return 0.0

    lcs = _lcs_length(hyp_tokens, ref_tokens)

    precision = lcs / len(hyp_tokens) if hyp_tokens else 0.0
    recall = lcs / len(ref_tokens) if ref_tokens else 0.0

    if precision + recall == 0:
        return 0.0

    f1 = (2 * precision * recall) / (precision + recall)
    return f1


class ROUGELMetric(BaseMetric):
    """ROUGE-L structural coherence metric.

    Measures how well the conversation's content preserves the structural
    patterns defined in the seed's expected flow and factual parameters.

    The score compares:
    - Conversation turns → seed's flujo_esperado (expected flow)
    - Conversation content → seed's contexto and restricciones

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

        Builds a reference from the seed's flow, context, and constraints,
        then compares it against the concatenated conversation content.
        """
        # Build reference from seed structure
        reference_parts: list[str] = []
        reference_parts.extend(seed.pasos_turnos.flujo_esperado)
        reference_parts.append(seed.parametros_factuales.contexto)
        reference_parts.extend(seed.parametros_factuales.restricciones)
        reference_parts.append(seed.objetivo)

        reference = " ".join(reference_parts)

        # Build hypothesis from conversation turns
        hypothesis_parts = [t.contenido for t in conversation.turnos if t.rol != "herramienta"]
        hypothesis = " ".join(hypothesis_parts)

        if not reference.strip() or not hypothesis.strip():
            return 0.0

        return rouge_l_score(hypothesis, reference)
