"""Memorization metric — extraction attack simulation.

Measures whether a generated conversation reproduces seed data verbatim,
which would indicate memorization rather than genuine synthesis.

The metric computes the longest common substring (LCS) between each
conversation turn and the seed reference text, then returns the maximum
overlap ratio across all turns:

    overlap_ratio(turn) = len(LCS(turn, seed_text)) / len(turn)
                          if len(LCS) >= MIN_LCS_LENGTH else 0.0
    score = max(overlap_ratio for each turn)

Common substrings shorter than ``MIN_LCS_LENGTH`` characters (~10 words)
are ignored as incidental word overlap.  Only contiguous verbatim copies
of 50+ characters count as memorization.

A score < 0.01 (1%) passes the quality gate.  Any higher value means
the generator is copying seed content instead of producing original text.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema

# Minimum LCS length (in characters) to consider as memorization.
# Shorter common substrings are treated as incidental overlap from
# common words and phrases in the language.  50 characters is roughly
# 8-12 words — enough to indicate deliberate copying.
MIN_LCS_LENGTH: Final[int] = 50


def _longest_common_substring_length(a: str, b: str) -> int:
    """Return the length of the longest common substring between *a* and *b*.

    Uses a rolling-row dynamic programming approach (O(n*m) time, O(min(n,m))
    space) which is efficient enough for typical conversation lengths.
    """
    if not a or not b:
        return 0

    # Ensure `b` is the shorter string to minimise memory usage.
    if len(a) < len(b):
        a, b = b, a

    prev = [0] * (len(b) + 1)
    best = 0

    for ch_a in a:
        curr = [0] * (len(b) + 1)
        for j, ch_b in enumerate(b):
            if ch_a == ch_b:
                curr[j + 1] = prev[j] + 1
                if curr[j + 1] > best:
                    best = curr[j + 1]
            # else: curr[j+1] stays 0
        prev = curr

    return best


def _extract_seed_text(seed: SeedSchema) -> str:
    """Build a single reference string from the seed's factual parameters and turn flow.

    This is the text against which we check for memorization.  It combines:
    - ``parametros_factuales.contexto``
    - ``parametros_factuales.restricciones`` (joined)
    - ``parametros_factuales.metadata`` values
    - ``pasos_turnos.flujo_esperado`` (joined)
    - ``objetivo``
    """
    parts: list[str] = []

    pf = seed.parametros_factuales
    parts.append(pf.contexto)
    parts.extend(pf.restricciones)
    parts.extend(pf.metadata.values())

    parts.extend(seed.pasos_turnos.flujo_esperado)
    parts.append(seed.objetivo)

    return " ".join(parts).lower()


def _extract_tool_call_text(seed: SeedSchema, conversation: Conversation) -> str:
    """Extract stringified tool-call arguments from the conversation for comparison.

    Tool-call arguments are serialised to a single string so we can check
    whether seed data leaked through tool invocations.
    """
    parts: list[str] = []
    for turn in conversation.turnos:
        if turn.tool_calls:
            for tc in turn.tool_calls:
                if tc.arguments:
                    parts.append(json.dumps(tc.arguments, ensure_ascii=False, sort_keys=True))
    return " ".join(parts).lower()


def _overlap_ratio(text: str, reference: str, min_length: int = MIN_LCS_LENGTH) -> float:
    """Return the overlap ratio of *text* against *reference*.

    Only common substrings of at least *min_length* characters are
    counted.  Shorter matches are treated as incidental word overlap
    and contribute 0.0 to the score.
    """
    if not text or not reference:
        return 0.0
    lcs_len = _longest_common_substring_length(text, reference)
    if lcs_len < min_length:
        return 0.0
    return lcs_len / len(text)


def compute_memorization_score(conversation: Conversation, seed: SeedSchema) -> float:
    """Compute the memorization score for a conversation against its seed.

    Returns a value in [0.0, 1.0] representing the maximum fraction of any
    single turn that is a verbatim copy of seed text.  Only common substrings
    of at least ``MIN_LCS_LENGTH`` characters are considered.

    Args:
        conversation: The generated conversation to evaluate.
        seed: The origin seed to compare against.

    Returns:
        Maximum overlap ratio across all turns (0.0 = no memorization).
    """
    seed_text = _extract_seed_text(seed)

    if not seed_text:
        return 0.0

    max_ratio = 0.0

    # Check each conversation turn's content against seed text.
    for turn in conversation.turnos:
        turn_text = turn.contenido.lower()
        ratio = _overlap_ratio(turn_text, seed_text)
        if ratio > max_ratio:
            max_ratio = ratio

    # Also check tool-call arguments for verbatim seed leakage.
    tool_text = _extract_tool_call_text(seed, conversation)
    if tool_text:
        ratio = _overlap_ratio(tool_text, seed_text)
        if ratio > max_ratio:
            max_ratio = ratio

    return min(1.0, max_ratio)


class MemorizationMetric(BaseMetric):
    """Extraction-attack memorization metric.

    Target: < 0.01 (less than 1% verbatim overlap with seed).
    Any score >= 0.01 indicates problematic memorization and causes
    the composite quality gate to fail unconditionally.

    This is a lightweight, deterministic check that does NOT require an
    LLM.  It uses longest-common-substring analysis to detect whether
    the generator copied seed content into the output conversation.
    """

    @property
    def name(self) -> str:
        return "memorizacion"

    @property
    def display_name(self) -> str:
        return "Memorization (Extraction Attack)"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute the memorization score.

        Returns:
            Ratio in [0.0, 1.0]. Lower is better; < 0.01 passes.
        """
        return compute_memorization_score(conversation, seed)
