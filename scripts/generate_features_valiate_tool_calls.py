#!/usr/bin/env python3
"""
Validates tool calling correctness in the merged training dataset.
Checks: tool names, argument validity, required args, type correctness,
        tool_call→tool_response sequence, string prices in numeric fields.
"""

import json
import re
import sys
from collections import defaultdict, Counter

DATASET_PATH = "/Users/marianomorales/Downloads/fine-tuning/inference/datasets/merged_v10_together_train.jsonl"

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOL_DEFS = {
    "buscar_vehiculos": {
        "valid_args": {
            "marca", "modelo", "año_minimo", "año_maximo",
            "precio_minimo", "precio_maximo", "tipo_carroceria",
            "transmision", "combustible", "kilometraje_max",
            "ubicacion", "garantia", "motor", "limite"
        },
        "required": set(),
        "numeric_fields": {
            "año_minimo", "año_maximo", "precio_minimo", "precio_maximo",
            "kilometraje_max", "limite"
        },
    },
    "obtener_vehiculo": {
        "valid_args": {"id", "slug"},
        "required": set(),  # either id or slug
        "numeric_fields": {"id"},
    },
    "buscar_alternativas": {
        "valid_args": {
            "marca_original", "modelo_original", "presupuesto",
            "tipo_uso", "carroceria", "ubicacion"
        },
        "required": {"marca_original", "presupuesto"},
        "numeric_fields": {"presupuesto"},
    },
    "comparar_vehiculos": {
        "valid_args": {"vehiculo_ids"},
        "required": {"vehiculo_ids"},
        "numeric_fields": set(),
        "special": "vehiculo_ids_array",
    },
    "estadisticas_inventario": {
        "valid_args": set(),
        "required": set(),
        "numeric_fields": set(),
        "special": "empty_args",
    },
    "calcular_financiamiento": {
        "valid_args": {
            "precio_vehiculo", "enganche_porcentaje", "plazo_meses",
            "tasa_anual", "vehiculo_id"
        },
        "required": set(),
        "numeric_fields": {
            "precio_vehiculo", "enganche_porcentaje", "plazo_meses",
            "tasa_anual", "vehiculo_id"
        },
    },
    "buscar_informacion": {
        "valid_args": {"pregunta", "categoria"},
        "required": {"pregunta"},
        "numeric_fields": set(),
    },
    "obtener_info_negocio": {
        "valid_args": {"tema"},
        "required": {"tema"},
        "numeric_fields": set(),
    },
    "obtener_faqs": {
        "valid_args": {"categoria"},
        "required": set(),
        "numeric_fields": set(),
    },
    "solicitar_datos_contacto": {
        "valid_args": {
            "nombre", "email", "telefono", "vehiculo_interes", "comentarios"
        },
        "required": {"nombre", "telefono"},
        "numeric_fields": set(),
    },
    "enviar_cotizacion_email": {
        "valid_args": {
            "email_destino", "nombre_cliente", "vehiculo_id",
            "enganche_porcentaje", "plazo_meses"
        },
        "required": {"email_destino", "nombre_cliente", "vehiculo_id"},
        "numeric_fields": {"vehiculo_id", "enganche_porcentaje", "plazo_meses"},
    },
}

VALID_TOOL_NAMES = set(TOOL_DEFS.keys())

# All numeric fields across all tools (for string-price detection)
ALL_NUMERIC_FIELDS = set()
for td in TOOL_DEFS.values():
    ALL_NUMERIC_FIELDS |= td["numeric_fields"]

# Pattern for string prices like "$243,434" or "243,434" or "$300000"
STRING_PRICE_RE = re.compile(r'^\$?[\d,]+\.?\d*$')


