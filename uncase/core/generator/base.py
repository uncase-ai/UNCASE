"""Synthetic conversation generator abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema


class BaseGenerator(ABC):
    """Abstract base for Layer 3 — synthetic conversation generation."""

    @abstractmethod
    async def generate(self, seed: SeedSchema, count: int = 1) -> list[Conversation]:
        """Generate synthetic conversations from a seed."""
        raise NotImplementedError

    @abstractmethod
    async def generate_with_feedback(self, seed: SeedSchema, quality_report: QualityReport) -> list[Conversation]:
        """Generate improved conversations using quality feedback."""
        raise NotImplementedError
