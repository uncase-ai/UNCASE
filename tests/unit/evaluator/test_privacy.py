"""Tests for privacy (PII detection) metric."""

from __future__ import annotations

from tests.factories import make_conversation, make_seed
from uncase.core.evaluator.metrics.privacy import PrivacyMetric, detect_pii_heuristic
from uncase.schemas.conversation import ConversationTurn


class TestDetectPIIHeuristic:
    """Tests for the PII heuristic detection."""

    def test_detects_email(self) -> None:
        matches = detect_pii_heuristic("Contact me at juan.perez@example.com")
        assert len(matches) > 0
        assert any(m.category == "email" for m in matches)

    def test_detects_phone_us_format(self) -> None:
        matches = detect_pii_heuristic("Call me at 555-123-4567")
        assert len(matches) > 0
        assert any(m.category == "phone_local" for m in matches)

    def test_detects_ssn(self) -> None:
        matches = detect_pii_heuristic("SSN: 123-45-6789")
        assert len(matches) > 0
        assert any(m.category == "ssn_us" for m in matches)

    def test_detects_credit_card(self) -> None:
        matches = detect_pii_heuristic("Card: 4111-1111-1111-1111")
        assert len(matches) > 0
        assert any(m.category == "credit_card" for m in matches)

    def test_clean_text_no_pii(self) -> None:
        matches = detect_pii_heuristic("Buenos dias, busco un vehiculo electrico para mi familia")
        assert len(matches) == 0

    def test_detects_international_phone(self) -> None:
        matches = detect_pii_heuristic("Mi numero es +52 55 1234 5678")
        assert len(matches) > 0

    def test_detects_ip_address(self) -> None:
        matches = detect_pii_heuristic("Server at 192.168.1.100")
        assert len(matches) > 0
        assert any(m.category == "ip_address" for m in matches)

    def test_multiple_pii_entities(self) -> None:
        text = "Email: test@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        matches = detect_pii_heuristic(text)
        categories = {m.category for m in matches}
        assert "email" in categories
        assert "phone_local" in categories
        assert "ssn_us" in categories


class TestPrivacyMetric:
    """Tests for the PrivacyMetric class."""

    def test_name(self) -> None:
        metric = PrivacyMetric()
        assert metric.name == "privacy_score"

    def test_clean_conversation_scores_zero(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = PrivacyMetric()
        score = metric.compute(conversation, seed)
        assert score == 0.0

    def test_conversation_with_email_scores_nonzero(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Hola"),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi email es juan@example.com"),
            ],
        )
        metric = PrivacyMetric()
        score = metric.compute(conversation, seed)
        assert score > 0.0

    def test_conversation_with_multiple_pii(self) -> None:
        seed = make_seed()
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="cliente",
                    contenido="Mi email es test@example.com y telefono 555-123-4567",
                ),
                ConversationTurn(
                    turno=2,
                    rol="vendedor",
                    contenido="Su SSN es 123-45-6789",
                ),
            ],
        )
        metric = PrivacyMetric()
        score = metric.compute(conversation, seed)
        assert score > 0.1  # Multiple PII entities

    def test_score_capped_at_one(self) -> None:
        seed = make_seed()
        # Create conversation with many PII entities
        pii_text = " ".join(
            [f"email{i}@test.com" for i in range(20)]
        )
        conversation = make_conversation(
            seed_id=seed.seed_id,
            turnos=[ConversationTurn(turno=1, rol="cliente", contenido=pii_text)],
        )
        metric = PrivacyMetric()
        score = metric.compute(conversation, seed)
        assert score <= 1.0

    def test_returns_bounded_score(self) -> None:
        seed = make_seed()
        conversation = make_conversation(seed_id=seed.seed_id)
        metric = PrivacyMetric()
        score = metric.compute(conversation, seed)
        assert 0.0 <= score <= 1.0
