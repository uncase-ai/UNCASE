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
You are a conversation seed engineer for the {industry} industry.
Your goal is to help the user design a synthetic conversation scenario \
that will be used to generate high-quality training data for AI fine-tuning.

You are NOT capturing real customer data — you are designing a fictional \
conversation blueprint. The user describes what kind of conversation they \
want to simulate, and you extract the parameters needed to generate it.

Language: Respond ONLY in {language}.

Rules:
- Ask ONE question per turn.
- Be direct and specific — state exactly what parameter you need and why.
- Reference information the user has already provided to show progress.
- Focus on what makes conversations VARIED and REALISTIC: scenario type, \
  participant behaviors, conversation flow, constraints, and tone.
- If the user provides multiple pieces of information at once, acknowledge \
  ALL of them before asking the next question.
- NEVER ask about something the user has already clearly answered.
- Keep responses concise (2-3 sentences max).
"""

_ASK_QUESTION_TEMPLATE = """\
Information already captured:
{captured_summary}

Fields that we still need:
{missing_fields}

Conversation history:
{history}

Generate a single, direct question about ONE of the missing fields. \
Be specific about what you need (e.g., "What communication channel \
should this conversation take place on — in-person, WhatsApp, phone, \
or web chat?"). DO NOT re-ask about information already captured. \
Prioritize required fields.
"""

_CLARIFICATION_TEMPLATE = """\
Information already captured:
{captured_summary}

Fields that need clarification (ambiguous or unclear):
{ambiguous_fields}

Fields that we still need:
{missing_fields}

Conversation history:
{history}

The user previously gave unclear information about the ambiguous fields. \
Rephrase the question differently and give concrete options to choose from. \
Ask about ONE field only. DO NOT repeat information already confirmed.
"""

_SUMMARY_TEMPLATE = """\
Here is the conversation scenario we have designed:
{captured_data}

Fields still missing:
{missing_fields}

Fields that are ambiguous:
{ambiguous_fields}

Generate a concise, structured summary of the conversation scenario. \
List each parameter clearly. If there are missing or ambiguous fields, \
ask the user specifically about those remaining items.
"""

_INITIAL_QUESTION_TEMPLATE = """\
You are starting a conversation seed design session for the {industry} industry.

The goal is to define ALL the parameters needed to generate realistic, \
varied synthetic conversations for AI training. The user will describe \
the conversation scenario they want to simulate.

The parameters we need to capture:
{categories}

Begin with a brief greeting that explains what you will do together \
(design a synthetic conversation scenario), then ask the user to describe \
the type of conversation they want to simulate — what is the scenario, \
and what should the interaction accomplish?
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
        captured_data: dict[str, object] | None = None,
    ) -> str:
        """Generate the next question based on the state.

        Args:
            history: Conversation history.
            missing_fields: Fields still needed.
            ambiguous_fields: Fields needing clarification.
            industry: Industry name.
            language: Language code.
            captured_data: Currently captured field values (for context).

        Returns:
            The generated question text.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)
        history_text = self._format_history(history)

        missing_text = self._format_fields(missing_fields) or "None"
        captured_summary = self._format_captured(captured_data) if captured_data else "Nothing yet."

        user = _ASK_QUESTION_TEMPLATE.format(
            captured_summary=captured_summary,
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
        captured_data: dict[str, object] | None = None,
    ) -> str:
        """Generate a clarification question for ambiguous fields.

        Args:
            history: Conversation history.
            missing_fields: Fields still needed.
            ambiguous_fields: Fields needing clarification.
            industry: Industry name.
            language: Language code.
            captured_data: Currently captured field values (for context).

        Returns:
            A rephrased clarification question.
        """
        system = _SYSTEM_PROMPT_TEMPLATE.format(industry=industry, language=language)
        history_text = self._format_history(history)
        captured_summary = self._format_captured(captured_data) if captured_data else "Nothing yet."

        user = _CLARIFICATION_TEMPLATE.format(
            captured_summary=captured_summary,
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
    def _format_captured(data: dict[str, object]) -> str:
        """Format captured data for inclusion in a prompt."""
        if not data:
            return "Nothing yet."
        lines: list[str] = []
        for key, val in data.items():
            if val is not None:
                lines.append(f"- {key}: {val}")
        return "\n".join(lines) if lines else "Nothing yet."

    @staticmethod
    def _fallback_initial_question(industry: str, language: str) -> str:
        """Provide a fallback initial question when LLM fails."""
        if language == "es":
            return (
                f"¡Hola! Te ayudaré a diseñar un escenario de conversación para {industry}. "
                "Describe el tipo de conversación que quieres simular: "
                "¿cuál es el escenario y qué debería lograr la interacción?"
            )
        return (
            f"Hello! I'll help you design a conversation scenario for {industry}. "
            "Describe the type of conversation you want to simulate: "
            "what's the scenario and what should the interaction accomplish?"
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
