"""Tests for ROUGE-L metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_seed
from uncase.core.evaluator.metrics.rouge import ROUGELMetric, _lcs_length, rouge_l_score
from uncase.schemas.conversation import ConversationTurn


class TestLCSLength:
    """Tests for the Longest Common Subsequence helper."""

    def test_identical_sequences(self) -> None:
        assert _lcs_length(["a", "b", "c"], ["a", "b", "c"]) == 3

    def test_no_common_elements(self) -> None:
        assert _lcs_length(["a", "b"], ["c", "d"]) == 0

    def test_partial_overlap(self) -> None:
        assert _lcs_length(["a", "b", "c", "d"], ["b", "d"]) == 2

    def test_empty_sequences(self) -> None:
        assert _lcs_length([], ["a", "b"]) == 0
        assert _lcs_length(["a"], []) == 0
        assert _lcs_length([], []) == 0

    def test_single_element_match(self) -> None:
        assert _lcs_length(["x"], ["x"]) == 1

    def test_single_element_no_match(self) -> None:
        assert _lcs_length(["x"], ["y"]) == 0


class TestROUGELScore:
    """Tests for the rouge_l_score function."""

    def test_identical_text(self) -> None:
        score = rouge_l_score("hello world test", "hello world test")
        assert score == 1.0

    def test_empty_hypothesis(self) -> None:
        assert rouge_l_score("", "some reference") == 0.0

    def test_empty_reference(self) -> None:
        assert rouge_l_score("some hypothesis", "") == 0.0

    def test_partial_overlap(self) -> None:
        score = rouge_l_score("the cat sat on the mat", "the cat on mat")
        assert 0.0 < score < 1.0

    def test_no_overlap(self) -> None:
        score = rouge_l_score("alpha beta gamma", "delta epsilon zeta")
        assert score == 0.0

    def test_score_is_symmetric_for_f1(self) -> None:
        s1 = rouge_l_score("a b c d e", "a c e")
        s2 = rouge_l_score("a c e", "a b c d e")
        # F1 is symmetric
        assert abs(s1 - s2) < 1e-10


class TestROUGELMetric:
    """Tests for the ROUGE-L metric class."""

    def test_name(self) -> None:
        metric = ROUGELMetric()
        assert metric.name == "rouge_l"

    def test_display_name(self) -> None:
        metric = ROUGELMetric()
        assert "ROUGE" in metric.display_name

    def test_compute_with_matching_content(self) -> None:
        seed = make_seed(
            objetivo="consulta vehiculos disponibles",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario"),
                ConversationTurn(turno=2, rol="cliente", contenido="Consulta sobre vehiculos disponibles"),
            ],
        )
        metric = ROUGELMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 < score <= 1.0

    def test_compute_with_no_overlap(self) -> None:
        seed = make_seed(
            objetivo="analysis financiero completo",
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="xyz abc def"),
                ConversationTurn(turno=2, rol="cliente", contenido="ghi jkl mno"),
            ],
        )
        metric = ROUGELMetric()
        score = metric.compute(conversation, seed)
        # Some overlap likely through common words like "de", but score should be low
        assert score < 0.5

    def test_compute_returns_bounded_score(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = ROUGELMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0
