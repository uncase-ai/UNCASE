"""Parser and validator abstract base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.validation import ValidationReport


class BaseParser(ABC):
    """Abstract base for Layer 1 — conversation parsers."""

    @abstractmethod
    async def parse(self, raw_input: str, format: str) -> list[Conversation]:
        """Parse raw input into structured conversations."""
        raise NotImplementedError

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return list of supported input formats."""
        raise NotImplementedError


class ConversationValidator(ABC):
    """Abstract base for conversation validation."""

    @abstractmethod
    async def validate(self, conversation: Conversation) -> ValidationReport:
        """Validate a parsed conversation."""
        raise NotImplementedError
