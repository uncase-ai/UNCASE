"""Known-score evaluator tests — validates metrics against pre-computed expected values.

These tests use carefully crafted conversations with known quality properties to
validate that the evaluator produces expected metric ranges. All data is fictional.
"""

from __future__ import annotations

import pytest

from tests.factories import make_seed
from uncase.core.evaluator.evaluator import ConversationEvaluator
from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.quality import QualityMetrics, compute_composite_score
from uncase.schemas.seed import MetricasCalidad, ParametrosFactuales, PasosTurnos, Privacidad


# ─── Fixtures ───


@pytest.fixture()
def evaluator() -> ConversationEvaluator:
    return ConversationEvaluator()


def _make_automotive_seed() -> object:
    """Create a detailed automotive seed for known-score testing."""
    return make_seed(
        dominio="automotive.sales",
        idioma="es",
        roles=["vendedor", "cliente"],
        descripcion_roles={
            "vendedor": "Asesor de ventas ficticio del concesionario",
            "cliente": "Cliente ficticio interesado en comprar un vehiculo",
        },
        objetivo="Cliente ficticio consultando sobre vehiculos sedanes disponibles con opciones de financiamiento",
        tono="profesional",
        pasos_turnos=PasosTurnos(
            turnos_min=6,
            turnos_max=12,
            flujo_esperado=["saludo", "consulta de necesidades", "presentacion de opciones", "financiamiento", "cierre"],
        ),
        parametros_factuales=ParametrosFactuales(
            contexto="Concesionario ficticio de vehiculos nuevos y seminuevos",
            restricciones=["Solo vehiculos del anio 2024", "Precios en pesos mexicanos"],
            herramientas=["crm", "calculadora_financiera"],
            metadata={},
        ),
    )


def _high_quality_conversation(seed_id: str) -> Conversation:
    """Conversation that follows the seed flow closely with diverse vocabulary."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario. Soy asesor de ventas, en que puedo ayudarle hoy?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Hola, estoy buscando informacion sobre vehiculos sedanes del modelo actual. Necesito algo comodo para la familia."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Con mucho gusto le ayudo. Para entender mejor sus necesidades, podria decirme cuantas personas viajan regularmente y que tipo de recorridos realizan?"),
            ConversationTurn(turno=4, rol="cliente", contenido="Somos cuatro personas. Principalmente uso urbano para ir al trabajo y los fines de semana salidas familiares a carretera."),
            ConversationTurn(turno=5, rol="vendedor", contenido="Excelente. Tenemos tres opciones de sedanes que se ajustan perfectamente a su perfil. El modelo Corsa tiene amplio espacio interior y bajo consumo de combustible."),
            ConversationTurn(turno=6, rol="cliente", contenido="Me interesa conocer los precios y las opciones de financiamiento disponibles para ese modelo."),
            ConversationTurn(turno=7, rol="vendedor", contenido="El Corsa 2024 tiene un precio de lista de cuatrocientos cincuenta mil pesos mexicanos. Contamos con planes de financiamiento desde 48 hasta 72 mensualidades.", herramientas_usadas=["calculadora_financiera"]),
            ConversationTurn(turno=8, rol="cliente", contenido="Las mensualidades de 60 meses me parecen adecuadas. Que enganche necesitaria y cual seria el pago mensual aproximado?"),
            ConversationTurn(turno=9, rol="vendedor", contenido="Con un enganche del veinte por ciento, que serian noventa mil pesos, su mensualidad quedaria en aproximadamente ocho mil quinientos pesos. Incluye seguro el primer anio."),
            ConversationTurn(turno=10, rol="cliente", contenido="Me parece una buena opcion. Me gustaria agendar una prueba de manejo para confirmar mi decision."),
        ],
        es_sintetica=True,
    )


def _low_diversity_conversation(seed_id: str) -> Conversation:
    """Conversation with highly repetitive vocabulary — low lexical diversity."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Hola, bienvenido al concesionario. Bienvenido al concesionario."),
            ConversationTurn(turno=2, rol="cliente", contenido="Hola, quiero un carro. Quiero un carro. Quiero un carro."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Tenemos carros. Tenemos carros buenos. Tenemos carros buenos aqui."),
            ConversationTurn(turno=4, rol="cliente", contenido="Quiero un carro bueno. Quiero un carro bueno. Quiero un carro bueno."),
            ConversationTurn(turno=5, rol="vendedor", contenido="El carro es bueno. El carro es bueno. El carro es bueno."),
            ConversationTurn(turno=6, rol="cliente", contenido="Quiero el carro. Quiero el carro. Quiero el carro bueno."),
        ],
        es_sintetica=True,
    )


