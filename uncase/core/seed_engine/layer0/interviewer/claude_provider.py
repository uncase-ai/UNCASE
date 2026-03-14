"""Anthropic Claude LLM provider for the Interviewer.

Fallback provider. Uses the ``anthropic`` SDK.
"""

from __future__ import annotations

from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from uncase.core.seed_engine.layer0.interviewer.base_provider import BaseLLMProvider
from uncase.log_config import get_logger

logger = get_logger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation.

    Args:
        model: Claude model identifier.
        api_key: Optional API key. If *None*, reads from ``ANTHROPIC_API_KEY``.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._client: Any = None
        logger.info("claude_provider_initialized", model=model)

    @property
    def provider_name(self) -> str:
        return "claude"

    def _get_client(self) -> Any:
        """Lazily initialise the Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                kwargs: dict[str, Any] = {}
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = anthropic.AsyncAnthropic(**kwargs)
            except ImportError as exc:
                msg = (
                    "The 'anthropic' package is required for the Claude "
                    "provider. Install it with: pip install anthropic"
                )
                raise ImportError(msg) from exc
        return self._client

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Generate text using Anthropic Claude."""
        client = self._get_client()

        try:
            response = await client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
            )

            text = response.content[0].text
            logger.debug("claude_response_generated", model=self._model, length=len(text))
            return text

        except Exception:
            logger.exception("claude_generation_failed", model=self._model)
            raise
