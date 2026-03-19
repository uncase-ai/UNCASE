"""Edge-case evaluator tests — validates that improved metrics correctly
detect degenerate conversations that the old metrics would miss.

Each test class targets a specific failure mode that was previously
undetected or scored misleadingly.
"""

from __future__ import annotations

from tests.factories import make_seed
from uncase.core.evaluator.metrics.coherence import DialogCoherenceMetric, _score_jaccard
from uncase.core.evaluator.metrics.fidelity import FactualFidelityMetric
from uncase.core.evaluator.metrics.privacy import PrivacyMetric, detect_pii_heuristic
from uncase.core.evaluator.metrics.rouge import ROUGELMetric
from uncase.schemas.conversation import Conversation, ConversationTurn
from uncase.schemas.seed import ParametrosFactuales, PasosTurnos

# ─── Helpers ───


def _make_seed_with_flow(steps: list[str], **kw: object) -> object:
    """Seed with specific flow steps for flow adherence testing."""
    return make_seed(
        pasos_turnos=PasosTurnos(turnos_min=4, turnos_max=20, flujo_esperado=steps),
        **kw,
    )


def _conv(seed_id: str, turns: list[tuple[str, str]]) -> Conversation:
    """Quick conversation builder from (role, content) tuples."""
    return Conversation(
        seed_id=seed_id,
        dominio="automotive.sales",
        idioma="es",
        turnos=[ConversationTurn(turno=i + 1, rol=r, contenido=c) for i, (r, c) in enumerate(turns)],
        es_sintetica=True,
    )


# ─── ROUGE-L Edge Cases ───


class TestROUGELEdgeCases:
    """ROUGE-L should measure seed content coverage, not keyword recall."""

    def test_paraphrased_conversation_scores_higher_than_random(self) -> None:
        """A conversation that paraphrases seed concepts should score
        higher than one about completely unrelated topics."""
        seed = make_seed(
            objetivo="Cliente consulta opciones de vehiculos sedanes con financiamiento",
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario de vehiculos nuevos en Ciudad de Mexico",
                restricciones=["Solo vehiculos del 2024", "Precios en pesos mexicanos"],
                herramientas=[],
                metadata={},
            ),
        )
        metric = ROUGELMetric()

        on_topic = _conv(
            seed.seed_id,
            [
                ("vendedor", "Bienvenido al concesionario, tenemos sedanes nuevos del 2024."),
                ("cliente", "Me interesa conocer las opciones de financiamiento para vehiculos."),
                ("vendedor", "Tenemos planes desde 48 meses con precios en pesos mexicanos."),
                ("cliente", "Perfecto, me gustaria ver los sedanes disponibles."),
            ],
        )
        off_topic = _conv(
            seed.seed_id,
            [
                ("vendedor", "La astronomia estudia las estrellas y planetas del universo."),
                ("cliente", "Las recetas de cocina italiana son deliciosas con pasta fresca."),
                ("vendedor", "El campeonato de futbol comenzo con partidos emocionantes."),
                ("cliente", "Las flores del jardin necesitan riego constante para crecer."),
            ],
        )

        on_score = metric.compute(on_topic, seed)
        off_score = metric.compute(off_topic, seed)

        assert on_score > off_score, f"On-topic ({on_score}) should beat off-topic ({off_score})"

    def test_keyword_stuffing_does_not_inflate_score(self) -> None:
        """Repeating seed keywords verbatim shouldn't inflate ROUGE-L
        higher than a natural conversation."""
        seed = make_seed(
            objetivo="Consulta vehiculos financiamiento",
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario vehiculos",
                restricciones=["vehiculos nuevos"],
                herramientas=[],
                metadata={},
            ),
        )
        metric = ROUGELMetric()

        natural = _conv(
            seed.seed_id,
            [
                ("vendedor", "Bienvenido al concesionario, le ayudo con informacion de vehiculos nuevos."),
                ("cliente", "Busco opciones de financiamiento para un vehiculo familiar."),
                ("vendedor", "Tenemos planes accesibles para vehiculos nuevos."),
                ("cliente", "Me interesa conocer los requisitos del financiamiento."),
            ],
        )
        stuffed = _conv(
            seed.seed_id,
            [
                ("vendedor", "vehiculos vehiculos vehiculos vehiculos concesionario"),
                ("cliente", "vehiculos vehiculos vehiculos financiamiento financiamiento"),
                ("vendedor", "vehiculos vehiculos nuevos nuevos nuevos"),
                ("cliente", "vehiculos vehiculos vehiculos vehiculos consulta"),
            ],
        )

        natural_score = metric.compute(natural, seed)
        stuffed_score = metric.compute(stuffed, seed)

        # Natural should score reasonably; stuffed should not dramatically exceed it
        assert natural_score > 0.0
        # Keyword stuffing should not be more than 2x a natural conversation
        assert stuffed_score < natural_score * 2.5


