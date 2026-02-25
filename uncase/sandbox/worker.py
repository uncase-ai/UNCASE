"""Self-contained worker script that runs INSIDE each E2B sandbox.

This file is uploaded to the sandbox filesystem and executed as a standalone
Python script. It MUST NOT import from uncase.* — all required logic is
inlined here to keep the sandbox minimal.

The worker receives a JSON payload via stdin containing:
  - seed: SeedSchema dict
  - count: number of conversations to generate
  - model: LLM model string
  - temperature: float
  - api_key: LLM API key
  - api_base: optional API base URL
  - language_override: optional language override
  - evaluate_after: whether to run quality evaluation

It writes a JSON result to stdout containing:
  - conversations: list of generated conversations
  - reports: optional list of quality reports
  - error: optional error message
"""

from __future__ import annotations

import contextlib
import json
import re
import sys
import time
import uuid
from datetime import UTC, datetime
from typing import Any


def build_system_prompt(seed: dict[str, Any], language: str | None = None) -> str:
    """Build LLM system prompt from seed dict."""
    lang = language or seed.get("idioma", "es")
    dominio = seed.get("dominio", "")

    domain_contexts = {
        "automotive.sales": (
            "You are generating a conversation in the automotive sales domain. "
            "This involves vehicle sales interactions between dealership staff and potential buyers."
        ),
        "medical.consultation": (
            "You are generating a conversation in the medical consultation domain. "
            "This involves healthcare interactions between medical professionals and patients."
        ),
        "legal.advisory": (
            "You are generating a conversation in the legal advisory domain. "
            "This involves legal consultations between attorneys/legal advisors and clients."
        ),
        "finance.advisory": (
            "You are generating a conversation in the financial advisory domain. "
            "This involves financial planning interactions between advisors and clients."
        ),
        "industrial.support": (
            "You are generating a conversation in the industrial support domain. "
            "This involves technical support interactions for industrial equipment and processes."
        ),
        "education.tutoring": (
            "You are generating a conversation in the education tutoring domain. "
            "This involves educational interactions between tutors/instructors and students."
        ),
    }

    domain_desc = domain_contexts.get(dominio, f"You are generating a conversation in the {dominio} domain.")

    roles = seed.get("roles", [])
    desc_roles = seed.get("descripcion_roles", {})
    role_lines = [f'  - "{r}": {desc_roles.get(r, "No additional description.")}' for r in roles]
    roles_block = "\n".join(role_lines)

    pasos = seed.get("pasos_turnos", {})
    flow_lines = [f"  {i + 1}. {step}" for i, step in enumerate(pasos.get("flujo_esperado", []))]
    flow_block = "\n".join(flow_lines)

    params = seed.get("parametros_factuales", {})
    constraints = params.get("restricciones", [])
    constraints_block = ""
    if constraints:
        constraint_lines = [f"  - {c}" for c in constraints]
        constraints_block = "\n## Factual Constraints (MUST be respected)\n" + "\n".join(constraint_lines)

    tools = params.get("herramientas", [])
    tools_block = ""
    if tools:
        tool_lines = [f'  - "{t}"' for t in tools]
        tools_block = "\n## Available Tools\n" + "\n".join(tool_lines)

    lang_names = {"es": "Spanish (Latin American)", "en": "English", "pt": "Portuguese (Brazilian)"}
    lang_name = lang_names.get(lang, lang)

    turnos_min = pasos.get("turnos_min", 4)
    turnos_max = pasos.get("turnos_max", 12)

    return f"""You are an expert synthetic conversation generator for the UNCASE (SCSF) framework.

{domain_desc}

## Objective
{seed.get("objetivo", "")}

## Scenario Context
{params.get("contexto", "")}

## Conversation Parameters
- **Language**: {lang_name} — ALL dialogue content MUST be in {lang_name}.
- **Tone**: {seed.get("tono", "profesional")}
- **Number of turns**: Generate between {turnos_min} and {turnos_max} turns.
- **Domain**: {dominio}

## Participant Roles
{roles_block}

## Expected Conversation Flow
{flow_block}
{constraints_block}
{tools_block}

## Output Format
You MUST output ONLY a valid JSON array of turn objects.

Each turn object has:
- "turno": integer, 1-indexed
- "rol": string, one of ({", ".join(f'"{r}"' for r in roles)})
- "contenido": string, dialogue in {lang_name}
- "herramientas_usadas": array of strings

## Quality Requirements
- Substantive turns (1-2+ sentences), contextually relevant.
- Consistent character behavior across all turns.
- Varied vocabulary (avoid repeating phrases).
- Natural and realistic dialogue.
- NEVER include real personal information — use fictional placeholders.
- Respect ALL factual constraints."""


