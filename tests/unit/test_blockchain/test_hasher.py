"""Unit tests for deterministic canonicalization and SHA-256 hashing."""

from __future__ import annotations

from datetime import UTC, datetime

from uncase.core.blockchain.hasher import canonicalize_report, hash_report
from uncase.schemas.quality import QualityMetrics, QualityReport


def _make_report(**overrides: object) -> QualityReport:
    """Create a QualityReport with sensible defaults."""
    defaults = {
        "conversation_id": "conv-001",
        "seed_id": "seed-001",
        "metrics": QualityMetrics(
            rouge_l=0.75,
            fidelidad_factual=0.92,
            diversidad_lexica=0.60,
            coherencia_dialogica=0.88,
            privacy_score=0.0,
            memorizacion=0.005,
        ),
        "composite_score": 0.60,
        "passed": True,
        "failures": [],
        "evaluated_at": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return QualityReport(**defaults)  # type: ignore[arg-type]


class TestCanonicalizeReport:
    def test_deterministic(self) -> None:
        """Same report produces the same canonical JSON every time."""
        report = _make_report()
        assert canonicalize_report(report) == canonicalize_report(report)

    def test_sorted_keys(self) -> None:
        """Canonical JSON has sorted keys."""
        canonical = canonicalize_report(_make_report())
        # "composite_score" should come before "conversation_id" alphabetically
        assert canonical.index('"composite_score"') < canonical.index('"conversation_id"')

    def test_no_whitespace(self) -> None:
        """Canonical JSON has no spaces or newlines."""
        canonical = canonicalize_report(_make_report())
        assert " " not in canonical
        assert "\n" not in canonical

    def test_floats_rounded(self) -> None:
        """Floats are rounded to 6 decimal places (extra precision truncated)."""
        report = _make_report(
            metrics=QualityMetrics(
                rouge_l=0.7500001234567,
                fidelidad_factual=0.92,
                diversidad_lexica=0.60,
                coherencia_dialogica=0.88,
                privacy_score=0.0,
                memorizacion=0.005,
            )
        )
        canonical = canonicalize_report(report)
        # 7+ decimal places should NOT appear (truncated to 6)
        assert "0.7500001" not in canonical
        # round(0.7500001234567, 6) == 0.75 — JSON serializes trailing zeros
        assert "0.75" in canonical


class TestHashReport:
    def test_hex_digest_length(self) -> None:
        """SHA-256 produces a 64-char hex digest."""
        digest = hash_report(_make_report())
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_same_report_same_hash(self) -> None:
        """Identical reports produce the same hash."""
        r1 = _make_report()
        r2 = _make_report()
        assert hash_report(r1) == hash_report(r2)

    def test_different_report_different_hash(self) -> None:
        """Different reports produce different hashes."""
        r1 = _make_report(conversation_id="conv-001")
        r2 = _make_report(conversation_id="conv-002")
        assert hash_report(r1) != hash_report(r2)

    def test_metric_change_changes_hash(self) -> None:
        """A small metric change produces a completely different hash."""
        r1 = _make_report()
        r2 = _make_report(
            metrics=QualityMetrics(
                rouge_l=0.76,  # changed from 0.75
                fidelidad_factual=0.92,
                diversidad_lexica=0.60,
                coherencia_dialogica=0.88,
                privacy_score=0.0,
                memorizacion=0.005,
            )
        )
        assert hash_report(r1) != hash_report(r2)

    def test_passed_change_changes_hash(self) -> None:
        """Changing passed flag changes the hash."""
        r1 = _make_report(passed=True)
        r2 = _make_report(passed=False)
        assert hash_report(r1) != hash_report(r2)
