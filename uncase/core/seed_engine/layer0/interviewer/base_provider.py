"""Abstract base class for LLM providers used by the Interviewer.

Implements a strategy pattern so the Interviewer can swap providers
(Gemini, Claude, OpenAI, local models, etc.) without changing its logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract LLM provider for generating interview questions.

    Subclasses must implement :meth:`generate` to call their specific API.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the human-readable provider name (e.g. 'gemini', 'claude')."""
        ...

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            system_prompt: System-level instructions.
            user_prompt: The user-facing prompt content.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            **kwargs: Provider-specific extra arguments.

        Returns:
            The generated text response.

        Raises:
            Exception: If the API call fails.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is reachable and configured.

        Returns:
            ``True`` if the provider is healthy.
        """
        try:
            result = await self.generate(
                system_prompt="Return the word 'ok'.",
                user_prompt="Health check.",
                max_tokens=10,
            )
            return bool(result.strip())
        except Exception:
            return False