def _incoherent_conversation(seed_id: str) -> Conversation:
    """Conversation with topic jumps — low dialog coherence."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, le interesa comprar un vehiculo sedan nuevo?"),
            ConversationTurn(turno=2, rol="cliente", contenido="El clima esta muy agradable esta maniana, hace sol y buen tiempo."),
            ConversationTurn(turno=3, rol="vendedor", contenido="La receta de cocina lleva tres huevos y mantequilla."),
            ConversationTurn(turno=4, rol="cliente", contenido="Los partidos de futbol del fin de semana estuvieron muy emocionantes."),
            ConversationTurn(turno=5, rol="vendedor", contenido="La astronomia estudia los cuerpos celestes del universo."),
            ConversationTurn(turno=6, rol="cliente", contenido="Las flores del jardin necesitan agua diariamente para crecer bien."),
        ],
        es_sintetica=True,
    )


def _pii_contaminated_conversation(seed_id: str) -> Conversation:
    """Conversation containing PII — must fail privacy gate completely."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido al concesionario."),
            ConversationTurn(turno=2, rol="cliente", contenido="Hola, mi nombre es Juan Perez y mi email es juan.perez@correo.com y mi telefono es 555-123-4567"),
            ConversationTurn(turno=3, rol="vendedor", contenido="Gracias Juan, le envio la cotizacion a juan.perez@correo.com"),
            ConversationTurn(turno=4, rol="cliente", contenido="Mi numero de seguro social es 123-45-6789 y vivo en Av Principal 123, Ciudad."),
        ],
        es_sintetica=True,
    )


def _minimal_conversation(seed_id: str) -> Conversation:
    """Very short conversation — barely meets minimum turn count."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Hola."),
            ConversationTurn(turno=2, rol="cliente", contenido="Hola."),
        ],
        es_sintetica=True,
    )


def _single_role_conversation(seed_id: str) -> Conversation:
    """Conversation where only one role speaks — no alternation."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, bienvenido."),
            ConversationTurn(turno=2, rol="vendedor", contenido="Tenemos vehiculos disponibles hoy."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Le puedo mostrar el catalogo completo."),
            ConversationTurn(turno=4, rol="vendedor", contenido="Los precios empiezan desde doscientos mil pesos."),
            ConversationTurn(turno=5, rol="vendedor", contenido="Contamos con financiamiento sin intereses."),
            ConversationTurn(turno=6, rol="vendedor", contenido="Esperamos su visita al concesionario."),
        ],
        es_sintetica=True,
    )


# ─── Known-score tests ───


