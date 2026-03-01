#!/usr/bin/env python3
"""
JSONL Training Data Validator for Qwen3-14B / TREFA MCP Tool-Call Format
=========================================================================

Usage:
    python3 validate_jsonl.py <file.jsonl>              # validate & report
    python3 validate_jsonl.py <file.jsonl> --keep       # write valid/rejected files
    python3 validate_jsonl.py <file.jsonl> --report-only # summary only, no per-line output
    python3 validate_jsonl.py <file.jsonl> --warnings   # also show warning-only lines

Severity philosophy:
    INVALID (hard error) — anything that would cause the model to LEARN wrong
    behavior: wrong tool arg names/types, wrong role structure, unknown tools,
    missing required args, wrong enum values, string prices in tool responses
    (teaches the model to expect wrong data types from the API), fake/placeholder
    URLs in assistant text (teaches hallucinated links).

    WARNING (low impact) — issues unlikely to degrade tool-call quality:
    off-domain URLs in assistant prose (cosmetic, doesn't affect tool behavior).
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# MCP SCHEMA: valid tool names and their accepted argument keys
# ─────────────────────────────────────────────────────────────────────────────
VALID_TOOLS: dict[str, set[str]] = {
    "buscar_vehiculos": {
        "marca", "modelo", "año_minimo", "año_maximo",
        "precio_minimo", "precio_maximo", "tipo_carroceria",
        "transmision", "combustible", "ubicacion",
        "kilometraje_max", "garantia", "motor", "limite",
    },
    "obtener_vehiculo": {"id", "slug"},
    "buscar_alternativas": {
        "marca_original", "presupuesto", "modelo_original",
        "tipo_uso", "carroceria", "ubicacion",
    },
    "comparar_vehiculos": {"vehiculo_ids"},
    "estadisticas_inventario": set(),
    "calcular_financiamiento": {
        "precio_vehiculo", "vehiculo_id",
        "enganche_porcentaje", "plazo_meses", "tasa_anual",
    },
    "buscar_informacion": {"pregunta", "categoria"},
    "obtener_info_negocio": {"tema"},
    "obtener_faqs": {"categoria"},
    "solicitar_datos_contacto": {
        "nombre", "telefono", "email",
        "vehiculo_interes", "comentarios",
    },
    "enviar_cotizacion_email": {
        "email_destino", "nombre_cliente", "vehiculo_id",
        "enganche_porcentaje", "plazo_meses",
    },
}

REQUIRED_ARGS: dict[str, set[str]] = {
    "buscar_alternativas":      {"marca_original", "presupuesto"},
    "comparar_vehiculos":       {"vehiculo_ids"},
    "buscar_informacion":       {"pregunta"},
    "obtener_info_negocio":     {"tema"},
    "solicitar_datos_contacto": {"nombre", "telefono"},
    "enviar_cotizacion_email":  {"email_destino", "nombre_cliente", "vehiculo_id"},
}

# obtener_info_negocio: tema must be one of these
VALID_TEMA_VALUES = {
    "horarios", "ubicaciones", "contacto", "garantias",
    "financiamiento", "documentos_requeridos", "proceso_compra",
    "devoluciones", "intercambio", "servicios",
}

# buscar_informacion: categoria must be one of these (or absent)
VALID_CATEGORIA_VALUES = {
    "faq", "politicas", "procesos", "financiamiento",
    "garantias", "general",
}

# Allowed URL domains in assistant responses and tool responses
ALLOWED_DOMAINS = {"autostrefa.mx", "trefa.mx", "maps.app.goo.gl"}

# Domains that indicate a FAKE / placeholder response
FAKE_DOMAINS = {"ejemplo.com", "example.com", "tu_dominio.com", "placeholder"}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
_TOOL_CALL_RE  = re.compile(r"<tool_call>(.*?)</tool_call>",  re.DOTALL)
_TOOL_RESP_RE  = re.compile(r"<tool_response>(.*?)</tool_response>", re.DOTALL)
_URL_RE        = re.compile(r"https?://([^/\s\"\)\\]+)")

# Vehicle URL path pattern:  /autos/<slug>  (not /inventario/)
_VEH_URL_RE    = re.compile(r"autostrefa\.mx/autos/[\w\-]+")


def extract_tool_calls(text: str) -> list[dict]:
    """Parse all <tool_call> ... </tool_call> blocks in a string."""
    results = []
    for m in _TOOL_CALL_RE.finditer(text):
        try:
            results.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError as e:
            results.append({"_parse_error": str(e), "_raw": m.group(1)[:200]})
    return results


def extract_tool_responses(text: str) -> list[Any]:
    """Parse all <tool_response> ... </tool_response> blocks."""
    results = []
    for m in _TOOL_RESP_RE.finditer(text):
        try:
            results.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError:
            results.append(None)
    return results


def check_url(url_domain: str) -> str | None:
    """Return 'fake' | 'suspicious' | None."""
    for fd in FAKE_DOMAINS:
        if fd in url_domain:
            return "fake"
    # flag completely off-domain URLs inside assistant messages
    if (url_domain not in ALLOWED_DOMAINS and
            not any(url_domain.endswith("." + d) for d in ALLOWED_DOMAINS)):
        return "suspicious"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Core validator
# ─────────────────────────────────────────────────────────────────────────────
class ConversationError:
    def __init__(self, code: str, detail: str, is_warning: bool = False):
        self.code       = code
        self.detail     = detail
        self.is_warning = is_warning  # warnings don't make a line invalid by default

    def __str__(self):
        prefix = "WARN" if self.is_warning else self.code
        return f"[{prefix}] {self.detail}"


def validate_conversation(messages: list[dict]) -> list[ConversationError]:
    """Validate a single conversation's message list. Returns a list of errors.

    INVALID (hard error): wrong tool args, wrong roles, unknown tools, missing
    required args, wrong enums, string prices in tool responses, fake URLs.

    WARNING: off-domain URLs in assistant prose (low fine-tuning impact).
    """
    errors: list[ConversationError] = []

    # ── Structural checks ─────────────────────────────────────────────────────
    if not messages:
        errors.append(ConversationError("EMPTY", "messages list is empty"))
        return errors

    roles = [m.get("role") for m in messages]

    # Must have a system message (either real content or __SYSTEM_PROMPT__ placeholder)
    if "system" not in roles:
        errors.append(ConversationError("NO_SYSTEM", "missing system message"))
    else:
        system_content = next(
            m.get("content", "") for m in messages if m.get("role") == "system"
        )
        if not system_content.strip():
            errors.append(ConversationError("EMPTY_SYSTEM", "system message is empty"))

    # Must have at least one user turn
    if "user" not in roles:
        errors.append(ConversationError("NO_USER", "no user message found"))

    # Must have at least one assistant turn
    if "assistant" not in roles:
        errors.append(ConversationError("NO_ASSISTANT", "no assistant message found"))

    # ── Role-sequence checks ──────────────────────────────────────────────────
    tool_call_open = False
    prev_role = None
    for idx, m in enumerate(messages):
        role    = m.get("role", "")
        content = m.get("content", "")

        # Detect tool-call embedded as string inside user message (wrong pattern)
        if role == "user" and isinstance(content, str) and "<tool_response>" in content:
            errors.append(ConversationError(
                "WRONG_TOOL_ROLE",
                f"msg[{idx}] tool_response embedded in 'user' role; should be role='tool'"
            ))

        # Detect tool-call embedded directly inside user message (wrong pattern)
        if role == "user" and isinstance(content, str) and "<tool_call>" in content:
            errors.append(ConversationError(
                "WRONG_TOOL_ROLE",
                f"msg[{idx}] <tool_call> inside 'user' role; should be role='assistant'"
            ))

        # tool role must follow an assistant message that contains <tool_call>
        if role == "tool":
            if prev_role not in ("assistant",):
                errors.append(ConversationError(
                    "ORPHAN_TOOL",
                    f"msg[{idx}] role='tool' not preceded by an assistant turn"
                ))

        prev_role = role

    # ── Tool call validation ──────────────────────────────────────────────────
    for idx, m in enumerate(messages):
        role    = m.get("role", "")
        content = m.get("content", "")
        if not isinstance(content, str):
            continue

        # Parse tool calls from assistant messages
        if role == "assistant":
            tcs = extract_tool_calls(content)
            for tc in tcs:
                if "_parse_error" in tc:
                    errors.append(ConversationError(
                        "TOOL_PARSE_ERR",
                        f"msg[{idx}] JSON parse error in <tool_call>: {tc['_parse_error']}"
                    ))
                    continue

                name = tc.get("name", "")
                args = tc.get("arguments", {})

                # Unknown tool
                if name not in VALID_TOOLS:
                    errors.append(ConversationError(
                        "UNKNOWN_TOOL",
                        f"msg[{idx}] unknown tool '{name}'"
                    ))
                    continue

                allowed = VALID_TOOLS[name]
                given   = set(args.keys())

                # Check for unrecognized argument names
                unknown_args = given - allowed
                if unknown_args:
                    errors.append(ConversationError(
                        "INVALID_ARG",
                        f"msg[{idx}] tool '{name}' has invalid args: {unknown_args}"
                    ))

                # Check required arguments are present
                required = REQUIRED_ARGS.get(name, set())
                missing  = required - given
                if missing:
                    errors.append(ConversationError(
                        "MISSING_ARG",
                        f"msg[{idx}] tool '{name}' missing required args: {missing}"
                    ))

                # Enum validation
                if name == "obtener_info_negocio" and "tema" in args:
                    if args["tema"] not in VALID_TEMA_VALUES:
                        errors.append(ConversationError(
                            "INVALID_ENUM",
                            f"msg[{idx}] obtener_info_negocio.tema='{args['tema']}' "
                            f"not in {VALID_TEMA_VALUES}"
                        ))

                if name == "buscar_informacion" and "categoria" in args:
                    if args["categoria"] not in VALID_CATEGORIA_VALUES:
                        errors.append(ConversationError(
                            "INVALID_ENUM",
                            f"msg[{idx}] buscar_informacion.categoria='{args['categoria']}' "
                            f"not in {VALID_CATEGORIA_VALUES}"
                        ))

                # comparar_vehiculos: vehiculo_ids must be a list of 2-4 numbers
                if name == "comparar_vehiculos" and "vehiculo_ids" in args:
                    ids = args["vehiculo_ids"]
                    if not isinstance(ids, list):
                        errors.append(ConversationError(
                            "TYPE_ERR",
                            f"msg[{idx}] comparar_vehiculos.vehiculo_ids must be an array"
                        ))
                    elif not (2 <= len(ids) <= 4):
                        errors.append(ConversationError(
                            "RANGE_ERR",
                            f"msg[{idx}] comparar_vehiculos.vehiculo_ids must have 2-4 items, got {len(ids)}"
                        ))

                # obtener_vehiculo: id must be numeric
                if name == "obtener_vehiculo":
                    if "id" in args and not isinstance(args["id"], (int, float)):
                        errors.append(ConversationError(
                            "TYPE_ERR",
                            f"msg[{idx}] obtener_vehiculo.id must be a number, got {type(args['id']).__name__}"
                        ))

                # precio values in TOOL CALL args must be numbers, not strings
                for price_field in ("precio_vehiculo", "precio_minimo", "precio_maximo", "presupuesto"):
                    if price_field in args and isinstance(args[price_field], str):
                        errors.append(ConversationError(
                            "TYPE_ERR",
                            f"msg[{idx}] '{price_field}' must be a number, got string: '{args[price_field]}'",
                            is_warning=False,  # always hard error: LLM generated the wrong type
                        ))

        # ── URL checks in assistant messages ──────────────────────────────────
        if role == "assistant":
            for domain in _URL_RE.findall(content):
                verdict = check_url(domain)
                if verdict == "fake":
                    # Hard error: model learns fabricated URLs → hallucinations
                    errors.append(ConversationError(
                        "FAKE_URL",
                        f"msg[{idx}] contains fake/placeholder URL domain: {domain}"
                    ))
                elif verdict == "suspicious":
                    # Warning: off-domain URL in prose (low fine-tuning impact)
                    errors.append(ConversationError(
                        "SUSPICIOUS_URL",
                        f"msg[{idx}] off-domain URL: {domain}",
                        is_warning=True,
                    ))

            # Vehicle URLs should follow /autos/<slug> pattern, NOT /inventario/
            if "autostrefa.mx/inventario/" in content:
                errors.append(ConversationError(
                    "WRONG_URL_PATH",
                    f"msg[{idx}] URL uses /inventario/ — should be /autos/<slug>"
                ))

        # ── Tool response validation (role=tool or embedded <tool_response>) ──
        if role in ("tool", "user"):
            responses = extract_tool_responses(content)
            for resp in responses:
                if resp is None:
                    errors.append(ConversationError(
                        "TOOL_RESP_PARSE",
                        f"msg[{idx}] could not parse <tool_response> JSON"
                    ))
                    continue
                # Check vehicle records inside responses for fake URLs
                vehicles = []
                if isinstance(resp, dict):
                    vehicles = resp.get("vehiculos", []) + resp.get("alternativas", [])
                    if "liga_web" in resp:
                        vehicles.append(resp)
                for veh in vehicles:
                    if isinstance(veh, dict):
                        liga = veh.get("liga_web", "")
                        if liga:
                            # Must point to autostrefa.mx/autos/<slug>
                            if not _VEH_URL_RE.search(liga):
                                errors.append(ConversationError(
                                    "WRONG_VEH_URL",
                                    f"msg[{idx}] vehicle liga_web='{liga}' "
                                    f"should match autostrefa.mx/autos/<slug>"
                                ))
                        # precio must be numeric — string format teaches the model
                        # wrong data types from tool responses (hard error)
                        precio = veh.get("precio")
                        if isinstance(precio, str):
                            errors.append(ConversationError(
                                "STRING_PRICE",
                                f"msg[{idx}] vehicle.precio is a string ('{precio}') — "
                                f"must be a number; teaches model wrong data types",
                            ))

    # ── Hallucination / bare-invention checks ─────────────────────────────────
    for idx, m in enumerate(messages):
        role    = m.get("role", "")
        content = m.get("content", "")
        if role != "assistant" or not isinstance(content, str):
            continue
        # Flag fabricated vehicle links that are NOT backed by a tool response
        # (heuristic: URL present but no <tool_call> or <tool_response> anywhere in convo)
        has_any_tool_call = any(
            "<tool_call>" in (x.get("content") or "")
            for x in messages
        )
        has_veh_url = bool(_VEH_URL_RE.search(content))
        if has_veh_url and not has_any_tool_call:
            errors.append(ConversationError(
                "HALLUCINATED_URL",
                f"msg[{idx}] contains vehicle URL but conversation has no tool calls — "
                f"possible hallucination"
            ))

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# File-level runner
# ─────────────────────────────────────────────────────────────────────────────
def validate_file(
    path: Path,
    keep: bool = False,
    report_only: bool = False,
    verbose: bool = True,
    show_warnings: bool = False,
) -> dict:
    """
    Validates every line in a JSONL file.

    Returns a summary dict:
        total, valid, invalid, warning_only, error_counts (dict), error_lines (list)
    """
    total = valid = invalid = warning_only = 0
    error_counts:   dict[str, int] = {}
    warning_counts: dict[str, int] = {}
    error_lines:    list[dict]     = []

    valid_lines:    list[str] = []
    rejected_lines: list[str] = []

    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue

            total += 1

            # Parse JSON
            try:
                sample = json.loads(raw)
            except json.JSONDecodeError as e:
                err = ConversationError("JSON_PARSE", str(e))
                invalid += 1
                error_counts["JSON_PARSE"] = error_counts.get("JSON_PARSE", 0) + 1
                error_lines.append({"line": lineno, "errors": [str(err)]})
                if verbose:
                    print(f"  ✗ line {lineno:5d}: JSON_PARSE — {e}")
                if keep:
                    rejected_lines.append(raw)
                continue

            messages = sample.get("messages")
            if not isinstance(messages, list):
                err = ConversationError("SCHEMA", "'messages' key missing or not a list")
                invalid += 1
                error_counts["SCHEMA"] = error_counts.get("SCHEMA", 0) + 1
                error_lines.append({"line": lineno, "errors": [str(err)]})
                if verbose:
                    print(f"  ✗ line {lineno:5d}: SCHEMA — {err.detail}")
                if keep:
                    rejected_lines.append(raw)
                continue

            all_issues = validate_conversation(messages)
            hard_errors = [e for e in all_issues if not e.is_warning]
            warnings    = [e for e in all_issues if e.is_warning]

            if hard_errors:
                invalid += 1
                codes = [e.code for e in hard_errors]
                for code in codes:
                    error_counts[code] = error_counts.get(code, 0) + 1
                for w in warnings:
                    warning_counts[w.code] = warning_counts.get(w.code, 0) + 1
                error_lines.append({"line": lineno, "errors": [str(e) for e in hard_errors]})
                if verbose:
                    print(f"  ✗ line {lineno:5d}: " + " | ".join(str(e) for e in hard_errors[:3]))
                    if len(hard_errors) > 3:
                        print(f"         ... +{len(hard_errors)-3} more errors")
                if keep:
                    rejected_lines.append(raw)
            elif warnings:
                warning_only += 1
                valid += 1  # still valid — warnings are not disqualifying
                for w in warnings:
                    warning_counts[w.code] = warning_counts.get(w.code, 0) + 1
                if show_warnings and verbose:
                    print(f"  ⚠ line {lineno:5d}: " + " | ".join(str(w) for w in warnings[:3]))
                if keep:
                    valid_lines.append(raw)
            else:
                valid += 1
                if keep:
                    valid_lines.append(raw)

    # Write output files
    if keep and not report_only:
        valid_path    = path.with_stem(path.stem + "_valid")
        rejected_path = path.with_stem(path.stem + "_rejected")
        with open(valid_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(valid_lines) + "\n")
        with open(rejected_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(rejected_lines) + "\n")
        print(f"\n  → Saved {len(valid_lines)} valid lines  to: {valid_path}")
        print(f"  → Saved {len(rejected_lines)} rejected lines to: {rejected_path}")

    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "warning_only": warning_only,
        "error_counts": error_counts,
        "warning_counts": warning_counts,
        "error_lines": error_lines,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Print banner & report
# ─────────────────────────────────────────────────────────────────────────────
def print_report(path: Path, stats: dict):
    total        = stats["total"]
    valid        = stats["valid"]
    invalid      = stats["invalid"]
    warning_only = stats.get("warning_only", 0)
    clean_valid  = valid - warning_only
    pct          = (valid / total * 100) if total else 0.0

    print()
    print("=" * 64)
    print(f"  FILE         : {path.name}")
    print(f"  TOTAL        : {total:,}  lines")
    print(f"  VALID        : {valid:,}  ({pct:.1f}%)")
    print(f"    → clean    : {clean_valid:,}  (no warnings)")
    print(f"    → warnings : {warning_only:,}  (valid but has fixable issues)")
    print(f"  INVALID      : {invalid:,}")
    print("=" * 64)

    if stats["error_counts"]:
        print()
        print("  Hard-error breakdown (lines rejected):")
        for code, cnt in sorted(stats["error_counts"].items(), key=lambda x: -x[1]):
            print(f"    {code:<22} {cnt:>5}")

    if stats.get("warning_counts"):
        print()
        print("  Warning breakdown (valid but fixable):")
        for code, cnt in sorted(stats["warning_counts"].items(), key=lambda x: -x[1]):
            print(f"    {code:<22} {cnt:>5}")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Validate TREFA MCP tool-call training JSONL files for Qwen3-14B"
    )
    parser.add_argument("file", help="Path to the JSONL file to validate")
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Write <file>_valid.jsonl and <file>_rejected.jsonl",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only print the summary, suppress per-line output",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-line verbose output",
    )
    parser.add_argument(
        "--warnings",
        action="store_true",
        help="Also print lines that pass but have warnings (e.g. suspicious off-domain URLs)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    verbose = not (args.report_only or args.quiet)

    print(f"\nValidating: {path}")
    print("─" * 64)

    if verbose:
        print("  Per-line results (✗ = invalid, ⚠ = warning):")
        print()

    stats = validate_file(
        path,
        keep=args.keep and not args.report_only,
        report_only=args.report_only,
        verbose=verbose,
        show_warnings=args.warnings,
    )

    print_report(path, stats)


if __name__ == "__main__":
    main()

