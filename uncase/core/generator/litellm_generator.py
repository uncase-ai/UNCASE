"""LiteLLM-based synthetic conversation generator — Layer 3 implementation.

Takes a SeedSchema and generates realistic synthetic conversations by
prompting an LLM with carefully engineered system prompts that encode
the domain, roles, factual constraints, and expected flow.
"""

from __future__ import annotations

import contextlib
import json
import random
import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import structlog

from uncase.core.generator.base import BaseGenerator
from uncase.exceptions import GenerationError
from uncase.schemas.conversation import Conversation, ConversationTurn

if TYPE_CHECKING:
    from uncase.schemas.quality import QualityReport
    from uncase.schemas.scenario import ScenarioTemplate
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for the LiteLLM generator."""

    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096
    language_override: str | None = None
    max_retries: int = 3
    temperature_variation: float = 0.05
    api_base: str | None = None
    retry_temperature_step: float = 0.1  # Increase temperature on each retry


# -- Prompt templates --

_DOMAIN_CONTEXT: dict[str, str] = {
    "automotive.sales": (
        "You are generating a conversation in the automotive sales domain. "
        "This involves vehicle sales interactions between dealership staff and potential buyers. "
        "Conversations should reflect realistic sales processes: needs assessment, vehicle presentation, "
        "test drives, pricing negotiation, financing options, and closing."
    ),
    "medical.consultation": (
        "You are generating a conversation in the medical consultation domain. "
        "This involves healthcare interactions between medical professionals and patients. "
        "Conversations should reflect realistic clinical workflows: intake, symptom assessment, "
        "examination discussion, diagnosis explanation, treatment planning, and follow-up."
    ),
    "legal.advisory": (
        "You are generating a conversation in the legal advisory domain. "
        "This involves legal consultations between attorneys/legal advisors and clients. "
        "Conversations should reflect realistic legal processes: case intake, fact gathering, "
        "legal analysis discussion, strategy options, risk assessment, and next steps."
    ),
    "finance.advisory": (
        "You are generating a conversation in the financial advisory domain. "
        "This involves financial planning interactions between advisors and clients. "
        "Conversations should reflect realistic advisory processes: financial assessment, "
        "goal identification, risk profiling, product recommendations, and action planning."
    ),
    "industrial.support": (
        "You are generating a conversation in the industrial support domain. "
        "This involves technical support interactions for industrial equipment and processes. "
        "Conversations should reflect realistic support workflows: issue identification, "
        "troubleshooting, diagnostic steps, resolution guidance, and escalation paths."
    ),
    "education.tutoring": (
        "You are generating a conversation in the education tutoring domain. "
        "This involves educational interactions between tutors/instructors and students. "
        "Conversations should reflect realistic tutoring sessions: topic introduction, "
        "concept explanation, practice exercises, feedback, and progress assessment."
    ),
}


def _select_scenario(seed: SeedSchema, *, rng: random.Random | None = None) -> ScenarioTemplate | None:
    """Pick a scenario from the seed via weighted random selection.

    Returns None if the seed has no scenarios attached.
    """
    if not seed.scenarios:
        return None

    generator = rng or random
    weights = [s.weight for s in seed.scenarios]
    selected = generator.choices(seed.scenarios, weights=weights, k=1)[0]

    logger.debug(
        "scenario_selected",
        scenario=selected.name,
        seed_id=seed.seed_id,
    )
    return selected


def _build_scenario_block(scenario: ScenarioTemplate) -> str:
    """Build a prompt augmentation block from a scenario template."""
    lines: list[str] = []

    lines.append("\n## Scenario Archetype")
    lines.append(f"**Type**: {scenario.name}")
    lines.append(f"**Intent**: {scenario.intent}")

    if scenario.description:
        lines.append(f"**Description**: {scenario.description}")

    # Skill level guidance
    skill_hints = {
        "basic": (
            "Keep the conversation simple and focused. 3-6 turns, single topic, "
            "straightforward resolution. Suitable for basic training examples."
        ),
        "intermediate": (
            "Generate a moderately complex conversation. 6-12 turns, may span "
            "multiple related topics with natural transitions."
        ),
        "advanced": (
            "Generate a complex, multi-step conversation. 10-20+ turns with "
            "tool chains, branching logic, edge-case handling, and nuanced "
            "interpersonal dynamics."
        ),
    }
    lines.append(f"**Complexity**: {scenario.skill_level} — {skill_hints[scenario.skill_level]}")

    if scenario.expected_tool_sequence:
        tool_seq = " → ".join(scenario.expected_tool_sequence)
        lines.append(
            f"\n**Expected tool usage order**: {tool_seq}\n"
            "The assistant should call these tools in approximately this order "
            "during the conversation. Adapt naturally — not every call is mandatory "
            "but the sequence reflects the typical flow."
        )

    if scenario.edge_case:
        lines.append(
            "\n**Edge case scenario**: This is a NON-happy-path conversation. "
            "The conversation should include realistic complications, boundary "
            "enforcement, or graceful failure handling as described in the intent."
        )

    return "\n".join(lines)


def _build_system_prompt(
    seed: SeedSchema,
    *,
    language: str | None = None,
    scenario: ScenarioTemplate | None = None,
) -> str:
    """Build a detailed system prompt from a SeedSchema.

    The prompt instructs the LLM to generate a realistic multi-turn
    conversation that adheres to the seed's domain, roles, constraints,
    and expected flow.

    Args:
        seed: The seed schema to generate from.
        language: Optional language override (ISO 639-1).
        scenario: Optional scenario template to steer generation.

    Returns:
        Complete system prompt string.
    """
    lang = language or seed.idioma
    domain_desc = _DOMAIN_CONTEXT.get(seed.dominio, f"You are generating a conversation in the {seed.dominio} domain.")

    # Build role descriptions
    role_lines: list[str] = []
    for role in seed.roles:
        desc = seed.descripcion_roles.get(role, "No additional description provided.")
        role_lines.append(f'  - "{role}": {desc}')
    roles_block = "\n".join(role_lines)

    # Build flow steps — scenario flow_steps override seed defaults when present
    flow_source = (
        scenario.flow_steps
        if scenario and scenario.flow_steps
        else seed.pasos_turnos.flujo_esperado
    )
    flow_lines = [f"  {i + 1}. {step}" for i, step in enumerate(flow_source)]
    flow_block = "\n".join(flow_lines)

    # Build constraints
    constraints_block = ""
    if seed.parametros_factuales.restricciones:
        constraint_lines = [f"  - {c}" for c in seed.parametros_factuales.restricciones]
        constraints_block = "\n## Factual Constraints (MUST be respected)\n" + "\n".join(constraint_lines)

    # Build tools section
    tools_block = ""
    if seed.parametros_factuales.herramientas:
        tool_lines = [f'  - "{t}"' for t in seed.parametros_factuales.herramientas]
        tools_block = (
            "\n## Available Tools\n"
            "The following tools may be used by participants during the conversation. "
            "When a role uses a tool, include it in the 'herramientas_usadas' field of that turn.\n"
            + "\n".join(tool_lines)
        )

    # Build structured tool definitions if available
    tool_defs_block = ""
    if seed.parametros_factuales.herramientas_definidas:
        def_lines: list[str] = []
        for td in seed.parametros_factuales.herramientas_definidas:
            def_lines.append(f'  - "{td.name}": {td.description}')
            if td.input_schema:
                def_lines.append(f"    Input: {json.dumps(td.input_schema, ensure_ascii=False)}")
        tool_defs_block = "\n## Structured Tool Definitions\n" + "\n".join(def_lines)

    # Build scenario block if a scenario is active
    scenario_block = _build_scenario_block(scenario) if scenario else ""

    # Language map for prompt instruction
    lang_names: dict[str, str] = {
        "es": "Spanish (Latin American)",
        "en": "English",
        "pt": "Portuguese (Brazilian)",
        "fr": "French",
        "de": "German",
    }
    lang_name = lang_names.get(lang, lang)

    return f"""You are an expert synthetic conversation generator for the UNCASE (SCSF) framework.