# ── Balanced-brace JSON extraction ────────────────────────────────────────────
def extract_tool_calls(content: str) -> list[tuple[str, dict | None, str]]:
    """
    Extract tool_call blocks from assistant message content.
    Returns list of (raw_json_str, parsed_dict_or_None, parse_error_or_empty).
    Uses balanced brace matching for robustness.
    """
    results = []
    tag_open = "<tool_call>"
    tag_close = "</tool_call>"
    idx = 0
    while True:
        start = content.find(tag_open, idx)
        if start == -1:
            break
        end = content.find(tag_close, start)
        if end == -1:
            # Unclosed tool_call tag — take rest of content
            inner = content[start + len(tag_open):]
        else:
            inner = content[start + len(tag_open):end]
        inner = inner.strip()

        # Balanced-brace extraction: find the outermost { ... }
        parsed = None
        parse_error = ""
        brace_start = inner.find("{")
        if brace_start == -1:
            parse_error = "No JSON object found inside <tool_call>"
        else:
            depth = 0
            brace_end = -1
            in_string = False
            escape = False
            for i in range(brace_start, len(inner)):
                c = inner[i]
                if escape:
                    escape = False
                    continue
                if c == '\\' and in_string:
                    escape = True
                    continue
                if c == '"' and not escape:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        brace_end = i
                        break
            if brace_end == -1:
                parse_error = "Unbalanced braces in tool_call JSON"
            else:
                json_str = inner[brace_start:brace_end + 1]
                try:
                    parsed = json.loads(json_str)
                except json.JSONDecodeError as e:
                    parse_error = f"JSON parse error: {e}"

        results.append((inner, parsed, parse_error))
        idx = end + len(tag_close) if end != -1 else len(content)
    return results


