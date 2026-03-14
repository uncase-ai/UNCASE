"""Interviewer — LLM-powered question generation for the extraction loop.

The Interviewer is provider-agnostic: it builds prompts and delegates the
actual text generation to a ``BaseLLMProvider`` instance.  It generates
one question per turn, adapts tone to the configured industry, and handles
the different action types from the State Manager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.log_config import get_logger

if TYPE_CHECKING:
    from uncase.core.seed_engine.layer0.interviewer.base_provider import BaseLLMProvider
    from uncase.core.seed_engine.layer0.schemas.base import FieldMeta

logger = get_logger(__name__)


# ── Prompt templates ────────────────────────────────────────────────

_SYSTEM_PROMPT_TEMPLATE = """\
You are an information capture specialist for the {industry} industry.
Your goal is to gather the information needed to complete a data profile \
through a natural conversation.

Language: Respond ONLY in {language}.

Rules:
- Ask ONE question per turn.
- Be conversational and empathetic — do not sound like a form.
- Use terminology and context relevant to the {industry} industry.
- If the user provides extra information you did not ask for, acknowledge it naturally.
- NEVER invent or assume user data.
- Keep responses concise (2-4 sentences max).
"""

_ASK_QUESTION_TEMPLATE = """\
Fields that we still need:
{missing_fields}

Conversation history:
{history}

Generate a single, natural question to ask the user about one of the \
missing fields. Prioritize required fields. Be conversational and \
industry-specific.
"""

_CLARIFICATION_TEMPLATE = """\
Fields that need clarification (ambiguous or unclear):
{ambiguous_fields}

Fields that we still need:
{missing_fields}

Conversation history:
{history}

The user previously gave unclear information about the ambiguous fields. \
Rephrase the question in a different way to get clearer information. \
Ask about ONE field only.
"""

_SUMMARY_TEMPLATE = """\
Here is what we have captured so far:
{captured_data}

Fields still missing:
{missing_fields}

Fields that are ambiguous:
{ambiguous_fields}

Generate a friendly, readable summary of everything captured so far. \
If there are missing or ambiguous fields, mention them naturally \
and ask if the user wants to add anything else.
"""

_INITIAL_QUESTION_TEMPLATE = """\
You are starting a new data capture interview for the {industry} industry.

The goal is to capture information needed to generate synthetic training \
conversations. Start with a warm greeting and ask the first question.

The schema has these main categories:
{categories}

