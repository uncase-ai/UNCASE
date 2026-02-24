"""Tests for the evaluator service layer."""

from __future__ import annotations

import pytest

from tests.factories import make_conversation, make_seed
from uncase.services.evaluator import BatchEvaluationResult, EvaluatorService


class TestEvaluatorService:
    """Tests for the EvaluatorService class."""

    @pytest.fixture()
    def service(self) -> EvaluatorService:
        return EvaluatorService()

    async def test_evaluate_single(self, service: EvaluatorService) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)

        report = await service.evaluate_single(conversation, seed)

        assert report.conversation_id == conversation.conversation_id
        assert report.seed_id == seed.seed_id

    async def test_evaluate_batch_returns_summary(self, service: EvaluatorService) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id) for _ in range(3)]
        seeds = [seed] * 3

        result = await service.evaluate_batch(conversations, seeds)

        assert isinstance(result, BatchEvaluationResult)
        assert result.total == 3
        assert result.passed_count + result.failed_count == 3
        assert 0.0 <= result.pass_rate <= 100.0

    async def test_batch_result_metric_averages(self, service: EvaluatorService) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id) for _ in range(3)]
        seeds = [seed] * 3

        result = await service.evaluate_batch(conversations, seeds)

        assert "rouge_l" in result.metric_averages
        assert "fidelidad_factual" in result.metric_averages
        assert "diversidad_lexica" in result.metric_averages
        assert "coherencia_dialogica" in result.metric_averages

    async def test_batch_result_to_dict(self, service: EvaluatorService) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id)]
        seeds = [seed]

        result = await service.evaluate_batch(conversations, seeds)
        data = result.to_dict()

        assert "total" in data
        assert "passed" in data
        assert "failed" in data
        assert "pass_rate" in data
        assert "avg_composite_score" in data
        assert "reports" in data
        assert isinstance(data["reports"], list)

    async def test_pass_rate_property(self, service: EvaluatorService) -> None:
        seed = make_seed()
        conversations = [make_conversation(seed_id=seed.seed_id) for _ in range(5)]
        seeds = [seed] * 5

        result = await service.evaluate_batch(conversations, seeds)

        expected_rate = (result.passed_count / result.total * 100) if result.total > 0 else 0.0
        assert abs(result.pass_rate - expected_rate) < 0.01
