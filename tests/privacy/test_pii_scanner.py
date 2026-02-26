"""Seeded PII scanner tests — validates the privacy metric and PII detection
against known PII patterns with pre-seeded inputs.

All PII data used in these tests is entirely fictional and used solely
to validate the detection capabilities. No real PII is present.
"""

from __future__ import annotations

import pytest

from tests.factories import make_seed
from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.core.evaluator.metrics.privacy import PrivacyMetric, detect_pii_heuristic
from uncase.schemas.conversation import Conversation, ConversationTurn


# ─── Fixtures ───


@pytest.fixture()
def evaluator() -> ConversationEvaluator:
    return ConversationEvaluator()


@pytest.fixture()
def privacy_metric() -> PrivacyMetric:
    return PrivacyMetric()


# ─── Heuristic PII detection tests with seeded inputs ───


class TestSeededPIIDetection:
    """Tests PII detection with known-PII inputs and expected match counts."""

    @pytest.mark.parametrize(
        "text,pii_type,expected_min_matches",
        [
            # Email addresses
            ("Contacte a juan.perez@correo.com para informacion", "email", 1),
            ("Envie a test@empresa.mx y copia a admin@empresa.mx", "email", 2),
            ("Mi correo personal es maria_lopez123@gmail.com", "email", 1),

            # US phone numbers
            ("Llame al 555-123-4567 para agendar", "phone", 1),
            ("Telefonos: 555-111-2222 y 555-333-4444", "phone", 2),
            ("Contacto: 555.123.4567 directo", "phone", 1),

            # SSN-like patterns
            ("SSN del cliente: 123-45-6789", "ssn", 1),
            ("Numero social: 987-65-4321", "ssn", 1),

            # Credit card numbers
            ("Tarjeta: 4111-1111-1111-1111", "credit_card", 1),
            ("Pague con 5500 0000 0000 0004", "credit_card", 1),

            # IP addresses
            ("Conectado desde 192.168.1.100", "ip", 1),
            ("Servidores 10.0.0.1 y 10.0.0.2", "ip", 2),

            # Mexican phone numbers
            ("Celular: +52 55 1234 5678", "phone", 1),
        ],
        ids=[
            "email-single",
            "email-multiple",
            "email-complex",
            "phone-us-single",
            "phone-us-multiple",
            "phone-us-dots",
            "ssn-standard",
            "ssn-variant",
            "cc-visa",
            "cc-mastercard",
            "ip-single",
            "ip-multiple",
            "phone-mx",
        ],
    )
    def test_heuristic_detects_pii(self, text: str, pii_type: str, expected_min_matches: int) -> None:
        matches = detect_pii_heuristic(text)

        assert len(matches) >= expected_min_matches, (
            f"Expected at least {expected_min_matches} PII matches for {pii_type}, "
            f"got {len(matches)}: {matches}"
        )


class TestSeededPIICleanInputs:
    """Tests that clean text does NOT trigger false positives."""

    @pytest.mark.parametrize(
        "text",
        [
            "Buenos dias, bienvenido al concesionario ficticio",
            "El vehiculo tiene un precio de cuatrocientos mil pesos",
            "La cita esta programada para el martes a las tres de la tarde",
            "El modelo Corsa 2024 incluye frenos ABS y bolsas de aire",
            "Contamos con financiamiento de 48 a 72 mensualidades",
            "El taller de servicio se encuentra en la planta baja",
            "La garantia cubre componentes mecanicos durante tres anios",
            "El motor V6 de 3.5 litros produce 300 caballos de fuerza",
        ],
        ids=[
            "greeting",
            "price-text",
            "appointment",
            "car-features",
            "financing",
            "location",
            "warranty",
            "engine-specs",
        ],
    )
    def test_clean_text_no_pii(self, text: str) -> None:
        matches = detect_pii_heuristic(text)

        assert len(matches) == 0, f"False positive PII detected in clean text: {matches}"


# ─── Privacy metric scoring tests ───


