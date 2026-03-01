"""Semantic evaluation metrics — LLM-as-Judge and Embedding Drift.

These metrics complement the existing lexical metrics (ROUGE-L, TTR, Jaccard)
with semantic understanding capabilities:

1. SemanticFidelityMetric: Uses an LLM to grade conversation quality against
   rubrics for factual fidelity and logical coherence.

2. EmbeddingDriftMetric: Measures cosine distance between seed context and
   generated conversation using sentence embeddings.

Both metrics are optional — they require external API calls and fall back
gracefully to neutral scores (0.5) when the API is unavailable.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar

import structlog

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


class SemanticFidelityMetric(BaseMetric):
    """LLM-as-Judge metric for semantic fidelity and logical coherence.

    Uses a small, cheap LLM (default: claude-haiku) to evaluate:
    - Factual alignment with seed constraints
    - Logical flow and dialog coherence
    - Role consistency throughout the conversation
    - Domain-appropriate language and behavior

    The judge uses a structured rubric (1-5 scale) and returns a normalized
    score in [0.0, 1.0].

    Falls back to 0.5 (neutral) if the LLM call fails.
    """

    _RUBRIC: ClassVar[str] = """You are an expert quality evaluator for synthetic conversations.

Grade the following conversation on a 1-5 scale across these dimensions:

1. **Factual Fidelity** (does it respect the domain constraints and context?):
   1 = Contradicts constraints or invents facts
   2 = Partially follows constraints, some inconsistencies
   3 = Mostly follows constraints with minor issues
   4 = Follows all constraints with good domain accuracy
   5 = Perfect adherence to constraints with expert-level domain knowledge

2. **Logical Coherence** (does the dialog flow make sense?):
   1 = Incoherent, turns don't connect
   2 = Some turns connect but overall flow is broken
   3 = Generally coherent with occasional jumps
   4 = Smooth, logical progression throughout
   5 = Perfect natural flow, each turn builds on previous

3. **Role Consistency** (do participants stay in character?):
   1 = Roles are indistinguishable or break character constantly
   2 = Roles mostly similar with occasional differentiation
   3 = Roles are distinguishable but sometimes inconsistent
   4 = Clear role differentiation maintained throughout
   5 = Perfect role embodiment with domain-appropriate expertise

4. **Naturalness** (does it feel like a real conversation?):
   1 = Obviously scripted/robotic
   2 = Somewhat artificial, stilted language
   3 = Passable but with unnatural moments
   4 = Natural and fluid conversation
   5 = Indistinguishable from real conversation

