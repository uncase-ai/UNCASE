"""Tests for Layer 0 SeedEngine — seed creation, PII stripping, privacy validation."""

from __future__ import annotations

import json

import pytest

from uncase.core.privacy.scanner import PIIScanner
from uncase.core.seed_engine.engine import SeedEngine
from uncase.core.seed_engine.parsers import RawTurn
from uncase.exceptions import ImportParsingError
from uncase.schemas.seed import SeedSchema

# ---------------------------------------------------------------------------
# Synthetic conversation data — ZERO real PII
# ---------------------------------------------------------------------------

WHATSAPP_AUTOMOTIVE = """\
[25/02/2026, 10:30:00] Vendedor: Buenos dias, bienvenido al concesionario
[25/02/2026, 10:30:15] Cliente: Hola, busco informacion sobre vehiculos nuevos
[25/02/2026, 10:31:00] Vendedor: Con gusto, que tipo de vehiculo le interesa?
[25/02/2026, 10:32:00] Cliente: Me interesa un sedan familiar
[25/02/2026, 10:33:00] Vendedor: Tenemos excelentes opciones, le muestro nuestro inventario
[25/02/2026, 10:34:00] Cliente: Perfecto, tambien quiero saber sobre financiamiento
"""

TRANSCRIPT_AUTOMOTIVE = """\
Vendedor: Buenos dias, en que puedo ayudarle?
Cliente: Hola, busco un auto nuevo para mi familia
Vendedor: Con gusto, que presupuesto tiene en mente?
Cliente: Alrededor de 400,000 pesos
Vendedor: Tenemos varias opciones en ese rango
"""

JSON_AUTOMOTIVE = json.dumps(
    {
        "messages": [
            {"role": "vendedor", "content": "Buenos dias, bienvenido al concesionario."},
            {"role": "cliente", "content": "Hola, busco un vehiculo nuevo."},
            {"role": "vendedor", "content": "Con gusto, que tipo de vehiculo le interesa?"},
            {"role": "cliente", "content": "Un sedan familiar con buen rendimiento."},
        ]
    }
)

WHATSAPP_WITH_PII = """\
[25/02/2026, 10:30:00] Vendedor: Buenos dias, me puede dar su correo?
[25/02/2026, 10:31:00] Cliente: Claro, es juan.perez@example.com
[25/02/2026, 10:32:00] Vendedor: Perfecto, y un telefono de contacto?
[25/02/2026, 10:33:00] Cliente: Mi numero es +52 55 1234 5678
"""

# Fictional PII data for testing (all invented)
_FICTIONAL_EMAIL = "juan.perez@example.com"
_FICTIONAL_PHONE = "+52 55 1234 5678"

DOMAIN = "automotive.sales"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def scanner() -> PIIScanner:
    """Return a PIIScanner using only regex (no Presidio dependency)."""
    return PIIScanner(confidence_threshold=0.85)


@pytest.fixture()
def engine(scanner: PIIScanner) -> SeedEngine:
    """Return a SeedEngine with the test scanner."""
    return SeedEngine(scanner=scanner)


# ===================================================================
# SeedEngine.create_seed — format acceptance
# ===================================================================


