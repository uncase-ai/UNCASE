"""Tests for the Layer 0 State Manager."""

from __future__ import annotations

import pytest

from uncase.core.seed_engine.layer0.config import Layer0Config
from uncase.core.seed_engine.layer0.schemas.automotriz import SeedAutomotriz
from uncase.core.seed_engine.layer0.state_manager import ActionType, StateManager

# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def config() -> Layer0Config:
    """Layer 0 config with reduced max_turns for testing."""
    return Layer0Config(max_turns=5, min_confidence_required=0.8)


@pytest.fixture()
def state(config: Layer0Config) -> StateManager:
    """State manager with a fresh automotive schema."""
    schema = SeedAutomotriz()
    return StateManager(schema, config)


# ===================================================================
# Initialization
# ===================================================================


class TestStateManagerInit:
    """Test State Manager initialization."""

    def test_initial_turn_count_zero(self, state: StateManager) -> None:
        """Turn counter starts at zero."""
        assert state.turn_count == 0

    def test_not_complete_initially(self, state: StateManager) -> None:
        """State is not complete when no fields are filled."""
        assert state.is_complete is False

    def test_progress_shows_zero_filled(self, state: StateManager) -> None:
        """Progress shows zero fields filled initially."""
        progress = state.get_progress()
        assert progress["filled_fields"] == 0
        assert progress["required_filled"] == 0
        assert progress["turn"] == 0


# ===================================================================
# Field updates
# ===================================================================


class TestFieldUpdates:
    """Test State Manager update method."""

    def test_update_single_field(self, state: StateManager) -> None:
        """Updating a single field changes its status and confidence."""
        updated = state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95},
            }
        )
        assert "cliente_perfil.tipo_cliente" in updated
        assert state.schema.cliente_perfil.tipo_cliente == "particular"

    def test_update_multiple_fields(self, state: StateManager) -> None:
        """Multiple fields can be updated in one call."""
        updated = state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "empresa", "confidence": 0.9},
                "cliente_perfil.urgencia": {"value": "decidiendo", "confidence": 0.85},
                "intencion.uso_principal": {"value": "negocio", "confidence": 0.92},
            }
        )
        assert len(updated) == 3

    def test_high_confidence_field_not_overwritten(self, state: StateManager) -> None:
        """A field with confidence >= 0.9 is protected from lower-confidence overwrites."""
        state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95},
            }
        )
        state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "empresa", "confidence": 0.6},
            }
        )
        # Original value preserved
        assert state.schema.cliente_perfil.tipo_cliente == "particular"

    def test_unknown_field_skipped(self, state: StateManager) -> None:
        """Unknown field names are silently skipped."""
        updated = state.update(
            {
                "nonexistent.field": {"value": "test", "confidence": 0.9},
            }
        )
        assert len(updated) == 0

    def test_none_value_skipped(self, state: StateManager) -> None:
        """None values are not applied."""
        updated = state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": None, "confidence": 0.9},
            }
        )
        assert len(updated) == 0

    def test_confidence_status_mapping(self, state: StateManager) -> None:
        """Confidence maps to correct FieldStatus."""
        # >= 0.9 -> CONFIRMED
        state.update({"cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95}})
        progress = state.get_progress()
        assert progress["fields"]["cliente_perfil.tipo_cliente"]["status"] == "confirmed"

        # >= 0.7 and < 0.9 -> EXTRACTED
        state.update({"cliente_perfil.urgencia": {"value": "explorando", "confidence": 0.75}})
        progress = state.get_progress()
        assert progress["fields"]["cliente_perfil.urgencia"]["status"] == "extracted"

        # < 0.7 -> AMBIGUOUS
        state.update({"intencion.uso_principal": {"value": "personal", "confidence": 0.5}})
        progress = state.get_progress()
        assert progress["fields"]["intencion.uso_principal"]["status"] == "ambiguous"


# ===================================================================
# Turn management
# ===================================================================


class TestTurnManagement:
    """Test turn counter and max turns."""

    def test_increment_turn(self, state: StateManager) -> None:
        """Turn counter increments correctly."""
        state.increment_turn()
        assert state.turn_count == 1
        state.increment_turn()
        assert state.turn_count == 2

    def test_max_turns_triggers_completion(self, state: StateManager) -> None:
        """Reaching max_turns marks the state as complete."""
        for _ in range(5):
            state.increment_turn()
        assert state.is_complete is True


# ===================================================================
# User stop signal
# ===================================================================


class TestUserStop:
    """Test explicit user stop."""

    def test_user_stop_completes(self, state: StateManager) -> None:
        """request_stop marks the loop as complete."""
        assert state.is_complete is False
        state.request_stop()
        assert state.is_complete is True


# ===================================================================
# Completion detection
# ===================================================================


class TestCompletionDetection:
    """Test automatic completion when all required fields are filled."""

    def test_all_required_filled_completes(self, state: StateManager) -> None:
        """Filling all required fields with high confidence triggers completion."""
        from uncase.core.seed_engine.layer0.schemas.automotriz import REQUIRED_FIELDS_AUTOMOTRIZ

        # Fill all required fields
        for field_name in REQUIRED_FIELDS_AUTOMOTRIZ:
            state.update({field_name: {"value": "test_value", "confidence": 0.9}})

        assert state.is_complete is True

    def test_partial_required_not_complete(self, state: StateManager) -> None:
        """Only partially filling required fields does not trigger completion."""
        state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95},
                "cliente_perfil.urgencia": {"value": "urgente", "confidence": 0.9},
            }
        )
        assert state.is_complete is False


