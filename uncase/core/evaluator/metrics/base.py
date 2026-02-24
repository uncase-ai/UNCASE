"""Abstract base for individual quality metrics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema


class BaseMetric(ABC):
    """Abstract interface for a single quality metric.

    Each metric computes a score in [0.0, 1.0] comparing a generated
    conversation against its origin seed.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Machine-readable metric name (e.g. 'rouge_l')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable metric name."""
        ...

    @abstractmethod
    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute the metric score for a conversation-seed pair.

        Args:
            conversation: The generated/parsed conversation.
            seed: The origin seed that defined the generation constraints.

        Returns:
            Score in [0.0, 1.0].
        """
        ...
