"""Tool call validity metric — validates tool calls against seed definitions.

Inspired by real-world training data validation patterns, this metric checks
that generated conversations use tools correctly:

1. **Name validity** — Tool names match the seed's herramientas/herramientas_definidas.
2. **Argument correctness** — Argument keys match the tool's input_schema properties.
3. **Required args** — All required arguments from input_schema are present.
4. **Type correctness** — Argument values match expected JSON Schema types.
5. **Sequence validity** — Each tool_call has a corresponding tool_result.
6. **No hallucination** — herramientas_usadas entries are all recognized.

Score = valid_checks / total_checks, or 1.0 if no tools are involved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog

from uncase.core.evaluator.metrics.base import BaseMetric

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.seed import SeedSchema
    from uncase.tools.schemas import ToolDefinition

logger = structlog.get_logger(__name__)

# JSON Schema type → Python types mapping
_JSON_TYPE_MAP: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "integer": (int,),
    "number": (int, float),
    "boolean": (bool,),
    "array": (list,),
    "object": (dict,),
}


class ToolCallValidatorMetric(BaseMetric):
    """Validates tool call correctness against seed-defined tool schemas.

    Produces a score in [0.0, 1.0] representing the fraction of individual
    validation checks that pass.  When a seed defines no tools and the
    conversation uses none, the score is 1.0 (fully valid / not applicable).
    """

    @property
    def name(self) -> str:
        return "tool_call_validity"

    @property
    def display_name(self) -> str:
        return "Tool Call Validity"

    def compute(self, conversation: Conversation, seed: SeedSchema) -> float:
        """Compute tool call validity score."""
        # Build lookup structures from seed
        tool_names_from_list = set(seed.parametros_factuales.herramientas or [])
        tool_defs: dict[str, ToolDefinition] = {}
        if seed.parametros_factuales.herramientas_definidas:
            for td in seed.parametros_factuales.herramientas_definidas:
                tool_defs[td.name] = td

        all_valid_names = tool_names_from_list | set(tool_defs.keys())

        # Early return: if seed defines NO tools, just check for unsolicited usage
        if not all_valid_names:
            has_tool_usage = any(
                turn.herramientas_usadas or turn.tool_calls for turn in conversation.turnos
            )
            return 0.8 if has_tool_usage else 1.0

        # Collect all checks
        total_checks = 0
        passed_checks = 0

        for turn in conversation.turnos:
            # --- Check herramientas_usadas entries (name-level only) ---
            for tool_name in turn.herramientas_usadas:
                total_checks += 1
                if tool_name in all_valid_names:
                    passed_checks += 1
                else:
                    logger.debug(
                        "tool_call_invalid_name_in_herramientas",
                        turn=turn.turno,
                        tool_name=tool_name,
                    )

            # --- Check structured tool_calls ---
            if turn.tool_calls:
                for tc in turn.tool_calls:
                    # 1. Name validity
                    total_checks += 1
                    if tc.tool_name not in all_valid_names:
                        logger.debug(
                            "tool_call_unknown_name",
                            turn=turn.turno,
                            tool_name=tc.tool_name,
                        )
                        continue  # Name failed — skip arg checks for this call
                    passed_checks += 1

                    # 2-4. Argument validation (only if ToolDefinition exists)
                    if tc.tool_name in tool_defs:
                        td = tool_defs[tc.tool_name]
                        arg_passed, arg_total = self._validate_arguments(
                            tc.arguments, td.input_schema, turn.turno, tc.tool_name
                        )
                        passed_checks += arg_passed
                        total_checks += arg_total

        # --- Sequence validation: tool_calls should have tool_results ---
        seq_passed, seq_total = self._validate_sequence(conversation)
        passed_checks += seq_passed
        total_checks += seq_total

        # No tool usage in conversation despite seed defining tools —
        # this is a completeness concern handled by fidelity metric, not validity
        if total_checks == 0:
            return 1.0

        score = passed_checks / total_checks
        logger.debug(
            "tool_call_validity_computed",
            score=round(score, 4),
            passed=passed_checks,
            total=total_checks,
        )
        return score

    def _validate_arguments(
        self,
        arguments: dict[str, Any],
        input_schema: dict[str, Any],
        turn_number: int,
        tool_name: str,
    ) -> tuple[int, int]:
        """Validate tool call arguments against a JSON Schema definition.

        Returns:
            Tuple of (passed_checks, total_checks).
        """
        passed = 0
        total = 0

        properties = input_schema.get("properties", {})
        required_args = set(input_schema.get("required", []))

        # Check 2: No unknown argument keys
        if properties:
            for arg_name in arguments:
                total += 1
                if arg_name in properties:
                    passed += 1
                else:
                    logger.debug(
                        "tool_call_unknown_arg",
                        turn=turn_number,
                        tool=tool_name,
                        arg=arg_name,
                    )

        # Check 3: Required args present
        for req in required_args:
            total += 1
            if req in arguments:
                passed += 1
            else:
                logger.debug(
                    "tool_call_missing_required",
                    turn=turn_number,
                    tool=tool_name,
                    arg=req,
                )

        # Check 4: Type correctness
        for arg_name, arg_value in arguments.items():
            if arg_name not in properties:
                continue  # Already flagged as unknown
            expected_type = properties[arg_name].get("type")
            if expected_type is None:
                continue

            total += 1
            if self._type_matches(arg_value, expected_type):
                passed += 1
            else:
                logger.debug(
                    "tool_call_type_mismatch",
                    turn=turn_number,
                    tool=tool_name,
                    arg=arg_name,
                    expected=expected_type,
                    actual=type(arg_value).__name__,
                )

        # Check enum constraints
        for arg_name, arg_value in arguments.items():
            if arg_name not in properties:
                continue
            enum_values = properties[arg_name].get("enum")
            if enum_values is not None:
                total += 1
                if arg_value in enum_values:
                    passed += 1
                else:
                    logger.debug(
                        "tool_call_enum_mismatch",
                        turn=turn_number,
                        tool=tool_name,
                        arg=arg_name,
                        value=arg_value,
                        allowed=enum_values,
                    )

        return passed, total

    def _validate_sequence(self, conversation: Conversation) -> tuple[int, int]:
        """Check that each tool_call has a corresponding tool_result.

        Returns:
            Tuple of (passed_checks, total_checks).
        """
        passed = 0
        total = 0

        turnos = conversation.turnos
        for i, turn in enumerate(turnos):
            if not turn.tool_calls:
                continue

            for tc in turn.tool_calls:
                total += 1
                # Look for a matching tool_result in subsequent turns
                found = False
                for future_turn in turnos[i + 1 :]:
                    if future_turn.tool_results:
                        for tr in future_turn.tool_results:
                            if tr.tool_call_id == tc.tool_call_id:
                                found = True
                                break
                    if found:
                        break

                if found:
                    passed += 1
                else:
                    logger.debug(
                        "tool_call_missing_result",
                        turn=turn.turno,
                        tool_call_id=tc.tool_call_id,
                        tool_name=tc.tool_name,
                    )

        return passed, total

    @staticmethod
    def _type_matches(value: Any, expected_type: str) -> bool:
        """Check if a Python value matches a JSON Schema type string."""
        expected_types = _JSON_TYPE_MAP.get(expected_type)
        if expected_types is None:
            return True  # Unknown schema type — don't penalize

        # Special case: boolean is a subclass of int in Python,
        # but JSON Schema treats them as distinct types
        if expected_type == "integer" and isinstance(value, bool):
            return False
        if expected_type == "number" and isinstance(value, bool):
            return False

        return isinstance(value, expected_types)
