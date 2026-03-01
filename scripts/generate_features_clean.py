#!/usr/bin/env python3
"""
dedup_and_clean.py — Remove near-duplicates and no-tool vehicle listings
========================================================================

1. Near-duplicate removal: MinHash/LSH with 85% Jaccard threshold on word 3-grams
2. No-tool listing removal: Assistant lists vehicles (price + model/year) without prior tool_call

Usage:
    python3 dedup_and_clean.py                # dry-run
    python3 dedup_and_clean.py --apply        # apply changes
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

BASE = "/Users/marianomorales/Downloads/fine-tuning/inference/datasets"

FILES = [
    "merged_v10_together_train.jsonl",
    "merged_v10_together_eval.jsonl",
]


def extract_text(obj):
    """Extract normalized text from conversation for similarity."""
    msgs = obj.get("messages", [])
    parts = []
    for m in msgs:
        if m.get("role") in ("user", "assistant"):
            content = str(m.get("content", "") or "")
            content = re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL)
            content = re.sub(r'<tool_response>.*?</tool_response>', '', content, flags=re.DOTALL)
            content = re.sub(r'\s+', ' ', content).strip().lower()
            content = re.sub(r'[^\w\s]', '', content)
            if content:
                parts.append(content)
    return " ".join(parts)


def shingles(text, k=3):
    words = text.split()
    if len(words) < k:
        return {text} if text else set()
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}


def minhash(shingle_set, num_hashes=100):
    if not shingle_set:
        return tuple([0] * num_hashes)
    sig = []
    for i in range(num_hashes):
        min_hash = float('inf')
        for s in shingle_set:
            h = int(hashlib.md5(f"{i}:{s}".encode()).hexdigest()[:16], 16)
            if h < min_hash:
                min_hash = h
        sig.append(min_hash)
    return tuple(sig)


def jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0.0


def find_duplicates(conversations, threshold=0.85):
    """Find near-duplicate groups using MinHash/LSH."""
    num_hashes = 100
    num_bands = 20
    rows_per_band = num_hashes // num_bands

    # Generate signatures
    sigs = []
    for conv in conversations:
        sig = minhash(conv["shingles"], num_hashes)
        sigs.append(sig)

    # LSH bucketing
    candidates = set()
    for band in range(num_bands):
        buckets = defaultdict(list)
        start = band * rows_per_band
        end = start + rows_per_band
        for idx, sig in enumerate(sigs):
            bucket_key = hash(sig[start:end])
            buckets[bucket_key].append(idx)
        for members in buckets.values():
            if len(members) > 1:
                for i in range(len(members)):
                    for j in range(i+1, len(members)):
                        candidates.add((members[i], members[j]))

    # Verify with actual Jaccard
    confirmed = []
    for i, j in candidates:
        sim = jaccard(conversations[i]["shingles"], conversations[j]["shingles"])
        if sim >= threshold:
            confirmed.append((i, j, sim))

    # Union-Find to group
    parent = list(range(len(conversations)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i, j, _ in confirmed:
        union(i, j)

    groups = defaultdict(list)
    for idx in range(len(conversations)):
        groups[find(idx)].append(idx)

    # Lines to remove (keep lowest line number in each group)
    dup_lines = set()
    for root, members in groups.items():
        if len(members) > 1:
            members.sort(key=lambda x: conversations[x]["line"])
            for m in members[1:]:
                dup_lines.add(conversations[m]["line"])

    return dup_lines, len([g for g in groups.values() if len(g) > 1])


def has_listing_without_tool(msgs):
    """Check if assistant lists vehicles with prices/specs without prior tool call."""
    tools_called = set()

    for i, msg in enumerate(msgs):
        role = msg.get("role", "")
        content = str(msg.get("content", "") or "")

        # Track tool calls
        if role == "assistant":
            for tool in ["buscar_vehiculos", "buscar_alternativas", "obtenerVehiculo",
                         "obtener_vehiculo", "comparar_vehiculos", "estadisticas_inventario"]:
                if tool in content:
                    tools_called.add("search")
        if role == "tool":
            if any(k in content for k in ['"marca"', '"modelo"', '"precio"', '"id_vehiculo"']):
                tools_called.add("search")

        # Check for vehicle listing without prior tool
        if role == "assistant" and "search" not in tools_called:
            has_price = bool(re.search(r'\$\s*[\d,]{4,}', content))
            has_vehicle = bool(re.search(
                r'(?:Nissan|Toyota|Mazda|Chevrolet|Hyundai|Kia|Volkswagen|Honda|Suzuki|MG|BAIC|Ford|Dodge|Jeep|Renault|Fiat|Mitsubishi|Subaru)\s+\w+\s+20[12]\d|20[12]\d\s+(?:Nissan|Toyota|Mazda|Chevrolet|Hyundai|Kia|Volkswagen|Honda|Suzuki|MG|BAIC|Ford|Dodge|Jeep|Renault|Fiat|Mitsubishi|Subaru)',
                content, re.IGNORECASE
            ))
            has_monthly = bool(re.search(r'mensualidad(?:es)?\s+(?:de\s+)?\$[\d,]+', content, re.IGNORECASE))

            if has_price and has_vehicle and len(content) > 100:
                return True
            if has_monthly and has_vehicle:
                return True

    return False


def process_file(filepath, dry_run=True):
    fname = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    conversations = []
    for i, line in enumerate(raw_lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except:
            continue
        text = extract_text(obj)
        conversations.append({
            "line": i,
            "obj": obj,
            "raw": line,
            "text": text,
            "shingles": shingles(text),
        })

    total = len(conversations)
    print(f"\n  {fname}: {total} conversaciones")

    # Step 1: Find duplicates
    print(f"    Buscando duplicados (MinHash/LSH, threshold=0.85)...")
    dup_lines, dup_groups = find_duplicates(conversations, threshold=0.85)
    print(f"    Duplicados: {len(dup_lines)} líneas en {dup_groups} grupos")

    # Step 2: Find no-tool listings
    print(f"    Buscando listados sin tools...")
    notool_lines = set()
    for conv in conversations:
        msgs = conv["obj"].get("messages", [])
        if has_listing_without_tool(msgs):
            notool_lines.add(conv["line"])
    print(f"    Listados sin tools: {len(notool_lines)} conversaciones")

    # Combine removals
    all_remove = dup_lines | notool_lines
    overlap = dup_lines & notool_lines
    print(f"    Overlap: {len(overlap)}")
    print(f"    Total a remover: {len(all_remove)} ({100*len(all_remove)/total:.1f}%)")

    # Write cleaned file
    if not dry_run and all_remove:
        kept = [c["raw"] for c in conversations if c["line"] not in all_remove]
        with open(filepath, "w", encoding="utf-8") as f:
            for line in kept:
                f.write(line if line.endswith("\n") else line + "\n")
        print(f"    Escrito: {len(kept)} conversaciones (eliminadas {len(all_remove)})")

    return {
        "file": fname,
        "total": total,
        "dup_removed": len(dup_lines),
        "notool_removed": len(notool_lines - dup_lines),
        "total_removed": len(all_remove),
        "kept": total - len(all_remove),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("  dedup_and_clean.py — Deduplicación + limpieza de listados sin tools")
    print(f"  Modo: {'DRY-RUN' if dry_run else 'APLICANDO CAMBIOS'}")
    print("=" * 70)

    results = []
    for fname in FILES:
        fpath = os.path.join(BASE, fname)
        if not os.path.exists(fpath):
            print(f"\n  {fname}: NO ENCONTRADO")
            continue
        result = process_file(fpath, dry_run=dry_run)
        results.append(result)

    print(f"\n{'=' * 70}")
    print("  RESUMEN")
    print(f"{'=' * 70}")
    for r in results:
        print(f"  {r['file']}:")
        print(f"    Original: {r['total']}")
        print(f"    Duplicados removidos: {r['dup_removed']}")
        print(f"    Sin-tools removidos: {r['notool_removed']}")
        print(f"    Final: {r['kept']}")

    if dry_run:
        print(f"\n  Ejecuta con --apply para aplicar cambios")


if __name__ == "__main__":
    main()

