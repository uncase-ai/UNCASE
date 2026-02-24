"""Dialog coherence metric — inter-turn consistency evaluation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation, ConversationTurn
    from uncase.schemas.seed import SeedSchema


def _extract_tokens_set(text: str) -> set[str]:
    """Extract unique word tokens from text."""
    return {w.lower() for w in re.findall(r"\b\w+\b", text) if len(w) > 2}


def _jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


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
        """Measure topical continuity between adjacent turns."""
        if len(turns) < 2:
            return 1.0

        similarities: list[float] = []
        for i in range(len(turns) - 1):
            tokens_a = _extract_tokens_set(turns[i].contenido)
            tokens_b = _extract_tokens_set(turns[i + 1].contenido)
            sim = _jaccard_similarity(tokens_a, tokens_b)
            similarities.append(sim)

        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0

        # Map to [0, 1]: a sim of 0.05-0.3 is typical for good dialog
        # (too low = topic jumping, too high = repetition)
        # Score peaks at ~0.15 Jaccard and decays for both extremes
        if avg_sim < 0.02:
            return max(0.0, avg_sim * 20)  # Very low overlap → low score
        if avg_sim > 0.6:
            return max(0.3, 1.0 - (avg_sim - 0.6))  # Very high → possible repetition
        # Sweet spot: 0.02 to 0.6
        return min(1.0, 0.5 + avg_sim)

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
        """Check that later turns reference content from earlier turns."""
        if len(turns) < 3:
            return 1.0

        # For each turn after the first two, check if it shares tokens
        # with any previous turn (showing it builds on prior context)
        prior_tokens: set[str] = set()
        references_found = 0
        reference_checks = 0

        for i, turn in enumerate(turns):
            current_tokens = _extract_tokens_set(turn.contenido)

            if i >= 2 and turn.rol not in {"herramienta", "tool"}:
                reference_checks += 1
                overlap = current_tokens & prior_tokens
                if len(overlap) >= 1:
                    references_found += 1

            prior_tokens |= current_tokens

        if reference_checks == 0:
            return 1.0

        return references_found / reference_checks
