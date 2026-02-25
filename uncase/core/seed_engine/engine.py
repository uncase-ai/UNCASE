"""Seed Engine — Layer 0 implementation.

Takes raw conversations (from WhatsApp exports, CSV transcripts, support tickets)
and converts them into sanitized SeedSchema v1 objects with zero PII.
"""

from __future__ import annotations

from uncase.core.privacy.scanner import PIIScanner
from uncase.core.seed_engine.parsers import (
    JSONConversationParser,
    RawTurn,
    TranscriptParser,
    WhatsAppParser,
    detect_format,
)
from uncase.exceptions import ImportParsingError, PIIDetectedError
from uncase.logging import get_logger
from uncase.schemas.seed import (
    ParametrosFactuales,
    PasosTurnos,
    Privacidad,
    SeedSchema,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Language-detection word lists (kept small and deterministic)
# ---------------------------------------------------------------------------
_SPANISH_MARKERS: frozenset[str] = frozenset(
    {
        "el",
        "la",
        "los",
        "las",
        "de",
        "del",
        "en",
        "un",
        "una",
        "es",
        "que",
        "por",
        "con",
        "para",
        "como",
        "pero",
        "este",
        "esta",
        "su",
        "más",
        "también",
        "tiene",
        "puede",
        "hola",
        "gracias",
        "buenos",
        "buenas",
        "necesito",
        "quiero",
        "favor",
        "usted",
    }
)

_ENGLISH_MARKERS: frozenset[str] = frozenset(
    {
        "the",
        "is",
        "are",
        "was",
        "were",
        "of",
        "and",
        "in",
        "to",
        "for",
        "with",
        "that",
        "this",
        "have",
        "has",
        "can",
        "will",
        "would",
        "should",
        "hello",
        "thanks",
        "please",
        "need",
        "want",
        "help",
        "yes",
        "no",
        "not",
    }
)

# ---------------------------------------------------------------------------
# Tone markers
# ---------------------------------------------------------------------------
_FORMAL_MARKERS: frozenset[str] = frozenset(
    {
        "usted",
        "estimado",
        "estimada",
        "atentamente",
        "cordialmente",
        "le",
        "informo",
        "solicito",
        "adjunto",
        "sir",
        "madam",
        "regards",
        "sincerely",
        "kindly",
        "dear",
        "respectfully",
        "pursuant",
    }
)

_INFORMAL_MARKERS: frozenset[str] = frozenset(
    {
        "hey",
        "hola",
        "oye",
        "mira",
        "bueno",
        "ok",
        "vale",
        "genial",
        "cool",
        "nah",
        "jaja",
        "lol",
        "xd",
        "bro",
        "wey",
        "güey",
        "dude",
        "awesome",
        "yeah",
    }
)


class SeedEngine:
    """Layer 0 — Seed Engine.

    Converts raw conversations into sanitized ``SeedSchema`` v1 objects.

    The engine is purely deterministic (no LLM calls) and relies on regex-based
    PII scanning plus simple NLP heuristics for language, tone, and flow analysis.

    Args:
        scanner: Optional ``PIIScanner`` instance. If *None*, a default scanner
            is created with the given *confidence_threshold*.
        confidence_threshold: PII detection confidence threshold (0.0-1.0).
            Only used when *scanner* is not provided.
    """

    def __init__(
        self,
        scanner: PIIScanner | None = None,
        confidence_threshold: float = 0.85,
    ) -> None:
        self._confidence_threshold = confidence_threshold
        self._scanner = scanner or PIIScanner(confidence_threshold=confidence_threshold)
        logger.info(
            "seed_engine_initialized",
            confidence_threshold=confidence_threshold,
            has_presidio=self._scanner.has_presidio,
        )

    # ------------------------------------------------------------------
    # Public API (implements SeedEngineProtocol)
    # ------------------------------------------------------------------

    async def create_seed(self, raw_conversation: str, domain: str) -> SeedSchema:
        """Create a sanitized ``SeedSchema`` from a raw conversation.

        Steps:
            1. Parse raw text into structured turns.
            2. Scan and anonymize each turn for PII.
            3. Analyse conversation structure (roles, language, tone, etc.).
            4. Build and return a ``SeedSchema`` with all fields populated.

        Args:
            raw_conversation: Raw conversation text in any supported format.
            domain: Domain namespace (e.g. ``'automotive.sales'``).

        Returns:
            A fully populated ``SeedSchema`` with zero residual PII.

        Raises:
            ImportParsingError: If the raw conversation could not be parsed.
            PIIDetectedError: If PII is still present after anonymization.
        """
        # 1. Parse raw conversation into turns
        turns = self._parse_turns(raw_conversation)
        if not turns:
            raise ImportParsingError("Could not parse any turns from the raw conversation")

        logger.info("turns_parsed", turn_count=len(turns), domain=domain)

        # 2. Strip PII from each turn
        sensitive_fields: list[str] = []
        anonymized_turns: list[RawTurn] = []
        for turn in turns:
            clean_content = await self.strip_pii(turn.content)
            if clean_content != turn.content:
                sensitive_fields.append(f"turn_{turn.turn_number}_{turn.role}")
            anonymized_turns.append(
                RawTurn(
                    role=turn.role,
                    content=clean_content,
                    timestamp=turn.timestamp,
                    turn_number=turn.turn_number,
                )
            )

        # Also anonymize role names (they might contain real names)
        anonymized_roles: list[str] = []
        role_map: dict[str, str] = {}
        for turn in anonymized_turns:
            if turn.role not in role_map:
                clean_role = await self.strip_pii(turn.role)
                role_map[turn.role] = clean_role
            anonymized_roles.append(role_map[turn.role])

        # Update turns with clean role names
        for i, turn in enumerate(anonymized_turns):
            anonymized_turns[i] = RawTurn(
                role=role_map[turn.role],
                content=turn.content,
                timestamp=turn.timestamp,
                turn_number=turn.turn_number,
            )

        # 3. Analyse conversation structure
        unique_roles = list(dict.fromkeys(role_map.values()))
        if len(unique_roles) < 2:
            # Ensure at least two roles by splitting into generic ones
            unique_roles = ["Participante_1", "Participante_2"]

        all_content = " ".join(t.content for t in anonymized_turns)
        turn_contents = [t.content for t in anonymized_turns]

        language = self._detect_language(all_content)
        tone = self._analyze_tone(turn_contents)
        objective = self._extract_objective(anonymized_turns)
        flow_steps = self._extract_flow_steps(anonymized_turns)

        # Turn count range: allow some variation around the actual count
        actual_turns = len(anonymized_turns)
        turnos_min = max(1, actual_turns - 2)
        turnos_max = actual_turns + 4
        # Guarantee min < max
        if turnos_min >= turnos_max:
            turnos_max = turnos_min + 2

        # 4. Build context from the conversation content
        context_summary = self._build_context_summary(anonymized_turns, domain)

        # 5. Assemble the SeedSchema
        seed = SeedSchema(
            dominio=domain,
            idioma=language,
            roles=unique_roles,
            descripcion_roles={role: f"Participant: {role}" for role in unique_roles},
            objetivo=objective,
            tono=tone,
            pasos_turnos=PasosTurnos(
                turnos_min=turnos_min,
                turnos_max=turnos_max,
                flujo_esperado=flow_steps,
            ),
            parametros_factuales=ParametrosFactuales(
                contexto=context_summary,
                restricciones=[],
                metadata={"source_format": detect_format(raw_conversation), "original_turn_count": str(actual_turns)},
            ),
            privacidad=Privacidad(
                pii_eliminado=True,
                metodo_anonimizacion="presidio" if self._scanner.has_presidio else "regex",
                nivel_confianza=self._confidence_threshold,
                campos_sensibles_detectados=sensitive_fields,
            ),
        )

        # 6. Final privacy validation
        is_clean = await self.validate_privacy(seed)
        if not is_clean:
            raise PIIDetectedError("Residual PII detected in generated seed after anonymization")

        logger.info("seed_created", seed_id=seed.seed_id, domain=domain, roles=unique_roles)
        return seed

    async def strip_pii(self, text: str) -> str:
        """Remove all PII from text using the configured scanner.

        Args:
            text: Input text potentially containing PII.

        Returns:
            Anonymized text with PII replaced by placeholder tokens.
        """
        result = self._scanner.scan_and_anonymize(text)
        if result.pii_found:
            logger.debug("pii_stripped", entity_count=result.entity_count)
        return result.anonymized_text

    async def validate_privacy(self, seed: SeedSchema) -> bool:
        """Validate that a seed contains zero residual PII.

        Re-scans all text fields in the seed for any PII that may have survived
        the anonymization pass.

        Args:
            seed: The ``SeedSchema`` to validate.

        Returns:
            ``True`` only if zero PII entities are detected.
        """
        text_fields: list[str] = [
            seed.objetivo,
            seed.tono,
            seed.parametros_factuales.contexto,
            *seed.parametros_factuales.restricciones,
            *seed.roles,
            *seed.pasos_turnos.flujo_esperado,
        ]
        # Also check role descriptions
        text_fields.extend(seed.descripcion_roles.values())
        # Check metadata values
        text_fields.extend(seed.parametros_factuales.metadata.values())

        for text in text_fields:
            scan_result = self._scanner.scan(text)
            if scan_result.pii_found:
                logger.warning(
                    "residual_pii_detected",
                    seed_id=seed.seed_id,
                    entity_count=scan_result.entity_count,
                    categories=[e.category for e in scan_result.entities],
                )
                return False

        logger.debug("privacy_validated", seed_id=seed.seed_id)
        return True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_turns(raw: str) -> list[RawTurn]:
        """Parse raw conversation text into structured turns.

        Automatically detects the format (WhatsApp, numbered, or simple
        transcript) and delegates to the appropriate parser.

        Args:
            raw: Raw conversation text.

        Returns:
            List of parsed turns, or an empty list if parsing fails.
        """
        fmt = detect_format(raw)
        logger.debug("format_detected", format=fmt)

        if fmt == "json":
            return JSONConversationParser.parse(raw)
        if fmt == "whatsapp":
            return WhatsAppParser.parse(raw)
        # Both "numbered" and "transcript" are handled by TranscriptParser
        if fmt in {"numbered", "transcript"}:
            return TranscriptParser.parse(raw)

        # Fallback: try JSON parser first (structured data)
        turns = JSONConversationParser.parse(raw)
        if turns:
            return turns

        # Then try transcript parser (it handles both numbered and plain)
        turns = TranscriptParser.parse(raw)
        if turns:
            return turns

        # Last resort: try WhatsApp parser
        return WhatsAppParser.parse(raw)

    @staticmethod
    def _detect_language(text: str) -> str:
        """Detect conversation language using word-frequency heuristics.

        Args:
            text: Combined conversation text.

        Returns:
            ISO 639-1 language code (``"es"`` or ``"en"``).
        """
        words = set(text.lower().split())
        es_count = len(words & _SPANISH_MARKERS)
        en_count = len(words & _ENGLISH_MARKERS)

        if es_count > en_count:
            return "es"
        if en_count > es_count:
            return "en"
        # Default to Spanish per framework convention
        return "es"

    @staticmethod
    def _analyze_tone(turns: list[str]) -> str:
        """Determine conversation tone from vocabulary analysis.

        Args:
            turns: List of turn content strings.

        Returns:
            One of ``"formal"``, ``"informal"``, or ``"profesional"``.
        """
        all_words = set()
        for turn in turns:
            all_words.update(turn.lower().split())

        formal_hits = len(all_words & _FORMAL_MARKERS)
        informal_hits = len(all_words & _INFORMAL_MARKERS)

        if formal_hits > informal_hits:
            return "formal"
        if informal_hits > formal_hits:
            return "informal"
        return "profesional"

    @staticmethod
    def _extract_objective(turns: list[RawTurn]) -> str:
        """Derive conversation objective from the first 2-3 turns.

        Examines the opening turns to infer what the conversation is about.
        Falls back to a generic description if turns are too short.

        Args:
            turns: List of parsed turns.

        Returns:
            A brief description of the conversation's objective.
        """
        if not turns:
            return "General conversation"

        # Take the first 3 turns (or fewer if conversation is shorter)
        opening = turns[: min(3, len(turns))]
        opening_text = " ".join(t.content for t in opening)

        # Truncate to a reasonable length for the objective field
        max_len = 200
        if len(opening_text) > max_len:
            # Cut at the last space before the limit
            cut_point = opening_text.rfind(" ", 0, max_len)
            if cut_point == -1:
                cut_point = max_len
            opening_text = opening_text[:cut_point] + "..."

        return f"Conversation about: {opening_text}"

    @staticmethod
    def _extract_flow_steps(turns: list[RawTurn]) -> list[str]:
        """Extract conversation flow stages from turn structure.

        Groups consecutive turns by role to identify the logical progression
        of the conversation (e.g. greeting, inquiry, response, closing).

        Args:
            turns: List of parsed turns.

        Returns:
            List of flow step descriptions (minimum 2 steps).
        """
        if not turns:
            return ["start", "end"]

        steps: list[str] = []
        total = len(turns)

        # Divide conversation into logical segments
        if total <= 2:
            steps.append(f"Opening: {turns[0].role} initiates")
            steps.append(f"Response: {turns[-1].role} responds")
            return steps

        # Opening phase (first ~20% of turns)
        opening_end = max(1, total // 5)
        opening_roles = {t.role for t in turns[:opening_end]}
        steps.append(f"Opening: {', '.join(sorted(opening_roles))} initiate conversation")

        # Development phase (middle ~60%)
        mid_start = opening_end
        mid_end = max(mid_start + 1, total - total // 5)
        mid_roles = {t.role for t in turns[mid_start:mid_end]}
        steps.append(f"Development: {', '.join(sorted(mid_roles))} exchange information")

        # Check for role changes that indicate topic shifts
        prev_role = turns[0].role
        role_switches = 0
        for turn in turns[1:]:
            if turn.role != prev_role:
                role_switches += 1
            prev_role = turn.role

        if role_switches > total * 0.6:
            steps.append("Active dialogue: frequent role alternation detected")

        # Closing phase (last ~20%)
        closing_start = mid_end
        if closing_start < total:
            closing_roles = {t.role for t in turns[closing_start:]}
            steps.append(f"Closing: {', '.join(sorted(closing_roles))} conclude")
        else:
            steps.append("Closing: conversation ends")

        return steps

    @staticmethod
    def _build_context_summary(turns: list[RawTurn], domain: str) -> str:
        """Build a context summary from anonymized turns and domain.

        Args:
            turns: Anonymized parsed turns.
            domain: Domain namespace.

        Returns:
            A context description string.
        """
        role_set = sorted({t.role for t in turns})
        turn_count = len(turns)

        parts = [
            f"Domain: {domain}.",
            f"Participants: {', '.join(role_set)}.",
            f"Total turns: {turn_count}.",
        ]

        # Add a snippet from the first turn for context
        if turns:
            first_content = turns[0].content
            snippet_len = 100
            if len(first_content) > snippet_len:
                first_content = first_content[:snippet_len] + "..."
            parts.append(f"Opens with: {first_content}")

        return " ".join(parts)
