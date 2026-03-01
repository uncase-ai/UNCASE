#!/usr/bin/env python3
"""
uncase_prepare_dataset.py — Unified data quality pipeline + training advisor
=============================================================================

Cleans, deduplicates, validates, and analyzes JSONL datasets for fine-tuning.
Optionally recommends training hyperparameters based on dataset analysis.

Usage:
    # Full pipeline: clean + analyze + recommend
    python scripts/uncase_prepare_dataset.py \
        --input data/train.jsonl \
        --output-dir data/cleaned/ \
        --dedup --dedup-threshold 0.85 \
        --filter-patterns \
        --validate-tools --tool-schemas tools.json \
        --split --eval-ratio 0.1 \
        --system-prompt system_prompt.txt \
        --advise --vram 48 --model-size 14

    # Analysis only (no cleaning)
    python scripts/uncase_prepare_dataset.py \
        --input data/train.jsonl \
        --analyze-only --vram 24

    # Dry run (report only)
    python scripts/uncase_prepare_dataset.py \
        --input data/train.jsonl --dedup --filter-patterns --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PrepareReport:
    """Report from the data preparation pipeline."""

    input_files: list[str]
    original_count: int = 0
    dedup_removed: int = 0
    pattern_removed: int = 0
    tool_invalid_removed: int = 0
    final_count: int = 0
    train_count: int = 0
    eval_count: int = 0
    output_dir: str = ""


@dataclass
class DatasetProfile:
    """Profile of a dataset for training advisor."""

    total_conversations: int = 0
    avg_turns_per_conversation: float = 0.0
    avg_tokens_per_turn: float = 0.0
    max_sequence_length_needed: int = 0
    p95_sequence_length: int = 0
    tool_call_percentage: float = 0.0
    unique_tools_used: set[str] = field(default_factory=set)
    scenario_distribution: dict[str, int] = field(default_factory=dict)
    language: str = "unknown"
    has_system_prompt: bool = False
    quality_score: float = 0.0


@dataclass
class TrainingRecommendation:
    """Recommended training hyperparameters."""

    epochs_min: int = 2
    epochs_max: int = 3
    learning_rate: float = 2e-4
    lora_r: int = 16
    lora_alpha: int = 32
    max_seq_length: int = 2048
    batch_size: int = 2
    grad_accum: int = 8
    neftune_noise: int = 5
    model: str = ""
    model_reason: str = ""
    alternative_model: str = ""
    estimated_time_minutes: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# MinHash Deduplication (from generate_features_clean.py)
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_text(obj: dict[str, Any]) -> str:
    """Extract normalized text from conversation for similarity comparison."""
    msgs = obj.get("messages", [])
    parts = []
    for m in msgs:
        if m.get("role") in ("user", "assistant"):
            content = str(m.get("content", "") or "")
            content = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.DOTALL)
            content = re.sub(r"<tool_response>.*?</tool_response>", "", content, flags=re.DOTALL)
            content = re.sub(r"\s+", " ", content).strip().lower()
            content = re.sub(r"[^\w\s]", "", content)
            if content:
                parts.append(content)
    return " ".join(parts)


def _shingles(text: str, k: int = 3) -> set[str]:
    """Generate word k-grams (shingles) from text."""
    words = text.split()
    if len(words) < k:
        return {text} if text else set()
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def _minhash(shingle_set: set[str], num_hashes: int = 100) -> tuple[int, ...]:
    """Compute MinHash signature for a set of shingles."""
    if not shingle_set:
        return tuple([0] * num_hashes)
    sig = []
    for i in range(num_hashes):
        min_hash = float("inf")
        for s in shingle_set:
            h = int(hashlib.md5(f"{i}:{s}".encode()).hexdigest()[:16], 16)  # noqa: S324
            if h < min_hash:
                min_hash = h
        sig.append(int(min_hash))
    return tuple(sig)


def _jaccard(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0.0


def dedup_minhash(
    conversations: list[dict[str, Any]],
    threshold: float = 0.85,
    num_hashes: int = 100,
) -> tuple[list[dict[str, Any]], int]:
    """Remove near-duplicate conversations using MinHash/LSH.

    Returns (deduplicated_conversations, num_removed).
    """
    if not conversations:
        return conversations, 0

    num_bands = 20
    rows_per_band = num_hashes // num_bands

    # Compute text + shingles + signatures
    entries = []
    for conv in conversations:
        text = _extract_text(conv)
        shings = _shingles(text)
        sig = _minhash(shings, num_hashes)
        entries.append({"conv": conv, "shingles": shings, "sig": sig})

    # LSH bucketing
    candidates: set[tuple[int, int]] = set()
    for band in range(num_bands):
        buckets: dict[int, list[int]] = defaultdict(list)
        start = band * rows_per_band
        end = start + rows_per_band
        for idx, entry in enumerate(entries):
            bucket_key = hash(entry["sig"][start:end])
            buckets[bucket_key].append(idx)
        for members in buckets.values():
            if len(members) > 1:
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        candidates.add((members[i], members[j]))

    # Verify candidates with actual Jaccard
    confirmed = []
    for i, j in candidates:
        sim = _jaccard(entries[i]["shingles"], entries[j]["shingles"])
        if sim >= threshold:
            confirmed.append((i, j))

    # Union-Find grouping
    parent = list(range(len(entries)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i, j in confirmed:
        union(i, j)

    groups: dict[int, list[int]] = defaultdict(list)
    for idx in range(len(entries)):
        groups[find(idx)].append(idx)

    # Keep first in each group, remove the rest
    remove_indices: set[int] = set()
    for members in groups.values():
        if len(members) > 1:
            members.sort()
            for m in members[1:]:
                remove_indices.add(m)

    kept = [entries[i]["conv"] for i in range(len(entries)) if i not in remove_indices]
    return kept, len(remove_indices)


# ═══════════════════════════════════════════════════════════════════════════════
# Pattern Filtering (from generate_features_fix_patterns.py)
# ═══════════════════════════════════════════════════════════════════════════════

# Generic conversational anti-patterns (domain-agnostic)
_REDUNDANT_CONFIRM_PATTERNS = [
    re.compile(r"(?:solo para|permíteme)\s+confirmar", re.IGNORECASE),
    re.compile(r"para confirmar[,:]?\s*(?:¿|¡)?", re.IGNORECASE),
    re.compile(r"es correcto que\s+", re.IGNORECASE),
]


def filter_context_failures(conversations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Remove conversations where assistant ignores available context.

    P1: Assistant has relevant data from tool responses but asks
    redundant questions or searches again instead of using it.
    """
    kept = []
    removed = 0

    for conv in conversations:
        msgs = conv.get("messages", [])
        has_failure = False

        for i, msg in enumerate(msgs):
            if msg.get("role") != "assistant":
                continue
            content = str(msg.get("content", "") or "")

            # Check if there's a recent tool response with data
            has_tool_data = False
            for j in range(max(0, i - 4), i):
                prev_content = str(msgs[j].get("content", "") or "")
                if msgs[j].get("role") == "tool" or "<tool_response>" in prev_content:
                    has_tool_data = True
                    break

            if not has_tool_data:
                continue

            # Check if assistant asks for what was already provided
            if "<tool_call>" in content:
                continue  # Using tools is fine

            # Check for redundant re-asking patterns
            for pattern in _REDUNDANT_CONFIRM_PATTERNS:
                if pattern.search(content):
                    has_failure = True
                    break

            if has_failure:
                break

        if has_failure:
            removed += 1
        else:
            kept.append(conv)

    return kept, removed