# ── Validation ────────────────────────────────────────────────────────────────
def validate_tool_call(parsed: dict, conv_idx: int) -> list[dict]:
    """Validate a single parsed tool_call dict. Returns list of error dicts."""
    errors = []
    tool_name = parsed.get("name", "<missing>")
    arguments = parsed.get("arguments", {})

    # (a) Tool name valid?
    if tool_name not in VALID_TOOL_NAMES:
        errors.append({
            "type": "invalid_tool_name",
            "conv": conv_idx,
            "tool": tool_name,
            "detail": f"Tool '{tool_name}' is not in the valid tool list",
        })
        return errors  # Can't validate args if tool name unknown

    tdef = TOOL_DEFS[tool_name]

    # (b) Unknown argument keys?
    if not isinstance(arguments, dict):
        errors.append({
            "type": "arguments_not_dict",
            "conv": conv_idx,
            "tool": tool_name,
            "detail": f"arguments is {type(arguments).__name__}, expected dict",
        })
        return errors

    unknown_keys = set(arguments.keys()) - tdef["valid_args"]
    for k in sorted(unknown_keys):
        errors.append({
            "type": "unknown_argument",
            "conv": conv_idx,
            "tool": tool_name,
            "detail": f"Unknown argument '{k}' (value: {arguments[k]!r})",
        })

    # (c) Missing required args?
    for req in sorted(tdef["required"]):
        if req not in arguments:
            errors.append({
                "type": "missing_required_arg",
                "conv": conv_idx,
                "tool": tool_name,
                "detail": f"Missing required argument '{req}'",
            })

    # (d) Numeric fields: must be int/float, not string
    for nf in sorted(tdef["numeric_fields"]):
        if nf in arguments:
            val = arguments[nf]
            if isinstance(val, str):
                errors.append({
                    "type": "numeric_field_is_string",
                    "conv": conv_idx,
                    "tool": tool_name,
                    "detail": f"'{nf}' should be numeric but is string: {val!r}",
                })
            elif isinstance(val, bool):
                errors.append({
                    "type": "numeric_field_is_bool",
                    "conv": conv_idx,
                    "tool": tool_name,
                    "detail": f"'{nf}' should be numeric but is bool: {val!r}",
                })
            elif not isinstance(val, (int, float)):
                errors.append({
                    "type": "numeric_field_wrong_type",
                    "conv": conv_idx,
                    "tool": tool_name,
                    "detail": f"'{nf}' should be numeric but is {type(val).__name__}: {val!r}",
                })

    # (d-extra) String prices like "$243,434" in numeric fields
    for nf in sorted(tdef["numeric_fields"]):
        if nf in arguments:
            val = arguments[nf]
            if isinstance(val, str) and STRING_PRICE_RE.match(val.strip()):
                errors.append({
                    "type": "string_price_in_numeric",
                    "conv": conv_idx,
                    "tool": tool_name,
                    "detail": f"'{nf}' contains string price: {val!r}",
                })

    # (e) comparar_vehiculos: vehiculo_ids must be array of numbers
    if tool_name == "comparar_vehiculos" and "vehiculo_ids" in arguments:
        vids = arguments["vehiculo_ids"]
        if not isinstance(vids, list):
            errors.append({
                "type": "vehiculo_ids_not_array",
                "conv": conv_idx,
                "tool": tool_name,
                "detail": f"vehiculo_ids should be array but is {type(vids).__name__}: {vids!r}",
            })
        else:
            if len(vids) < 2 or len(vids) > 4:
                errors.append({
                    "type": "vehiculo_ids_wrong_count",
                    "conv": conv_idx,
                    "tool": tool_name,
                    "detail": f"vehiculo_ids should have 2-4 items but has {len(vids)}",
                })
            for i_v, v in enumerate(vids):
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    errors.append({
                        "type": "vehiculo_ids_non_numeric",
                        "conv": conv_idx,
                        "tool": tool_name,
                        "detail": f"vehiculo_ids[{i_v}] is {type(v).__name__}: {v!r}",
                    })

    # (f) estadisticas_inventario: must have empty arguments
    if tool_name == "estadisticas_inventario" and arguments:
        errors.append({
            "type": "estadisticas_non_empty_args",
            "conv": conv_idx,
            "tool": tool_name,
            "detail": f"estadisticas_inventario should have empty args but got: {arguments}",
        })

    return errors


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    with open(DATASET_PATH) as f:
        lines = f.readlines()

    total_convs = len(lines)
    total_tool_calls = 0
    tool_name_counts = Counter()
    all_errors = []
    convs_with_errors = set()

    # Per-conversation tracking for sequence check
    for conv_idx, line in enumerate(lines):
        conv = json.loads(line)
        messages = conv["messages"]

        # Collect all tool_calls per assistant message and check sequence
        for msg_idx, msg in enumerate(messages):
            role = msg.get("role", "")
            content = msg.get("content", "") or ""

            if role == "assistant" and "<tool_call>" in content:
                tool_calls = extract_tool_calls(content)
                for raw, parsed, parse_error in tool_calls:
                    total_tool_calls += 1

                    if parse_error:
                        all_errors.append({
                            "type": "json_parse_error",
                            "conv": conv_idx,
                            "tool": "<unparseable>",
                            "detail": parse_error,
                        })
                        convs_with_errors.add(conv_idx)
                        continue

                    if parsed is None:
                        continue

                    tool_name = parsed.get("name", "<missing>")
                    tool_name_counts[tool_name] += 1

                    # Validate the tool call
                    errs = validate_tool_call(parsed, conv_idx)
                    all_errors.extend(errs)
                    if errs:
                        convs_with_errors.add(conv_idx)

                # Sequence check: after an assistant message with tool_call(s),
                # the NEXT message(s) should be role="tool"
                num_calls = len(tool_calls)
                for tc_offset in range(num_calls):
                    next_idx = msg_idx + 1 + tc_offset
                    if next_idx >= len(messages):
                        all_errors.append({
                            "type": "missing_tool_response",
                            "conv": conv_idx,
                            "tool": f"call #{tc_offset + 1}",
                            "detail": f"No message at index {next_idx} after tool_call (conversation ends prematurely)",
                        })
                        convs_with_errors.add(conv_idx)
                    elif messages[next_idx].get("role") != "tool":
                        # Check if at least the immediate next message is tool
                        if tc_offset == 0:
                            next_role = messages[next_idx].get("role", "?")
                            all_errors.append({
                                "type": "missing_tool_response",
                                "conv": conv_idx,
                                "tool": f"call #{tc_offset + 1}",
                                "detail": f"Expected role='tool' at msg index {next_idx}, got role='{next_role}'",
                            })
                            convs_with_errors.add(conv_idx)

    # ── Report ────────────────────────────────────────────────────────────────
    error_type_counts = Counter(e["type"] for e in all_errors)
    total_errors = len(all_errors)
    total_calls_with_no_parse_error = total_tool_calls - error_type_counts.get("json_parse_error", 0)
    validation_errors = total_errors - error_type_counts.get("json_parse_error", 0)

    print("=" * 80)
    print("  TOOL CALL VALIDATION REPORT")
    print("=" * 80)

    print(f"\nDataset: {DATASET_PATH}")
    print(f"Total conversations: {total_convs}")
    print(f"Total tool calls extracted: {total_tool_calls}")

    print(f"\n--- Tool Call Breakdown by Name ---")
    for name, count in tool_name_counts.most_common():
        print(f"  {name:30s} : {count:5d}")
    print(f"  {'TOTAL':30s} : {sum(tool_name_counts.values()):5d}")

    print(f"\n--- Error Summary ---")
    print(f"Total errors found: {total_errors}")
    print(f"Conversations with errors: {len(convs_with_errors)} / {total_convs} ({len(convs_with_errors)/total_convs*100:.2f}%)")

    calls_without_errors = total_tool_calls - len([e for e in all_errors if e["type"] not in ("missing_tool_response",)])
    # More precise: count tool calls that produced at least one error
    error_convs_by_call = set()
    for e in all_errors:
        error_convs_by_call.add((e["conv"], e.get("tool", "")))
    tool_calls_with_errors = len([e for e in all_errors if e["type"] != "missing_tool_response"])

    pass_rate_calls = (total_tool_calls - tool_calls_with_errors) / total_tool_calls * 100 if total_tool_calls else 0
    pass_rate_convs = (total_convs - len(convs_with_errors)) / total_convs * 100

    print(f"\nPass rate (tool calls): {total_tool_calls - tool_calls_with_errors} / {total_tool_calls} ({pass_rate_calls:.2f}%)")
    print(f"Pass rate (conversations): {total_convs - len(convs_with_errors)} / {total_convs} ({pass_rate_convs:.2f}%)")

    print(f"\n--- Error Breakdown by Type ---")
    for etype, count in error_type_counts.most_common():
        print(f"  {etype:35s} : {count:5d}")

    # Examples per error type
    print(f"\n--- Examples per Error Type (up to 5 each) ---")
    errors_by_type = defaultdict(list)
    for e in all_errors:
        errors_by_type[e["type"]].append(e)

    for etype in sorted(errors_by_type.keys()):
        examples = errors_by_type[etype][:5]
        print(f"\n  [{etype}] ({len(errors_by_type[etype])} total)")
        for ex in examples:
            print(f"    Conv #{ex['conv']}, tool='{ex['tool']}': {ex['detail']}")

    # List ALL conversations with errors
    print(f"\n--- ALL Conversations with Errors ({len(convs_with_errors)}) ---")
    sorted_error_convs = sorted(convs_with_errors)
    for ci in sorted_error_convs:
        conv_errors = [e for e in all_errors if e["conv"] == ci]
        error_types = set(e["type"] for e in conv_errors)
        tools_involved = set(e["tool"] for e in conv_errors)
        print(f"  Conv #{ci}: {len(conv_errors)} error(s) | types: {sorted(error_types)} | tools: {sorted(tools_involved)}")

    print("\n" + "=" * 80)
    print("  END OF REPORT")
    print("=" * 80)


if __name__ == "__main__":
    main()

