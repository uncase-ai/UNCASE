"""Abstract base class for data connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation


@dataclass
class ConnectorResult:
    """Result of a connector import operation."""

    conversations: list[Conversation] = field(default_factory=list)
    total_imported: int = 0
    total_skipped: int = 0
    total_pii_anonymized: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BaseConnector(ABC):
    """Abstract base for data source connectors.

    All connectors follow the same pattern:
    1. Accept raw input (file, webhook payload, API response)
    2. Parse into internal Conversation format
    3. Run PII scan and anonymize before returning
    4. Return ConnectorResult with import statistics
    """

    @abstractmethod
    async def ingest(self, raw_input: str | bytes, **kwargs: object) -> ConnectorResult:
        """Ingest raw data and return parsed conversations.

        All PII scanning and anonymization happens inside this method.
        Callers receive clean, privacy-compliant conversations.
        """
        raise NotImplementedError

    @abstractmethod
    def connector_name(self) -> str:
        """Return the display name of this connector."""
        raise NotImplementedError

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return the list of accepted input formats."""
        raise NotImplementedError
