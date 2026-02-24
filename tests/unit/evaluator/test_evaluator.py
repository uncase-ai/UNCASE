"""Tests for the ConversationEvaluator orchestrator."""

from __future__ import annotations

import pytest

from tests.factories import make_conversation, make_conversation_with_tools, make_seed
from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.schemas.conversation import ConversationTurn


class TestConversationEvaluator:
    """Tests for the main evaluator class."""

    @pytest.fixture()
    def evaluator(self) -> ConversationEvaluator:
        return ConversationEvaluator()

    async def test_evaluate_returns_quality_report(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        assert report.conversation_id == conversation.conversation_id
        assert report.seed_id == seed.seed_id
        assert 0.0 <= report.composite_score <= 1.0
        assert isinstance(report.passed, bool)
        assert isinstance(report.failures, list)

    async def test_evaluate_all_metrics_populated(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        assert report.metrics.rouge_l >= 0.0
        assert report.metrics.fidelidad_factual >= 0.0
        assert report.metrics.diversidad_lexica >= 0.0
        assert report.metrics.coherencia_dialogica >= 0.0
        assert report.metrics.privacy_score >= 0.0
        assert report.metrics.memorizacion >= 0.0

    async def test_clean_conversation_has_zero_privacy(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        assert report.metrics.privacy_score == 0.0

    async def test_pii_conversation_fails(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi email es juan@example.com y SSN 123-45-6789"),
            ],
        )

        report = await evaluator.evaluate(conversation, seed)

        assert report.metrics.privacy_score > 0.0
        assert report.composite_score == 0.0
        assert report.passed is False
        assert any("privacy_score" in f for f in report.failures)

    async def test_evaluate_batch_matching_sizes(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id) for _ in range(3)]
        seeds = [seed] * 3

        reports = await evaluator.evaluate_batch(conversations, seeds)

        assert len(reports) == 3
        for report in reports:
            assert report.seed_id == seed.seed_id

    async def test_evaluate_batch_mismatched_sizes_raises(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id)]
        seeds = [seed, seed]

        with pytest.raises(ValueError, match="Mismatched batch sizes"):
            await evaluator.evaluate_batch(conversations, seeds)

    async def test_evaluate_conversation_with_tools(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation_with_tools(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        assert report.conversation_id == conversation.conversation_id
        assert 0.0 <= report.composite_score <= 1.0

    async def test_metrics_are_clamped(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        # All metrics must be in [0, 1]
        for field_name in [
            "rouge_l",
            "fidelidad_factual",
            "diversidad_lexica",
            "coherencia_dialogica",
            "privacy_score",
            "memorizacion",
        ]:
            value = getattr(report.metrics, field_name)
            assert 0.0 <= value <= 1.0, f"{field_name}={value} out of bounds"

    async def test_memorization_defaults_to_zero(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await evaluator.evaluate(conversation, seed)

        # Memorization requires a trained model — defaults to 0.0
        assert report.metrics.memorizacion == 0.0
