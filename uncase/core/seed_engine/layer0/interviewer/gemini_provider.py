"""Google Gemini LLM provider for the Interviewer.

Default provider for development. Uses the ``google-generativeai`` SDK.
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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini 2.5 Pro provider implementation.

    Args:
        model: Gemini model identifier.
        api_key: Optional API key. If *None*, reads from ``GOOGLE_API_KEY`` /
                 ``GEMINI_API_KEY`` env var (SDK default).
    """

    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._client: Any = None
        logger.info("gemini_provider_initialized", model=model)

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _get_client(self) -> Any:
        """Lazily initialise the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                if self._api_key:
                    genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model)
            except ImportError as exc:
                msg = (
                    "The 'google-generativeai' package is required for the "
                    "Gemini provider. Install it with: pip install google-generativeai"
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
        """Generate text using Google Gemini."""
        client = self._get_client()

        # Gemini uses a combined prompt approach
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            response = await client.generate_content_async(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            text = response.text
            logger.debug("gemini_response_generated", model=self._model, length=len(text))
            return text

        except Exception:
            logger.exception("gemini_generation_failed", model=self._model)
            raise
