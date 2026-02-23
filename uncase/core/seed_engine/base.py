"""Seed engine protocol definition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from uncase.schemas.seed import SeedSchema


@runtime_checkable
class SeedEngineProtocol(Protocol):
    """Protocol for Layer 0 — Seed Engine implementations."""

    async def create_seed(self, raw_conversation: str, domain: str) -> SeedSchema:
        """Create a seed from a raw conversation, stripping all PII."""
        ...

    async def strip_pii(self, text: str) -> str:
        """Remove all PII from text."""
        ...

    async def validate_privacy(self, seed: SeedSchema) -> bool:
        """Validate that a seed contains zero residual PII."""
        ...
