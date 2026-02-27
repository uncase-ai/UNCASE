"""Tests for quality metrics and composite score calculation."""

from __future__ import annotations

from tests.factories import make_quality_metrics
from uncase.schemas.quality import compute_composite_score


class TestCompositeScore:
    """Tests for the Q = min(metrics) formula with privacy/memorization gates."""

    def test_passing_metrics(self) -> None:
        metrics = make_quality_metrics()
        score, passed, failures = compute_composite_score(metrics)
        assert passed is True
        assert score > 0
        assert len(failures) == 0

    def test_score_is_min_of_metrics(self) -> None:
        metrics = make_quality_metrics(
            rouge_l=0.70,
            fidelidad_factual=0.95,
            diversidad_lexica=0.60,
            coherencia_dialogica=0.90,
            tool_call_validity=1.0,
        )
        score, _, _ = compute_composite_score(metrics)
        assert score == 0.60

    def test_privacy_gate_fails(self) -> None:
        metrics = make_quality_metrics(privacy_score=0.05)
        score, passed, failures = compute_composite_score(metrics)
        assert score == 0.0
        assert passed is False
        assert any("privacy_score" in f for f in failures)

    def test_memorization_gate_fails(self) -> None:
        metrics = make_quality_metrics(memorizacion=0.02)
        score, passed, failures = compute_composite_score(metrics)
        assert score == 0.0
        assert passed is False
        assert any("memorizacion" in f for f in failures)

    def test_both_gates_fail(self) -> None:
        metrics = make_quality_metrics(privacy_score=0.1, memorizacion=0.05)
        score, passed, failures = compute_composite_score(metrics)
        assert score == 0.0
        assert passed is False
        assert len(failures) == 2

    def test_individual_threshold_failure(self) -> None:
        metrics = make_quality_metrics(rouge_l=0.50)
        score, passed, failures = compute_composite_score(metrics)
        assert score == 0.50
        assert passed is False
        assert any("rouge_l" in f for f in failures)

    def test_all_thresholds_met_exactly(self) -> None:
        metrics = make_quality_metrics(
            rouge_l=0.65,
            fidelidad_factual=0.90,
            diversidad_lexica=0.55,
            coherencia_dialogica=0.85,
            tool_call_validity=0.90,
            privacy_score=0.0,
            memorizacion=0.0,
        )
        score, passed, _failures = compute_composite_score(metrics)
        assert passed is True
        assert score == 0.55

    def test_tool_call_validity_below_threshold(self) -> None:
        metrics = make_quality_metrics(tool_call_validity=0.80)
        _score, passed, failures = compute_composite_score(metrics)
        assert passed is False
        assert any("tool_call_validity" in f for f in failures)

    def test_tool_call_validity_drags_composite_when_lowest(self) -> None:
        metrics = make_quality_metrics(
            rouge_l=0.95,
            fidelidad_factual=0.95,
            diversidad_lexica=0.95,
            coherencia_dialogica=0.95,
            tool_call_validity=0.50,
        )
        score, passed, failures = compute_composite_score(metrics)
        assert score == 0.50
        assert passed is False
        assert any("tool_call_validity" in f for f in failures)

    def test_memorization_boundary_at_001(self) -> None:
        metrics = make_quality_metrics(memorizacion=0.01)
        score, passed, _ = compute_composite_score(metrics)
        assert score == 0.0
        assert passed is False

    def test_memorization_just_below_boundary(self) -> None:
        metrics = make_quality_metrics(memorizacion=0.009)
        score, passed, _ = compute_composite_score(metrics)
        assert passed is True
        assert score > 0