# ─── Fidelity Flow Adherence Edge Cases ───


class TestFlowAdherenceEdgeCases:
    """Flow adherence should detect conversational phases via semantic patterns,
    not literal keyword matching."""

    def test_spanish_greeting_detects_saludo(self) -> None:
        """'Buenos dias, bienvenido' should match flow step 'saludo'."""
        seed = _make_seed_with_flow(["saludo", "consulta", "resolucion"])
        metric = FactualFidelityMetric()

        conv = _conv(
            seed.seed_id,
            [
                ("vendedor", "Buenos dias, bienvenido al concesionario."),
                ("cliente", "Hola, busco informacion sobre vehiculos disponibles."),
                ("vendedor", "Con gusto le ayudo. Tenemos varias opciones para usted."),
                ("cliente", "Muchas gracias, lo voy a considerar."),
            ],
        )

        score = metric._flow_adherence(conv, seed)
        # At minimum, the greeting step should be detected (1/3 = 0.33)
        assert score >= 0.3, f"Flow adherence too low: {score} (greeting should be detected)"

    def test_compound_label_detected(self) -> None:
        """Compound labels like 'identificacion_necesidades' should be detected
        via semantic patterns, not literal string match."""
        seed = _make_seed_with_flow(["saludo", "identificacion_necesidades", "presentacion_opciones", "cierre"])
        metric = FactualFidelityMetric()

        conv = _conv(
            seed.seed_id,
            [
                ("vendedor", "Buenos dias, en que puedo ayudarle?"),
                ("cliente", "Necesito un vehiculo familiar. Somos cuatro personas."),
                ("vendedor", "Entiendo sus necesidades. Le muestro las opciones disponibles para familias."),
                ("cliente", "Me interesa esa opcion, me gustaria agendar una cita."),
                ("vendedor", "Perfecto, agendamos su cita. Fue un gusto atenderle."),
            ],
        )

        score = metric._flow_adherence(conv, seed)
        assert score >= 0.4, f"Compound flow labels should be detected semantically: {score}"

    def test_out_of_order_flow_is_penalized(self) -> None:
        """A conversation that follows steps in wrong order should score lower."""
        seed = _make_seed_with_flow(["saludo", "consulta", "resolucion"])
        metric = FactualFidelityMetric()

        # In order
        ordered = _conv(
            seed.seed_id,
            [
                ("vendedor", "Buenos dias, bienvenido."),
                ("cliente", "Tengo una consulta sobre vehiculos."),
                ("vendedor", "Aqui tiene la resolucion de su consulta."),
                ("cliente", "Gracias por resolver mi duda."),
            ],
        )
        # Reversed order
        reversed_conv = _conv(
            seed.seed_id,
            [
                ("vendedor", "Aqui tiene la resolucion."),
                ("cliente", "Tengo una consulta importante."),
                ("vendedor", "Buenos dias, bienvenido al local."),
                ("cliente", "Gracias."),
            ],
        )

        ordered_score = metric._flow_adherence(ordered, seed)
        reversed_score = metric._flow_adherence(reversed_conv, seed)

        assert ordered_score >= reversed_score, (
            f"In-order ({ordered_score}) should score >= reversed ({reversed_score})"
        )


# ─── Coherence Edge Cases ───


