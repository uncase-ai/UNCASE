"""Seed Extractor — Structured data extraction from conversation history.

Uses Claude (via the ``anthropic`` SDK) with ``instructor`` to produce
validated JSON that maps conversational text to seed schema fields.

The Extractor is **idempotent**: it receives the full conversation history
every time and re-derives the schema, never losing previously confirmed data
(fields with confidence ≥ 0.9 are protected).
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.log_config import get_logger

logger = get_logger(__name__)


# ── Extraction result models ────────────────────────────────────────


class ExtractedField(BaseModel):
    """A single field extracted from the conversation."""

    field_name: str = Field(..., description="Dot-path name of the field (e.g. 'cliente_perfil.tipo_cliente').")
    value: Any = Field(..., description="Extracted value for the field.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this extraction.")
    reasoning: str = Field(default="", description="Brief explanation of why this value was extracted.")


class ExtractionResult(BaseModel):
    """Complete output from a single extraction pass."""

    fields: list[ExtractedField] = Field(default_factory=list, description="List of extracted fields.")
    notes: str = Field(default="", description="General notes about the extraction quality.")


# ── System prompt for extraction ────────────────────────────────────

EXTRACTOR_SYSTEM_PROMPT = """\
You are a structured data extractor. You are given a conversation between \
an interviewer and a user, plus a JSON schema that is partially filled.

Your task is ONLY to extract factual information from the conversation and \
map it to the fields of the schema.

Rules:
- Do NOT invent data that is not explicitly in the conversation.
- If a datum is ambiguous, assign confidence < 0.7.
- If a datum is clear and explicit, assign confidence >= 0.9.
- Return ONLY the fields you can fill or update based on the conversation.
- Use dot-path notation for field names (e.g. 'cliente_perfil.tipo_cliente').
- For list fields, provide the complete list value.
- Pay attention to the field descriptions to choose correct enum values.
- Respond in valid JSON matching the ExtractionResult schema.
"""


class SeedExtractor:
    """Extract structured seed data from conversation history using an LLM.

    Args:
        config: Layer 0 configuration with model and retry settings.
        anthropic_client: Optional pre-configured ``anthropic.AsyncAnthropic``
            client.  If *None*, a new client is created from ``ANTHROPIC_API_KEY``.
    """

    def __init__(
        self,
        config: Layer0Config | None = None,
        anthropic_client: Any | None = None,
    ) -> None:
        self._config = config or Layer0Config()
        self._client = anthropic_client
        self._model = self._config.extractor_model

        logger.info("extractor_initialized", model=self._model)

    def _get_client(self) -> Any:
        """Lazily initialise the Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.AsyncAnthropic()
            except ImportError as exc:
                msg = (
                    "The 'anthropic' package is required for the Extractor. "
                    "Install it with: pip install anthropic"
                )
                raise ImportError(msg) from exc
        return self._client

    async def extract(
        self,
        conversation_history: list[dict[str, str]],
        current_schema_state: dict[str, Any],
        field_descriptions: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run extraction on the full conversation history.

        Args:
            conversation_history: List of ``{"role": "...", "content": "..."}``.
            current_schema_state: Current field values as a flat dict.
            field_descriptions: Optional mapping of field names to descriptions.

        Returns:
            Dict mapping field dot-paths to ``{"value": ..., "confidence": float}``.

        Raises:
            ExtractionError: If the LLM call fails after all retries.
        """
        user_prompt = self._build_prompt(
            conversation_history, current_schema_state, field_descriptions
        )

        try:
            extraction = await self._call_llm(user_prompt)
        except Exception:
            logger.exception("extraction_failed", turn_count=len(conversation_history) // 2)
            return {}

        # Convert ExtractionResult to the dict format StateManager expects
        result: dict[str, Any] = {}
        for field in extraction.fields:
            result[field.field_name] = {
                "value": field.value,
                "confidence": field.confidence,
            }

        logger.info(
            "extraction_complete",
            fields_extracted=len(result),
            turn_count=len(conversation_history) // 2,
        )
        return result

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _call_llm(self, user_prompt: str) -> ExtractionResult:
        """Call Claude and parse the response into an ExtractionResult.

        Uses ``instructor`` if available for structured outputs; falls back
        to manual JSON parsing otherwise.
        """
        client = self._get_client()

        try:
            import instructor

            patched = instructor.from_anthropic(client)
            result = await patched.messages.create(
                model=self._model,
                max_tokens=4096,
                system=EXTRACTOR_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                response_model=ExtractionResult,
            )
            return result  # type: ignore[return-value]
        except ImportError:
            logger.debug("instructor_not_available_falling_back_to_json_parsing")

        # Fallback: raw API call + manual parsing
        response = await client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=EXTRACTOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text
        # Try to extract JSON from the response
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON block in markdown
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
            else:
                logger.warning("extraction_json_parse_failed")
                return ExtractionResult()

        return ExtractionResult.model_validate(data)

    def _build_prompt(
        self,
        conversation_history: list[dict[str, str]],
        current_state: dict[str, Any],
        field_descriptions: dict[str, str] | None = None,
    ) -> str:
        """Build the extraction prompt with conversation and schema context."""
        parts: list[str] = []

        # Conversation transcript
        parts.append("## Conversation Transcript\n")
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            parts.append(f"**{role}**: {content}")
        parts.append("")

        # Current schema state
        parts.append("## Current Schema State (partially filled)\n")
        parts.append("```json")
        parts.append(json.dumps(current_state, indent=2, ensure_ascii=False, default=str))
        parts.append("```\n")

        # Field descriptions
        if field_descriptions:
            parts.append("## Field Descriptions\n")
            for name, desc in field_descriptions.items():
                parts.append(f"- **{name}**: {desc}")
            parts.append("")

        # Instructions
        parts.append("## Instructions\n")
        parts.append(
            "Extract any new or updated information from the conversation above "
            "and return an ExtractionResult JSON with the fields you can fill."
        )

        return "\n".join(parts)