{domain_desc}

## Objective
{seed.objetivo}

## Scenario Context
{seed.parametros_factuales.contexto}

## Conversation Parameters
- **Language**: {lang_name} — ALL dialogue content MUST be in {lang_name}.
- **Tone**: {seed.tono}
- **Number of turns**: Generate between {seed.pasos_turnos.turnos_min} and {seed.pasos_turnos.turnos_max} turns.
- **Domain**: {seed.dominio}

## Participant Roles
{roles_block}

## Expected Conversation Flow
The conversation should follow these stages naturally (not rigidly — allow organic transitions):
{flow_block}
{constraints_block}
{tools_block}
{tool_defs_block}
{scenario_block}

## Output Format

You MUST output ONLY a valid JSON array of turn objects. No markdown, no explanation, no preamble.

Each turn object has the following fields:
- "turno": integer, 1-indexed turn number
- "rol": string, one of the defined roles ({", ".join(f'"{r}"' for r in seed.roles)})
- "contenido": string, the actual dialogue content for this turn (MUST be in {lang_name})
- "herramientas_usadas": array of strings, tools used in this turn (empty array if none)

Example of the EXACT expected format:
[
  {{
    "turno": 1,
    "rol": "{seed.roles[0]}",
    "contenido": "...",
    "herramientas_usadas": []
  }},
  {{
    "turno": 2,
    "rol": "{seed.roles[1] if len(seed.roles) > 1 else seed.roles[0]}",
    "contenido": "...",
    "herramientas_usadas": []
  }}
]

