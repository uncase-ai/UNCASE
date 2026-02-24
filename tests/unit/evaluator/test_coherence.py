"""Tests for dialog coherence metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_seed
from uncase.core.evaluator.metrics.coherence import DialogCoherenceMetric, _jaccard_similarity
from uncase.schemas.conversation import ConversationTurn


class TestJaccardSimilarity:
    """Tests for the Jaccard similarity helper."""

    def test_identical_sets(self) -> None:
        assert _jaccard_similarity({"a", "b", "c"}, {"a", "b", "c"}) == 1.0

    def test_disjoint_sets(self) -> None:
        assert _jaccard_similarity({"a", "b"}, {"c", "d"}) == 0.0

    def test_partial_overlap(self) -> None:
        sim = _jaccard_similarity({"a", "b", "c"}, {"b", "c", "d"})
        assert sim == 2 / 4  # intersection=2, union=4

    def test_empty_sets(self) -> None:
        assert _jaccard_similarity(set(), set()) == 1.0
        assert _jaccard_similarity({"a"}, set()) == 0.0
        assert _jaccard_similarity(set(), {"a"}) == 0.0


class TestDialogCoherenceMetric:
    """Tests for the dialog coherence metric."""

    def test_name(self) -> None:
        metric = DialogCoherenceMetric()
        assert metric.name == "coherencia_dialogica"

    def test_single_turn_is_coherent(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[ConversationTurn(turno=1, rol="vendedor", contenido="Hola buenos dias")],
        )
        metric = DialogCoherenceMetric()
        score = metric.compute(conversation, seed)
        assert score == 1.0

    def test_coherent_dialog(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario"),
                ConversationTurn(turno=2, rol="cliente", contenido="Buenos dias, busco un vehiculo familiar"),
                ConversationTurn(turno=3, rol="vendedor", contenido="Para vehiculo familiar tenemos varias opciones"),
                ConversationTurn(turno=4, rol="cliente", contenido="Que opciones de vehiculo tienen disponibles?"),
            ],
        )
        metric = DialogCoherenceMetric()
        score = metric.compute(conversation, seed)
        assert score > 0.5

    def test_role_alternation_perfect(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente"])
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola"),
                ConversationTurn(turno=3, rol="vendedor", contenido="Ayuda"),
                ConversationTurn(turno=4, rol="cliente", contenido="Gracias"),
            ],
        )
        metric = DialogCoherenceMetric()
        score = metric._role_alternation(conversation.turnos, seed)
        assert score == 1.0

    def test_role_alternation_same_role_consecutive(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente"])
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="vendedor", contenido="Bienvenido"),
                ConversationTurn(turno=3, rol="vendedor", contenido="Que necesita"),
                ConversationTurn(turno=4, rol="cliente", contenido="Gracias"),
            ],
        )
        metric = DialogCoherenceMetric()
        score = metric._role_alternation(conversation.turnos, seed)
        assert score < 1.0

    def test_progressive_flow_with_duplicates(self) -> None:
        metric = DialogCoherenceMetric()
        turns = [
            ConversationTurn(turno=1, rol="vendedor", contenido="Hola como esta"),
            ConversationTurn(turno=2, rol="cliente", contenido="Hola como esta"),  # duplicate
            ConversationTurn(turno=3, rol="vendedor", contenido="Hola como esta"),  # duplicate
        ]
        score = metric._progressive_flow(turns)
        assert score < 0.8  # Penalized for duplication

    def test_progressive_flow_unique(self) -> None:
        metric = DialogCoherenceMetric()
        turns = [
            ConversationTurn(turno=1, rol="vendedor", contenido="Bienvenido al concesionario"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco un vehiculo electrico"),
            ConversationTurn(turno=3, rol="vendedor", contenido="Tenemos varias opciones disponibles"),
        ]
        score = metric._progressive_flow(turns)
        assert score > 0.8

    def test_returns_bounded_score(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = DialogCoherenceMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0
