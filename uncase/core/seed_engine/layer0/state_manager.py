"""State Manager — Deterministic orchestrator for the agentic extraction loop.

The State Manager is the brain of the extraction loop.  It is **not** an ML
model — it is pure Python logic that:

- Maintains the Pydantic schema as the source of truth.
- Tracks per-field status (``empty → extracted → confirmed``) and confidence.
- Decides when the conversation is complete.
- Tells the Interviewer what to ask next.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.schemas.base import (
    BaseSeedExtraction,
    FieldMeta,
    FieldStatus,
)
from uncase.log_config import get_logger

logger = get_logger(__name__)


class ActionType(StrEnum):
    """What the loop should do next."""

    ASK_QUESTION = "ask_question"
    REQUEST_CLARIFICATION = "request_clarification"
    PRESENT_SUMMARY = "present_summary"
    COMPLETE = "complete"


class NextAction(BaseModel):
    """Decision object produced by the State Manager after each turn."""

    action: ActionType = Field(..., description="Type of action to take.")
    missing_fields: list[FieldMeta] = Field(
        default_factory=list,
        description="Required fields that still need values.",
    )
    ambiguous_fields: list[FieldMeta] = Field(
        default_factory=list,
        description="Fields with low confidence that need clarification.",
    )
    message: str = Field(
        default="",
        description="Human-readable explanation of the decision.",
    )


class StateManager:
    """Deterministic state tracker for the agentic extraction loop.

    Args:
        schema: The seed extraction schema instance (e.g. ``SeedAutomotriz``).
        config: Layer 0 configuration (max turns, confidence thresholds, etc.).
    """

    def __init__(
        self,
        schema: BaseSeedExtraction,
        config: Layer0Config | None = None,
    ) -> None:
        self._config = config or Layer0Config()
        self._schema = schema
        self._required_fields: frozenset[str] = self._resolve_required_fields()
        self._field_registry: dict[str, FieldMeta] = {
            fm.field_name: fm for fm in schema.get_field_registry()
        }
        # Override is_required based on the schema's explicit declaration
        for name in self._required_fields:
            if name in self._field_registry:
                self._field_registry[name].is_required = True

        self._turn_count: int = 0
        self._user_requested_stop: bool = False

        logger.info(
            "state_manager_initialized",
            total_fields=len(self._field_registry),
            required_fields=len(self._required_fields),
            max_turns=self._config.max_turns,
        )

    # ── Public API ───────────────────────────────────────────────────

    @property
    def turn_count(self) -> int:
        """Current number of completed interview turns."""
        return self._turn_count

    @property
    def schema(self) -> BaseSeedExtraction:
        """Current schema instance with extracted values."""
        return self._schema

    @property
    def is_complete(self) -> bool:
        """Whether the extraction loop should stop."""
        if self._user_requested_stop:
            return True
        if self._turn_count >= self._config.max_turns:
            return True
        return self._all_required_complete()

    def increment_turn(self) -> None:
        """Advance the turn counter by one."""
        self._turn_count += 1

    def request_stop(self) -> None:
        """Signal that the user explicitly asked to end the interview."""
        self._user_requested_stop = True
        logger.info("user_requested_stop", turn=self._turn_count)

    def update(self, extraction_result: dict[str, Any]) -> list[str]:
        """Apply extracted field values and confidence scores to the state.

        Args:
            extraction_result: A dict whose keys are dot-path field names
                and values are dicts with ``value`` and ``confidence`` keys.

                Example::

                    {
                        "cliente_perfil.tipo_cliente": {
                            "value": "particular",
                            "confidence": 0.95,
                        }
                    }

        Returns:
            List of field names that were actually updated.
        """
        updated: list[str] = []

        for field_name, data in extraction_result.items():
            if field_name not in self._field_registry:
                logger.warning("unknown_field_skipped", field_name=field_name)
                continue

            value = data.get("value")
            confidence = float(data.get("confidence", 0.0))

            if value is None:
                continue

            meta = self._field_registry[field_name]

            # Never overwrite a high-confidence field with lower confidence
            if meta.confidence >= 0.9 and confidence < meta.confidence:
                logger.debug(
                    "high_confidence_field_preserved",
                    field_name=field_name,
                    existing_confidence=meta.confidence,
                    new_confidence=confidence,
                )
                continue

            # Apply value to schema
            self._schema.set_field_value(field_name, value)

            # Update metadata
            if confidence >= 0.9:
                meta.status = FieldStatus.CONFIRMED
            elif confidence >= 0.7:
                meta.status = FieldStatus.EXTRACTED
            else:
                meta.status = FieldStatus.AMBIGUOUS

            meta.confidence = confidence
            updated.append(field_name)

            logger.debug(
                "field_updated",
                field_name=field_name,
                status=meta.status.value,
                confidence=confidence,
            )

        return updated

    def decide_next_action(self) -> NextAction:
        """Determine what the loop should do next.

        Returns:
            A ``NextAction`` describing the recommended course of action.
        """
        if self.is_complete:
            return NextAction(
                action=ActionType.COMPLETE,
                message="All required fields are complete or loop terminated.",
            )

        # Gather fields needing attention
        missing = self._get_missing_required()
        ambiguous = self._get_ambiguous()

        # Near the end of allowed turns, present a summary
        remaining_turns = self._config.max_turns - self._turn_count
        if remaining_turns <= 2 and (missing or ambiguous):
            return NextAction(
                action=ActionType.PRESENT_SUMMARY,
                missing_fields=missing,
                ambiguous_fields=ambiguous,
                message=f"Only {remaining_turns} turn(s) remaining. Presenting summary.",
            )

        # If there are ambiguous fields, clarify them first
        if ambiguous:
            return NextAction(
                action=ActionType.REQUEST_CLARIFICATION,
                missing_fields=missing,
                ambiguous_fields=ambiguous,
                message=f"{len(ambiguous)} field(s) need clarification.",
            )

        # Normal flow — ask about missing fields
        if missing:
            return NextAction(
                action=ActionType.ASK_QUESTION,
                missing_fields=missing,
                ambiguous_fields=ambiguous,
                message=f"{len(missing)} required field(s) still missing.",
            )

        # All required done — present summary for optional fields
        return NextAction(
            action=ActionType.PRESENT_SUMMARY,
            message="All required fields complete. Ready for summary.",
        )

    def get_progress(self) -> dict[str, Any]:
        """Return a progress snapshot of all fields.

        Returns:
            A dict with overall stats and per-field details.
        """
        total = len(self._field_registry)
        filled = sum(
            1
            for m in self._field_registry.values()
            if m.status in {FieldStatus.EXTRACTED, FieldStatus.CONFIRMED}
        )
        required_total = len(self._required_fields)
        required_filled = sum(
            1
            for name in self._required_fields
            if name in self._field_registry
            and self._field_registry[name].status
            in {FieldStatus.EXTRACTED, FieldStatus.CONFIRMED}
            and self._field_registry[name].confidence >= self._config.min_confidence_required
        )

        return {
            "turn": self._turn_count,
            "max_turns": self._config.max_turns,
            "total_fields": total,
            "filled_fields": filled,
            "required_total": required_total,
            "required_filled": required_filled,
            "is_complete": self.is_complete,
            "fields": {
                name: {
                    "status": meta.status.value,
                    "confidence": meta.confidence,
                    "is_required": meta.is_required,
                }
                for name, meta in self._field_registry.items()
            },
        }

    def get_seed_final(self) -> BaseSeedExtraction:
        """Return the final extracted schema."""
        return self._schema

    # ── Private helpers ──────────────────────────────────────────────

    def _resolve_required_fields(self) -> frozenset[str]:
        """Get required field names from the schema class."""
        if hasattr(self._schema, "required_field_names"):
            return self._schema.required_field_names()
        # Fallback: use the field registry's is_required
        return frozenset(
            fm.field_name for fm in self._schema.get_field_registry() if fm.is_required
        )

    def _all_required_complete(self) -> bool:
        """Check if all required fields meet the confidence threshold."""
        for name in self._required_fields:
            meta = self._field_registry.get(name)
            if meta is None:
                return False
            if meta.status not in {FieldStatus.EXTRACTED, FieldStatus.CONFIRMED}:
                return False
            if meta.confidence < self._config.min_confidence_required:
                return False
        return True

    def _get_missing_required(self) -> list[FieldMeta]:
        """Return required fields that are still empty or below threshold."""
        missing: list[FieldMeta] = []
        for name in sorted(self._required_fields):
            meta = self._field_registry.get(name)
            if meta is None:
                continue
            if meta.status == FieldStatus.EMPTY or meta.confidence < self._config.min_confidence_required:
                missing.append(meta)
        return missing

    def _get_ambiguous(self) -> list[FieldMeta]:
        """Return fields that are marked as ambiguous (confidence < 0.7)."""
        return [
            meta
            for meta in self._field_registry.values()
            if meta.status == FieldStatus.AMBIGUOUS
        ]
