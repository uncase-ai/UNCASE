"""Tests for format_detector — extension-based and content-based detection."""

from __future__ import annotations

from pathlib import Path

from uncase.core.parser.format_detector import detect_format


def test_detect_csv_by_extension(tmp_path: Path) -> None:
    """A .csv file is detected as 'csv'."""
    f = tmp_path / "data.csv"
    f.write_text("conversation_id,turn_number,role,content\n", encoding="utf-8")
    assert detect_format(f) == "csv"


def test_detect_jsonl_by_extension(tmp_path: Path) -> None:
    """A .jsonl file is detected as 'jsonl'."""
    f = tmp_path / "data.jsonl"
    f.write_text('{"messages": []}\n', encoding="utf-8")
    assert detect_format(f) == "jsonl"


def test_detect_json_by_extension(tmp_path: Path) -> None:
    """A .json file is detected as 'json'."""
    f = tmp_path / "data.json"
    f.write_text('[{"id": 1}]', encoding="utf-8")
    assert detect_format(f) == "json"


def test_detect_unknown(tmp_path: Path) -> None:
    """A .txt file with non-matching content is detected as 'unknown'."""
    f = tmp_path / "notes.txt"
    f.write_text("Just some plain text notes.\nNothing special here.", encoding="utf-8")
    assert detect_format(f) == "unknown"


def test_detect_csv_by_content(tmp_path: Path) -> None:
    """A .dat file with CSV-like headers is detected as 'csv' by content heuristic."""
    f = tmp_path / "data.dat"
    f.write_text(
        "conversation_id,turn_number,role,content\nc1,1,user,hello\n",
        encoding="utf-8",
    )
    assert detect_format(f) == "csv"


def test_detect_jsonl_by_content(tmp_path: Path) -> None:
    """A .dat file with multiple JSON lines is detected as 'jsonl' by content heuristic."""
    f = tmp_path / "data.dat"
    f.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
    assert detect_format(f) == "jsonl"


def test_detect_json_by_content(tmp_path: Path) -> None:
    """A .dat file starting with '[' is detected as 'json' by content heuristic."""
    f = tmp_path / "data.dat"
    f.write_text('[{"id": 1}]', encoding="utf-8")
    assert detect_format(f) == "json"


def test_detect_empty_file(tmp_path: Path) -> None:
    """An empty file with unknown extension returns 'unknown'."""
    f = tmp_path / "empty.dat"
    f.write_text("", encoding="utf-8")
    assert detect_format(f) == "unknown"