class TestSeededPrivacyMetricScoring:
    """Tests the PrivacyMetric class with known inputs and expected score ranges."""

    def test_clean_conversation_scores_zero(self, privacy_metric: PrivacyMetric) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario."),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola, busco informacion sobre vehiculos."),
                ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto, que modelo le interesa?"),
            ],
            es_sintetica=True,
        )

        score = privacy_metric.compute(conv, seed)

        assert score == 0.0

    def test_email_in_conversation_nonzero(self, privacy_metric: PrivacyMetric) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias."),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi correo es ficticio@correo.com para la cotizacion."),
            ],
            es_sintetica=True,
        )

        score = privacy_metric.compute(conv, seed)

        assert score > 0.0

    def test_multiple_pii_higher_score(self, privacy_metric: PrivacyMetric) -> None:
        seed = make_seed()

        single_pii = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias."),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi correo es ficticio@correo.com"),
            ],
            es_sintetica=True,
        )

        multi_pii = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias."),
                ConversationTurn(
                    turno=2,
                    rol="cliente",
                    contenido="Mi email es ficticio@correo.com, telefono 555-123-4567, SSN 123-45-6789",
                ),
            ],
            es_sintetica=True,
        )

        single_score = privacy_metric.compute(single_pii, seed)
        multi_score = privacy_metric.compute(multi_pii, seed)

        assert multi_score >= single_score

    def test_privacy_score_capped_at_one(self, privacy_metric: PrivacyMetric) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(
                    turno=1,
                    rol="cliente",
                    contenido=(
                        "Emails: a@b.com c@d.com e@f.com g@h.com i@j.com "
                        "Phones: 555-111-2222 555-333-4444 555-555-6666 "
                        "SSNs: 111-22-3333 444-55-6666 "
                        "Cards: 4111-1111-1111-1111 5500-0000-0000-0004"
                    ),
                ),
            ],
            es_sintetica=True,
        )

        score = privacy_metric.compute(conv, seed)

        assert score <= 1.0


# ─── Full evaluator pipeline PII gate tests ───


class TestSeededPIIEvaluatorGate:
    """Tests that the full evaluator enforces the PII gate correctly."""

    async def test_single_email_kills_composite(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario."),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola, soy Maria. Mi email es maria@correo.com"),
                ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto le ayudo con la cotizacion."),
                ConversationTurn(turno=4, rol="cliente", contenido="Busco un sedan para uso familiar diario."),
                ConversationTurn(turno=5, rol="vendedor", contenido="Le recomiendo el modelo Corsa, muy confortable."),
                ConversationTurn(turno=6, rol="cliente", contenido="Me parece bien, agendemos una prueba de manejo."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        # Even one email should kill the entire composite score
        assert report.composite_score == 0.0
        assert report.passed is False
        assert report.metrics.privacy_score > 0.0

    async def test_phone_number_kills_composite(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias."),
                ConversationTurn(turno=2, rol="cliente", contenido="Llameme al 555-123-4567 para confirmar."),
                ConversationTurn(turno=3, rol="vendedor", contenido="Perfecto, le llamaremos."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        assert report.composite_score == 0.0
        assert report.passed is False

    async def test_ssn_kills_composite(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Necesitamos sus datos para el credito."),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi seguro social es 123-45-6789."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        assert report.composite_score == 0.0
        assert report.passed is False

    async def test_credit_card_kills_composite(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Puede pagar con tarjeta."),
                ConversationTurn(turno=2, rol="cliente", contenido="Mi tarjeta es 4111-1111-1111-1111."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        assert report.composite_score == 0.0
        assert report.passed is False

    async def test_clean_conversation_passes_gate(self, evaluator: ConversationEvaluator) -> None:
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario ficticio."),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola, busco informacion sobre vehiculos sedanes."),
                ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto le ayudo. Tenemos varias opciones disponibles."),
                ConversationTurn(turno=4, rol="cliente", contenido="Me interesa conocer precios y opciones de financiamiento."),
                ConversationTurn(turno=5, rol="vendedor", contenido="El sedan Corsa tiene un precio de cuatrocientos mil pesos."),
                ConversationTurn(turno=6, rol="cliente", contenido="Gracias por la informacion, voy a considerarlo."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        # Clean conversation should not be killed by privacy gate
        assert report.metrics.privacy_score == 0.0
        assert report.composite_score > 0.0

    async def test_pii_in_later_turns_still_detected(self, evaluator: ConversationEvaluator) -> None:
        """PII appearing deep in the conversation must still be caught."""
        seed = make_seed()
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio="automotive.sales",
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias."),
                ConversationTurn(turno=2, rol="cliente", contenido="Hola, busco un vehiculo."),
                ConversationTurn(turno=3, rol="vendedor", contenido="Que modelo le interesa?"),
                ConversationTurn(turno=4, rol="cliente", contenido="Un sedan."),
                ConversationTurn(turno=5, rol="vendedor", contenido="Perfecto, necesito su correo."),
                ConversationTurn(turno=6, rol="cliente", contenido="Es ficticio@correo.com"),
                ConversationTurn(turno=7, rol="vendedor", contenido="Gracias, le envio la cotizacion."),
                ConversationTurn(turno=8, rol="cliente", contenido="Perfecto, agradezco la atencion."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        assert report.metrics.privacy_score > 0.0
        assert report.composite_score == 0.0
