#!/usr/bin/env python3
"""
filter_bad_patterns.py — Elimina conversaciones con patrones problemáticos
==========================================================================

Detecta y elimina dos tipos de problemas:

P1 - FALLO DE CONTEXTO:
   Mariana tiene IDs de vehículos en un tool_response previo, el usuario
   selecciona uno, y ella NO usa obtenerVehiculo con el ID. En su lugar
   pregunta cuál quiere, inventa datos, o busca de nuevo.

P2 - PREGUNTAS OBVIAS:
   El usuario dice algo claramente identificable ("busco un Versa") y
   Mariana pregunta redundantemente ("¿te refieres a un Nissan Versa?")

Uso:
    python3 filter_bad_patterns.py                  # dry-run (solo reporta)
    python3 filter_bad_patterns.py --apply          # aplica filtros a archivos fuente
    python3 filter_bad_patterns.py --apply --merge  # aplica + regenera merge
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

BASE = "/Users/marianomorales/Downloads/fine-tuning/inference/datasets"

# Archivos fuente a limpiar (los mismos que usa merge_all_v10.py)
SOURCE_FILES = [
    "v10_real_train.jsonl",
    "v10_real_eval.jsonl",
    "v8_train.jsonl",
    "v8_eval.jsonl",
    "trefa_train.jsonl",
    "trefa_eval.jsonl",
    "mariana_training_v1.jsonl",
    "golden_qwen_mariana.jsonl",
    "golden_system_prompts.jsonl",
    "semillas_mariana.jsonl",
    "semillas_obtener_vehiculo.jsonl",
    "semillas_solicitud_financiamiento.jsonl",
    "saludos_mariana.jsonl",
    "estilo_conversacional_mariana.jsonl",
    "etapa1_40_calidad_gold.jsonl",
    "synthetic_cleaned.jsonl",
]

# ─── Patrones de detección ──────────────────────────────────────

# P2: Preguntas obvias/redundantes del asistente
OBVIOUS_Q_PATTERNS = [
    # "¿Te refieres a un Nissan Versa?" cuando el usuario ya dijo Versa
    r"(?:¿|¡)?[Tt]e refieres a(?:l| un[ao]?| la)?\s+(?:Nissan|Toyota|Mazda|Chevrolet|Hyundai|Kia|Volkswagen|Honda|Suzuki|MG|BAIC|Fiat|Dodge|Jeep|RAM|Ford|Renault|Peugeot|Mitsubishi|Subaru|JAC|Changan|SEat|Audi|BMW|Mercedes)",
    # "¿Te refieres al modelo X?" cuando el usuario ya lo dijo
    r"(?:¿|¡)?[Tt]e refieres al?\s+(?:modelo|vehículo|carro|auto|camioneta)",
    # "¿Buscas un [marca/modelo]?" repitiendo lo que el usuario dijo
    r"(?:¿|¡)?[Bb]uscas\s+(?:un[ao]?\s+)?(?:Nissan|Toyota|Mazda|Chevrolet|Hyundai|Kia|Volkswagen|Honda|Suzuki|MG|BAIC|Fiat|Versa|Sentra|Kicks|March|Aveo|CX-|RAV4|Corolla|Camry|Forte|Tucson|Accent|HB20)",
    # "Solo para confirmar, ¿buscas un [lo que acaba de decir]?"
    r"[Ss]olo para (?:confirmar|asegurarme)[,:]?\s*(?:¿|¡)?(?:buscas|quieres|te interesa|necesitas)",
    # "Permíteme confirmar" seguido de repetir lo que dijo el usuario
    r"[Pp]ermíteme confirmar",
    # "Para confirmar, ¿la marca es...?" cuando ya lo dijo
    r"[Pp]ara confirmar[,:]?\s*(?:¿|¡)?(?:la marca|el modelo|buscas|quieres)",
    # "¿Quieres decir [lo que acaba de decir]?"
    r"(?:¿|¡)?[Qq]uieres decir\s+(?:un[ao]?\s+)?(?:Nissan|Toyota|Mazda|Chevrolet|Kia|Honda|Versa|Sentra|Kicks)",
    # "¿Hablas de [lo obvio]?"
    r"(?:¿|¡)?[Hh]ablas de(?:l| un[ao]?)",
    # "¿Es correcto que buscas...?" redundante
    r"(?:¿|¡)?[Ee]s correcto que\s+(?:buscas|quieres|te interesa|necesitas)",
]

# Marcas/modelos conocidos para validar que la pregunta es realmente obvia
KNOWN_BRANDS = {
    "nissan", "toyota", "mazda", "chevrolet", "hyundai", "kia", "volkswagen",
    "honda", "suzuki", "mg", "baic", "fiat", "dodge", "jeep", "ram", "ford",
    "renault", "peugeot", "mitsubishi", "subaru", "jac", "changan", "audi",
    "bmw", "mercedes", "seat",
}

KNOWN_MODELS = {
    "versa", "sentra", "kicks", "march", "np300", "frontier", "xtrail", "x-trail",
    "corolla", "camry", "rav4", "hilux", "yaris", "avanza",
    "cx-3", "cx-30", "cx-5", "cx-50", "cx-90", "mazda2", "mazda3", "mazda6",
    "aveo", "onix", "cavalier", "captiva", "equinox", "trax", "tracker",
    "tucson", "creta", "accent", "venue", "palisade", "santa fe",
    "forte", "rio", "seltos", "sportage", "sorento",
    "jetta", "taos", "tiguan", "tcross", "t-cross", "nivus",
    "civic", "crv", "cr-v", "hrv", "hr-v", "city", "fit",
    "swift", "vitara", "ertiga", "jimny",
    "hb20", "hb20s", "creta",
    "zs", "hs", "gt", "marvel",
    "x55", "x35", "x25",
    "mobi", "pulse", "fastback",
    "neon", "attitude",
}

# Patrones de interés del usuario (selecciona un vehículo del listado)
USER_INTEREST_PATTERNS = [
    r"me (?:gusta|interesa|llama la atención|late|encanta)",
    r"(?:cuéntame|dime|háblame|platícame|info(?:rmación)?)\s*(?:más\s+)?(?:del?|de la|sobre|acerca)",
    r"(?:el|la)\s+(?:primer[oa]?|segund[oa]?|tercer[oa]?|cuart[oa]?|quint[oa]?|últim[oa]?|1r[oa]|2d[oa]|3r[oa])",
    r"(?:quiero|quisiera|me gustaría)\s+(?:ver|saber|conocer|más info)",
    r"(?:ese|esa|este|esta)\s+(?:me\s+)?(?:gusta|interesa|late|está bien|va|jala)",
    r"(?:el|la|ese|esa|del|de la)\s+(?:mazda|toyota|nissan|honda|kia|hyundai|chevrolet|volkswagen|suzuki|mg|baic|fiat|dodge|ford|renault|peugeot|mitsubishi|subaru|jac|changan|audi|bmw|mercedes)",
    r"(?:el|la|ese|esa|del|de la)\s+(?:versa|sentra|kicks|march|corolla|camry|rav4|cx-|aveo|onix|cavalier|tucson|creta|forte|rio|seltos|jetta|taos|tiguan|civic|crv|hrv|swift|vitara|hb20)",
    r"(?:el|la)\s+(?:de\s+)?\$?\d{1,3}[,.]?\d{3}",  # "el de $250,000"
    r"(?:el|la|ese|esa)\s+(?:roj[oa]|blanc[oa]|negr[oa]|gris|azul|plat[ea]|dorad[oa])",  # "el rojo"
    r"(?:el|la)\s+(?:del?\s+)?(?:20\d{2})",  # "el 2023", "el del 2024"
]

# Herramientas que implican uso correcto del contexto (no son fallo)
VALID_CONTEXT_TOOLS = [
    "obtenerVehiculo",
    "obtener_vehiculo",
    "comparar_vehiculos",
    "calcular_financiamiento",
    "enviarCotizacionEmail",
    "enviar_cotizacion_email",
    "agendarCita",
    "agendar_cita",
    "crear_solicitud_financiamiento",
    "crearSolicitudFinanciamiento",
]


# ─── Detección ──────────────────────────────────────────────────


def has_vehicle_ids_in_context(msgs, up_to_idx, lookback=6):
    """Verifica si hay IDs de vehículos disponibles en mensajes recientes."""
    ids_found = []
    for j in range(max(0, up_to_idx - lookback), up_to_idx):
        content = str(msgs[j].get("content", "") or "")
        # IDs en tool_response JSON
        ids = re.findall(r'"id_vehiculo":\s*(\d+)', content)
        ids.extend(re.findall(r'"id":\s*(\d+)', content))
        if ids and ("vehiculo" in content.lower() or "marca" in content.lower()
                     or "modelo" in content.lower() or "precio" in content.lower()
                     or "año" in content.lower()):
            ids_found.extend(ids)
    return ids_found


def detect_p1_context_failure(msgs):
    """
    Detecta fallo de contexto: hay IDs disponibles, usuario selecciona,
    asistente NO usa el ID correctamente.
    Retorna lista de (msg_idx, severidad, descripción).
    """
    issues = []

    for i in range(len(msgs)):
        if msgs[i].get("role") != "user":
            continue

        user_text = str(msgs[i].get("content", "") or "").lower()

        # ¿El usuario expresa interés en un vehículo específico?
        if not any(re.search(p, user_text, re.IGNORECASE) for p in USER_INTEREST_PATTERNS):
            continue

        # ¿Hay IDs de vehículos disponibles en el contexto previo?
        available_ids = has_vehicle_ids_in_context(msgs, i)
        if not available_ids:
            continue

        # ¿Qué hace el siguiente mensaje del asistente?
        if i + 1 >= len(msgs):
            continue

        next_msg = msgs[i + 1]
        if next_msg.get("role") != "assistant":
            continue

        next_content = str(next_msg.get("content", "") or "")

        # ¿Usa alguna herramienta válida con el contexto?
        uses_valid_tool = any(tool in next_content for tool in VALID_CONTEXT_TOOLS)
        if uses_valid_tool:
            continue

        # Ahora es un problema. Clasificar severidad.
        asks_id = bool(re.search(
            r"(?:necesito|proporcion|indic|compart|dam|decirme).*(?:id|ID|número|identificador|código)",
            next_content, re.IGNORECASE
        ))
        asks_which = bool(re.search(
            r"(?:cuál|cuáles?).*(?:te interesa|prefieres|quieres|te gusta|te llama)",
            next_content, re.IGNORECASE
        ))
        searches_again = "buscar_vehiculos" in next_content or "buscar_alternativas" in next_content

        if asks_id:
            severity = "CRITICAL"
            desc = "Pide ID al usuario"
        elif asks_which:
            severity = "CRITICAL"
            desc = "Pregunta cuál quiere (ya lo dijo)"
        elif searches_again:
            severity = "HIGH"
            desc = "Busca de nuevo en vez de usar ID disponible"
        else:
            severity = "HIGH"
            desc = "No usa obtenerVehiculo con ID disponible"

        issues.append((i, severity, desc))

    return issues


def detect_p2_obvious_questions(msgs):
    """
    Detecta preguntas obvias/redundantes del asistente.
    Retorna lista de (msg_idx, pattern_matched, context).
    """
    issues = []

    for i in range(len(msgs)):
        if msgs[i].get("role") != "assistant":
            continue

        content = str(msgs[i].get("content", "") or "")

        for pattern in OBVIOUS_Q_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if not match:
                continue

            # Obtener el mensaje previo del usuario para contexto
            prev_user = ""
            for j in range(i - 1, -1, -1):
                if msgs[j].get("role") == "user":
                    prev_user = str(msgs[j].get("content", "") or "").lower()
                    break

            # Verificar que realmente es redundante (el usuario ya dijo marca/modelo)
            user_mentions_brand = any(b in prev_user for b in KNOWN_BRANDS)
            user_mentions_model = any(m in prev_user for m in KNOWN_MODELS)

            # Casos legítimos de confirmación (no son problema):
            # - Montos ambiguos: "40" podría ser $40,000 o 40%
            # - Ubicaciones: si hay múltiples sucursales
            if re.search(r"te refieres a\s*\$?\d", content, re.IGNORECASE):
                continue  # pregunta sobre monto, puede ser legítimo
            if re.search(r"te refieres a(?:l?| la)\s+sucursal", content, re.IGNORECASE):
                continue  # pregunta sobre ubicación, puede ser legítimo

            # Si el usuario mencionó marca o modelo, la pregunta es claramente redundante
            if user_mentions_brand or user_mentions_model:
                issues.append((i, match.group()[:60], prev_user[:80]))
                break

            # Si el patrón es "Solo para confirmar/Permíteme confirmar" es redundante en general
            if re.search(r"(?:solo para|permíteme)\s+confirmar", match.group(), re.IGNORECASE):
                issues.append((i, match.group()[:60], prev_user[:80]))
                break

    return issues


# ─── Procesamiento de archivos ──────────────────────────────────


def process_file(filepath, dry_run=True):
    """Procesa un archivo JSONL, detecta problemas, retorna estadísticas."""
    fname = os.path.basename(filepath)

    if not os.path.exists(filepath):
        return {"file": fname, "exists": False}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total = len(lines)
    kept = []
    removed = []
    p1_count = 0
    p2_count = 0
    p1_critical = 0

    for line_num, raw_line in enumerate(lines, 1):
        raw_line_stripped = raw_line.strip()
        if not raw_line_stripped:
            kept.append(raw_line)
            continue

        try:
            obj = json.loads(raw_line_stripped)
        except json.JSONDecodeError:
            kept.append(raw_line)
            continue

        msgs = obj.get("messages", [])
        if not msgs:
            kept.append(raw_line)
            continue

        # Detectar problemas
        p1_issues = detect_p1_context_failure(msgs)
        p2_issues = detect_p2_obvious_questions(msgs)

        has_critical_p1 = any(sev in ("CRITICAL", "HIGH") for _, sev, _ in p1_issues)
        has_p2 = len(p2_issues) > 0

        if has_critical_p1 or has_p2:
            removed.append({
                "line": line_num,
                "p1": [(idx, sev, desc) for idx, sev, desc in p1_issues],
                "p2": [(idx, pat, ctx) for idx, pat, ctx in p2_issues],
                "data": raw_line,
            })
            p1_count += len(p1_issues)
            p2_count += len(p2_issues)
            p1_critical += sum(1 for _, s, _ in p1_issues if s == "CRITICAL")
        else:
            kept.append(raw_line)

    result = {
        "file": fname,
        "exists": True,
        "total": total,
        "kept": len(kept),
        "removed": len(removed),
        "p1_issues": p1_count,
        "p1_critical": p1_critical,
        "p2_issues": p2_count,
        "removed_details": removed,
        "kept_lines": kept,
    }

    if not dry_run and removed:
        # Escribir archivo limpio
        with open(filepath, "w", encoding="utf-8") as f:
            for line in kept:
                f.write(line if line.endswith("\n") else line + "\n")

        # Guardar removidos para auditoría
        removed_path = filepath.replace(".jsonl", "_pattern_removed.jsonl")
        with open(removed_path, "w", encoding="utf-8") as f:
            for entry in removed:
                reasons = []
                for idx, sev, desc in entry["p1"]:
                    reasons.append(f"P1[{sev}]: {desc} (msg {idx})")
                for idx, pat, ctx in entry["p2"]:
                    reasons.append(f"P2: '{pat}' (msg {idx})")
                meta = {"_removal_reasons": reasons}
                obj = json.loads(entry["data"].strip())
                obj["_removal_meta"] = meta
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    return result


# ─── Main ───────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Filtra conversaciones con patrones problemáticos"
    )
    parser.add_argument("--apply", action="store_true",
                        help="Aplicar filtros (sin esto, solo reporta)")
    parser.add_argument("--merge", action="store_true",
                        help="Re-ejecutar merge_all_v10.py después de filtrar")
    parser.add_argument("--dir", type=str, default=BASE,
                        help="Directorio base")
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 80)
    print("  filter_bad_patterns.py — Limpieza de patrones problemáticos")
    print(f"  Modo: {'DRY-RUN (solo reporta)' if dry_run else 'APLICANDO CAMBIOS'}")
    print("=" * 80)

    total_removed = 0
    total_kept = 0
    total_p1 = 0
    total_p2 = 0

    for fname in SOURCE_FILES:
        filepath = os.path.join(args.dir, fname)
        result = process_file(filepath, dry_run=dry_run)

        if not result["exists"]:
            continue

        removed = result["removed"]
        if removed > 0:
            pct = 100 * removed / result["total"]
            print(f"\n  {fname}")
            print(f"    Total: {result['total']} → Kept: {result['kept']}, "
                  f"Removed: {removed} ({pct:.1f}%)")
            print(f"    P1(contexto): {result['p1_issues']} "
                  f"({result['p1_critical']} critical)")
            print(f"    P2(obvias): {result['p2_issues']}")

            # Mostrar algunos ejemplos
            for entry in result["removed_details"][:3]:
                reasons = []
                for idx, sev, desc in entry["p1"]:
                    reasons.append(f"P1[{sev}]: {desc}")
                for idx, pat, ctx in entry["p2"]:
                    reasons.append(f"P2: {pat}")
                print(f"      L{entry['line']}: {'; '.join(reasons)}")
        else:
            print(f"\n  {fname}: OK ({result['total']} convos, sin problemas)")

        total_removed += removed
        total_kept += result["kept"]
        total_p1 += result["p1_issues"]
        total_p2 += result["p2_issues"]

    print(f"\n{'=' * 80}")
    print(f"  RESUMEN")
    print(f"{'=' * 80}")
    print(f"  Conversaciones totales:  {total_kept + total_removed}")
    print(f"  Conservadas:             {total_kept}")
    print(f"  Eliminadas:              {total_removed} "
          f"({100 * total_removed / max(total_kept + total_removed, 1):.1f}%)")
    print(f"  Problemas P1 (contexto): {total_p1}")
    print(f"  Problemas P2 (obvias):   {total_p2}")

    if dry_run:
        print(f"\n  Para aplicar cambios, ejecuta:")
        print(f"    python3 filter_bad_patterns.py --apply")
        print(f"    python3 filter_bad_patterns.py --apply --merge")
    else:
        print(f"\n  Cambios aplicados a archivos fuente.")
        if args.merge:
            print(f"\n  Regenerando merge...")
            merge_script = os.path.join(args.dir, "merge_all_v10.py")
            subprocess.run([sys.executable, merge_script], cwd=args.dir)
            print(f"\n  Merge regenerado.")
        else:
            print(f"  Para regenerar merge: python3 merge_all_v10.py")


if __name__ == "__main__":
    main()

