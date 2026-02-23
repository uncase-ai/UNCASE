"""LoRA pipeline abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from uncase.schemas.conversation import Conversation


class BasePipeline(ABC):
    """Abstract base for Layer 4 — LoRA fine-tuning pipeline."""

    @abstractmethod
    async def prepare_dataset(self, conversations: list[Conversation]) -> Path:
        """Prepare training dataset from validated conversations."""
        raise NotImplementedError

    @abstractmethod
    async def train(self, dataset_path: Path, config: dict[str, Any]) -> Path:
        """Train a LoRA adapter."""
        raise NotImplementedError

    @abstractmethod
    async def evaluate_model(self, adapter_path: Path) -> dict[str, float]:
        """Evaluate a trained adapter."""
        raise NotImplementedError
