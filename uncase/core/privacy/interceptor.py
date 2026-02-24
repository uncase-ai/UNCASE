"""Privacy interceptor — gateway-level PII scanning for all LLM traffic."""

from __future__ import annotations

from dataclasses import dataclass, field

from uncase.core.privacy.scanner import PIIScanner, PIIScanResult
from uncase.logging import get_logger

logger = get_logger(__name__)


@dataclass
class InterceptResult:
    """Result of intercepting and scanning a message."""

    direction: str  # "outbound" (to LLM) or "inbound" (from LLM)
    scan: PIIScanResult
    blocked: bool = False
    message: str = ""


@dataclass
class InterceptSummary:
    """Summary of all interceptions for a request."""

    outbound_scans: list[InterceptResult] = field(default_factory=list)
    inbound_scans: list[InterceptResult] = field(default_factory=list)
    total_pii_found: int = 0
    any_blocked: bool = False

    def add_outbound(self, result: InterceptResult) -> None:
        self.outbound_scans.append(result)
        self.total_pii_found += result.scan.entity_count
        if result.blocked:
            self.any_blocked = True

    def add_inbound(self, result: InterceptResult) -> None:
        self.inbound_scans.append(result)
        self.total_pii_found += result.scan.entity_count
        if result.blocked:
            self.any_blocked = True


class PrivacyInterceptor:
    """Gateway-level privacy interceptor.

    Sits between the application and LLM providers, scanning all traffic
    for PII. Can operate in three modes:

    - **audit**: Scan and log PII but don't block (default)
    - **warn**: Scan, log, and include warnings in results
    - **block**: Scan and block requests containing PII

    Usage:
        interceptor = PrivacyInterceptor(mode="audit")

        # Before sending to LLM
        result = interceptor.scan_outbound(prompt_text)
        if result.blocked:
            raise PIIDetectedError(...)

        # After receiving from LLM
        result = interceptor.scan_inbound(response_text)
    """

    def __init__(
        self,
        *,
        mode: str = "audit",
        confidence_threshold: float = 0.85,
        anonymize_outbound: bool = True,
    ) -> None:
        if mode not in ("audit", "warn", "block"):
            msg = f"Invalid mode '{mode}'. Must be: audit, warn, block"
            raise ValueError(msg)

        self.mode = mode
        self.anonymize_outbound = anonymize_outbound
        self._scanner = PIIScanner(confidence_threshold=confidence_threshold)

    @property
    def has_presidio(self) -> bool:
        """Whether Presidio NER is available for enhanced detection."""
        return self._scanner.has_presidio

    def scan_outbound(self, text: str) -> InterceptResult:
        """Scan text being sent TO an LLM provider.

        In anonymize_outbound mode, PII is replaced with tokens before
        the text reaches the LLM. This prevents real PII from being
        sent to external providers.
        """
        scan = self._scanner.scan_and_anonymize(text) if self.anonymize_outbound else self._scanner.scan(text)

        blocked = self.mode == "block" and scan.pii_found
        message = ""
        if scan.pii_found:
            categories = {e.category for e in scan.entities}
            message = f"PII detected in outbound text: {', '.join(sorted(categories))}"

        result = InterceptResult(
            direction="outbound",
            scan=scan,
            blocked=blocked,
            message=message,
        )

        if scan.pii_found:
            logger.warning(
                "pii_detected_outbound",
                mode=self.mode,
                entity_count=scan.entity_count,
                categories=[e.category for e in scan.entities],
                blocked=blocked,
            )

        return result

    def scan_inbound(self, text: str) -> InterceptResult:
        """Scan text received FROM an LLM provider.

        Checks LLM responses for PII that may have leaked through
        generation. This is the final safety net before data reaches
        the user or is stored.
        """
        scan = self._scanner.scan(text)

        blocked = self.mode == "block" and scan.pii_found
        message = ""
        if scan.pii_found:
            categories = {e.category for e in scan.entities}
            message = f"PII detected in LLM response: {', '.join(sorted(categories))}"

        result = InterceptResult(
            direction="inbound",
            scan=scan,
            blocked=blocked,
            message=message,
        )

        if scan.pii_found:
            logger.warning(
                "pii_detected_inbound",
                mode=self.mode,
                entity_count=scan.entity_count,
                categories=[e.category for e in scan.entities],
                blocked=blocked,
            )

        return result

    def scan_conversation_text(self, turns: list[str]) -> InterceptSummary:
        """Scan all turns in a conversation.

        Useful for batch scanning imported conversations before they
        enter the SCSF pipeline.
        """
        summary = InterceptSummary()

        for text in turns:
            result = self.scan_outbound(text)
            summary.add_outbound(result)

        return summary