def parse_llm_response(raw_content: str, roles: list[str]) -> list[dict[str, Any]]:
    """Parse LLM response into turn dicts."""
    content = raw_content.strip()
    parsed = None

    with contextlib.suppress(json.JSONDecodeError):
        parsed = json.loads(content)

    if parsed is None:
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", content, re.DOTALL)
        if code_block:
            with contextlib.suppress(json.JSONDecodeError):
                parsed = json.loads(code_block.group(1).strip())

    if parsed is None:
        bracket = re.search(r"\[.*\]", content, re.DOTALL)
        if bracket:
            with contextlib.suppress(json.JSONDecodeError):
                parsed = json.loads(bracket.group(0))

    if parsed is None or not isinstance(parsed, list) or len(parsed) == 0:
        raise ValueError("Failed to parse LLM response as JSON array")

    valid_roles = set(roles)
    turns = []
    for i, td in enumerate(parsed):
        if not isinstance(td, dict):
            continue
        rol = td.get("rol", "")
        contenido = td.get("contenido", "")
        if not contenido or not contenido.strip():
            continue
        if rol not in valid_roles and roles:
            rol = roles[i % len(roles)]
        turns.append(
            {
                "turno": i + 1,
                "rol": rol,
                "contenido": contenido.strip(),
                "herramientas_usadas": td.get("herramientas_usadas", []),
                "metadata": {},
            }
        )

    if not turns:
        raise ValueError("No valid turns parsed from LLM response")
    return turns


def compute_ttr(text: str) -> float:
    """Compute Type-Token Ratio for lexical diversity."""
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def compute_coherence(turns: list[dict[str, Any]]) -> float:
    """Simplified dialog coherence: check role alternation and content continuity."""
    if len(turns) < 2:
        return 1.0
    score = 0.0
    for i in range(1, len(turns)):
        # Role alternation bonus
        if turns[i]["rol"] != turns[i - 1]["rol"]:
            score += 0.5
        # Content length consistency (penalize very short turns)
        avg_len = sum(len(t["contenido"]) for t in turns) / len(turns)
        if len(turns[i]["contenido"]) > avg_len * 0.3:
            score += 0.5
    return min(1.0, score / (len(turns) - 1))


def evaluate_conversation(turns: list[dict[str, Any]], seed: dict[str, Any]) -> dict[str, Any]:
    """Lightweight quality evaluation (subset of the full evaluator)."""
    all_text = " ".join(t["contenido"] for t in turns)

    # Lexical diversity (TTR)
    ttr = compute_ttr(all_text)

    # Dialog coherence
    coherence = compute_coherence(turns)

    # Factual fidelity (simplified: check constraint keywords are present)
    constraints = seed.get("parametros_factuales", {}).get("restricciones", [])
    fidelity = 1.0
    if constraints:
        constraint_text = " ".join(constraints).lower()
        keywords = set(re.findall(r"\w+", constraint_text))
        text_lower = all_text.lower()
        if keywords:
            found = sum(1 for kw in keywords if kw in text_lower)
            fidelity = min(1.0, found / max(len(keywords) * 0.3, 1))

    # ROUGE-L approximation (check flow step coverage)
    flow_steps = seed.get("pasos_turnos", {}).get("flujo_esperado", [])
    rouge_approx = 1.0
    if flow_steps:
        step_keywords = set()
        for step in flow_steps:
            step_keywords.update(re.findall(r"\w+", step.lower()))
        if step_keywords:
            found = sum(1 for kw in step_keywords if kw in all_text.lower())
            rouge_approx = min(1.0, found / max(len(step_keywords) * 0.3, 1))

    # Privacy: simple PII check (phone, email, SSN patterns)
    pii_patterns = [
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    ]
    privacy_score = 0.0
    for pattern in pii_patterns:
        if re.search(pattern, all_text):
            privacy_score = 1.0
            break

    metrics = {
        "rouge_l": round(rouge_approx, 4),
        "fidelidad_factual": round(fidelity, 4),
        "diversidad_lexica": round(ttr, 4),
        "coherencia_dialogica": round(coherence, 4),
        "privacy_score": round(privacy_score, 4),
        "memorizacion": 0.0,
    }

    # Composite score
    if privacy_score > 0.0 or metrics["memorizacion"] >= 0.01:
        composite = 0.0
        passed = False
    else:
        composite = min(
            metrics["rouge_l"],
            metrics["fidelidad_factual"],
            metrics["diversidad_lexica"],
            metrics["coherencia_dialogica"],
        )
        passed = (
            metrics["rouge_l"] >= 0.65
            and metrics["fidelidad_factual"] >= 0.90
            and metrics["diversidad_lexica"] >= 0.55
            and metrics["coherencia_dialogica"] >= 0.85
            and privacy_score == 0.0
        )

    failures = []
    if metrics["rouge_l"] < 0.65:
        failures.append(f"rouge_l={metrics['rouge_l']} (min 0.65)")
    if metrics["fidelidad_factual"] < 0.90:
        failures.append(f"fidelidad_factual={metrics['fidelidad_factual']} (min 0.90)")
    if metrics["diversidad_lexica"] < 0.55:
        failures.append(f"diversidad_lexica={metrics['diversidad_lexica']} (min 0.55)")
    if metrics["coherencia_dialogica"] < 0.85:
        failures.append(f"coherencia_dialogica={metrics['coherencia_dialogica']} (min 0.85)")
    if privacy_score != 0.0:
        failures.append(f"privacy_score={privacy_score} (must be 0.0)")

    return {
        "metrics": metrics,
        "composite_score": round(composite, 4),
        "passed": passed,
        "failures": failures,
    }


