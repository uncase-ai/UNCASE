"""Quality evaluator abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.seed import SeedSchema


class BaseEvaluator(ABC):
    """Abstract base for Layer 2 — quality evaluation."""

    @abstractmethod
    async def evaluate(self, conversation: Conversation, seed: SeedSchema) -> QualityReport:
        """Evaluate a single conversation against its seed."""
        raise NotImplementedError

    @abstractmethod
    async def evaluate_batch(self, conversations: list[Conversation], seeds: list[SeedSchema]) -> list[QualityReport]:
        """Evaluate a batch of conversations."""
        raise NotImplementedError
