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
        "DOMAIN: Automotive Sales (dealership environment).\n"
        "This conversation takes place in a vehicle dealership between sales staff and "
        "potential buyers. The interaction must follow realistic automotive sales processes: "
        "customer greeting, needs assessment (budget, usage, preferences), vehicle presentation "
        "with specific specs, test drive coordination, pricing with transparent breakdowns, "
        "financing options with rates/terms, trade-in evaluation, and deal closing.\n"
        "INDUSTRY CONTEXT: Use realistic vehicle specifications (engine displacement, "
        "horsepower, fuel economy in km/l), pricing in local currency, financing terms "
        "(APR, monthly payments, down payment percentages), and dealership procedures."
    ),
    "medical.consultation": (
        "DOMAIN: Medical Consultation (clinical environment).\n"
        "This conversation takes place in a healthcare setting between medical professionals "
        "and patients. The interaction must follow realistic clinical workflows: patient intake "
        "with medical history, structured symptom assessment (onset, duration, severity, "
        "aggravating/relieving factors), physical examination discussion, differential diagnosis "
        "explanation, treatment plan with specific medications/dosages, and follow-up scheduling.\n"
        "INDUSTRY CONTEXT: Use proper medical terminology (ICD codes, drug names, dosages), "
        "follow clinical reasoning patterns, respect patient autonomy and informed consent, "
        "document allergies and contraindications. NEVER provide real medical advice."
    ),
    "legal.advisory": (
        "DOMAIN: Legal Advisory (law firm/legal office environment).\n"
        "This conversation takes place in a legal consultation setting between attorneys "
        "and clients. The interaction must follow realistic legal workflows: conflict check, "
        "case intake with fact pattern gathering, legal issue identification, applicable law "
        "analysis, strategy options with risk assessment, fee structure discussion, engagement "
        "letter terms, and next steps with deadlines.\n"
        "INDUSTRY CONTEXT: Reference specific legal frameworks (codes, statutes, precedents), "
        "use proper legal terminology, maintain attorney-client privilege awareness, discuss "
        "statutes of limitations, and provide balanced risk assessments. Include jurisdictional "
        "considerations where relevant."
    ),
    "finance.advisory": (
        "DOMAIN: Financial Advisory (advisory firm/banking environment).\n"
        "This conversation takes place in a financial planning setting between advisors "
        "and clients. The interaction must follow realistic advisory processes: client "
        "onboarding with KYC, financial health assessment (income, expenses, assets, "
        "liabilities), goal identification with time horizons, risk profiling with "
        "questionnaire, product recommendations with fee disclosures, portfolio construction, "
        "and periodic review scheduling.\n"
        "INDUSTRY CONTEXT: Use specific financial metrics (ROI, Sharpe ratio, expense ratios), "
        "regulatory disclaimers, suitability requirements, and diversification principles. "
        "Include risk disclosures and past-performance caveats."
    ),
    "industrial.support": (
        "DOMAIN: Industrial Technical Support (manufacturing/plant environment).\n"
        "This conversation takes place in an industrial support context between technical "
        "specialists and plant operators/engineers. The interaction must follow realistic "
        "support workflows: incident logging with equipment identification (model, serial, "
        "location), symptom description with error codes, structured diagnostic steps, "
        "root cause analysis, resolution guidance with safety warnings, parts ordering, "
        "and escalation to field service when needed.\n"
        "INDUSTRY CONTEXT: Use specific equipment terminology, reference maintenance manuals "
        "and procedures, include safety protocols (LOTO, PPE requirements), cite error codes "
        "and diagnostic parameters, and follow escalation matrices."
    ),
    "education.tutoring": (
        "DOMAIN: Education Tutoring (academic/training environment).\n"
        "This conversation takes place in a tutoring session between instructors and "
        "students. The interaction must follow realistic pedagogical patterns: learning "
        "objective introduction, prior knowledge assessment, concept explanation with "
        "examples, guided practice with scaffolding, independent practice, formative "
        "assessment with specific feedback, misconception correction, and progress summary.\n"
        "INDUSTRY CONTEXT: Use age-appropriate language, follow Bloom's taxonomy levels, "
        "employ Socratic questioning, provide constructive feedback with specific examples, "
        "and adapt difficulty based on student responses. Reference curriculum standards "
        "where relevant."
    ),
}