## Quality Requirements
- Each turn must be substantive (at least 1-2 sentences) and contextually relevant.
- Maintain consistent character/role behavior across all turns.
- Ensure factual accuracy within the domain.
- Use varied vocabulary — avoid repeating the same phrases.
- The conversation should feel natural and realistic, not scripted or robotic.
- Roles should alternate logically (not necessarily strictly alternating).
- NEVER include any real personal information (names, phone numbers, addresses, IDs).
  Use realistic but fictional placeholders if needed.
- Respect ALL factual constraints listed above."""


def _build_feedback_augmentation(quality_report: QualityReport) -> str:
    """Build additional prompt instructions based on quality report failures.

    Args:
        quality_report: The quality report with identified failures.

    Returns:
        Additional prompt text addressing specific quality issues.
    """
    if not quality_report.failures:
        return ""

    instructions: list[str] = []
    instructions.append(
        "\n## Quality Improvement Instructions\n"
        "Previous generation attempts did not meet quality thresholds. "
        "Pay special attention to the following:"
    )

    for failure in quality_report.failures:
        metric_name = failure.split("=")[0].strip() if "=" in failure else failure

        if "coherencia_dialogica" in metric_name:
            instructions.append(
                "- **Dialog Coherence**: Ensure each turn directly responds to or builds upon "
                "the previous turn. Maintain consistent topic threading. Avoid abrupt topic "
                "changes. Each role should acknowledge what the other said before contributing."
            )
        elif "diversidad_lexica" in metric_name:
            instructions.append(
                "- **Lexical Diversity**: Use varied vocabulary throughout the conversation. "
                "Avoid repeating the same words and phrases. Use synonyms, paraphrasing, "
                "and varied sentence structures. Each turn should introduce some new terms."
            )
        elif "rouge_l" in metric_name:
            instructions.append(
                "- **Structural Coherence**: Follow the expected conversation flow more closely. "
                "Ensure the conversation covers all the defined stages in a logical progression. "
                "The structure should match the seed's expected flow."
            )
        elif "fidelidad_factual" in metric_name:
            instructions.append(
                "- **Factual Fidelity**: Strictly adhere to domain-specific facts and constraints. "
                "Do not introduce information that contradicts the given context. "
                "All technical terms and procedures must be accurate for the domain."
            )
        elif "privacy_score" in metric_name:
            instructions.append(
                "- **Privacy (CRITICAL)**: ABSOLUTELY NO real personal identifiable information. "
                "Do not use real names, phone numbers, email addresses, ID numbers, "
                "addresses, or any other PII. Use obviously fictional placeholders."
            )
        elif "memorizacion" in metric_name:
            instructions.append(
                "- **Originality**: Generate fully original content. Do not reproduce "
                "memorized text from training data. Create unique dialogue that fits "
                "the scenario but is not a copy of existing conversations."
            )

    return "\n".join(instructions)


def _extract_json_array(raw_content: str) -> list[dict[str, Any]]:
    """Extract a JSON array from LLM output text.

    Tries direct parse first, then extracts from markdown code blocks.
    Avoids fragile regex bracket-matching — if structured extraction fails,
    raises GenerationError so the caller can trigger a smart retry.

    Args:
        raw_content: Raw string content from the LLM response.

    Returns:
        Parsed list of dicts.

    Raises:
        GenerationError: If no valid JSON array can be extracted.
    """
    content = raw_content.strip()

    # Strategy 1: Direct JSON parse (works when response_format=json_object)
    with contextlib.suppress(json.JSONDecodeError):
        parsed: Any = json.loads(content)
        if isinstance(parsed, list):
            return parsed        # Some models wrap array in an object: {"turns": [...]}
        if isinstance(parsed, dict):
            for key in ("turns", "conversation", "messages", "data"):
                val = parsed.get(key)
                if isinstance(val, list):
                    return val
    # Strategy 2: Extract from markdown code blocks
    code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", content, re.DOTALL)
    if code_block_match:
        with contextlib.suppress(json.JSONDecodeError):
            parsed = json.loads(code_block_match.group(1).strip())
            if isinstance(parsed, list):
                return parsed
    msg = "Failed to extract JSON array from LLM response"
    raise GenerationError(msg)


def _validate_turns(raw_turns: list[dict[str, Any]], seed: SeedSchema) -> list[ConversationTurn]:
    """Validate and convert raw dicts to ConversationTurn objects using Pydantic.

    Args:
        raw_turns: Parsed JSON turn dicts.
        seed: The seed schema (for role validation).

    Returns:
        List of validated ConversationTurn objects.

    Raises:
        GenerationError: If no valid turns could be constructed.
    """
    if not raw_turns:
        msg = "LLM returned an empty array of turns"
        raise GenerationError(msg)

    valid_roles = set(seed.roles)
    turns: list[ConversationTurn] = []

    for i, turn_data in enumerate(raw_turns):
        if not isinstance(turn_data, dict):
            logger.warning("skipping_invalid_turn", index=i, reason="not a dict")
            continue

        turno = turn_data.get("turno", i + 1)
        rol = turn_data.get("rol", "")
        contenido = turn_data.get("contenido", "")
        herramientas = turn_data.get("herramientas_usadas", [])

        if rol not in valid_roles:
            logger.warning(
                "turn_role_not_in_seed",
                turno=turno,
                rol=rol,
                valid_roles=sorted(valid_roles),
            )
            if not rol:
                rol = seed.roles[i % len(seed.roles)]

        if not contenido or not contenido.strip():
            logger.warning("skipping_empty_turn", turno=turno, rol=rol)
            continue

        try:
            turn = ConversationTurn(
                turno=turno if isinstance(turno, int) and turno >= 1 else i + 1,
                rol=rol,
                contenido=contenido.strip(),
                herramientas_usadas=herramientas if isinstance(herramientas, list) else [],
            )
            turns.append(turn)
        except Exception as exc:
            logger.warning("skipping_invalid_turn", turno=turno, error=str(exc))

    if not turns:
        msg = "No valid turns could be parsed from LLM response"
        raise GenerationError(msg)

    for idx, turn in enumerate(turns):
        turn.turno = idx + 1

    return turns


def _parse_llm_response(raw_content: str, seed: SeedSchema) -> list[ConversationTurn]:
    """Parse the LLM response into validated ConversationTurn objects.

    Uses structured JSON extraction + Pydantic validation. No regex bracket
    fallback — structural failures propagate to trigger smart retry.

    Args:
        raw_content: Raw string content from the LLM response.
        seed: The seed schema (for validation context).

    Returns:
        List of validated ConversationTurn objects.

    Raises:
        GenerationError: If parsing or validation fails.
    """
    raw_turns = _extract_json_array(raw_content)
    return _validate_turns(raw_turns, seed)


class LiteLLMGenerator(BaseGenerator):
    """Synthetic conversation generator powered by LiteLLM.

    Uses carefully engineered prompts to generate realistic multi-turn
    conversations from SeedSchema definitions. Supports multiple LLM
    providers through LiteLLM's unified interface.

    Usage:
        config = GenerationConfig(model="claude-sonnet-4-20250514", temperature=0.8)
        generator = LiteLLMGenerator(config=config)
        conversations = await generator.generate(seed, count=5)
    """

    def __init__(
        self,
        *,
        config: GenerationConfig | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
    ) -> None:
        """Initialize the generator.

        Args:
            config: Generation configuration. Uses defaults if None.
            api_key: API key for the LLM provider. If None, LiteLLM will
                     use environment variables.
            api_base: Base URL for the LLM provider API. Overrides config.api_base.
        """
        self._config = config or GenerationConfig()
        self._api_key = api_key
        self._api_base = api_base or self._config.api_base

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
    ) -> str:
        """Call the LLM via LiteLLM with smart retry on failure.

        Smart retry strategy:
        1. First attempt uses ``response_format=json_object`` when supported.
        2. On JSON format failure, retries without ``response_format``.
        3. On each retry, raises temperature by ``retry_temperature_step``
           to encourage diverse output and escape degenerate patterns.
        4. On structural parse failure (caller catches), the higher temperature
           from retry helps the model break out of malformed patterns.

        Args:
            system_prompt: The system message.
            user_prompt: The user message.
            temperature: Override temperature for this call.

        Returns:
            Raw string content from the LLM response.

        Raises:
            GenerationError: If the LLM call fails after all retries.
        """
        import litellm

        base_temp = temperature if temperature is not None else self._config.temperature

        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self._config.max_tokens,
        }

        if self._api_key:
            kwargs["api_key"] = self._api_key

        if self._api_base:
            kwargs["api_base"] = self._api_base

        # Request JSON output format when supported.
        # Gemini models don't fully support response_format — skip it entirely.
        model_lower = self._config.model.lower()
        supports_response_format = not (
            "gemini" in model_lower
            or "google" in model_lower
        )

        last_error: Exception | None = None
        for attempt in range(self._config.max_retries + 1):
            # Smart retry: escalate temperature on each attempt
            retry_temp = min(2.0, base_temp + attempt * self._config.retry_temperature_step)
            kwargs["temperature"] = retry_temp

            try:
                if attempt == 0 and supports_response_format:
                    kwargs["response_format"] = {"type": "json_object"}

                response = await litellm.acompletion(**kwargs)
                content = response.choices[0].message.content

                if not content:
                    msg = "LLM returned empty response"
                    raise GenerationError(msg)

                return content  # type: ignore[no-any-return]
            except Exception as exc:
                last_error = exc
                if "response_format" in kwargs:
                    kwargs.pop("response_format", None)
                    logger.warning(
                        "retrying_without_response_format",
                        model=self._config.model,
                        attempt=attempt + 1,
                        temperature=retry_temp,
                        error=str(exc),
                    )
                else:
                    logger.warning(
                        "llm_call_retry",
                        model=self._config.model,
                        attempt=attempt + 1,
                        max_retries=self._config.max_retries,
                        temperature=retry_temp,
                        error=str(exc),
                    )

        msg = f"LLM call failed after {self._config.max_retries + 1} attempts"
        raise GenerationError(msg) from last_error

    async def generate(self, seed: SeedSchema, count: int = 1) -> list[Conversation]:
        """Generate synthetic conversations from a seed.

        Creates `count` conversations with slight temperature variation
        for diversity. Each conversation traces back to the origin seed.

        Args:
            seed: The seed schema to generate from.
            count: Number of conversations to generate (default 1).

        Returns:
            List of generated Conversation objects.

        Raises:
            GenerationError: If generation fails.
            LLMConfigurationError: If LLM provider is not configured.
        """
        language = self._config.language_override or seed.idioma
        user_prompt = (
            f"Generate a complete synthetic conversation following the specification above. "
            f"Output ONLY a valid JSON array of turn objects. "
            f"Generate between {seed.pasos_turnos.turnos_min} and {seed.pasos_turnos.turnos_max} turns."
        )

        conversations: list[Conversation] = []

        for i in range(count):
            # Vary temperature slightly for diversity
            temp_variation = (i - count / 2) * self._config.temperature_variation
            adjusted_temp = max(0.0, min(2.0, self._config.temperature + temp_variation))

            # Select a scenario for this conversation (if seed has scenarios)
            scenario = _select_scenario(seed)

            # Build system prompt with scenario context
            system_prompt = _build_system_prompt(seed, language=language, scenario=scenario)

            logger.info(
                "generating_conversation",
                index=i + 1,
                total=count,
                model=self._config.model,
                temperature=round(adjusted_temp, 3),
                seed_id=seed.seed_id,
                domain=seed.dominio,
                scenario=scenario.name if scenario else None,
            )

            try:
                raw_content = await self._call_llm(
                    system_prompt,
                    user_prompt,
                    temperature=adjusted_temp,
                )

                turns = _parse_llm_response(raw_content, seed)

                # Record scenario in conversation metadata for traceability
                conv_metadata: dict[str, str] = {
                    "generator": "litellm",
                    "model": self._config.model,
                    "temperature": str(round(adjusted_temp, 3)),
                    "generation_index": str(i),
                }
                if scenario:
                    conv_metadata["scenario"] = scenario.name
                    conv_metadata["scenario_skill_level"] = scenario.skill_level
                    if scenario.edge_case:
                        conv_metadata["edge_case"] = "true"

                conversation = Conversation(
                    conversation_id=uuid.uuid4().hex,
                    seed_id=seed.seed_id,
                    dominio=seed.dominio,
                    idioma=language,
                    turnos=turns,
                    es_sintetica=True,
                    metadata=conv_metadata,
                )

                conversations.append(conversation)

                logger.info(
                    "conversation_generated",
                    conversation_id=conversation.conversation_id,
                    seed_id=seed.seed_id,
                    num_turns=conversation.num_turnos,
                )

            except GenerationError:
                logger.error(
                    "conversation_generation_failed",
                    index=i + 1,
                    total=count,
                    seed_id=seed.seed_id,
                )
                raise

            except Exception as exc:
                logger.error(
                    "unexpected_generation_error",
                    index=i + 1,
                    total=count,
                    seed_id=seed.seed_id,
                    error=str(exc),
                )
                msg = f"Unexpected error during generation: {exc}"
                raise GenerationError(msg) from exc

        logger.info(
            "generation_batch_complete",
            total_generated=len(conversations),
            seed_id=seed.seed_id,
        )

        return conversations

    async def generate_with_feedback(self, seed: SeedSchema, quality_report: QualityReport) -> list[Conversation]:
        """Generate improved conversations using quality feedback.

        Analyzes which metrics failed in the quality report and augments
        the generation prompt with specific instructions to address those
        failures.

        Args:
            seed: The seed schema to generate from.
            quality_report: Quality report from a previous evaluation.

        Returns:
            List of improved Conversation objects (single conversation).
        """
        language = self._config.language_override or seed.idioma
        scenario = _select_scenario(seed)
        system_prompt = _build_system_prompt(seed, language=language, scenario=scenario)

        # Augment with feedback-driven instructions
        feedback = _build_feedback_augmentation(quality_report)
        if feedback:
            system_prompt += "\n" + feedback

        user_prompt = (
            f"Generate an IMPROVED synthetic conversation following the specification above. "
            f"The previous attempt scored {quality_report.composite_score:.2f} composite quality. "
            f"Focus especially on the quality improvement instructions. "
            f"Output ONLY a valid JSON array of turn objects. "
            f"Generate between {seed.pasos_turnos.turnos_min} and {seed.pasos_turnos.turnos_max} turns."
        )

        logger.info(
            "generating_with_feedback",
            seed_id=seed.seed_id,
            previous_score=quality_report.composite_score,
            failures=quality_report.failures,
            model=self._config.model,
        )

        raw_content = await self._call_llm(system_prompt, user_prompt)
        turns = _parse_llm_response(raw_content, seed)

        feedback_metadata: dict[str, str] = {
            "generator": "litellm",
            "model": self._config.model,
            "temperature": str(self._config.temperature),
            "feedback_from": quality_report.conversation_id,
            "previous_score": str(quality_report.composite_score),
        }
        if scenario:
            feedback_metadata["scenario"] = scenario.name

        conversation = Conversation(
            conversation_id=uuid.uuid4().hex,
            seed_id=seed.seed_id,
            dominio=seed.dominio,
            idioma=language,
            turnos=turns,
            es_sintetica=True,
            metadata=feedback_metadata,
        )

        logger.info(
            "feedback_conversation_generated",
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            num_turns=conversation.num_turnos,
            previous_score=quality_report.composite_score,
        )

        return [conversation]