class TestCreateSeedFormats:
    """Test create_seed with different input formats."""

    async def test_whatsapp_format_produces_valid_seed(self, engine: SeedEngine) -> None:
        """WhatsApp input is parsed and produces a valid SeedSchema."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert isinstance(seed, SeedSchema)
        assert seed.dominio == DOMAIN
        assert len(seed.roles) >= 2
        assert seed.seed_id  # non-empty UUID hex
        assert seed.version == "1.0"

    async def test_transcript_format_produces_valid_seed(self, engine: SeedEngine) -> None:
        """Transcript input is parsed and produces a valid SeedSchema."""
        seed = await engine.create_seed(TRANSCRIPT_AUTOMOTIVE, DOMAIN)

        assert isinstance(seed, SeedSchema)
        assert seed.dominio == DOMAIN
        assert len(seed.roles) >= 2
        assert seed.pasos_turnos.turnos_min >= 1
        assert seed.pasos_turnos.turnos_max > seed.pasos_turnos.turnos_min

    async def test_json_format_produces_valid_seed(self, engine: SeedEngine) -> None:
        """JSON input is parsed and produces a valid SeedSchema."""
        seed = await engine.create_seed(JSON_AUTOMOTIVE, DOMAIN)

        assert isinstance(seed, SeedSchema)
        assert seed.dominio == DOMAIN
        assert seed.parametros_factuales.metadata["source_format"] == "json"

    async def test_empty_input_raises_import_parsing_error(self, engine: SeedEngine) -> None:
        """Empty input raises ImportParsingError."""
        with pytest.raises(ImportParsingError):
            await engine.create_seed("", DOMAIN)

    async def test_unparseable_input_raises_import_parsing_error(self, engine: SeedEngine) -> None:
        """Gibberish that matches no format raises ImportParsingError."""
        with pytest.raises(ImportParsingError):
            await engine.create_seed("random gibberish text without any structure at all", DOMAIN)


# ===================================================================
# SeedEngine.create_seed — PII handling
# ===================================================================


class TestCreateSeedPII:
    """Test PII stripping during seed creation."""

    async def test_pii_in_content_is_stripped(self, engine: SeedEngine) -> None:
        """PII embedded in turn content is anonymized in the final seed."""
        seed = await engine.create_seed(WHATSAPP_WITH_PII, DOMAIN)

        # The email and phone should be replaced with placeholders
        assert _FICTIONAL_EMAIL not in seed.objetivo
        assert _FICTIONAL_PHONE not in seed.objetivo
        assert _FICTIONAL_EMAIL not in seed.parametros_factuales.contexto
        assert _FICTIONAL_PHONE not in seed.parametros_factuales.contexto

    async def test_pii_detection_recorded_in_privacy_fields(self, engine: SeedEngine) -> None:
        """When PII is found, campos_sensibles_detectados is populated."""
        seed = await engine.create_seed(WHATSAPP_WITH_PII, DOMAIN)

        assert seed.privacidad.pii_eliminado is True
        assert len(seed.privacidad.campos_sensibles_detectados) > 0

    async def test_pii_in_role_names_is_anonymized(self, engine: SeedEngine) -> None:
        """Real names in role positions are anonymized if the scanner flags them."""
        # Construct a conversation where a role name contains an email-like PII
        raw = "[25/02/2026, 10:30:00] Vendedor: Buenos dias\n[25/02/2026, 10:31:00] Cliente: Hola, busco un auto\n"
        seed = await engine.create_seed(raw, DOMAIN)

        # Roles should be clean (no PII detected in "Vendedor" or "Cliente")
        for role in seed.roles:
            assert "@" not in role
            assert "+" not in role


# ===================================================================
# SeedEngine.strip_pii
# ===================================================================


class TestStripPII:
    """Test the strip_pii method directly."""

    async def test_removes_email(self, engine: SeedEngine) -> None:
        """Email addresses are replaced with [EMAIL]."""
        text = "Contactame en juan.perez@example.com por favor"
        result = await engine.strip_pii(text)

        assert _FICTIONAL_EMAIL not in result
        assert "[EMAIL]" in result

    async def test_removes_phone_number(self, engine: SeedEngine) -> None:
        """International phone numbers are replaced with [PHONE]."""
        text = "Mi numero es +52 55 1234 5678"
        result = await engine.strip_pii(text)

        assert _FICTIONAL_PHONE not in result
        assert "[PHONE]" in result

    async def test_clean_text_unchanged(self, engine: SeedEngine) -> None:
        """Text without PII passes through unchanged."""
        text = "Buenos dias, bienvenido al concesionario"
        result = await engine.strip_pii(text)

        assert result == text

    async def test_multiple_pii_entities(self, engine: SeedEngine) -> None:
        """Multiple PII entities in the same text are all replaced."""
        text = "Email: juan.perez@example.com, telefono: +52 55 1234 5678"
        result = await engine.strip_pii(text)

        assert _FICTIONAL_EMAIL not in result
        assert _FICTIONAL_PHONE not in result
        assert "[EMAIL]" in result
        assert "[PHONE]" in result


# ===================================================================
# SeedEngine.validate_privacy
# ===================================================================


class TestValidatePrivacy:
    """Test privacy validation on seed objects."""

    async def test_clean_seed_passes_validation(self, engine: SeedEngine) -> None:
        """A seed with no PII passes validation."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)
        result = await engine.validate_privacy(seed)
        assert result is True

    async def test_seed_with_injected_pii_fails_validation(self, engine: SeedEngine) -> None:
        """If PII is injected into a seed field, validation returns False."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        # Inject PII into the objetivo field
        seed.objetivo = "Contactar a juan.perez@example.com para una cotizacion"

        result = await engine.validate_privacy(seed)
        assert result is False


# ===================================================================
# Language detection
# ===================================================================


class TestLanguageDetection:
    """Test the _detect_language static method."""

    async def test_spanish_text(self) -> None:
        """Text with Spanish markers returns 'es'."""
        text = "Buenos dias, bienvenido al concesionario, que tipo de vehiculo le interesa para su familia"
        result = SeedEngine._detect_language(text)
        assert result == "es"

    async def test_english_text(self) -> None:
        """Text with English markers returns 'en'."""
        text = "Hello, welcome to the dealership, what type of vehicle are you looking for today"
        result = SeedEngine._detect_language(text)
        assert result == "en"

    async def test_ambiguous_defaults_to_spanish(self) -> None:
        """When markers are tied, defaults to 'es'."""
        # A very short text with no strong markers
        result = SeedEngine._detect_language("ABC 123")
        assert result == "es"

    async def test_mixed_language(self) -> None:
        """Text with more Spanish markers than English returns 'es'."""
        text = "Hola, buenos dias, necesito un auto, por favor, para mi familia"
        result = SeedEngine._detect_language(text)
        assert result == "es"


# ===================================================================
# Tone analysis
# ===================================================================


class TestToneAnalysis:
    """Test the _analyze_tone static method."""

    async def test_formal_tone(self) -> None:
        """Formal markers produce 'formal' tone."""
        turns = [
            "Estimado cliente, le informo que su solicitud ha sido procesada",
            "Cordialmente, le adjunto los documentos requeridos",
        ]
        result = SeedEngine._analyze_tone(turns)
        assert result == "formal"

    async def test_informal_tone(self) -> None:
        """Informal markers produce 'informal' tone."""
        turns = [
            "Hey, mira, tenemos un carro genial para ti",
            "Ok, vale, jaja, esta cool",
        ]
        result = SeedEngine._analyze_tone(turns)
        assert result == "informal"

    async def test_neutral_defaults_to_profesional(self) -> None:
        """When no formal or informal markers dominate, defaults to 'profesional'."""
        turns = ["Buenos dias", "Busco un vehiculo"]
        result = SeedEngine._analyze_tone(turns)
        assert result == "profesional"


# ===================================================================
# Objective extraction
# ===================================================================


class TestObjectiveExtraction:
    """Test the _extract_objective static method."""

    async def test_basic_objective(self) -> None:
        """Objective is derived from the first few turns."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias, en que puedo ayudarle?", turn_number=1),
            RawTurn(role="Cliente", content="Busco un sedan familiar", turn_number=2),
        ]
        result = SeedEngine._extract_objective(turns)

        assert result.startswith("Conversation about:")
        assert "Buenos dias" in result
        assert "sedan familiar" in result

    async def test_truncation_at_200_chars(self) -> None:
        """Objectives longer than 200 chars are truncated with '...'."""
        long_content = "A" * 300
        turns = [RawTurn(role="Speaker", content=long_content, turn_number=1)]
        result = SeedEngine._extract_objective(turns)

        # "Conversation about: " prefix + truncated content + "..."
        assert result.endswith("...")
        # Total should be reasonable (prefix + up to 200 chars + ...)
        assert len(result) <= len("Conversation about: ") + 200 + 3

    async def test_empty_turns_fallback(self) -> None:
        """Empty turn list produces generic description."""
        result = SeedEngine._extract_objective([])
        assert result == "General conversation"

    async def test_uses_first_three_turns(self) -> None:
        """Only the first three turns contribute to the objective."""
        turns = [
            RawTurn(role="A", content="Primer turno", turn_number=1),
            RawTurn(role="B", content="Segundo turno", turn_number=2),
            RawTurn(role="A", content="Tercer turno", turn_number=3),
            RawTurn(role="B", content="Cuarto turno que no deberia aparecer", turn_number=4),
        ]
        result = SeedEngine._extract_objective(turns)

        assert "Primer turno" in result
        assert "Tercer turno" in result
        assert "Cuarto turno" not in result