# Industry-specific compliance rules injected automatically based on domain
_DOMAIN_COMPLIANCE: dict[str, list[str]] = {
    "automotive.sales": [
        "All prices must include transparent breakdowns (base price, taxes, fees).",
        "Financing terms must include APR, total cost of credit, and payment schedule.",
        "Never misrepresent vehicle condition, history, or specifications.",
        "Trade-in valuations must reference market data or appraisal tools.",
        "Warranty terms must be explicitly stated with coverage details.",
    ],
    "medical.consultation": [
        "Always verify patient identity before discussing clinical details.",
        "Document allergies and current medications before prescribing.",
        "Explain risks, benefits, and alternatives for any proposed treatment.",
        "Never diagnose without adequate clinical assessment.",
        "Maintain HIPAA-equivalent privacy standards throughout.",
        "Use evidence-based medicine references when recommending treatments.",
    ],
    "legal.advisory": [
        "Perform conflict of interest check before engaging.",
        "Clearly distinguish between legal information and legal advice.",
        "Always mention applicable statutes of limitations.",
        "Discuss potential outcomes with realistic probability assessments.",
        "Include fee structure and billing expectations early in consultation.",
        "Document client instructions and agreed-upon strategy.",
    ],
    "finance.advisory": [
        "Complete KYC/AML verification before providing personalized advice.",
        "All product recommendations must include risk disclosures.",
        "Past performance disclaimers are mandatory when discussing returns.",
        "Suitability assessment must precede any product recommendation.",
        "Fee structures must be transparently disclosed (management fees, loads, expense ratios).",
        "Diversification principles must be explained for portfolio recommendations.",
    ],
    "industrial.support": [
        "Safety warnings must precede any hands-on troubleshooting steps.",
        "LOTO (Lock Out Tag Out) procedures must be referenced for electrical/mechanical work.",
        "Equipment model and serial numbers must be verified before diagnostics.",
        "Escalation criteria must be clearly defined (when to call field service).",
        "All diagnostic steps must reference applicable maintenance manual sections.",
    ],
    "education.tutoring": [
        "Adapt language complexity to the student's demonstrated level.",
        "Provide positive reinforcement before corrective feedback.",
        "Use multiple explanation approaches when the student struggles.",
        "Check for understanding before progressing to the next concept.",
        "Reference specific learning objectives and curriculum standards.",
    ],
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
    """Build a comprehensive system prompt from a SeedSchema.

    The prompt is structured to produce conversations that pass all
    evaluator metrics: ROUGE-L, fidelity, diversity, coherence, tool
    call validity, privacy, and memorization.

    Args:
        seed: The seed schema to generate from.
        language: Optional language override (ISO 639-1).
        scenario: Optional scenario template to steer generation.

    Returns:
        Complete system prompt string.
    """
    lang = language or seed.idioma
    domain_desc = _DOMAIN_CONTEXT.get(
        seed.dominio,
        f"DOMAIN: {seed.dominio}.\nGenerate a domain-appropriate professional conversation.",
    )

    # Language map
    lang_names: dict[str, str] = {
        "es": "Spanish (Latin American)",
        "en": "English",
        "pt": "Portuguese (Brazilian)",
        "fr": "French",
        "de": "German",
    }
    lang_name = lang_names.get(lang, lang)

    # ── Section 1: Identity & Domain ──
    sections: list[str] = []
    sections.append(
        "You are an expert synthetic conversation generator for the UNCASE (SCSF) "
        "framework — a system that produces high-quality training data for regulated "
        "industries. Your output will be evaluated by automated quality metrics and "
        "must pass ALL of them. Follow every instruction below precisely."
    )
    sections.append(f"\n## Domain Context\n{domain_desc}")

    # ── Section 2: Objective & Context ──
    sections.append(f"\n## Conversation Objective\n{seed.objetivo}")
    sections.append(f"\n## Scenario Context\n{seed.parametros_factuales.contexto}")

    # ── Section 3: Parameters ──
    sections.append(
        f"\n## Conversation Parameters\n"
        f"- **Language**: {lang_name} — ALL dialogue content MUST be in {lang_name}.\n"
        f"- **Tone**: {seed.tono}\n"
        f"- **Turn count**: EXACTLY between {seed.pasos_turnos.turnos_min} "
        f"and {seed.pasos_turnos.turnos_max} turns (inclusive). "
        f"This is a HARD requirement — generating fewer or more turns is a failure.\n"
        f"- **Domain**: {seed.dominio}"
    )

    # ── Section 4: Participant Roles (critical for fidelity + coherence) ──
    role_lines: list[str] = []
    for role in seed.roles:
        desc = seed.descripcion_roles.get(role, "")
        if desc:
            role_lines.append(f'  - **"{role}"**: {desc}')
        else:
            role_lines.append(f'  - **"{role}"**')

    valid_roles_str = ", ".join(f'"{r}"' for r in seed.roles)
    sections.append(
        f"\n## Participant Roles (STRICT)\n"
        f"The conversation has EXACTLY {len(seed.roles)} participants:\n"
        + "\n".join(role_lines)
        + f"\n\nCRITICAL RULES:\n"
        f'- The "rol" field in each turn MUST be one of: {valid_roles_str}\n'
        f'- Do NOT use generic names like "user", "assistant", "agent", "bot", '
        f'"system", "human", "AI". Use ONLY the exact role names listed above.\n'
        f"- Roles MUST strictly alternate between turns. In a 2-participant "
        f"conversation, every odd turn is one role and every even turn is the other.\n"
        f'- The first turn should be from "{seed.roles[0]}".'
    )

    # ── Section 5: Conversation Flow (critical for fidelity flow_adherence) ──
    flow_source = scenario.flow_steps if scenario and scenario.flow_steps else seed.pasos_turnos.flujo_esperado
    flow_lines = [f"  {i + 1}. {step}" for i, step in enumerate(flow_source)]

    flow_text = "\n".join(flow_lines)
    sections.append(
        "\n## Expected Conversation Flow (MUST follow this progression)\n"
        "The conversation MUST progress through these stages IN ORDER. "
        "Each stage should be clearly reflected in the dialogue content. "
        "Use the vocabulary and key terms from each stage description — the "
        "evaluator checks for their presence.\n" + flow_text
    )

    # Role-annotated flow if available
    if seed.pasos_turnos.flujo_con_roles:
        annotated_lines = [f"  {i + 1}. {step}" for i, step in enumerate(seed.pasos_turnos.flujo_con_roles)]
        sections.append(
            "\n### Role-Specific Flow Annotations\n"
            "Each step indicates which role leads that stage:\n" + "\n".join(annotated_lines)
        )

    # ── Section 6: Domain Constraints (critical for fidelity context_presence) ──
    if seed.parametros_factuales.restricciones:
        constraint_lines = [f"  - {c}" for c in seed.parametros_factuales.restricciones]
        sections.append(
            "\n## Factual Constraints (MANDATORY — violation is a quality failure)\n"
            "Every constraint below MUST be respected in the generated conversation. "
            "The evaluator extracts key terms from these constraints and verifies "
            "they appear in the dialogue.\n" + "\n".join(constraint_lines)
        )

    # Domain compliance rules
    compliance_rules = _DOMAIN_COMPLIANCE.get(seed.dominio, [])
    if compliance_rules:
        compliance_lines = [f"  - {r}" for r in compliance_rules]
        sections.append(
            "\n## Industry Compliance Rules\n"
            "These domain-specific regulations must be reflected in the conversation:\n" + "\n".join(compliance_lines)
        )

    # Seed-embedded domain instructions
    if seed.instrucciones_dominio:
        instr_lines = [f"  - {inst}" for inst in seed.instrucciones_dominio]
        sections.append("\n## Domain-Specific Generation Instructions\n" + "\n".join(instr_lines))

    # ── Section 7: Tool Usage Protocol (critical for tool_call_validity) ──
    has_tools = bool(seed.parametros_factuales.herramientas or seed.parametros_factuales.herramientas_definidas)
    if has_tools:
        sections.append("\n## Tool Usage Protocol")

        if seed.parametros_factuales.herramientas_definidas:
            sections.append(
                "The following tools are available. When a participant uses a tool, "
                'you MUST include the tool name in the "herramientas_usadas" array '
                "for that turn. Tool names must EXACTLY match the definitions below."
            )
            for td in seed.parametros_factuales.herramientas_definidas:
                tool_block = f'\n### Tool: "{td.name}"\n{td.description}'
                if td.input_schema:
                    # Show schema compactly
                    props = td.input_schema.get("properties", {})
                    required = td.input_schema.get("required", [])
                    if props:
                        param_lines: list[str] = []
                        for pname, pdef in props.items():
                            ptype = pdef.get("type", "any")
                            pdesc = pdef.get("description", "")
                            req_mark = " (REQUIRED)" if pname in required else ""
                            enum_vals = pdef.get("enum")
                            enum_str = f" — values: {enum_vals}" if enum_vals else ""
                            param_lines.append(f"    - {pname} ({ptype}{req_mark}): {pdesc}{enum_str}")
                        tool_block += "\n  **Parameters:**\n" + "\n".join(param_lines)
                sections.append(tool_block)
        elif seed.parametros_factuales.herramientas:
            tool_names = [f'  - "{t}"' for t in seed.parametros_factuales.herramientas]
            sections.append("Available tools (use exact names in herramientas_usadas):\n" + "\n".join(tool_names))

        sections.append(
            "\n**Tool usage rules:**\n"
            "- Only use tools listed above. Using unlisted tools is a quality failure.\n"
            "- Tool names in herramientas_usadas must match EXACTLY (case-sensitive).\n"
            "- Use tools at natural points in the conversation where domain workflow demands them.\n"
            "- After a tool is used, the next turn should reference or act on the tool's results."
        )
    else:
        sections.append(
            "\n## Tool Usage\nNo tools are defined for this seed. "
            'Leave "herramientas_usadas" as an empty array [] for every turn.'
        )

    # ── Section 8: Scenario block (if active) ──
    if scenario:
        sections.append(_build_scenario_block(scenario))

    # ── Section 9: Example conversation (few-shot) ──
    if seed.ejemplo_conversacion:
        example_lines: list[str] = []
        for ex_turn in seed.ejemplo_conversacion:
            ex_rol = ex_turn.get("rol", seed.roles[0])
            ex_content = ex_turn.get("contenido", "...")
            example_lines.append(f'  {ex_rol}: "{ex_content}"')
        sections.append(
            "\n## Example Conversation Style\n"
            "The following example turns demonstrate the expected tone, vocabulary, "
            "and level of detail. Match this style:\n" + "\n".join(example_lines)
        )

    # ── Section 10: Quality Guardrails (aligned to evaluator metrics) ──
    sections.append(
        "\n## Quality Guardrails (your output is scored on ALL of these)\n\n"
        "### Structural Coherence (ROUGE-L metric)\n"
        "- Your conversation MUST incorporate key vocabulary from the objective, "
        "context, constraints, and flow steps defined above.\n"
        "- Use the same domain terminology found in the seed fields — the evaluator "
        "checks for token overlap between your output and the seed specification.\n"
        "- Cover ALL flow stages defined above; skipping stages reduces your score.\n\n"
        "### Factual Fidelity\n"
        "- Use ONLY the defined role names. Role compliance is scored as a ratio.\n"
        "- Follow flow steps IN ORDER. Out-of-order progression incurs a 20% penalty.\n"
        "- Stay within the turn count range — over/under is penalized proportionally.\n"
        "- Embed domain-specific keywords from the context and constraints.\n"
        "- Use tools correctly if defined (name, required args, value types).\n\n"
        "### Lexical Diversity (TTR metric, threshold >= 0.55)\n"
        "- Use VARIED vocabulary throughout. Avoid repeating the same words/phrases.\n"
        "- Use synonyms, paraphrasing, and varied sentence structures.\n"
        "- Each turn should introduce new terminology relevant to the domain.\n"
        "- Do NOT use filler phrases repeatedly (e.g. 'por supuesto', 'claro que sí').\n\n"
        "### Dialog Coherence (threshold >= 0.65)\n"
        "- Each turn MUST respond to or build upon the previous turn.\n"
        "- Adjacent turns should share some topic vocabulary (but not too much — "
        "avoid parroting back what was just said).\n"
        "- Later turns MUST reference earlier points in the conversation "
        "(e.g. 'as you mentioned earlier', 'regarding the X you asked about').\n"
        "- Roles MUST alternate strictly. Two consecutive turns from the same role "
        "will score 0.0 on role alternation.\n"
        "- Each turn must be unique — do not repeat or closely paraphrase earlier turns.\n"
        "- Maintain consistent turn length throughout (don't let turns get very short "
        "toward the end).\n\n"
        "### Privacy (ZERO tolerance — score must be exactly 0.0)\n"
        "- ABSOLUTELY NO real personal identifiable information.\n"
        "- No real names, phone numbers, email addresses, ID numbers, credit cards, "
        "addresses, or dates of birth.\n"
        "- If the scenario needs personal data, use OBVIOUSLY FICTIONAL placeholders "
        "(e.g. 'Sr. García', '+52 55 0000 0000', 'ejemplo@correo.com').\n"
        "- The evaluator runs PII detection with regex patterns (Luhn, IBAN, phone "
        "formats) — any match fails the entire conversation.\n\n"
        "### Originality (memorization < 1%)\n"
        "- Generate FULLY ORIGINAL content. Do not reproduce memorized text.\n"
        "- Create unique dialogue that fits the scenario but is not copied from "
        "any existing source."
    )

    # ── Section 11: Negative constraints ──
    negative_rules: list[str] = [
        'Do NOT use "user", "assistant", "agent", "bot", "system", or "human" as role names.',
        "Do NOT generate fewer or more turns than the specified range.",
        "Do NOT skip any of the expected flow stages.",
        "Do NOT include markdown, code blocks, or explanatory text outside the JSON array.",
        "Do NOT include a trailing comma after the last element in the JSON array.",
        "Do NOT start or end with conversational meta-commentary (e.g. 'Here is the conversation...').",
        "Do NOT include greetings or closings that are not part of the domain workflow.",
    ]
    if seed.restricciones_negativas:
        negative_rules.extend(seed.restricciones_negativas)

    neg_lines = [f"  - {r}" for r in negative_rules]
    sections.append("\n## FORBIDDEN (negative constraints)\n" + "\n".join(neg_lines))

    # ── Section 12: Output Format (strict JSON spec) ──
    # Build a realistic 3-turn example using actual seed roles
    r0 = seed.roles[0]
    r1 = seed.roles[1] if len(seed.roles) > 1 else seed.roles[0]
    tool_val = ""
    if has_tools and seed.parametros_factuales.herramientas:
        tool_defs = seed.parametros_factuales.herramientas_definidas
        t_name = tool_defs[0].name if tool_defs else seed.parametros_factuales.herramientas[0]
        tool_val = f'"{t_name}"'

    tool_arr = tool_val if tool_val else ""
    sections.append(
        f"\n## Output Format (STRICT — any deviation is a failure)\n\n"
        f"Output ONLY a valid JSON array. No markdown fences. No preamble. No explanation.\n\n"
        f"Each element is an object with exactly these fields:\n"
        f'- "turno": integer (1-indexed, sequential)\n'
        f'- "rol": string (MUST be one of: {valid_roles_str})\n'
        f'- "contenido": string (the dialogue text in {lang_name}, min 2 sentences)\n'
        f'- "herramientas_usadas": array of strings (tool names used, or empty [])\n\n'
        f"EXACT format example:\n"
        f"[\n"
        f'  {{"turno": 1, "rol": "{r0}", "contenido": "...", '
        f'"herramientas_usadas": []}},\n'
        f'  {{"turno": 2, "rol": "{r1}", "contenido": "...", '
        f'"herramientas_usadas": [{tool_arr}]}},\n'
        f'  {{"turno": 3, "rol": "{r0}", "contenido": "...", '
        f'"herramientas_usadas": []}}\n'
        f"]"
    )

    return "\n".join(sections)


def _build_feedback_augmentation(quality_report: QualityReport) -> str:
    """Build additional prompt instructions based on quality report failures.

    Each failure maps to specific, actionable instructions that address
    the exact sub-metrics measured by the evaluator.

    Args:
        quality_report: The quality report with identified failures.

    Returns:
        Additional prompt text addressing specific quality issues.
    """
    if not quality_report.failures:
        return ""

    instructions: list[str] = []
    instructions.append(
        "\n## Quality Improvement Instructions (CRITICAL — previous attempt FAILED)\n"
        f"Previous score: {quality_report.composite_score:.2f}/1.00. "
        "The following metrics failed and MUST be fixed:"
    )

    for failure in quality_report.failures:
        metric_name = failure.split("=")[0].strip() if "=" in failure else failure

        if "coherencia_dialogica" in metric_name:
            instructions.append(
                "- **Dialog Coherence (FAILED)**: The evaluator measures 4 sub-metrics:\n"
                "  1. Turn-pair coherence: Adjacent turns must share some vocabulary "
                "(but not too much). Each reply should reference what was said before.\n"
                "  2. Role alternation: Roles MUST strictly alternate. Use the EXACT "
                "role names from the seed, never 'user'/'assistant'/'agent'.\n"
                "  3. Progressive flow: Each turn must be unique. Do not repeat content.\n"
                "  4. Referential consistency: Later turns must reference earlier points "
                "(e.g. 'regarding what you mentioned about...', 'as we discussed')."
            )
        elif "diversidad_lexica" in metric_name:
            instructions.append(
                "- **Lexical Diversity (FAILED)**: TTR must be >= 0.55. The evaluator "
                "uses a 50-token sliding window (MATTR). To fix:\n"
                "  - Use synonyms instead of repeating the same words.\n"
                "  - Vary sentence structures (questions, statements, conditionals).\n"
                "  - Introduce domain-specific jargon progressively.\n"
                "  - Avoid filler phrases ('por supuesto', 'claro', 'exactamente')."
            )
        elif "rouge_l" in metric_name:
            instructions.append(
                "- **ROUGE-L Structural Coverage (FAILED)**: The evaluator extracts tokens "
                "from the seed's objetivo, contexto, restricciones, flujo_esperado, and "
                "descripcion_roles, then checks how many appear in your conversation. To fix:\n"
                "  - Explicitly use vocabulary from the objective and context fields.\n"
                "  - Cover ALL flow stages using their exact terminology.\n"
                "  - Reference constraint keywords in the dialogue."
            )
        elif "fidelidad_factual" in metric_name:
            instructions.append(
                "- **Factual Fidelity (FAILED)**: The evaluator checks 5 sub-metrics:\n"
                "  1. Role compliance: ONLY use seed-defined role names.\n"
                "  2. Flow adherence: Hit all flow steps IN ORDER.\n"
                "  3. Turn count: Stay within min/max range.\n"
                "  4. Context presence: Include keywords from seed context/constraints.\n"
                "  5. Tool compliance: Use ONLY seed-defined tools with correct names."
            )
        elif "tool_call_validity" in metric_name:
            instructions.append(
                "- **Tool Call Validity (FAILED)**: The evaluator checks:\n"
                "  - Tool names match seed definitions exactly.\n"
                "  - Required arguments are present with correct types.\n"
                "  - Enum values are from the allowed set.\n"
                "  - Each tool call has a corresponding result in a later turn.\n"
                "  Fix: Use ONLY the exact tool names defined in the seed."
            )
        elif "privacy_score" in metric_name:
            instructions.append(
                "- **Privacy (CRITICAL FAILURE)**: The evaluator detected PII. "
                "Use ONLY obviously fictional data:\n"
                "  - Names: 'Sr. García', 'Dra. Martínez' (common surnames)\n"
                "  - Phone: '+52 55 0000 0000' (all zeros)\n"
                "  - Email: 'ejemplo@correo.com'\n"
                "  - IDs: 'XX000000' (placeholder format)\n"
                "  - NO real credit card numbers, IBANs, or national IDs."
            )
        elif "memorizacion" in metric_name:
            instructions.append(
                "- **Originality (FAILED)**: Content too similar to seed text. "
                "Paraphrase all seed content instead of copying. Use the domain "
                "knowledge but express it in completely original dialogue."
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
            return parsed  # Some models wrap array in an object: {"turns": [...]}
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

    # Strategy 3: Find bare JSON array in surrounding prose text
    # LLMs often wrap the JSON array in explanatory text before/after
    first_bracket = content.find("[")
    last_bracket = content.rfind("]")
    if first_bracket != -1 and last_bracket > first_bracket:
        with contextlib.suppress(json.JSONDecodeError):
            parsed = json.loads(content[first_bracket : last_bracket + 1])
            if isinstance(parsed, list):
                return parsed

    msg = "Failed to extract JSON array from LLM response"
    raise GenerationError(msg)


def _validate_turns(raw_turns: list[dict[str, Any]], seed: SeedSchema) -> list[ConversationTurn]:
    """Validate, repair, and convert raw dicts to ConversationTurn objects.

    Applies multi-pass post-processing:
    1. Role correction — maps invalid roles to seed roles
    2. Role alternation enforcement — fixes consecutive same-role turns
    3. Tool name validation — strips invalid tool references
    4. Turn renumbering — ensures sequential 1-indexed turno values

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

    # Build valid tool name set
    valid_tools: set[str] = set(seed.parametros_factuales.herramientas or [])
    if seed.parametros_factuales.herramientas_definidas:
        valid_tools |= {td.name for td in seed.parametros_factuales.herramientas_definidas}

    turns: list[ConversationTurn] = []

    for i, turn_data in enumerate(raw_turns):
        if not isinstance(turn_data, dict):
            logger.warning("skipping_invalid_turn", index=i, reason="not a dict")
            continue

        turno = turn_data.get("turno", i + 1)
        rol = turn_data.get("rol", "")
        contenido = turn_data.get("contenido", "")
        herramientas = turn_data.get("herramientas_usadas", [])

        # -- Pass 1: Role correction --
        if rol not in valid_roles:
            assigned_role = seed.roles[i % len(seed.roles)]
            logger.warning(
                "turn_role_not_in_seed",
                turno=turno,
                original_rol=rol,
                assigned_rol=assigned_role,
                valid_roles=sorted(valid_roles),
            )
            rol = assigned_role

        if not contenido or not contenido.strip():
            logger.warning("skipping_empty_turn", turno=turno, rol=rol)
            continue

        # -- Pass 2: Tool name validation --
        if isinstance(herramientas, list) and valid_tools:
            cleaned_tools = [t for t in herramientas if isinstance(t, str) and t in valid_tools]
            if len(cleaned_tools) != len(herramientas):
                logger.warning(
                    "invalid_tools_stripped",
                    turno=turno,
                    original=herramientas,
                    cleaned=cleaned_tools,
                )
            herramientas = cleaned_tools

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

    # -- Pass 3: Role alternation enforcement (for 2-participant conversations) --
    if len(seed.roles) == 2:
        repairs = 0
        for idx in range(1, len(turns)):
            if turns[idx].rol == turns[idx - 1].rol:
                expected_role = seed.roles[0] if turns[idx - 1].rol == seed.roles[1] else seed.roles[1]
                logger.warning(
                    "role_alternation_repaired",
                    turno=turns[idx].turno,
                    was=turns[idx].rol,
                    corrected_to=expected_role,
                )
                turns[idx].rol = expected_role
                repairs += 1
        if repairs:
            logger.info("role_alternation_total_repairs", count=repairs)

    # -- Pass 4: Renumber turns sequentially --
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
            "timeout": 90,  # Generation prompts are large — allow more time
        }

        if self._api_key:
            kwargs["api_key"] = self._api_key

        if self._api_base:
            kwargs["api_base"] = self._api_base

        # Request JSON output format when supported.
        # Gemini models don't fully support response_format — skip it entirely.
        model_lower = self._config.model.lower()
        supports_response_format = not ("gemini" in model_lower or "google" in model_lower)

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
        valid_roles = ", ".join(f'"{r}"' for r in seed.roles)
        user_prompt = (
            f"Generate a complete synthetic conversation following ALL specifications above. "
            f"Output ONLY a valid JSON array — no markdown, no explanation.\n\n"
            f"CHECKLIST before outputting:\n"
            f"1. Turn count is between {seed.pasos_turnos.turnos_min} and {seed.pasos_turnos.turnos_max}\n"
            f"2. Every 'rol' field is one of: {valid_roles}\n"
            f"3. Roles alternate strictly between turns\n"
            f"4. All flow stages are covered in order\n"
            f"5. Domain terminology from context/constraints appears in dialogue\n"
            f"6. No PII (no real names, phones, emails, IDs)\n"
            f"7. Varied vocabulary (no repetitive phrases)\n"
            f"8. Each turn is substantive (2+ sentences) and references prior turns"
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

        valid_roles = ", ".join(f'"{r}"' for r in seed.roles)
        user_prompt = (
            f"Generate an IMPROVED synthetic conversation following ALL specifications above. "
            f"The previous attempt scored {quality_report.composite_score:.2f}/1.00 composite quality "
            f"and FAILED these metrics: {', '.join(quality_report.failures)}.\n\n"
            f"Output ONLY a valid JSON array — no markdown, no explanation.\n\n"
            f"FOCUS AREAS:\n"
            f"1. Fix the specific failures listed in Quality Improvement Instructions\n"
            f"2. Turn count between {seed.pasos_turnos.turnos_min} and {seed.pasos_turnos.turnos_max}\n"
            f"3. Every 'rol' is one of: {valid_roles} (alternating strictly)\n"
            f"4. All flow stages covered, domain vocabulary present, no PII"
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