Respond with ONLY a JSON object:
{
    "factual_fidelity": <1-5>,
    "logical_coherence": <1-5>,
    "role_consistency": <1-5>,
    "naturalness": <1-5>,
    "overall_reasoning": "<1-2 sentence justification>"
}"""

    def __init__(
        self,
        *,
        model: str = "claude-haiku-4-5-20251001",
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._last_reasoning: str = ""

    @property
    def name(self) -> str:
        return "semantic_fidelity"

    @property
    def display_name(self) -> str:
        return "Semantic Fidelity (LLM Judge)"

    @property
    def last_reasoning(self) -> str:
        """The LLM judge's reasoning from the most recent evaluation."""
        return self._last_reasoning

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute semantic fidelity score synchronously.

        Since BaseMetric.compute() is synchronous, we run the async LLM call
        in a blocking manner. For production use, prefer compute_async().
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already in an async context — can't use asyncio.run()
            # Fall back to neutral score and log
            logger.debug(
                "semantic_fidelity_sync_fallback",
                reason="cannot run async in existing event loop",
            )
            return 0.5

        try:
            return asyncio.run(self.compute_async(conversation, seed))
        except Exception as exc:
            logger.warning(
                "semantic_fidelity_fallback",
                error=str(exc),
                fallback_score=0.5,
            )
            return 0.5

    async def compute_async(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute semantic fidelity score asynchronously."""
        try:
            import litellm
        except ImportError:
            logger.warning("semantic_fidelity_no_litellm", fallback_score=0.5)
            return 0.5

        # Build conversation text for the judge
        conv_text = "\n".join(
            f"[{t.rol}] (Turn {t.turno}): {t.contenido}"
            for t in conversation.turnos
        )

        # Build seed context summary
        seed_context = (
            f"Domain: {seed.dominio}\n"
            f"Objective: {seed.objetivo}\n"
            f"Roles: {', '.join(seed.roles)}\n"
            f"Context: {seed.parametros_factuales.contexto}\n"
            f"Constraints: {'; '.join(seed.parametros_factuales.restricciones)}\n"
            f"Expected flow: {' → '.join(seed.pasos_turnos.flujo_esperado)}"
        )

        user_message = (
            f"## Seed Specification\n{seed_context}\n\n"
            f"## Generated Conversation ({conversation.num_turnos} turns)\n{conv_text}"
        )

        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": self._RUBRIC},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.0,
                "max_tokens": 300,
                "response_format": {"type": "json_object"},
            }
            if self._api_key:
                kwargs["api_key"] = self._api_key

            response = await litellm.acompletion(**kwargs)
            content = response.choices[0].message.content

            if not content:
                return 0.5

            grades = json.loads(content)

            # Extract scores (1-5 scale → 0.0-1.0)
            fidelity = float(grades.get("factual_fidelity", 3))
            coherence = float(grades.get("logical_coherence", 3))
            role_consistency = float(grades.get("role_consistency", 3))
            naturalness = float(grades.get("naturalness", 3))
            self._last_reasoning = str(grades.get("overall_reasoning", ""))

            # Weighted average, normalized from 1-5 to 0-1
            weighted = (
                fidelity * 0.35
                + coherence * 0.30
                + role_consistency * 0.20
                + naturalness * 0.15
            )
            score = (weighted - 1.0) / 4.0  # Map [1,5] → [0,1]

            logger.info(
                "semantic_fidelity_evaluated",
                conversation_id=conversation.conversation_id,
                fidelity=fidelity,
                coherence=coherence,
                role_consistency=role_consistency,
                naturalness=naturalness,
                score=round(score, 4),
            )

            return max(0.0, min(1.0, score))

        except Exception as exc:
            logger.warning(
                "semantic_fidelity_llm_failed",
                error=str(exc),
                model=self._model,
                fallback_score=0.5,
            )
            return 0.5


class EmbeddingDriftMetric(BaseMetric):
    """Cosine similarity between seed context and generated conversation embeddings.

    Measures how much the generated conversation "drifts" from the original
    seed specification. High similarity = conversation stays on topic.
    Low similarity = conversation wandered off.

    Uses LiteLLM's embedding API for provider-agnostic embedding generation.
    Falls back to a simple TF-IDF cosine similarity when embeddings are unavailable.
    """

    def __init__(
        self,
        *,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        drift_threshold: float = 0.5,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._drift_threshold = drift_threshold

    @property
    def name(self) -> str:
        return "embedding_drift"

    @property
    def display_name(self) -> str:
        return "Semantic Drift (Embedding Distance)"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute embedding drift synchronously with TF-IDF fallback."""
        # Use TF-IDF fallback (always available, no API needed)
        return self._compute_tfidf(conversation, seed)

    async def compute_async(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute embedding drift using LLM embeddings."""
        try:
            import litellm
        except ImportError:
            return self._compute_tfidf(conversation, seed)

        seed_text = self._build_seed_text(seed)
        conv_text = self._build_conv_text(conversation)

        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "input": [seed_text[:8000], conv_text[:8000]],  # Respect token limits
            }
            if self._api_key:
                kwargs["api_key"] = self._api_key

            response = await litellm.aembedding(**kwargs)

            seed_embedding = response.data[0]["embedding"]
            conv_embedding = response.data[1]["embedding"]

            similarity = self._cosine_similarity(seed_embedding, conv_embedding)

            logger.info(
                "embedding_drift_evaluated",
                conversation_id=conversation.conversation_id,
                seed_id=seed.seed_id,
                cosine_similarity=round(similarity, 4),
                model=self._model,
            )

            return max(0.0, min(1.0, similarity))

        except Exception as exc:
            logger.warning(
                "embedding_drift_api_failed",
                error=str(exc),
                fallback="tfidf",
            )
            return self._compute_tfidf(conversation, seed)

    def _build_seed_text(self, seed: SeedSchema) -> str:
        """Extract representative text from a seed for embedding."""
        parts = [
            seed.objetivo,
            seed.parametros_factuales.contexto,
            " ".join(seed.parametros_factuales.restricciones),
            " ".join(seed.pasos_turnos.flujo_esperado),
        ]
        return " ".join(p for p in parts if p)

    def _build_conv_text(self, conversation: Conversation) -> str:
        """Extract text from a conversation for embedding."""
        return " ".join(t.contenido for t in conversation.turnos)

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=True))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def _compute_tfidf(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Fallback: TF-IDF-based cosine similarity (no API required).

        Computes term frequency vectors for seed and conversation text,
        then measures cosine similarity.
        """
        import math
        import re

        seed_text = self._build_seed_text(seed).lower()
        conv_text = self._build_conv_text(conversation).lower()

        # Tokenize
        seed_tokens = re.findall(r"\b\w{3,}\b", seed_text)
        conv_tokens = re.findall(r"\b\w{3,}\b", conv_text)

        if not seed_tokens or not conv_tokens:
            return 0.0

        # Build term frequency vectors
        all_terms = set(seed_tokens) | set(conv_tokens)

        seed_freq: dict[str, float] = {}
        for token in seed_tokens:
            seed_freq[token] = seed_freq.get(token, 0) + 1

        conv_freq: dict[str, float] = {}
        for token in conv_tokens:
            conv_freq[token] = conv_freq.get(token, 0) + 1

        # Compute cosine similarity over term frequency vectors
        dot = sum(seed_freq.get(t, 0) * conv_freq.get(t, 0) for t in all_terms)
        norm_a = math.sqrt(sum(v * v for v in seed_freq.values()))
        norm_b = math.sqrt(sum(v * v for v in conv_freq.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot / (norm_a * norm_b)

        logger.debug(
            "embedding_drift_tfidf",
            seed_terms=len(seed_tokens),
            conv_terms=len(conv_tokens),
            similarity=round(similarity, 4),
        )

        return max(0.0, min(1.0, similarity))
