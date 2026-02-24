"""Privacy metric — PII residual detection in conversations."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema


# Regex patterns for common PII categories.
# These are fast heuristic checks. Full PII detection uses Presidio in Layer 0.
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


class PIIMatch:
    """Represents a detected PII entity in text."""

    __slots__ = ("category", "end", "start", "value")

    def __init__(self, category: str, value: str, start: int, end: int) -> None:
        self.category = category
        self.value = value
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"PIIMatch(category={self.category!r}, start={self.start}, end={self.end})"


def detect_pii_heuristic(text: str) -> list[PIIMatch]:
    """Detect potential PII in text using regex heuristics.

    This is NOT a replacement for Presidio. It serves as a fast first-pass
    check that catches obvious PII leaks. Layer 0 uses Presidio for the
    comprehensive NER-based detection.

    Args:
        text: Text to scan for PII.

    Returns:
        List of detected PII matches.
    """
    matches: list[PIIMatch] = []

    for category, pattern in _PII_PATTERNS.items():
        for match in pattern.finditer(text):
            matches.append(
                PIIMatch(
                    category=category,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
            )

    return matches


class PrivacyMetric(BaseMetric):
    """Privacy score metric — PII residual detection.

    Target: 0.0 (zero PII detected = perfect privacy).
    Any score > 0.0 means PII was found and the conversation FAILS
    the quality gate unconditionally.

    Uses regex heuristics for fast detection. The full Presidio pipeline
    in Layer 0 is the authoritative PII check; this metric serves as
    a final safety net.
    """

    @property
    def name(self) -> str:
        return "privacy_score"

    @property
    def display_name(self) -> str:
        return "Privacy Score (PII Residual)"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute PII residual score.

        Returns:
            0.0 if no PII detected (clean), >0.0 proportional to PII found.
        """
        full_text = " ".join(t.contenido for t in conversation.turnos)

        matches = detect_pii_heuristic(full_text)

        if not matches:
            return 0.0

        # Score proportional to the number of PII entities found,
        # capped at 1.0. Even one PII entity is a failure, but the
        # score indicates severity for debugging.
        return min(1.0, len(matches) * 0.1)
