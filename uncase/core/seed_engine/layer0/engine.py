"""Agentic Extraction Engine — Orchestrator for the Layer 0 interview loop.

Connects the State Manager, Extractor, and Interviewer into a single
async loop that captures seed data through natural conversation.

Usage::

    engine = AgenticExtractionEngine(config=Layer0Config())
    async for message in engine.run():
        if message["type"] == "question":
            # Show question to user
            user_answer = await get_user_input()
            engine.send_response(user_answer)
        elif message["type"] == "summary":
            # Show final summary
            seed = message["seed"]
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.extractor import SeedExtractor
from uncase.core.seed_engine.layer0.interviewer.interviewer import Interviewer
from uncase.core.seed_engine.layer0.schemas.automotriz import SeedAutomotriz
from uncase.core.seed_engine.layer0.state_manager import ActionType, StateManager
from uncase.log_config import get_logger

if TYPE_CHECKING:
    from uncase.core.seed_engine.layer0.interviewer.base_provider import BaseLLMProvider
    from uncase.core.seed_engine.layer0.schemas.base import BaseSeedExtraction

logger = get_logger(__name__)


def _create_provider(config: Layer0Config) -> BaseLLMProvider:
    """Factory: create an LLM provider based on the config.

    Args:
        config: Layer 0 configuration with provider settings.

    Returns:
        A concrete ``BaseLLMProvider`` instance.

    Raises:
        ValueError: If the provider name is unrecognized.
    """
    provider_name = config.interviewer_provider.lower()

    if provider_name == "gemini":
        from uncase.core.seed_engine.layer0.interviewer.gemini_provider import (
            GeminiProvider,
        )

        return GeminiProvider(model=config.interviewer_model)

    if provider_name == "claude":
        from uncase.core.seed_engine.layer0.interviewer.claude_provider import (
            ClaudeProvider,
        )

        return ClaudeProvider(model=config.interviewer_model)

    msg = f"Unknown interviewer provider: '{provider_name}'. Supported: gemini, claude."
    raise ValueError(msg)


def _load_schema(industry: str) -> BaseSeedExtraction:
    """Load the extraction schema for a given industry.

    Args:
        industry: Industry identifier (e.g. 'automotive').

    Returns:
        A fresh ``BaseSeedExtraction`` subclass instance.

    Raises:
        ValueError: If the industry is not supported.
    """
    schemas: dict[str, type[BaseSeedExtraction]] = {
        "automotive": SeedAutomotriz,
    }
    schema_cls = schemas.get(industry.lower())
    if schema_cls is None:
        supported = ", ".join(sorted(schemas.keys()))
        msg = f"Unknown industry: '{industry}'. Supported: {supported}."
        raise ValueError(msg)

    return schema_cls()


class AgenticExtractionEngine:
    """Orchestrator for the agentic seed extraction loop.

    The engine ties together the three core components:

    1. **State Manager** — Tracks field completion and decides next steps.
    2. **Extractor** — Extracts structured data from conversation history.
    3. **Interviewer** — Generates natural-language questions.

    Args:
        config: Layer 0 configuration.
        schema: Optional pre-built schema instance.  If *None*, one is loaded
            based on ``config.industry``.
        extractor: Optional pre-built ``SeedExtractor``.
        interviewer: Optional pre-built ``Interviewer``.
        provider: Optional pre-built ``BaseLLMProvider`` for the Interviewer.
    """

    def __init__(
        self,
        config: Layer0Config | None = None,
        *,
        schema: BaseSeedExtraction | None = None,
        extractor: SeedExtractor | None = None,
        interviewer: Interviewer | None = None,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self._config = config or Layer0Config()
        self._schema = schema or _load_schema(self._config.industry)
        self._state = StateManager(self._schema, self._config)
        self._extractor = extractor or SeedExtractor(self._config)

        if interviewer:
            self._interviewer = interviewer
        else:
            _provider = provider or _create_provider(self._config)
            self._interviewer = Interviewer(_provider, self._config)

        self._history: list[dict[str, str]] = []
        self._response_event: asyncio.Event = asyncio.Event()
        self._pending_response: str | None = None

        logger.info(
            "agentic_engine_initialized",
            industry=self._config.industry,
            max_turns=self._config.max_turns,
        )

    # ── Public API ───────────────────────────────────────────────────

    @property
    def state(self) -> StateManager:
        """Return the state manager."""
        return self._state

    @property
    def history(self) -> list[dict[str, str]]:
        """Return the conversation history."""
        return list(self._history)

    def send_response(self, response: str) -> None:
        """Provide the user's response to the current question.

        This is called externally (by a frontend, API handler, or CLI) to
        feed user input into the running loop.

        Args:
            response: The user's text response.
        """
        self._pending_response = response
        self._response_event.set()

    async def run(self) -> list[dict[str, Any]]:
        """Execute the full extraction loop and return all messages.

        This is a simpler interface that collects all messages. For interactive
        use, see :meth:`run_interactive`.

        Returns:
            A list of message dicts with keys ``type`` and ``content``.
        """
        messages: list[dict[str, Any]] = []

        # Resolve categories from the schema
        categories = self._get_categories()
        industry = self._config.industry
        language = self._schema.idioma

        # Generate initial question
        question = await self._interviewer.generate_initial_question(
            industry=industry,
            categories=categories,
            language=language,
        )

        while not self._state.is_complete:
            # Emit question
            messages.append({"type": "question", "content": question})

            # Wait for response
            user_response = await self._wait_for_response()
            if user_response is None:
                break

            # Check for explicit stop signals
            if self._is_stop_signal(user_response):
                self._state.request_stop()
                break

            # Record conversation
            self._history.append({"role": "interviewer", "content": question})
            self._history.append({"role": "user", "content": user_response})
            self._state.increment_turn()

            logger.info(
                "turn_completed",
                turn=self._state.turn_count,
                user_response_length=len(user_response),
            )

            # Extract data from the full conversation
            field_descriptions = {
                fm.field_name: fm.description
                for fm in self._schema.get_field_registry()
            }
            extraction_result = await self._extractor.extract(
                conversation_history=self._history,
                current_schema_state=self._schema.to_extraction_dict(),
                field_descriptions=field_descriptions,
            )

            # Update state with extraction results
            updated = self._state.update(extraction_result)
            logger.info(
                "state_updated",
                turn=self._state.turn_count,
                fields_updated=len(updated),
                updated_fields=updated,
            )

            # Decide what to do next
            action = self._state.decide_next_action()

            if action.action == ActionType.COMPLETE:
                break

            # Generate next question based on action type
            question = await self._generate_for_action(action, industry, language)

        # Generate final summary
        final_action = self._state.decide_next_action()
        summary = await self._interviewer.generate_summary(
            captured_data=self._schema.to_extraction_dict(),
            missing_fields=final_action.missing_fields,
            ambiguous_fields=final_action.ambiguous_fields,
            industry=industry,
            language=language,
        )

        messages.append({
            "type": "summary",
            "content": summary,
            "seed": self._state.get_seed_final(),
            "progress": self._state.get_progress(),
        })

        logger.info(
            "extraction_loop_complete",
            total_turns=self._state.turn_count,
            progress=self._state.get_progress(),
        )

        return messages

    async def process_turn(self, user_response: str) -> dict[str, Any]:
        """Process a single turn: extract, update state, generate next question.

        This is the primary interface for integrations (APIs, frontends)
        that handle one turn at a time rather than running a full loop.

        Args:
            user_response: The user's text response.

        Returns:
            A message dict with ``type``, ``content``, and optionally ``seed``
            and ``progress``.
        """
        industry = self._config.industry
        language = self._schema.idioma

        # Check for stop signal
        if self._is_stop_signal(user_response):
            self._state.request_stop()
            return await self._build_summary_message(industry, language)

        # Record the user response
        self._history.append({"role": "user", "content": user_response})
        self._state.increment_turn()

        # Extract — gracefully handle failures
        field_descriptions = {
            fm.field_name: fm.description
            for fm in self._schema.get_field_registry()
        }
        try:
            extraction_result = await self._extractor.extract(
                conversation_history=self._history,
                current_schema_state=self._schema.to_extraction_dict(),
                field_descriptions=field_descriptions,
            )
        except Exception:
            logger.exception("extraction_failed_in_turn", turn=self._state.turn_count)
            extraction_result = {}

        # Update state
        updated = self._state.update(extraction_result)
        logger.info(
            "turn_processed",
            turn=self._state.turn_count,
            fields_updated=len(updated),
        )

        # Decide next action
        action = self._state.decide_next_action()

        if action.action == ActionType.COMPLETE:
            return await self._build_summary_message(industry, language)

        # Generate next question
        question = await self._generate_for_action(action, industry, language)
        self._history.append({"role": "interviewer", "content": question})

        return {
            "type": "question",
            "content": question,
            "progress": self._state.get_progress(),
        }

    async def get_initial_question(self) -> dict[str, Any]:
        """Generate and return the initial greeting/question.

        Returns:
            A message dict with ``type`` = ``"question"``.
        """
        categories = self._get_categories()
        industry = self._config.industry
        language = self._schema.idioma

        question = await self._interviewer.generate_initial_question(
            industry=industry,
            categories=categories,
            language=language,
        )
        self._history.append({"role": "interviewer", "content": question})

        return {
            "type": "question",
            "content": question,
            "progress": self._state.get_progress(),
        }

    # ── Private helpers ──────────────────────────────────────────────

    async def _wait_for_response(self) -> str | None:
        """Wait for a user response via :meth:`send_response`."""
        self._response_event.clear()
        self._pending_response = None

        try:
            await asyncio.wait_for(self._response_event.wait(), timeout=600)
        except TimeoutError:
            logger.warning("response_timeout")
            return None

        return self._pending_response

    async def _generate_for_action(
        self,
        action: Any,
        industry: str,
        language: str,
    ) -> str:
        """Generate the appropriate interviewer response for an action."""
        if action.action == ActionType.REQUEST_CLARIFICATION:
            return await self._interviewer.generate_clarification(
                history=self._history,
                missing_fields=action.missing_fields,
                ambiguous_fields=action.ambiguous_fields,
                industry=industry,
                language=language,
            )

        if action.action == ActionType.PRESENT_SUMMARY:
            return await self._interviewer.generate_summary(
                captured_data=self._schema.to_extraction_dict(),
                missing_fields=action.missing_fields,
                ambiguous_fields=action.ambiguous_fields,
                industry=industry,
                language=language,
            )

        # Default: ask a new question
        return await self._interviewer.generate_question(
            history=self._history,
            missing_fields=action.missing_fields,
            ambiguous_fields=action.ambiguous_fields,
            industry=industry,
            language=language,
        )

    async def _build_summary_message(
        self,
        industry: str,
        language: str,
    ) -> dict[str, Any]:
        """Build the final summary message."""
        action = self._state.decide_next_action()
        summary = await self._interviewer.generate_summary(
            captured_data=self._schema.to_extraction_dict(),
            missing_fields=action.missing_fields,
            ambiguous_fields=action.ambiguous_fields,
            industry=industry,
            language=language,
        )
        return {
            "type": "summary",
            "content": summary,
            "seed": self._state.get_seed_final(),
            "progress": self._state.get_progress(),
        }

    def _get_categories(self) -> list[str]:
        """Extract category names from the schema's nested model fields."""
        categories: list[str] = []
        for name, field_info in type(self._schema).model_fields.items():
            if name == "idioma":
                continue
            desc = field_info.description or name
            categories.append(desc)
        return categories

    @staticmethod
    def _is_stop_signal(text: str) -> bool:
        """Check if the user's response is an explicit stop signal."""
        stop_words = {
            "terminar",
            "finalizar",
            "listo",
            "eso es todo",
            "no más",
            "stop",
            "done",
            "finish",
            "that's all",
            "end",
            "salir",
            "exit",
        }
        normalized = text.strip().lower()
        return normalized in stop_words