Begin with a warm greeting and ask about the most natural starting point \
(usually the type of customer or the main purpose of the vehicle).
"""


class Interviewer:
    """Provider-agnostic question generator for the extraction loop.

    Args:
        provider: An LLM provider implementing ``BaseLLMProvider``.
        config: Layer 0 configuration.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        config: Layer0Config | None = None,
    ) -> None:
        self._provider = provider
        self._config = config or Layer0Config()
        logger.info(
            "interviewer_initialized",
            provider=provider.provider_name,
            model=self._config.interviewer_model,
        )

    @property
    def provider(self) -> BaseLLMProvider:
        """Return the configured LLM provider."""
        return self._provider

    async def generate_initial_question(
        self,
        industry: str,
        categories: list[str],
        language: str = "es",
    ) -> str:
        """Generate the opening question for a new interview.

        Args:
            industry: Industry name (e.g. 'automotive').
            categories: List of schema category names.
            language: Language code for the response.

        Returns:
            The generated initial greeting + question.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)
        user = _INITIAL_QUESTION_TEMPLATE.format(
            industry=industry,
            categories="\n".join(f"- {c}" for c in categories),
        )

        try:
            response = await self._provider.generate(
                system_prompt=system,
                user_prompt=user,
                temperature=self._config.interviewer_temperature,
            )
            logger.debug("initial_question_generated", length=len(response))
            return response.strip()
        except Exception:
            logger.exception("initial_question_generation_failed")
            return self._fallback_initial_question(industry, language)

    async def generate_question(
        self,
        history: list[dict[str, str]],
        missing_fields: list[FieldMeta],
        ambiguous_fields: list[FieldMeta],
        industry: str,
        language: str = "es",
    ) -> str:
        """Generate the next question based on the state.

        Args:
            history: Conversation history.
            missing_fields: Fields still needed.
            ambiguous_fields: Fields needing clarification.
            industry: Industry name.
            language: Language code.

        Returns:
            The generated question text.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)
        history_text = self._format_history(history)

        missing_text = self._format_fields(missing_fields) or "None"

        user = _ASK_QUESTION_TEMPLATE.format(
            missing_fields=missing_text,
            history=history_text,
        )

        try:
            response = await self._provider.generate(
                system_prompt=system,
                user_prompt=user,
                temperature=self._config.interviewer_temperature,
            )
            logger.debug("question_generated", length=len(response))
            return response.strip()
        except Exception:
            logger.exception("question_generation_failed")
            return self._fallback_question(missing_fields, language)

    async def generate_clarification(
        self,
        history: list[dict[str, str]],
        missing_fields: list[FieldMeta],
        ambiguous_fields: list[FieldMeta],
        industry: str,
        language: str = "es",
    ) -> str:
        """Generate a clarification question for ambiguous fields.

        Args:
            history: Conversation history.
            missing_fields: Fields still needed.
            ambiguous_fields: Fields needing clarification.
            industry: Industry name.
            language: Language code.

        Returns:
            A rephrased clarification question.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)
        history_text = self._format_history(history)

        user = _CLARIFICATION_TEMPLATE.format(
            ambiguous_fields=self._format_fields(ambiguous_fields),
            missing_fields=self._format_fields(missing_fields) or "None",
            history=history_text,
        )

        try:
            response = await self._provider.generate(
                system_prompt=system,
                user_prompt=user,
                temperature=self._config.interviewer_temperature,
            )
            return response.strip()
        except Exception:
            logger.exception("clarification_generation_failed")
            return self._fallback_question(ambiguous_fields, language)

    async def generate_summary(
        self,
        captured_data: dict[str, object],
        missing_fields: list[FieldMeta],
        ambiguous_fields: list[FieldMeta],
        industry: str,
        language: str = "es",
    ) -> str:
        """Generate a human-readable summary of the captured data.

        Args:
            captured_data: Current extracted field values.
            missing_fields: Fields still needed.
            ambiguous_fields: Fields needing clarification.
            industry: Industry name.
            language: Language code.

        Returns:
            A friendly summary of all captured information.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)

        captured_text = "\n".join(f"- {k}: {v}" for k, v in captured_data.items() if v is not None)
        if not captured_text:
            captured_text = "No data captured yet."

        user = _SUMMARY_TEMPLATE.format(
            captured_data=captured_text,
            missing_fields=self._format_fields(missing_fields) or "None",
            ambiguous_fields=self._format_fields(ambiguous_fields) or "None",
        )

        try:
            response = await self._provider.generate(
                system_prompt=system,
                user_prompt=user,
                temperature=self._config.interviewer_temperature,
            )
            return response.strip()
        except Exception:
            logger.exception("summary_generation_failed")
            return self._fallback_summary(captured_data, language)

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _format_history(history: list[dict[str, str]]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "(No conversation yet)"
        lines: list[str] = []
        for msg in history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    @staticmethod
    def _format_fields(fields: list[FieldMeta]) -> str:
        """Format a list of FieldMeta for inclusion in a prompt."""
        if not fields:
            return ""
        lines: list[str] = []
        for f in fields:
            req = " [REQUIRED]" if f.is_required else ""
            lines.append(f"- {f.field_name}{req}: {f.description}")
        return "\n".join(lines)

    @staticmethod
    def _fallback_initial_question(industry: str, language: str) -> str:
        """Provide a fallback initial question when LLM fails."""
        if language == "es":
            return (
                f"¡Hola! Soy tu asistente de captura de datos para {industry}. "
                "Para comenzar, ¿podría decirme qué tipo de cliente será el "
                "participante en la conversación? (particular, flotilla, empresa, revendedor)"
            )
        return (
            f"Hello! I'm your data capture assistant for {industry}. "
            "To get started, could you tell me what type of customer will "
            "participate in the conversation? (individual, fleet, business, reseller)"
        )

    @staticmethod
    def _fallback_question(fields: list[FieldMeta], language: str) -> str:
        """Provide a fallback question when LLM fails."""
        if not fields:
            if language == "es":
                return "¿Hay algo más que quiera agregar?"
            return "Is there anything else you'd like to add?"

        field = fields[0]
        if language == "es":
            return f"¿Podría proporcionarme información sobre: {field.description}?"
        return f"Could you provide information about: {field.description}?"

    @staticmethod
    def _fallback_summary(data: dict[str, object], language: str) -> str:
        """Provide a fallback summary when LLM fails."""
        lines: list[str] = []
        if language == "es":
            lines.append("Resumen de la información capturada:")
        else:
            lines.append("Summary of captured information:")

        for key, val in data.items():
            if val is not None:
                lines.append(f"  • {key}: {val}")

        return "\n".join(lines)