class TestKnownScoreHighQuality:
    """Tests for a well-crafted conversation that should score high."""

    async def test_privacy_score_is_zero(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        assert report.metrics.privacy_score == 0.0

    async def test_coherence_above_threshold(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Well-structured alternating dialog should have high coherence
        assert report.metrics.coherencia_dialogica >= 0.70

    async def test_diversity_above_threshold(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Varied vocabulary across 10 turns should yield good diversity
        assert report.metrics.diversidad_lexica >= 0.50

    async def test_fidelity_above_threshold(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Conversation follows seed's roles, domain, and constraints
        assert report.metrics.fidelidad_factual >= 0.60

    async def test_memorization_is_zero(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # No trained model — memorization defaults to 0.0
        assert report.metrics.memorizacion == 0.0

    async def test_composite_score_positive(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _high_quality_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Overall quality should be positive (not killed by privacy gate)
        assert report.composite_score > 0.0


class TestKnownScoreLowDiversity:
    """Tests for a repetitive conversation — should have low lexical diversity."""

    async def test_diversity_is_low(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _low_diversity_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Highly repetitive text should yield low TTR
        assert report.metrics.diversidad_lexica < 0.55

    async def test_diversity_lower_than_high_quality(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        good = _high_quality_conversation(seed.seed_id)
        bad = _low_diversity_conversation(seed.seed_id)

        good_report = await evaluator.evaluate(good, seed)
        bad_report = await evaluator.evaluate(bad, seed)

        assert bad_report.metrics.diversidad_lexica < good_report.metrics.diversidad_lexica


class TestKnownScoreIncoherent:
    """Tests for an incoherent conversation — should have low dialog coherence."""

    async def test_coherence_is_low(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _incoherent_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Random topics should produce low coherence
        assert report.metrics.coherencia_dialogica < 0.85

    async def test_coherence_lower_than_high_quality(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        good = _high_quality_conversation(seed.seed_id)
        bad = _incoherent_conversation(seed.seed_id)

        good_report = await evaluator.evaluate(good, seed)
        bad_report = await evaluator.evaluate(bad, seed)

        assert bad_report.metrics.coherencia_dialogica < good_report.metrics.coherencia_dialogica


class TestKnownScorePIIContaminated:
    """Tests for PII-contaminated conversation — privacy gate kills composite score."""

    async def test_privacy_score_is_nonzero(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _pii_contaminated_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        assert report.metrics.privacy_score > 0.0

    async def test_composite_score_is_zero(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _pii_contaminated_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # PII gate: any PII → composite = 0.0
        assert report.composite_score == 0.0

    async def test_evaluation_fails(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _pii_contaminated_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        assert report.passed is False
        assert any("privacy_score" in f for f in report.failures)

    async def test_multiple_pii_types_detected(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _pii_contaminated_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # With email + phone + SSN, privacy score should be significant
        assert report.metrics.privacy_score >= 0.05


class TestKnownScoreMinimalConversation:
    """Tests for a very short conversation — metrics should degrade."""

    async def test_short_conversation_evaluates(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _minimal_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Should still produce a valid report
        assert 0.0 <= report.composite_score <= 1.0

    async def test_fidelity_lower_than_full_conversation(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        good = _high_quality_conversation(seed.seed_id)
        short = _minimal_conversation(seed.seed_id)

        good_report = await evaluator.evaluate(good, seed)
        short_report = await evaluator.evaluate(short, seed)

        # 2-turn "Hola/Hola" can't match the flow of a 10-turn detailed conversation
        assert short_report.metrics.fidelidad_factual <= good_report.metrics.fidelidad_factual


class TestKnownScoreSingleRole:
    """Tests for a conversation with no role alternation."""

    async def test_coherence_penalized_for_no_alternation(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _single_role_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # No role alternation should lower coherence
        assert report.metrics.coherencia_dialogica < 0.90

    async def test_fidelity_penalized_for_missing_role(self, evaluator: ConversationEvaluator) -> None:
        seed = _make_automotive_seed()
        conv = _single_role_conversation(seed.seed_id)

        report = await evaluator.evaluate(conv, seed)

        # Only "vendedor" present but seed expects "vendedor" + "cliente"
        assert report.metrics.fidelidad_factual < 0.95


# ─── Composite score formula tests ───


class TestCompositeScoreFormula:
    """Tests for the composite score computation formula."""

    def test_all_passing_metrics(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.80,
            fidelidad_factual=0.95,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.90,
            privacy_score=0.0,
            memorizacion=0.005,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.70  # min of the four quality dimensions
        assert passed is True
        assert failures == []

    def test_privacy_gate_kills_score(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.90,
            fidelidad_factual=0.95,
            diversidad_lexica=0.80,
            coherencia_dialogica=0.95,
            privacy_score=0.01,  # Any PII
            memorizacion=0.0,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.0
        assert passed is False
        assert any("privacy_score" in f for f in failures)

    def test_memorization_gate_kills_score(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.90,
            fidelidad_factual=0.95,
            diversidad_lexica=0.80,
            coherencia_dialogica=0.95,
            privacy_score=0.0,
            memorizacion=0.01,  # At threshold (>= 0.01 fails)
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.0
        assert passed is False
        assert any("memorizacion" in f for f in failures)

    def test_both_gates_failed(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.90,
            fidelidad_factual=0.95,
            diversidad_lexica=0.80,
            coherencia_dialogica=0.95,
            privacy_score=0.05,
            memorizacion=0.02,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.0
        assert passed is False
        assert len(failures) >= 2

    def test_single_metric_below_threshold(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.50,  # Below 0.65 threshold
            fidelidad_factual=0.95,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.90,
            privacy_score=0.0,
            memorizacion=0.0,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.50  # min() still works, just below threshold
        assert passed is False
        assert any("rouge_l" in f for f in failures)

    def test_all_metrics_below_threshold(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.30,
            fidelidad_factual=0.40,
            diversidad_lexica=0.20,
            coherencia_dialogica=0.50,
            privacy_score=0.0,
            memorizacion=0.0,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.20  # min of all four
        assert passed is False
        assert len(failures) == 4

    def test_perfect_scores(self) -> None:
        metrics = QualityMetrics(
            rouge_l=1.0,
            fidelidad_factual=1.0,
            diversidad_lexica=1.0,
            coherencia_dialogica=1.0,
            privacy_score=0.0,
            memorizacion=0.0,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 1.0
        assert passed is True
        assert failures == []

    def test_minimum_passing_scores(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.65,
            fidelidad_factual=0.90,
            diversidad_lexica=0.55,
            coherencia_dialogica=0.85,
            privacy_score=0.0,
            memorizacion=0.009,
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score == 0.55  # min of the four
        assert passed is True
        assert failures == []

    def test_memorization_just_below_threshold_passes(self) -> None:
        metrics = QualityMetrics(
            rouge_l=0.80,
            fidelidad_factual=0.95,
            diversidad_lexica=0.70,
            coherencia_dialogica=0.90,
            privacy_score=0.0,
            memorizacion=0.009,  # Just below 0.01
        )

        score, passed, failures = compute_composite_score(metrics)

        assert score > 0.0
        assert not any("memorizacion" in f for f in failures)


# ─── Cross-domain evaluation tests ───


class TestCrossDomainEvaluation:
    """Tests ensuring the evaluator works consistently across all domains."""

    @pytest.mark.parametrize(
        "domain",
        [
            "automotive.sales",
            "medical.consultation",
            "legal.advisory",
            "finance.advisory",
            "industrial.support",
            "education.tutoring",
        ],
    )
    async def test_evaluation_produces_valid_report_for_domain(
        self, evaluator: ConversationEvaluator, domain: str
    ) -> None:
        seed = make_seed(dominio=domain)
        conv = Conversation(
            seed_id=seed.seed_id,
            dominio=domain,
            idioma="es",
            turnos=[
                ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle con su consulta?"),
                ConversationTurn(turno=2, rol="cliente", contenido="Necesito informacion detallada sobre el servicio."),
                ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto le explico las opciones disponibles para usted."),
                ConversationTurn(turno=4, rol="cliente", contenido="Perfecto, me interesa saber mas sobre los costos y requisitos."),
                ConversationTurn(turno=5, rol="vendedor", contenido="Los costos varian segun el plan elegido. Permita mostrarle la tabla."),
                ConversationTurn(turno=6, rol="cliente", contenido="Gracias por la informacion, lo voy a considerar con detenimiento."),
            ],
            es_sintetica=True,
        )

        report = await evaluator.evaluate(conv, seed)

        assert report.conversation_id == conv.conversation_id
        assert report.seed_id == seed.seed_id
        assert 0.0 <= report.composite_score <= 1.0
        assert 0.0 <= report.metrics.rouge_l <= 1.0
        assert 0.0 <= report.metrics.fidelidad_factual <= 1.0
        assert 0.0 <= report.metrics.diversidad_lexica <= 1.0
        assert 0.0 <= report.metrics.coherencia_dialogica <= 1.0
        assert report.metrics.privacy_score == 0.0
        assert report.metrics.memorizacion == 0.0