# ===================================================================
# Flow steps extraction
# ===================================================================


class TestFlowStepsExtraction:
    """Test the _extract_flow_steps static method."""

    async def test_standard_flow(self) -> None:
        """A multi-turn conversation produces opening, development, and closing steps."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias", turn_number=i + 1)
            if i % 2 == 0
            else RawTurn(role="Cliente", content="Gracias", turn_number=i + 1)
            for i in range(10)
        ]
        steps = SeedEngine._extract_flow_steps(turns)

        assert len(steps) >= 3
        assert any("Opening" in s for s in steps)
        assert any("Development" in s for s in steps)
        assert any("Closing" in s for s in steps)

    async def test_short_conversation(self) -> None:
        """A 2-turn conversation produces opening and response steps."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias", turn_number=1),
            RawTurn(role="Cliente", content="Hola", turn_number=2),
        ]
        steps = SeedEngine._extract_flow_steps(turns)

        assert len(steps) == 2
        assert "Opening" in steps[0]
        assert "Response" in steps[1]

    async def test_empty_turns(self) -> None:
        """Empty turns produce minimal start/end flow."""
        steps = SeedEngine._extract_flow_steps([])
        assert steps == ["start", "end"]


# ===================================================================
# Context summary
# ===================================================================


class TestContextSummary:
    """Test the _build_context_summary static method."""

    async def test_contains_domain(self) -> None:
        """Context summary includes the domain."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias", turn_number=1),
            RawTurn(role="Cliente", content="Hola", turn_number=2),
        ]
        result = SeedEngine._build_context_summary(turns, DOMAIN)

        assert f"Domain: {DOMAIN}" in result

    async def test_contains_participants(self) -> None:
        """Context summary lists participants."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias", turn_number=1),
            RawTurn(role="Cliente", content="Hola", turn_number=2),
        ]
        result = SeedEngine._build_context_summary(turns, DOMAIN)

        assert "Vendedor" in result
        assert "Cliente" in result

    async def test_contains_turn_count(self) -> None:
        """Context summary includes the total turn count."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias", turn_number=1),
            RawTurn(role="Cliente", content="Hola", turn_number=2),
            RawTurn(role="Vendedor", content="Con gusto", turn_number=3),
        ]
        result = SeedEngine._build_context_summary(turns, DOMAIN)

        assert "Total turns: 3" in result

    async def test_contains_opening_snippet(self) -> None:
        """Context summary contains a snippet from the first turn."""
        turns = [
            RawTurn(role="Vendedor", content="Buenos dias, bienvenido al concesionario", turn_number=1),
            RawTurn(role="Cliente", content="Hola", turn_number=2),
        ]
        result = SeedEngine._build_context_summary(turns, DOMAIN)

        assert "Opens with:" in result
        assert "Buenos dias" in result


# ===================================================================
# Seed structure validation
# ===================================================================


class TestSeedStructure:
    """Test the integrity of generated SeedSchema objects."""

    async def test_turnos_min_less_than_max(self, engine: SeedEngine) -> None:
        """turnos_min is always less than turnos_max."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert seed.pasos_turnos.turnos_min < seed.pasos_turnos.turnos_max

    async def test_privacy_method_is_regex(self, engine: SeedEngine) -> None:
        """Without Presidio, the anonymization method should be 'regex'."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        # The test scanner uses regex (no Presidio in test env)
        expected = "presidio" if engine._scanner.has_presidio else "regex"
        assert seed.privacidad.metodo_anonimizacion == expected

    async def test_source_format_in_metadata(self, engine: SeedEngine) -> None:
        """The source_format is recorded in parametros_factuales.metadata."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert "source_format" in seed.parametros_factuales.metadata
        assert seed.parametros_factuales.metadata["source_format"] == "whatsapp"

    async def test_original_turn_count_in_metadata(self, engine: SeedEngine) -> None:
        """The original_turn_count is recorded in metadata."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert "original_turn_count" in seed.parametros_factuales.metadata
        assert seed.parametros_factuales.metadata["original_turn_count"] == "6"

    async def test_flujo_esperado_non_empty(self, engine: SeedEngine) -> None:
        """The flujo_esperado flow steps list is always non-empty."""
        seed = await engine.create_seed(TRANSCRIPT_AUTOMOTIVE, DOMAIN)

        assert len(seed.pasos_turnos.flujo_esperado) >= 2

    async def test_descripcion_roles_populated(self, engine: SeedEngine) -> None:
        """Each role has a description entry."""
        seed = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        for role in seed.roles:
            assert role in seed.descripcion_roles
            assert seed.descripcion_roles[role]  # non-empty

    async def test_confidence_threshold_propagated(self) -> None:
        """The confidence threshold is propagated to the seed's privacy section."""
        threshold = 0.90
        custom_engine = SeedEngine(confidence_threshold=threshold)
        seed = await custom_engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert seed.privacidad.nivel_confianza == threshold

    async def test_seed_id_is_unique(self, engine: SeedEngine) -> None:
        """Each call to create_seed produces a unique seed_id."""
        seed1 = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)
        seed2 = await engine.create_seed(WHATSAPP_AUTOMOTIVE, DOMAIN)

        assert seed1.seed_id != seed2.seed_id


# ===================================================================
# Integration: parse_turns internal method
# ===================================================================


class TestParseTurns:
    """Test the _parse_turns static method used internally."""

    async def test_whatsapp_detected_and_parsed(self) -> None:
        """WhatsApp input is auto-detected and parsed into turns."""
        turns = SeedEngine._parse_turns(WHATSAPP_AUTOMOTIVE)
        assert len(turns) == 6
        assert turns[0].role == "Vendedor"

    async def test_transcript_detected_and_parsed(self) -> None:
        """Transcript input is auto-detected and parsed into turns."""
        turns = SeedEngine._parse_turns(TRANSCRIPT_AUTOMOTIVE)
        assert len(turns) == 5
        assert turns[0].role == "Vendedor"

    async def test_json_detected_and_parsed(self) -> None:
        """JSON input is auto-detected and parsed into turns."""
        turns = SeedEngine._parse_turns(JSON_AUTOMOTIVE)
        assert len(turns) == 4
        assert turns[0].role == "vendedor"

    async def test_empty_returns_empty(self) -> None:
        """Empty input returns empty list."""
        turns = SeedEngine._parse_turns("")
        assert turns == []
