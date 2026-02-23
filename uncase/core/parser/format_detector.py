"""Auto-detect file format from extension and content heuristics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import structlog

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

# Expected CSV header column names used for heuristic detection.
_CSV_EXPECTED_COLUMNS = {"conversation_id", "turn_number", "role", "content"}

# Maximum number of bytes to read for content-based heuristics.
_SNIFF_BYTES = 4096


def detect_format(path: Path) -> Literal["csv", "jsonl", "json", "unknown"]:
    """Detect the file format from its extension and content heuristics.

    Args:
        path: Path to the file to inspect.

    Returns:
        One of ``"csv"``, ``"jsonl"``, ``"json"``, or ``"unknown"``.
    """
    suffix = path.suffix.lower()

    # 1. Fast path — unambiguous extensions.
    if suffix == ".csv":
        logger.debug("format_detected_by_extension", path=str(path), format="csv")
        return "csv"
    if suffix == ".jsonl":
        logger.debug("format_detected_by_extension", path=str(path), format="jsonl")
        return "jsonl"
    if suffix == ".json":
        logger.debug("format_detected_by_extension", path=str(path), format="json")
        return "json"

    # 2. Ambiguous extension — fall back to content heuristics.
    try:
        head = path.read_text(encoding="utf-8")[:_SNIFF_BYTES].lstrip()
    except (OSError, UnicodeDecodeError):
        logger.warning("format_detection_read_error", path=str(path))
        return "unknown"

    if not head:
        return "unknown"

    # JSONL heuristic: each non-empty line starts with '{'.
    lines = [ln.strip() for ln in head.splitlines() if ln.strip()]
    if lines and all(ln.startswith("{") for ln in lines) and len(lines) >= 2:
        logger.debug("format_detected_by_content", path=str(path), format="jsonl")
        return "jsonl"

    # JSON heuristic: starts with '[' or '{'.
    if head.startswith("[") or head.startswith("{"):
        logger.debug("format_detected_by_content", path=str(path), format="json")
        return "json"

    # CSV heuristic: first line contains expected column names separated by commas.
    first_line = lines[0] if lines else ""
    columns = {col.strip().strip('"').strip("'").lower() for col in first_line.split(",")}
    if _CSV_EXPECTED_COLUMNS.issubset(columns):
        logger.debug("format_detected_by_content", path=str(path), format="csv")
        return "csv"

    logger.debug("format_detection_unknown", path=str(path))
    return "unknown"
