"""Deterministic canonicalization and SHA-256 hashing of QualityReport."""

from __future__ import annotations

import hashlib
import json
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uncase.schemas.quality import QualityReport


def _round_floats(obj: Any, precision: int = 6) -> Any:
    """Recursively round all floats to *precision* decimal places.

    NaN / Inf values are coerced to 0.0 so that the canonical form is
    always valid JSON.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return round(obj, precision)
    if isinstance(obj, dict):
        return {k: _round_floats(v, precision) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, precision) for v in obj]
    return obj


def canonicalize_report(report: QualityReport) -> str:
    """Return a deterministic JSON string for *report*.

    Rules:
    - ``model_dump(mode="json")`` for Pydantic serialization
    - All floats rounded to 6 decimal places
    - Keys sorted recursively
    - No whitespace (``separators=(",", ":")``)
    """
    data = report.model_dump(mode="json")
    data = _round_floats(data)
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hash_report(report: QualityReport) -> str:
    """Return the SHA-256 hex digest (64 chars) of the canonical JSON."""
    canonical = canonicalize_report(report)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