def filter_redundant_questions(conversations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Remove conversations where assistant asks obvious/redundant questions.

    P2: User states something clearly and assistant asks
    redundant confirmation questions.
    """
    kept = []
    removed = 0

    for conv in conversations:
        msgs = conv.get("messages", [])
        has_issue = False

        for i, msg in enumerate(msgs):
            if msg.get("role") != "assistant":
                continue
            content = str(msg.get("content", "") or "")

            # Skip short responses (unlikely to be problematic)
            if len(content) < 30:
                continue

            # Check if previous user message was clear
            prev_user = ""
            for j in range(i - 1, -1, -1):
                if msgs[j].get("role") == "user":
                    prev_user = str(msgs[j].get("content", "") or "")
                    break

            if not prev_user or len(prev_user) < 5:
                continue

            # Count confirmation questions — flag if excessive
            confirm_count = sum(1 for p in _REDUNDANT_CONFIRM_PATTERNS if p.search(content))
            if confirm_count >= 2:
                has_issue = True
                break

        if has_issue:
            removed += 1
        else:
            kept.append(conv)

    return kept, removed


# ═══════════════════════════════════════════════════════════════════════════════
# Tool Call Validation (from generate_features_validate_tools.py)
# ═══════════════════════════════════════════════════════════════════════════════

_TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)


def validate_tool_calls(
    conversations: list[dict[str, Any]],
    tool_schemas: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Validate tool call JSON structure and optionally check against schemas.

    Removes conversations with malformed tool calls:
    - Invalid JSON inside <tool_call> tags
    - Missing 'name' or 'arguments' keys
    - Unknown tool names (if schemas provided)
    - Missing required arguments (if schemas provided)

    Returns (valid_conversations, num_removed).
    """
    kept = []
    removed = 0

    for conv in conversations:
        msgs = conv.get("messages", [])
        is_valid = True

        for msg in msgs:
            if msg.get("role") != "assistant":
                continue
            content = str(msg.get("content", "") or "")

            for match in _TOOL_CALL_RE.finditer(content):
                raw = match.group(1).strip()
                try:
                    tc = json.loads(raw)
                except json.JSONDecodeError:
                    is_valid = False
                    break

                name = tc.get("name")
                args = tc.get("arguments", {})

                if not name:
                    is_valid = False
                    break

                if not isinstance(args, dict):
                    is_valid = False
                    break

                # Schema validation if provided
                if tool_schemas and name in tool_schemas:
                    schema = tool_schemas[name]
                    allowed_args = set(schema.get("properties", {}).keys())
                    required_args = set(schema.get("required", []))

                    given_args = set(args.keys())
                    if required_args - given_args:
                        is_valid = False
                        break
                    if given_args - allowed_args:
                        is_valid = False
                        break
                elif tool_schemas and name not in tool_schemas:
                    is_valid = False
                    break

            if not is_valid:
                break

        if is_valid:
            kept.append(conv)
        else:
            removed += 1

    return kept, removed


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario Classification (from generate_features_structures.py)
# ═══════════════════════════════════════════════════════════════════════════════


def classify_scenarios(conversations: list[dict[str, Any]]) -> dict[str, int]:
    """Categorize conversations by scenario type and tool usage patterns.

    Returns dict mapping scenario type to count.
    """
    categories: Counter[str] = Counter()

    for conv in conversations:
        msgs = conv.get("messages", [])
        all_content = " ".join(str(m.get("content", "") or "") for m in msgs)

        has_tool_call = "<tool_call>" in all_content
        has_tool_response = "<tool_response>" in all_content or any(m.get("role") == "tool" for m in msgs)

        if has_tool_call and has_tool_response:
            categories["tool_assisted"] += 1
        elif has_tool_call:
            categories["tool_attempted"] += 1
        else:
            categories["conversational"] += 1

        # Subcategorize by user intent
        user_content = " ".join(str(m.get("content", "") or "") for m in msgs if m.get("role") == "user").lower()

        if any(w in user_content for w in ["compare", "comparar", "vs", "versus", "diferencia"]):
            categories["comparison"] += 1
        elif any(w in user_content for w in ["search", "buscar", "find", "encontrar", "busco"]):
            categories["search"] += 1
        elif any(w in user_content for w in ["price", "precio", "cost", "costo", "financ"]):
            categories["pricing"] += 1
        elif any(w in user_content for w in ["hello", "hola", "hi ", "hey", "buenos", "buenas"]):
            categories["greeting"] += 1
        else:
            categories["other"] += 1

    return dict(categories)


# ═══════════════════════════════════════════════════════════════════════════════
# Dataset Utilities
# ═══════════════════════════════════════════════════════════════════════════════


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL file into a list of dicts."""
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError:
                continue
    return records


def save_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    """Save list of dicts to JSONL file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def split_train_eval(
    conversations: list[dict[str, Any]],
    eval_ratio: float = 0.1,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split conversations into train and eval sets."""
    import random

    shuffled = list(conversations)
    random.shuffle(shuffled)
    eval_count = max(1, int(len(shuffled) * eval_ratio))
    return shuffled[eval_count:], shuffled[:eval_count]


def inject_system_prompt(
    conversations: list[dict[str, Any]],
    prompt_file: str | Path,
) -> list[dict[str, Any]]:
    """Inject or replace system prompt in all conversations."""
    prompt_text = Path(prompt_file).read_text(encoding="utf-8").strip()
    result = []

    for conv in conversations:
        msgs = list(conv.get("messages", []))
        if msgs and msgs[0].get("role") == "system":
            msgs[0] = {"role": "system", "content": prompt_text}
        else:
            msgs.insert(0, {"role": "system", "content": prompt_text})
        result.append({**conv, "messages": msgs})

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Training Advisor
# ═══════════════════════════════════════════════════════════════════════════════


def _detect_language(conversations: list[dict[str, Any]]) -> str:
    """Detect dominant language from conversation content."""
    es_words = {"el", "la", "de", "que", "en", "un", "es", "por", "con", "para", "los", "del"}
    en_words = {"the", "is", "and", "to", "of", "in", "for", "with", "that", "this", "are", "was"}

    sample_text = ""
    for conv in conversations[:50]:
        for msg in conv.get("messages", []):
            if msg.get("role") in ("user", "assistant"):
                sample_text += " " + str(msg.get("content", "") or "")

    words = sample_text.lower().split()
    es_count = sum(1 for w in words if w in es_words)
    en_count = sum(1 for w in words if w in en_words)

    if es_count > en_count * 1.2:
        return "es"
    elif en_count > es_count * 1.2:
        return "en"
    return "mixed"


def _extract_tools_used(conversations: list[dict[str, Any]]) -> set[str]:
    """Extract unique tool names used across all conversations."""
    tools: set[str] = set()
    for conv in conversations:
        for msg in conv.get("messages", []):
            content = str(msg.get("content", "") or "")
            for match in _TOOL_CALL_RE.finditer(content):
                try:
                    tc = json.loads(match.group(1).strip())
                    name = tc.get("name", "")
                    if name:
                        tools.add(name)
                except json.JSONDecodeError:
                    continue
    return tools


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate (4 chars per token)."""
    return max(1, len(text) // 4)


def analyze_dataset(conversations: list[dict[str, Any]]) -> DatasetProfile:
    """Produce a full dataset profile for the training advisor."""
    profile = DatasetProfile()
    profile.total_conversations = len(conversations)

    if not conversations:
        return profile

    turn_counts = []
    token_counts = []
    seq_lengths = []
    tool_call_convs = 0
    has_system = 0

    for conv in conversations:
        msgs = conv.get("messages", [])
        non_system = [m for m in msgs if m.get("role") != "system"]
        turn_counts.append(len(non_system))

        if any(m.get("role") == "system" for m in msgs):
            has_system += 1

        seq_tokens = 0
        conv_has_tool = False
        for msg in msgs:
            content = str(msg.get("content", "") or "")
            tokens = _estimate_tokens(content)
            token_counts.append(tokens)
            seq_tokens += tokens
            if "<tool_call>" in content:
                conv_has_tool = True

        seq_lengths.append(seq_tokens)
        if conv_has_tool:
            tool_call_convs += 1

    profile.avg_turns_per_conversation = sum(turn_counts) / len(turn_counts)
    profile.avg_tokens_per_turn = sum(token_counts) / max(len(token_counts), 1)

    sorted_seqs = sorted(seq_lengths)
    p95_idx = int(len(sorted_seqs) * 0.95)
    profile.p95_sequence_length = sorted_seqs[min(p95_idx, len(sorted_seqs) - 1)]
    profile.max_sequence_length_needed = sorted_seqs[-1]

    profile.tool_call_percentage = (tool_call_convs / len(conversations)) * 100
    profile.unique_tools_used = _extract_tools_used(conversations)
    profile.scenario_distribution = classify_scenarios(conversations)
    profile.language = _detect_language(conversations)
    profile.has_system_prompt = has_system > len(conversations) * 0.5

    return profile


def compute_quality_score(
    original_count: int,
    dedup_removed: int,
    pattern_removed: int,
    tool_invalid: int,
) -> float:
    """Compute a quality score from 0.0 to 1.0 based on cleaning ratios."""
    if original_count == 0:
        return 0.0
    total_removed = dedup_removed + pattern_removed + tool_invalid
    clean_ratio = 1.0 - (total_removed / original_count)
    return round(max(0.0, min(1.0, clean_ratio)), 3)


def recommend_training(
    profile: DatasetProfile,
    vram_gb: int = 48,
    model_size_b: float = 14.0,
) -> TrainingRecommendation:
    """Generate adaptive training hyperparameter recommendations."""
    rec = TrainingRecommendation()
    n = profile.total_conversations

    # --- Epochs ---
    if n < 200:
        rec.epochs_min, rec.epochs_max = 5, 8
    elif n < 1000:
        rec.epochs_min, rec.epochs_max = 3, 5
    elif n < 5000:
        rec.epochs_min, rec.epochs_max = 2, 3
    else:
        rec.epochs_min, rec.epochs_max = 1, 2

    if profile.quality_score < 0.7:
        rec.epochs_min = max(1, rec.epochs_min - 1)
        rec.epochs_max = max(1, rec.epochs_max - 1)
    if profile.tool_call_percentage > 50:
        rec.epochs_max += 1

    # --- Learning rate ---
    if n < 500:
        rec.learning_rate = 1e-4
    elif n < 2000:
        rec.learning_rate = 2e-4
    else:
        rec.learning_rate = 3e-4

    if profile.tool_call_percentage > 30:
        rec.learning_rate *= 0.7

    rec.learning_rate = round(rec.learning_rate, 6)

    # --- LoRA rank & alpha ---
    tool_count = len(profile.unique_tools_used)
    if tool_count == 0:
        rec.lora_r, rec.lora_alpha = 8, 16
    elif tool_count < 5:
        rec.lora_r, rec.lora_alpha = 16, 32
    else:
        rec.lora_r, rec.lora_alpha = 32, 64

    if model_size_b >= 14:
        rec.lora_r = max(rec.lora_r, 32)
        rec.lora_alpha = rec.lora_r * 2
    elif model_size_b <= 7:
        rec.lora_r = min(rec.lora_r, 16)
        rec.lora_alpha = rec.lora_r * 2

    # --- Max sequence length ---
    p95 = profile.p95_sequence_length
    for power in [512, 1024, 2048, 4096, 8192]:
        if power >= p95:
            rec.max_seq_length = power
            break
    else:
        rec.max_seq_length = 8192

    # Cap by VRAM
    if vram_gb < 24:
        rec.max_seq_length = min(rec.max_seq_length, 1024)
    elif vram_gb < 48:
        rec.max_seq_length = min(rec.max_seq_length, 4096)

    # --- Batch size from VRAM ---
    if vram_gb >= 80:
        rec.batch_size, rec.grad_accum = 6, 2
    elif vram_gb >= 44:
        rec.batch_size, rec.grad_accum = 4, 4
    elif vram_gb >= 22:
        rec.batch_size, rec.grad_accum = 2, 8
    else:
        rec.batch_size, rec.grad_accum = 1, 16

    # --- NEFTune ---
    rec.neftune_noise = 0 if profile.quality_score > 0.95 else 5

    # --- Model recommendation ---
    if profile.tool_call_percentage > 30:
        if model_size_b >= 14 or n > 1000:
            rec.model = "Qwen/Qwen3-14B"
            rec.model_reason = f">30% tool calls, {profile.language}, {n} conversations"
            rec.alternative_model = "Qwen/Qwen2.5-7B"
        else:
            rec.model = "Qwen/Qwen2.5-7B"
            rec.model_reason = f"tool calls present, small dataset ({n})"
            rec.alternative_model = "meta-llama/Llama-3.2-3B"
    elif profile.language == "es":
        if n > 1000:
            rec.model = "Qwen/Qwen3-14B"
            rec.model_reason = f"Spanish, {n} conversations"
            rec.alternative_model = "meta-llama/Llama-3.1-8B"
        else:
            rec.model = "meta-llama/Llama-3.1-8B"
            rec.model_reason = f"Spanish, moderate dataset ({n})"
            rec.alternative_model = "Qwen/Qwen2.5-7B"
    else:
        if n > 2000:
            rec.model = "meta-llama/Llama-3.1-8B"
            rec.model_reason = f"Large dataset ({n})"
            rec.alternative_model = "Qwen/Qwen2.5-7B"
        else:
            rec.model = "meta-llama/Llama-3.2-3B"
            rec.model_reason = f"Small dataset ({n}), avoid overfitting"
            rec.alternative_model = "Qwen/Qwen2.5-7B"

    # --- Estimated time (very rough) ---
    steps = (n * rec.epochs_max) / (rec.batch_size * rec.grad_accum)
    secs_per_step = 0.5 if vram_gb >= 80 else 1.0 if vram_gb >= 44 else 2.0
    rec.estimated_time_minutes = max(1, int((steps * secs_per_step) / 60))

    return rec


def print_advisor_report(profile: DatasetProfile, rec: TrainingRecommendation, vram_gb: int) -> None:
    """Print human-readable training advisor report."""
    w = 55
    print()
    print("+" + "-" * w + "+")
    print(f"|{'UNCASE Dataset Analysis & Training Advisor':^{w}}|")
    print("+" + "-" * w + "+")
    print(f"|{'Dataset':^{w}}|")
    print(f"|  {'Conversations:':<25} {profile.total_conversations:>26,} |")
    print(f"|  {'Avg turns:':<25} {profile.avg_turns_per_conversation:>26.1f} |")
    print(f"|  {'Avg tokens/turn:':<25} {profile.avg_tokens_per_turn:>26.0f} |")
    print(f"|  {'Tool usage:':<25} {profile.tool_call_percentage:>22.0f}%"
          f" ({len(profile.unique_tools_used)} tools) |")
    print(f"|  {'Quality score:':<25} {profile.quality_score:>26.2f} |")
    print(f"|  {'Language:':<25} {profile.language:>26} |")
    print(f"|  {'Max seq needed (p95):':<25} {profile.p95_sequence_length:>20} tokens |")
    print("+" + "-" * w + "+")
    print(f"|{f'Recommended Config ({vram_gb}GB VRAM)':^{w}}|")
    print(f"|  {'Epochs:':<25} {f'{rec.epochs_min}-{rec.epochs_max}':>26} |")
    print(f"|  {'Learning rate:':<25} {rec.learning_rate:>26.1e} |")
    print(f"|  {'LoRA rank:':<25} {f'r={rec.lora_r}, alpha={rec.lora_alpha}':>26} |")
    print(f"|  {'Max seq length:':<25} {rec.max_seq_length:>26} |")
    eff = rec.batch_size * rec.grad_accum
    print(f"|  {'Batch:':<25} {f'{rec.batch_size} x {rec.grad_accum} = {eff} effective':>26} |")
    print(f"|  {'NEFTune noise:':<25} {rec.neftune_noise:>26} |")
    print(f"|  {'Est. training time:':<25} {f'~{rec.estimated_time_minutes} min':>26} |")
    print("+" + "-" * w + "+")
    print(f"|  {'Model:':<25} {rec.model:>26} |")
    print(f"|  {'Reason:':<25} {rec.model_reason[:26]:>26} |")
    print(f"|  {'Alternative:':<25} {rec.alternative_model:>26} |")
    print("+" + "-" * w + "+")
    print()


def export_advisor_json(
    profile: DatasetProfile,
    rec: TrainingRecommendation,
    output_path: str | Path,
) -> None:
    """Export advisor recommendation as JSON for shell scripts to read."""
    data = {
        "profile": {
            "total_conversations": profile.total_conversations,
            "avg_turns": round(profile.avg_turns_per_conversation, 1),
            "avg_tokens_per_turn": round(profile.avg_tokens_per_turn, 0),
            "p95_seq_length": profile.p95_sequence_length,
            "tool_call_pct": round(profile.tool_call_percentage, 1),
            "unique_tools": len(profile.unique_tools_used),
            "language": profile.language,
            "quality_score": profile.quality_score,
        },
        "recommendation": {
            "epochs_min": rec.epochs_min,
            "epochs_max": rec.epochs_max,
            "learning_rate": rec.learning_rate,
            "lora_r": rec.lora_r,
            "lora_alpha": rec.lora_alpha,
            "max_seq_length": rec.max_seq_length,
            "batch_size": rec.batch_size,
            "grad_accum": rec.grad_accum,
            "neftune_noise": rec.neftune_noise,
            "model": rec.model,
            "alternative_model": rec.alternative_model,
            "estimated_time_minutes": rec.estimated_time_minutes,
        },
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# Main Pipeline
# ═══════════════════════════════════════════════════════════════════════════════


def run_pipeline(args: argparse.Namespace) -> PrepareReport:
    """Run the full data preparation pipeline."""
    report = PrepareReport(input_files=[str(f) for f in args.input])

    # Load all input files
    all_conversations: list[dict[str, Any]] = []
    for input_file in args.input:
        convs = load_jsonl(input_file)
        print(f"  Loaded {len(convs)} conversations from {input_file}")
        all_conversations.extend(convs)

    report.original_count = len(all_conversations)
    print(f"\n  Total loaded: {report.original_count} conversations")

    if args.analyze_only:
        profile = analyze_dataset(all_conversations)
        profile.quality_score = 1.0  # Can't compute without cleaning
        rec = recommend_training(profile, args.vram, args.model_size)
        print_advisor_report(profile, rec, args.vram)
        if args.output_dir:
            advisor_path = os.path.join(args.output_dir, "advisor.json")
            export_advisor_json(profile, rec, advisor_path)
            print(f"  Advisor JSON saved to {advisor_path}")
        return report

    # Step 1: Deduplication
    if args.dedup:
        print(f"\n  Deduplicating (MinHash, threshold={args.dedup_threshold})...")
        all_conversations, removed = dedup_minhash(all_conversations, threshold=args.dedup_threshold)
        report.dedup_removed = removed
        print(f"    Removed {removed} duplicates, {len(all_conversations)} remaining")

    # Step 2: Pattern filtering
    if args.filter_patterns:
        print("\n  Filtering context failures (P1)...")
        all_conversations, r1 = filter_context_failures(all_conversations)
        print(f"    Removed {r1} context failure conversations")

        print("  Filtering redundant questions (P2)...")
        all_conversations, r2 = filter_redundant_questions(all_conversations)
        print(f"    Removed {r2} redundant question conversations")
        report.pattern_removed = r1 + r2

    # Step 3: Tool call validation
    if args.validate_tools:
        tool_schemas = None
        if args.tool_schemas:
            with open(args.tool_schemas) as f:
                tool_schemas = json.load(f)

        print("\n  Validating tool calls...")
        all_conversations, removed = validate_tool_calls(all_conversations, tool_schemas)
        report.tool_invalid_removed = removed
        print(f"    Removed {removed} conversations with invalid tool calls")

    # Step 4: System prompt injection
    if args.system_prompt:
        print(f"\n  Injecting system prompt from {args.system_prompt}...")
        all_conversations = inject_system_prompt(all_conversations, args.system_prompt)
        print(f"    System prompt injected into {len(all_conversations)} conversations")

    report.final_count = len(all_conversations)

    # Step 5: Split train/eval
    if args.split:
        train_set, eval_set = split_train_eval(all_conversations, args.eval_ratio)
        report.train_count = len(train_set)
        report.eval_count = len(eval_set)
        print(f"\n  Split: {report.train_count} train / {report.eval_count} eval")
    else:
        train_set = all_conversations
        eval_set = []
        report.train_count = len(train_set)

    # Save outputs
    if not args.dry_run and args.output_dir:
        report.output_dir = args.output_dir
        os.makedirs(args.output_dir, exist_ok=True)

        train_path = os.path.join(args.output_dir, "train.jsonl")
        save_jsonl(train_set, train_path)
        print(f"\n  Saved train: {train_path} ({len(train_set)} conversations)")

        if eval_set:
            eval_path = os.path.join(args.output_dir, "eval.jsonl")
            save_jsonl(eval_set, eval_path)
            print(f"  Saved eval:  {eval_path} ({len(eval_set)} conversations)")

    # Training advisor
    if args.advise:
        profile = analyze_dataset(train_set)
        profile.quality_score = compute_quality_score(
            report.original_count,
            report.dedup_removed,
            report.pattern_removed,
            report.tool_invalid_removed,
        )
        rec = recommend_training(profile, args.vram, args.model_size)
        print_advisor_report(profile, rec, args.vram)

        if args.output_dir:
            advisor_path = os.path.join(args.output_dir, "advisor.json")
            export_advisor_json(profile, rec, advisor_path)
            print(f"  Advisor JSON saved to {advisor_path}")

    # Summary
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Original:           {report.original_count:,}")
    if args.dedup:
        print(f"  Duplicates removed: {report.dedup_removed:,}")
    if args.filter_patterns:
        print(f"  Patterns removed:   {report.pattern_removed:,}")
    if args.validate_tools:
        print(f"  Invalid tools:      {report.tool_invalid_removed:,}")
    print(f"  Final:              {report.final_count:,}")
    if args.split:
        print(f"  Train / Eval:       {report.train_count:,} / {report.eval_count:,}")
    pct = (report.final_count / report.original_count * 100) if report.original_count else 0
    print(f"  Retention:          {pct:.1f}%")
    if args.dry_run:
        print("\n  (DRY RUN — no files written)")
    print()

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UNCASE dataset preparation pipeline + training advisor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input/output
    parser.add_argument("--input", "-i", nargs="+", required=True, help="Input JSONL file(s)")
    parser.add_argument("--output-dir", "-o", default="", help="Output directory for cleaned files")

    # Cleaning options
    parser.add_argument("--dedup", action="store_true", help="Run MinHash deduplication")
    parser.add_argument("--dedup-threshold", type=float, default=0.85, help="Jaccard threshold (default: 0.85)")
    parser.add_argument("--filter-patterns", action="store_true", help="Filter conversational anti-patterns")
    parser.add_argument("--validate-tools", action="store_true", help="Validate tool call JSON structure")
    parser.add_argument("--tool-schemas", type=str, default="", help="Path to tool schemas JSON file")

    # Dataset manipulation
    parser.add_argument("--split", action="store_true", help="Split into train/eval sets")
    parser.add_argument("--eval-ratio", type=float, default=0.1, help="Eval split ratio (default: 0.1)")
    parser.add_argument("--system-prompt", type=str, default="", help="Path to system prompt file to inject")

    # Training advisor
    parser.add_argument("--advise", action="store_true", help="Run training advisor and print recommendations")
    parser.add_argument("--vram", type=int, default=48, help="GPU VRAM in GB (default: 48)")
    parser.add_argument("--model-size", type=float, default=14.0, help="Target model size in billions (default: 14)")

    # Modes
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze dataset, no cleaning")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not write files")

    args = parser.parse_args()

    print("=" * 60)
    print("  UNCASE Dataset Preparation Pipeline")
    print(f"  Mode: {'ANALYZE ONLY' if args.analyze_only else 'DRY RUN' if args.dry_run else 'FULL PIPELINE'}")
    print("=" * 60)

    run_pipeline(args)


if __name__ == "__main__":
    main()
