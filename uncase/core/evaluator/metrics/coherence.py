"""Dialog coherence metric — inter-turn consistency evaluation."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics._stopwords import content_token_set
from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation, ConversationTurn
    from uncase.schemas.seed import SeedSchema


def _jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _score_jaccard(avg_sim: float) -> float:
    """Map average Jaccard similarity to a coherence score.

    Uses an asymmetric Gaussian centered at ``peak=0.15`` — the
    empirically healthy overlap range for dialog.  Below the peak a
    tighter sigma (0.08) penalizes topic jumping; above it a wider
    sigma (0.25) gives a gentler penalty for mild repetition.

    With stopword-filtered content tokens, adjacent-turn Jaccard is
    typically 0.02-0.10 for good dialog (each turn discusses different
    specifics with some domain vocabulary overlap).

    Approximate outputs::

        0.00 -> 0.00    (no continuity)
        0.03 -> ~0.75   (sparse but present overlap)
        0.07 -> 1.00    (sweet spot for content tokens)
        0.15 -> ~0.90   (moderate overlap, still ok)
        0.30 -> ~0.68   (some repetition)
        0.50 -> ~0.42   (notable repetition)
        0.80 -> ~0.14   (excessive repetition)
    """
    if avg_sim <= 0.0:
        return 0.0
    # Peak at 0.07 — empirically correct for content-token Jaccard in dialog.
    # Left sigma tighter (penalizes topic jumping), right sigma wider
    # (repetition penalty is gentler since domain vocabulary overlap is normal).
    peak = 0.07
    sigma = 0.065 if avg_sim <= peak else 0.30
    return math.exp(-((avg_sim - peak) ** 2) / (2 * sigma**2))


class DialogCoherenceMetric(BaseMetric):
    """Dialog coherence metric measuring inter-turn consistency.

    Evaluates multiple dimensions of dialog quality:

    1. **Turn-pair coherence** — Adjacent turns share topical continuity
       (measured via token overlap/Jaccard similarity).
    2. **Role alternation** — Proper turn-taking between participants
       (not the same role speaking multiple times consecutively without
       reason).
    3. **Progressive flow** — The conversation progresses (no exact
       duplicate turns, content evolves over time).
    4. **Referential consistency** — Later turns reference or build upon
       earlier content (measured by backward reference overlap).

    Final score = weighted combination of sub-scores.
    """

    @property
    def name(self) -> str:
        return "coherencia_dialogica"

    @property
    def display_name(self) -> str:
        return "Dialog Coherence"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute dialog coherence score."""
        turns = conversation.turnos
        if len(turns) < 2:
            return 1.0  # Single-turn can't be incoherent

        sub_scores: list[tuple[float, float]] = []

        sub_scores.append((self._turn_pair_coherence(turns), 0.35))
        sub_scores.append((self._role_alternation(turns, seed), 0.25))
        sub_scores.append((self._progressive_flow(turns), 0.20))
        sub_scores.append((self._referential_consistency(turns), 0.20))

        total_weight = sum(w for _, w in sub_scores)
        weighted_sum = sum(s * w for s, w in sub_scores)
        return weighted_sum / total_weight

    def _turn_pair_coherence(self, turns: list[ConversationTurn]) -> float:
        """Measure topical continuity between adjacent turns.

        Uses content tokens (stopwords filtered) for Jaccard similarity,
        then maps through an asymmetric Gaussian centered at 0.15 — the
        empirically healthy overlap range for dialog.  Left side (topic
        jumping) is penalized more sharply than right side (mild repetition).
        """
        if len(turns) < 2:
            return 1.0

        similarities: list[float] = []
        for i in range(len(turns) - 1):
            tokens_a = content_token_set(turns[i].contenido)
            tokens_b = content_token_set(turns[i + 1].contenido)
            sim = _jaccard_similarity(tokens_a, tokens_b)
            similarities.append(sim)

        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
        return _score_jaccard(avg_sim)

    def _role_alternation(self, turns: list[ConversationTurn], seed: SeedSchema) -> float:
        """Measure proper turn-taking between roles."""
        if len(turns) < 2:
            return 1.0

        # Filter out tool/system turns for alternation check
        dialog_turns = [t for t in turns if t.rol not in {"herramienta", "tool", "system"}]

        if len(dialog_turns) < 2:
            return 1.0

        alternations = 0
        for i in range(len(dialog_turns) - 1):
            if dialog_turns[i].rol != dialog_turns[i + 1].rol:
                alternations += 1

        max_alternations = len(dialog_turns) - 1
        return alternations / max_alternations if max_alternations > 0 else 1.0

    def _progressive_flow(self, turns: list[ConversationTurn]) -> float:
        """Check that the conversation progresses without exact duplication."""
        if len(turns) < 2:
            return 1.0

        contents = [t.contenido.strip().lower() for t in turns]
        unique_contents = set(contents)

        # Ratio of unique turns to total turns
        uniqueness = len(unique_contents) / len(contents)

        # Also check that content length generally doesn't collapse
        lengths = [len(c) for c in contents if c]
        if lengths:
            # Penalize if last turns become extremely short compared to early ones
            avg_first_half = sum(lengths[: len(lengths) // 2]) / max(len(lengths) // 2, 1)
            avg_second_half = sum(lengths[len(lengths) // 2 :]) / max(len(lengths) - len(lengths) // 2, 1)

            if avg_first_half > 0:
                ratio = avg_second_half / avg_first_half
                # Allow some natural shortening but penalize extreme collapse
                length_score = min(1.0, ratio + 0.3)  # generous margin
            else:
                length_score = 1.0
        else:
            length_score = 1.0

        return uniqueness * 0.6 + length_score * 0.4

    def _referential_consistency(self, turns: list[ConversationTurn]) -> float:
        """Check that later turns reference content from earlier turns.

        Uses content tokens (stopwords filtered) so that common function
        words like "que", "con", "una" do not trivially satisfy the check.
        Requires at least 2 shared content words to count as a backward
        reference.
        """
        if len(turns) < 3:
            return 1.0

        prior_content_tokens: set[str] = set()
        references_found = 0
        reference_checks = 0

        for i, turn in enumerate(turns):
            current_tokens = content_token_set(turn.contenido)

            if i >= 2 and turn.rol not in {"herramienta", "tool"}:
                reference_checks += 1
                overlap = current_tokens & prior_content_tokens
                if len(overlap) >= 2:
                    references_found += 1

            prior_content_tokens |= current_tokens

        if reference_checks == 0:
            return 1.0

        return references_found / reference_checks
