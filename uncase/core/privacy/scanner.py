"""PII scanner — multi-strategy detection combining regex heuristics and Presidio NER."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from uncase.logging import get_logger

logger = get_logger(__name__)

# Reuse the proven regex patterns from the evaluator metric
_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone_intl": re.compile(r"\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}"),
    "phone_local": re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "curp_mx": re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b"),
    "rfc_mx": re.compile(r"\b[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b"),
}

# Placeholder tokens for anonymization
_REPLACEMENT_MAP: dict[str, str] = {
    "email": "[EMAIL]",
    "phone_intl": "[PHONE]",
    "phone_local": "[PHONE]",
    "ssn_us": "[SSN]",
    "curp_mx": "[CURP]",
    "rfc_mx": "[RFC]",
    "credit_card": "[CREDIT_CARD]",
    "ip_address": "[IP_ADDRESS]",
    "iban": "[IBAN]",
    "PERSON": "[PERSON]",
    "LOCATION": "[LOCATION]",
    "DATE_TIME": "[DATE]",
    "NRP": "[ID_NUMBER]",
    "MEDICAL_LICENSE": "[LICENSE]",
    "US_BANK_NUMBER": "[BANK_ACCOUNT]",
    "US_PASSPORT": "[PASSPORT]",
    "US_DRIVER_LICENSE": "[DRIVER_LICENSE]",
}


@dataclass
class PIIEntity:
    """A single detected PII entity."""

    category: str
    text: str
    start: int
    end: int
    score: float = 1.0
    source: str = "regex"  # "regex" or "presidio"


@dataclass
class PIIScanResult:
    """Result of scanning text for PII."""

    original_text: str
    entities: list[PIIEntity] = field(default_factory=list)
    anonymized_text: str = ""
    pii_found: bool = False
    entity_count: int = 0

    def __post_init__(self) -> None:
        self.pii_found = len(self.entities) > 0
        self.entity_count = len(self.entities)


def _check_presidio_available() -> bool:
    """Check if Presidio is installed."""
    try:
        import presidio_analyzer  # noqa: F401
        import presidio_anonymizer  # noqa: F401

        return True
    except ImportError:
        return False


_PRESIDIO_AVAILABLE = _check_presidio_available()


class PIIScanner:
    """Multi-strategy PII scanner.

    Uses regex heuristics as the fast baseline. When the optional [privacy]
    extra is installed (presidio-analyzer + presidio-anonymizer + spacy),
    Presidio NER is used as an additional detection layer for higher accuracy.

    Usage:
        scanner = PIIScanner(confidence_threshold=0.85)
        result = scanner.scan("Call me at 555-123-4567")
        result = scanner.scan_and_anonymize("My SSN is 123-45-6789")
    """

    def __init__(self, confidence_threshold: float = 0.85, bypass_words: set[str] | None = None) -> None:
        self.confidence_threshold = confidence_threshold
        self.bypass_words: set[str] = {w.lower() for w in (bypass_words or set())}
        self._presidio_analyzer: object | None = None
        self._presidio_anonymizer: object | None = None

        if _PRESIDIO_AVAILABLE:
            self._init_presidio()

    def _init_presidio(self) -> None:
        """Initialize Presidio analyzer and anonymizer."""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine

            self._presidio_analyzer = AnalyzerEngine()
            self._presidio_anonymizer = AnonymizerEngine()
            logger.info("presidio_initialized", confidence_threshold=self.confidence_threshold)
        except Exception as exc:
            logger.warning("presidio_init_failed", error=str(exc))
            self._presidio_analyzer = None
            self._presidio_anonymizer = None

    @property
    def has_presidio(self) -> bool:
        """Whether Presidio NER is available."""
        return self._presidio_analyzer is not None

    def scan(self, text: str) -> PIIScanResult:
        """Scan text for PII using all available strategies.

        Returns a PIIScanResult with all detected entities.
        """
        entities: list[PIIEntity] = []

        # Strategy 1: Regex heuristics (always available)
        for category, pattern in _PII_PATTERNS.items():
            for match in pattern.finditer(text):
                entities.append(
                    PIIEntity(
                        category=category,
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        score=1.0,
                        source="regex",
                    )
                )

        # Strategy 2: Presidio NER (when available)
        if self._presidio_analyzer is not None:
            try:
                analyzer = self._presidio_analyzer
                results = analyzer.analyze(  # type: ignore[attr-defined]
                    text=text,
                    language="en",
                    score_threshold=self.confidence_threshold,
                )
                for result in results:
                    # Skip if a regex pattern already covers this span
                    overlap = any(
                        e.source == "regex" and e.start <= result.start and e.end >= result.end for e in entities
                    )
                    if not overlap:
                        entities.append(
                            PIIEntity(
                                category=result.entity_type,
                                text=text[result.start : result.end],
                                start=result.start,
                                end=result.end,
                                score=result.score,
                                source="presidio",
                            )
                        )
            except Exception as exc:
                logger.warning("presidio_scan_error", error=str(exc))

        # Sort by position
        entities.sort(key=lambda e: e.start)

        # Filter out bypassed words
        if self.bypass_words:
            entities = [e for e in entities if e.text.lower() not in self.bypass_words]

        return PIIScanResult(
            original_text=text,
            entities=entities,
            anonymized_text=text,
        )

    def scan_and_anonymize(self, text: str) -> PIIScanResult:
        """Scan text and replace all detected PII with placeholder tokens."""
        result = self.scan(text)

        if not result.entities:
            result.anonymized_text = text
            return result

        # Replace entities from end to start to preserve positions
        anonymized = text
        for entity in reversed(result.entities):
            replacement = _REPLACEMENT_MAP.get(entity.category, f"[{entity.category}]")
            anonymized = anonymized[: entity.start] + replacement + anonymized[entity.end :]

        result.anonymized_text = anonymized
        return result