# ===================================================================
# Next action decisions
# ===================================================================


class TestNextAction:
    """Test decide_next_action logic."""

    def test_initial_action_is_ask_question(self, state: StateManager) -> None:
        """Initial action should be to ask a question."""
        action = state.decide_next_action()
        assert action.action == ActionType.ASK_QUESTION
        assert len(action.missing_fields) > 0

    def test_ambiguous_triggers_clarification(self, state: StateManager) -> None:
        """Ambiguous fields trigger a clarification action."""
        state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.5},
            }
        )
        action = state.decide_next_action()
        assert action.action == ActionType.REQUEST_CLARIFICATION
        assert len(action.ambiguous_fields) > 0

    def test_near_max_turns_triggers_summary(self, state: StateManager) -> None:
        """When near max turns, a summary action is returned."""
        # Advance to turn 4 of 5 max
        for _ in range(4):
            state.increment_turn()
        action = state.decide_next_action()
        assert action.action == ActionType.PRESENT_SUMMARY

    def test_complete_returns_complete_action(self, state: StateManager) -> None:
        """When complete, the action is COMPLETE."""
        state.request_stop()
        action = state.decide_next_action()
        assert action.action == ActionType.COMPLETE

    def test_all_required_done_triggers_summary(self, state: StateManager) -> None:
        """When all required fields are done but optional remain, present summary."""
        from uncase.core.seed_engine.layer0.schemas.automotriz import REQUIRED_FIELDS_AUTOMOTRIZ

        for field_name in REQUIRED_FIELDS_AUTOMOTRIZ:
            state.update({field_name: {"value": "test", "confidence": 0.95}})

        action = state.decide_next_action()
        # Should be COMPLETE since all required are filled
        assert action.action == ActionType.COMPLETE


# ===================================================================
# Progress tracking
# ===================================================================


class TestProgressTracking:
    """Test get_progress method."""

    def test_progress_structure(self, state: StateManager) -> None:
        """Progress dict has the expected keys."""
        progress = state.get_progress()
        assert "turn" in progress
        assert "max_turns" in progress
        assert "total_fields" in progress
        assert "filled_fields" in progress
        assert "required_total" in progress
        assert "required_filled" in progress
        assert "is_complete" in progress
        assert "fields" in progress

    def test_progress_updates_after_fill(self, state: StateManager) -> None:
        """Progress reflects filled fields."""
        state.update(
            {
                "cliente_perfil.tipo_cliente": {"value": "particular", "confidence": 0.95},
            }
        )
        progress = state.get_progress()
        assert progress["filled_fields"] >= 1
