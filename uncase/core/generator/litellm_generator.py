"""LiteLLM-based synthetic conversation generator — Layer 3 implementation.

Takes a SeedSchema and generates realistic synthetic conversations by
prompting an LLM with carefully engineered system prompts that encode
the domain, roles, factual constraints, and expected flow.
"""

from __future__ import annotations

import contextlib
import json
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
    from uncase.schemas.seed import SeedSchema

logger = structlog.get_logger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for the LiteLLM generator."""

    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096
    language_override: str | None = None
    max_retries: int = 2
    temperature_variation: float = 0.05


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


def _build_system_prompt(seed: SeedSchema, *, language: str | None = None) -> str:
    """Build a detailed system prompt from a SeedSchema.

    The prompt instructs the LLM to generate a realistic multi-turn
    conversation that adheres to the seed's domain, roles, constraints,
    and expected flow.

    Args:
        seed: The seed schema to generate from.
        language: Optional language override (ISO 639-1).

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

    # Build flow steps
    flow_lines = [f"  {i + 1}. {step}" for i, step in enumerate(seed.pasos_turnos.flujo_esperado)]
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


def _parse_llm_response(raw_content: str, seed: SeedSchema) -> list[ConversationTurn]:
    """Parse the LLM response into a list of ConversationTurn objects.

    Attempts multiple parsing strategies:
    1. Direct JSON parse
    2. Extract JSON from markdown code blocks
    3. Extract JSON array from surrounding text

    Args:
        raw_content: Raw string content from the LLM response.
        seed: The seed schema (for validation context).

    Returns:
        List of validated ConversationTurn objects.

    Raises:
        GenerationError: If parsing fails completely.
    """
    content = raw_content.strip()

    # Strategy 1: Direct JSON parse
    parsed: list[dict[str, Any]] | None = None
    with contextlib.suppress(json.JSONDecodeError):
        parsed = json.loads(content)

    # Strategy 2: Extract from markdown code blocks
    if parsed is None:
        code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", content, re.DOTALL)
        if code_block_match:
            with contextlib.suppress(json.JSONDecodeError):
                parsed = json.loads(code_block_match.group(1).strip())

    # Strategy 3: Find first [ ... ] in the text
    if parsed is None:
        bracket_match = re.search(r"\[.*\]", content, re.DOTALL)
        if bracket_match:
            with contextlib.suppress(json.JSONDecodeError):
                parsed = json.loads(bracket_match.group(0))

    if parsed is None:
        msg = "Failed to parse LLM response as JSON after all strategies"
        raise GenerationError(msg)

    if not isinstance(parsed, list):
        msg = f"Expected JSON array, got {type(parsed).__name__}"
        raise GenerationError(msg)

    if len(parsed) == 0:
        msg = "LLM returned an empty array of turns"
        raise GenerationError(msg)

    # Validate and convert each turn
    valid_roles = set(seed.roles)
    turns: list[ConversationTurn] = []

    for i, turn_data in enumerate(parsed):
        if not isinstance(turn_data, dict):
            logger.warning("skipping_invalid_turn", index=i, reason="not a dict")
            continue

        # Normalize fields
        turno = turn_data.get("turno", i + 1)
        rol = turn_data.get("rol", "")
        contenido = turn_data.get("contenido", "")
        herramientas = turn_data.get("herramientas_usadas", [])

        # Validate role
        if rol not in valid_roles:
            logger.warning(
                "turn_role_not_in_seed",
                turno=turno,
                rol=rol,
                valid_roles=sorted(valid_roles),
            )
            # Try to find closest match or use first role
            if not rol:
                rol = seed.roles[i % len(seed.roles)]

        # Validate content
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
            logger.warning(
                "skipping_invalid_turn",
                turno=turno,
                error=str(exc),
            )

    if not turns:
        msg = "No valid turns could be parsed from LLM response"
        raise GenerationError(msg)

    # Re-number turns sequentially
    for idx, turn in enumerate(turns):
        turn.turno = idx + 1

    return turns


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

    def __init__(self, *, config: GenerationConfig | None = None, api_key: str | None = None) -> None:
        """Initialize the generator.

        Args:
            config: Generation configuration. Uses defaults if None.
            api_key: API key for the LLM provider. If None, LiteLLM will
                     use environment variables.
        """
        self._config = config or GenerationConfig()
        self._api_key = api_key

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
    ) -> str:
        """Call the LLM via LiteLLM and return the response content.

        Args:
            system_prompt: The system message.
            user_prompt: The user message.
            temperature: Override temperature for this call.

        Returns:
            Raw string content from the LLM response.

        Raises:
            GenerationError: If the LLM call fails.
        """
        import litellm

        temp = temperature if temperature is not None else self._config.temperature

        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temp,
            "max_tokens": self._config.max_tokens,
        }

        # Set API key if provided
        if self._api_key:
            kwargs["api_key"] = self._api_key

        # Request JSON output format when supported
        # Some models support response_format, some don't — catch and retry without it
        last_error: Exception | None = None
        for attempt in range(self._config.max_retries + 1):
            try:
                if attempt == 0:
                    kwargs["response_format"] = {"type": "json_object"}

                response = await litellm.acompletion(**kwargs)
                content = response.choices[0].message.content

                if not content:
                    msg = "LLM returned empty response"
                    raise GenerationError(msg)

                return content  # type: ignore[no-any-return]

            except GenerationError:
                raise

            except Exception as exc:
                last_error = exc
                # If response_format failed, retry without it
                if "response_format" in kwargs:
                    kwargs.pop("response_format", None)
                    logger.warning(
                        "retrying_without_response_format",
                        model=self._config.model,
                        attempt=attempt + 1,
                        error=str(exc),
                    )
                else:
                    logger.warning(
                        "llm_call_failed",
                        model=self._config.model,
                        attempt=attempt + 1,
                        max_retries=self._config.max_retries,
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
        system_prompt = _build_system_prompt(seed, language=language)
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

            logger.info(
                "generating_conversation",
                index=i + 1,
                total=count,
                model=self._config.model,
                temperature=round(adjusted_temp, 3),
                seed_id=seed.seed_id,
                domain=seed.dominio,
            )

            try:
                raw_content = await self._call_llm(
                    system_prompt,
                    user_prompt,
                    temperature=adjusted_temp,
                )

                turns = _parse_llm_response(raw_content, seed)

                conversation = Conversation(
                    conversation_id=uuid.uuid4().hex,
                    seed_id=seed.seed_id,
                    dominio=seed.dominio,
                    idioma=language,
                    turnos=turns,
                    es_sintetica=True,
                    metadata={
                        "generator": "litellm",
                        "model": self._config.model,
                        "temperature": str(round(adjusted_temp, 3)),
                        "generation_index": str(i),
                    },
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
        system_prompt = _build_system_prompt(seed, language=language)

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

        conversation = Conversation(
            conversation_id=uuid.uuid4().hex,
            seed_id=seed.seed_id,
            dominio=seed.dominio,
            idioma=language,
            turnos=turns,
            es_sintetica=True,
            metadata={
                "generator": "litellm",
                "model": self._config.model,
                "temperature": str(self._config.temperature),
                "feedback_from": quality_report.conversation_id,
                "previous_score": str(quality_report.composite_score),
            },
        )

        logger.info(
            "feedback_conversation_generated",
            conversation_id=conversation.conversation_id,
            seed_id=seed.seed_id,
            num_turns=conversation.num_turnos,
            previous_score=quality_report.composite_score,
        )

        return [conversation]
