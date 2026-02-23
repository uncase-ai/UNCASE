"""Privacy tests: scan codebase for accidental real PII.

These tests are MANDATORY before any merge/PR.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Patterns that suggest real PII
PII_PATTERNS = [
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "US phone number"),
    (r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "SSN-like pattern"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email address"),
    (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "credit card number"),
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "IP address"),
]

# Directories to scan
SCAN_DIRS = ["tests", "examples"]

# Files/patterns to exclude from scanning
EXCLUDE_PATTERNS = [
    "test_no_real_data.py",  # This file itself
    "__pycache__",
    ".pyc",
]

PROJECT_ROOT = Path(__file__).parent.parent.parent


def _should_scan(path: Path) -> bool:
    """Check if a file should be scanned."""
    path_str = str(path)
    return not any(excl in path_str for excl in EXCLUDE_PATTERNS) and path.suffix in (".py", ".json", ".yaml", ".yml")


def _scan_file(path: Path) -> list[tuple[str, int, str, str]]:
    """Scan a file for PII patterns.

    Returns list of (file, line_no, pattern_name, matched_text).
    """
    findings: list[tuple[str, int, str, str]] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return findings

    for line_no, line in enumerate(content.splitlines(), 1):
        for pattern, name in PII_PATTERNS:
            matches = re.findall(pattern, line)
            for match in matches:
                # Exclude common false positives
                if name == "IP address" and match in ("0.0.0.0", "127.0.0.1", "255.255.255.255"):
                    continue
                if name == "email address" and ("example.com" in match or "test" in match.lower()):
                    continue
                findings.append((str(path.relative_to(PROJECT_ROOT)), line_no, name, match))

    return findings


@pytest.mark.privacy
class TestNoRealData:
    """Ensure no real PII exists in test files or examples."""

    def test_no_pii_in_test_files(self) -> None:
        findings: list[tuple[str, int, str, str]] = []
        tests_dir = PROJECT_ROOT / "tests"
        if tests_dir.exists():
            for path in tests_dir.rglob("*"):
                if path.is_file() and _should_scan(path):
                    findings.extend(_scan_file(path))

        if findings:
            report = "\n".join(f"  {f}:{ln} [{name}] {text}" for f, ln, name, text in findings)
            pytest.fail(f"Potential PII found in test files:\n{report}")

    def test_no_pii_in_examples(self) -> None:
        findings: list[tuple[str, int, str, str]] = []
        examples_dir = PROJECT_ROOT / "examples"
        if examples_dir.exists():
            for path in examples_dir.rglob("*"):
                if path.is_file() and _should_scan(path):
                    findings.extend(_scan_file(path))

        if findings:
            report = "\n".join(f"  {f}:{ln} [{name}] {text}" for f, ln, name, text in findings)
            pytest.fail(f"Potential PII found in example files:\n{report}")

    def test_no_real_names_in_factories(self) -> None:
        """Check that test factories use clearly fictional data."""
        factories_path = PROJECT_ROOT / "tests" / "factories.py"
        if not factories_path.exists():
            return

        content = factories_path.read_text(encoding="utf-8")
        # Ensure "ficticio" (fictional) markers are present
        assert "fictici" in content.lower(), "Factory data should be marked as fictional"