async def run_generation(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the generation pipeline inside the sandbox."""
    import litellm

    seed = payload["seed"]
    count = payload.get("count", 1)
    model = payload.get("model", "claude-sonnet-4-20250514")
    temperature = payload.get("temperature", 0.7)
    api_key = payload.get("api_key")
    api_base = payload.get("api_base")
    language = payload.get("language_override") or seed.get("idioma", "es")
    evaluate_after = payload.get("evaluate_after", True)

    system_prompt = build_system_prompt(seed, language=language)
    pasos = seed.get("pasos_turnos", {})
    turnos_min = pasos.get("turnos_min", 4)
    turnos_max = pasos.get("turnos_max", 12)

    user_prompt = (
        f"Generate a complete synthetic conversation following the specification above. "
        f"Output ONLY a valid JSON array of turn objects. "
        f"Generate between {turnos_min} and {turnos_max} turns."
    )

    conversations = []
    reports = []

    for i in range(count):
        temp_variation = (i - count / 2) * 0.05
        adjusted_temp = max(0.0, min(2.0, temperature + temp_variation))

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": adjusted_temp,
            "max_tokens": 4096,
        }
        if api_key:
            kwargs["api_key"] = api_key
        if api_base:
            kwargs["api_base"] = api_base

        # Try with JSON response format first, fallback without it
        last_error = None
        for attempt in range(3):
            try:
                if attempt == 0:
                    kwargs["response_format"] = {"type": "json_object"}
                response = await litellm.acompletion(**kwargs)
                raw = response.choices[0].message.content
                if not raw:
                    raise ValueError("Empty LLM response")
                break
            except Exception as exc:
                last_error = exc
                kwargs.pop("response_format", None)
        else:
            raise RuntimeError(f"LLM call failed after 3 attempts: {last_error}")

        turns = parse_llm_response(raw, seed.get("roles", []))

        conversation = {
            "conversation_id": uuid.uuid4().hex,
            "seed_id": seed.get("seed_id", "unknown"),
            "dominio": seed.get("dominio", ""),
            "idioma": language,
            "turnos": turns,
            "es_sintetica": True,
            "created_at": datetime.now(UTC).isoformat(),
            "metadata": {
                "generator": "litellm-sandbox",
                "model": model,
                "temperature": str(round(adjusted_temp, 3)),
                "generation_index": str(i),
            },
        }
        conversations.append(conversation)

        if evaluate_after:
            report = evaluate_conversation(turns, seed)
            report["conversation_id"] = conversation["conversation_id"]
            report["seed_id"] = seed.get("seed_id", "unknown")
            report["evaluated_at"] = datetime.now(UTC).isoformat()
            reports.append(report)

    return {
        "conversations": conversations,
        "reports": reports if evaluate_after else None,
        "error": None,
    }


async def main() -> None:
    """Entry point: read JSON payload from stdin, run generation, write result to stdout."""
    raw_input = sys.stdin.read()
    payload = json.loads(raw_input)

    start = time.monotonic()
    try:
        result = await run_generation(payload)
        result["duration_seconds"] = round(time.monotonic() - start, 2)
    except Exception as exc:
        result = {
            "conversations": [],
            "reports": None,
            "error": str(exc),
            "duration_seconds": round(time.monotonic() - start, 2),
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
