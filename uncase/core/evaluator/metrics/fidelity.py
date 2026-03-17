"""Factual fidelity metric — domain constraint adherence."""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics._stopwords import content_token_set, match_flow_step
from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema


class FactualFidelityMetric(BaseMetric):
    """Factual fidelity metric for seed-conversation alignment.

    Measures how well a conversation adheres to the domain constraints
    and factual parameters defined in its origin seed. Evaluates:

    1. **Role compliance** — Does the conversation use only the roles
       defined in the seed?
    2. **Flow adherence** — Does the conversation follow the seed's
       flujo_esperado step sequence?
    3. **Turn count compliance** — Is the number of turns within the
       seed's defined range?
    4. **Domain context presence** — Are key terms from the seed's
       contexto and restricciones reflected in the conversation?
    5. **Tool usage compliance** — If the seed defines tools, are they
       used correctly in the conversation?

    Final score = weighted average of all sub-scores.
    """

    @property
    def name(self) -> str:
        return "fidelidad_factual"

    @property
    def display_name(self) -> str:
        return "Factual Fidelity"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute factual fidelity score."""
        sub_scores: list[tuple[float, float]] = []  # (score, weight)

        sub_scores.append((self._role_compliance(conversation, seed), 0.25))
        sub_scores.append((self._flow_adherence(conversation, seed), 0.25))
        sub_scores.append((self._turn_compliance(conversation, seed), 0.15))
        sub_scores.append((self._context_presence(conversation, seed), 0.20))
        sub_scores.append((self._tool_compliance(conversation, seed), 0.15))

        total_weight = sum(w for _, w in sub_scores)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(s * w for s, w in sub_scores)
        return weighted_sum / total_weight

    def _role_compliance(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Check that conversation roles are a subset of seed roles."""
        seed_roles = set(seed.roles)
        # Allow 'herramienta' / 'tool' / 'system' as implicit roles
        allowed_roles = seed_roles | {"herramienta", "tool", "system"}

        conv_roles = conversation.roles_presentes
        if not conv_roles:
            return 0.0

        compliant = sum(1 for r in conv_roles if r in allowed_roles)
        return compliant / len(conv_roles)

    def _flow_adherence(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Check how many expected flow steps appear in the conversation.

        For each step, finds the best-matching conversation turn using
        ``match_flow_step``.  Also checks whether detected steps appear
        in the expected order; an out-of-order penalty (x0.8) is applied
        when the earliest detection indices are not monotonically
        increasing.
        """
        expected_flow = seed.pasos_turnos.flujo_esperado
        if not expected_flow:
            return 1.0

        # Build per-turn text segments
        segments = [t.contenido for t in conversation.turnos]
        if not segments:
            return 0.0

        step_scores: list[float] = []
        # For each step, record the turn index of the best match (for order check)
        best_indices: list[int | None] = []

        for step in expected_flow:
            best_score = 0.0
            best_idx: int | None = None
            for idx, segment in enumerate(segments):
                score = match_flow_step(step, segment)
                if score > best_score:
                    best_score = score
                    best_idx = idx
            step_scores.append(best_score)
            best_indices.append(best_idx if best_score > 0 else None)

        if not step_scores:
            return 0.0

        avg_score = sum(step_scores) / len(step_scores)

        # Order check: collect earliest detection indices for matched steps
        detected_indices = [i for i in best_indices if i is not None]
        if len(detected_indices) >= 2:
            is_ordered = all(a <= b for a, b in pairwise(detected_indices))
            if not is_ordered:
                avg_score *= 0.8

        return min(avg_score, 1.0)

    def _turn_compliance(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Check that the conversation's turn count is within seed range."""
        n = conversation.num_turnos
        min_t = seed.pasos_turnos.turnos_min
        max_t = seed.pasos_turnos.turnos_max

        if min_t <= n <= max_t:
            return 1.0

        # Partial credit for being close to the range
        if n < min_t:
            return max(0.0, 1.0 - (min_t - n) / max(min_t, 1))
        # n > max_t
        return max(0.0, 1.0 - (n - max_t) / max(max_t, 1))

    def _context_presence(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Check for seed context keywords in the conversation.

        Uses ``content_token_set`` to extract meaningful content words,
        filtering out Spanish function words and short tokens so that
        only true domain-signal terms contribute to the score.
        """
        context = seed.parametros_factuales.contexto
        constraints = seed.parametros_factuales.restricciones

        reference_text = context + " " + " ".join(constraints)
        keywords = content_token_set(reference_text)

        if not keywords:
            return 1.0

        conv_text = " ".join(t.contenido.lower() for t in conversation.turnos)
        conv_tokens = content_token_set(conv_text)

        found = len(keywords & conv_tokens)
        return found / len(keywords)

    def _tool_compliance(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Check tool usage matches seed's tool definitions."""
        seed_tools = set(seed.parametros_factuales.herramientas)

        if not seed_tools:
            # No tools expected — any tool usage is a small penalty
            has_tools = any(t.tool_calls for t in conversation.turnos if t.tool_calls)
            return 0.8 if has_tools else 1.0

        # Tools are expected — check which ones were used
        used_tools: set[str] = set()
        for turn in conversation.turnos:
            if turn.tool_calls:
                used_tools.update(tc.tool_name for tc in turn.tool_calls)
            if turn.herramientas_usadas:
                used_tools.update(turn.herramientas_usadas)

        if not used_tools:
            return 0.3  # Tools expected but none used

        # Intersection ratio
        matched = len(seed_tools & used_tools)
        return matched / len(seed_tools)