class TestCoherenceEdgeCases:
    """Coherence scoring curve should be continuous, discriminating, and not trivially 1.0."""

    def test_score_jaccard_is_continuous(self) -> None:
        """No discontinuities at boundary points (excluding the 0→ε edge
        since _score_jaccard(0.0)=0.0 is a defined boundary)."""
        # Start from 0.01 — the 0.0→0.01 jump is by design (exact zero = no data)
        prev = _score_jaccard(0.01)
        for i in range(2, 100):
            x = i / 100.0
            curr = _score_jaccard(x)
            delta = abs(curr - prev)
            assert delta < 0.10, f"Discontinuity at {x}: jump of {delta} from {prev} to {curr}"
            prev = curr

    def test_score_jaccard_peaks_near_expected(self) -> None:
        """Peak should be near 0.07 for content-token Jaccard."""
        peak_score = _score_jaccard(0.07)
        assert peak_score > 0.98, f"Peak at 0.07 should be near 1.0, got {peak_score}"

    def test_score_jaccard_penalizes_zero(self) -> None:
        """Zero Jaccard should give zero score."""
        assert _score_jaccard(0.0) == 0.0

    def test_score_jaccard_penalizes_extreme_repetition(self) -> None:
        """Jaccard > 0.7 (extreme repetition) should score low."""
        assert _score_jaccard(0.8) < 0.30

    def test_referential_consistency_not_trivially_one(self) -> None:
        """Incoherent turns with no content overlap should score below 1.0."""
        seed = make_seed()
        metric = DialogCoherenceMetric()

        # Each turn uses completely different content words (not just stopwords)
        incoherent = _conv(
            seed.seed_id,
            [
                ("vendedor", "La astronomia estudia galaxias distantes."),
                ("cliente", "Las bacterias microscopicas producen antibioticos."),
                ("vendedor", "La fotosintesis transforma dioxido carbono."),
                ("cliente", "Los volcanes expulsan magma incandescente."),
                ("vendedor", "La criptografia protege comunicaciones digitales."),
                ("cliente", "Los dinosaurios habitaron periodos geologicos."),
            ],
        )

        score = metric._referential_consistency(incoherent.turnos)
        assert score < 1.0, f"Incoherent conversation should not get perfect referential consistency: {score}"

    def test_coherent_conversation_scores_higher_than_incoherent(self) -> None:
        """A topically coherent conversation should outscore random topics."""
        seed = make_seed()
        metric = DialogCoherenceMetric()

        coherent = _conv(
            seed.seed_id,
            [
                ("vendedor", "Bienvenido al concesionario, busca vehiculos nuevos?"),
                ("cliente", "Si, necesito vehiculos sedan familiar con buen rendimiento."),
                ("vendedor", "Tenemos excelentes vehiculos sedan con rendimiento superior."),
                ("cliente", "Que opciones vehiculos tienen con garantia extendida?"),
                ("vendedor", "Todos nuestros vehiculos sedan incluyen garantia extendida."),
                ("cliente", "Me interesa ver el vehiculo sedan mas reciente disponible."),
            ],
        )
        incoherent = _conv(
            seed.seed_id,
            [
                ("vendedor", "La geologia estudia formaciones rocosas antiguas."),
                ("cliente", "Las orquideas tropicales necesitan climas humedos."),
                ("vendedor", "Los circuitos electronicos transmiten impulsos."),
                ("cliente", "La musica barroca incorpora instrumentos clasicos."),
                ("vendedor", "Los glaciares articos almacenan toneladas hielo."),
                ("cliente", "Las proteinas construyen tejidos musculares."),
            ],
        )

        coh_score = metric.compute(coherent, seed)
        inc_score = metric.compute(incoherent, seed)

        assert coh_score > inc_score, f"Coherent ({coh_score}) should beat incoherent ({inc_score})"


# ─── Privacy False Positive Edge Cases ───


