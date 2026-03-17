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

# Context patterns that indicate a match is NOT real PII (version numbers,
# model IDs, SKUs, serial references, etc.).
_EXCLUDE_CONTEXT = re.compile(
    r"(?:\bversion\b|\bver\.?(?:\s|$)|\bv\d|\bmodelo\b|\bmodel\b|\bserie\b|\breferencia\b|\bcodigo\b|\bsku\b|\bid[:\s]|#)",
    re.IGNORECASE,
)

# Pattern that precedes an IP-like match and indicates a version string.
_VERSION_PREFIX = re.compile(r"(?:v|ver\.?|version\s*)$", re.IGNORECASE)

# Pattern that indicates more dotted groups around a match (software versions
# like "1.2.3.4.5" or "10.0.36.1.2").
_EXTRA_DOTTED = re.compile(r"(?:^\.?\d|\d\.?$)")


def _luhn_check(digits: str) -> bool:
    """Validate a number string using the Luhn algorithm."""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _is_valid_ip(value: str, text: str, start: int, end: int) -> bool:
    """Check whether an IP-like match is likely a real IP address.

    Rejects version numbers (e.g. v1.2.3.4), octets outside 0-255,
    and strings with extra dotted segments on either side.
    """
    octets = value.split(".")
    # Each octet must be 0-255
    for octet in octets:
        if not octet.isdigit() or int(octet) > 255:
            return False

    # Check for version-like prefix (v, ver, version, #)
    prefix = text[max(0, start - 20) : start]
    if _VERSION_PREFIX.search(prefix):
        return False
    # Immediate preceding character: 'v', '#'
    if start > 0 and text[start - 1] in ("v", "V", "#"):
        return False

    # Extra dotted groups on either side indicate a software version
    if start > 0 and text[start - 1] == ".":
        return False
    return not (end < len(text) and text[end] == ".")


def _is_valid_credit_card(value: str) -> bool:
    """Check whether a credit-card-like match passes the Luhn algorithm."""
    digits = re.sub(r"[-\s]", "", value)
    if not digits.isdigit() or len(digits) != 16:
        return False
    return _luhn_check(digits)


def _is_valid_rfc_mx(value: str) -> bool:
    """Validate that an RFC MX match has a plausible date and correct length.

    RFC format: {3-4 letters}{YYMMDD}{3 alphanumeric}
    Total length must be 12 or 13 characters.
    """
    if len(value) not in (12, 13):
        return False
    # Extract the 6-digit date portion: skip the letter prefix (3 or 4 chars)
    prefix_len = len(value) - 9  # 6 date digits + 3 suffix = 9
    date_str = value[prefix_len : prefix_len + 6]
    if not date_str.isdigit():
        return False
    month = int(date_str[2:4])
    day = int(date_str[4:6])
    if month < 1 or month > 12:
        return False
    return not (day < 1 or day > 31)


def _is_valid_iban(value: str) -> bool:
    """Validate IBAN length (15-34 chars) and check digits via mod-97."""
    length = len(value)
    if length < 15 or length > 34:
        return False
    # Move first 4 chars to end and convert letters to digits (A=10, B=11, …)
    rearranged = value[4:] + value[:4]
    numeric = ""
    for ch in rearranged:
        if ch.isdigit():
            numeric += ch
        else:
            numeric += str(ord(ch) - ord("A") + 10)
    return int(numeric) % 97 == 1


def _has_exclude_context(text: str, start: int) -> bool:
    """Check whether the 20 characters before *start* contain a false-positive context word."""
    window = text[max(0, start - 20) : start]
    return _EXCLUDE_CONTEXT.search(window) is not None


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
            value = match.group()
            start = match.start()
            end = match.end()

            # --- False-positive exclusion zone ---
            # Skip matches preceded by context words that indicate non-PII
            # (version, model, serial, SKU, etc.). Applies to all categories.
            if _has_exclude_context(text, start):
                continue

            # --- Category-specific validation ---
            if category == "ip_address" and not _is_valid_ip(value, text, start, end):
                continue

            if category == "credit_card" and not _is_valid_credit_card(value):
                continue

            if category == "rfc_mx" and not _is_valid_rfc_mx(value):
                continue

            if category == "iban" and not _is_valid_iban(value):
                continue

            matches.append(
                PIIMatch(
                    category=category,
                    value=value,
                    start=start,
                    end=end,
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