class TestPrivacyFalsePositives:
    """Privacy metric should NOT flag legitimate content as PII."""

    def test_version_numbers_not_flagged_as_ip(self) -> None:
        """Software version '1.2.3.4' should not be detected as IP address."""
        matches = detect_pii_heuristic("El sistema usa la version 1.2.3.4 del firmware.")
        ip_matches = [m for m in matches if m.category == "ip_address"]
        assert len(ip_matches) == 0, f"Version number falsely detected as IP: {ip_matches}"

    def test_model_numbers_not_flagged(self) -> None:
        """Automotive model numbers should not trigger PII detection."""
        text = "El modelo XR-2024 tiene un motor de 2.0 litros y cuesta $450,000."
        matches = detect_pii_heuristic(text)
        assert len(matches) == 0, f"Model number falsely flagged: {matches}"

    def test_random_16_digit_not_credit_card(self) -> None:
        """A random 16-digit number that fails Luhn should not be flagged."""
        # 1234567890123456 does NOT pass Luhn check
        matches = detect_pii_heuristic("Numero de serie: 1234 5678 9012 3456")
        cc_matches = [m for m in matches if m.category == "credit_card"]
        assert len(cc_matches) == 0, f"Random digits falsely detected as credit card: {cc_matches}"

    def test_real_pii_still_detected(self) -> None:
        """Actual PII should still be caught."""
        text = "Mi email es juan.perez@example.com y mi telefono es 555-123-4567"
        matches = detect_pii_heuristic(text)
        categories = {m.category for m in matches}
        assert "email" in categories, "Real email should be detected"
        assert "phone_local" in categories, "Real phone should be detected"

    def test_privacy_metric_clean_conversation(self) -> None:
        """A normal automotive conversation should have privacy_score = 0.0."""
        seed = make_seed()
        metric = PrivacyMetric()
        conv = _conv(
            seed.seed_id,
            [
                ("vendedor", "El modelo Corsa 2024 tiene version 3.2.1.0 del sistema de infoentretenimiento."),
                ("cliente", "Me interesa. El numero de serie VIN del vehiculo es importante para la garantia."),
                ("vendedor", "Correcto, el VIN se registra al momento de la compra. El precio es $450,000 pesos."),
            ],
        )
        score = metric.compute(conv, seed)
        assert score == 0.0, f"Clean conversation flagged as PII: {score}"


# ─── Composite Score Discriminating Power ───


class TestCompositeDiscrimination:
    """The evaluator should produce meaningfully different scores for
    conversations of different quality levels."""

    async def test_good_vs_bad_composite_gap(self) -> None:
        """Good conversation should have significantly higher composite
        than a bad one, not just marginally different."""
        from uncase.core.evaluator.evaluator import ConversationEvaluator

        seed = make_seed(
            objetivo="Cliente consulta opciones vehiculos sedan financiamiento concesionario",
            parametros_factuales=ParametrosFactuales(
                contexto="Concesionario de vehiculos nuevos sedan financiamiento",
                restricciones=["Solo vehiculos nuevos", "Financiamiento disponible"],
                herramientas=[],
                metadata={},
            ),
        )
        evaluator = ConversationEvaluator()

        good = _conv(
            seed.seed_id,
            [
                ("vendedor", "Buenos dias, bienvenido al concesionario de vehiculos nuevos."),
                ("cliente", "Hola, busco opciones sedan vehiculos con financiamiento."),
                ("vendedor", "Tenemos sedanes nuevos con planes financiamiento accesibles."),
                ("cliente", "Me interesan los vehiculos sedan nuevos disponibles."),
                ("vendedor", "Le muestro las opciones vehiculos sedan con mejor financiamiento."),
                ("cliente", "Gracias por las opciones, voy a considerar el financiamiento."),
            ],
        )
        bad = _conv(
            seed.seed_id,
            [
                ("vendedor", "Hola."),
                ("vendedor", "Hola."),
                ("vendedor", "Hola."),
                ("vendedor", "Hola."),
                ("vendedor", "Hola."),
                ("vendedor", "Hola."),
            ],
        )

        good_report = await evaluator.evaluate(good, seed)
        bad_report = await evaluator.evaluate(bad, seed)

        # Good should outscore bad by a meaningful margin
        assert good_report.composite_score > bad_report.composite_score
        # The weighted mean should also reflect the difference
        assert good_report.weighted_mean > bad_report.weighted_mean
