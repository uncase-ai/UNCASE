#!/usr/bin/env python3
"""UNCASE Doc Agent — Haiku-powered documentation assistant.

Runs after commits to:
1. Translate documentation files (en <-> es)
2. Generate changelog entries from commit messages
3. Report what documentation may need updating

Usage:
    python scripts/doc-agent.py                  # process last commit
    python scripts/doc-agent.py --all            # process all doc files
    python scripts/doc-agent.py --translate FILE  # translate a specific file
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# The script uses the anthropic SDK. Install with: pip install anthropic
# or it's available in the project via: uv sync --extra dev
try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]

HAIKU_MODEL = "claude-haiku-4-5-20251001"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
FRONTEND_DOCS_DATA = PROJECT_ROOT / "frontend" / "src" / "assets" / "data" / "docs.ts"


def get_api_key() -> str | None:
    """Get Anthropic API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")


def run_git(*args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result.stdout.strip()


def get_changed_files_last_commit() -> list[str]:
    """Get files changed in the last commit."""
    output = run_git("diff", "--name-only", "HEAD~1", "HEAD")
    if not output:
        return []
    return [f for f in output.split("\n") if f]


def get_last_commits(n: int = 5) -> list[str]:
    """Get the last n commit messages."""
    output = run_git("log", f"-{n}", "--pretty=format:%s")
    if not output:
        return []
    return output.split("\n")


def translate_text(client: anthropic.Anthropic, text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using Claude Haiku."""
    lang_names = {"en": "English", "es": "Spanish"}
    message = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Translate the following {lang_names[source_lang]} text to "
                    f"{lang_names[target_lang]}. Preserve all markdown formatting, "
                    f"code blocks, HTML tags, and technical terms exactly as they are. "
                    f"Only output the translation, nothing else.\n\n{text}"
                ),
            }
        ],
    )
    return message.content[0].text


def generate_changelog_entry(client: anthropic.Anthropic, commits: list[str]) -> dict[str, str]:
    """Generate a bilingual changelog entry from commit messages."""
    message = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Based on these git commit messages, generate a concise changelog entry "
                    "as a JSON object with 'en' (English) and 'es' (Spanish) keys. "
                    "Each value should be a short bullet-point summary in HTML format "
                    "(using <ul><li> tags). Only output valid JSON, nothing else.\n\n"
                    "Commits:\n" + "\n".join(f"- {c}" for c in commits)
                ),
            }
        ],
    )
    try:
        return json.loads(message.content[0].text)
    except json.JSONDecodeError:
        return {"en": "See git log for details.", "es": "Ver git log para detalles."}


def translate_markdown_file(client: anthropic.Anthropic, filepath: Path, target_lang: str) -> Path:
    """Translate a markdown file and save the translated version."""
    content = filepath.read_text(encoding="utf-8")

    # Determine source language from path or content
    source_lang = "es" if target_lang == "en" else "en"

    translated = translate_text(client, content, source_lang, target_lang)

    # Create output path
    parent = filepath.parent
    target_dir = parent / target_lang if parent.name not in ("en", "es") else parent.parent / target_lang
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filepath.name

    target_path.write_text(translated, encoding="utf-8")
    return target_path


def analyze_changes(changed_files: list[str]) -> dict[str, list[str]]:
    """Categorize changed files by type."""
    categories: dict[str, list[str]] = {
        "docs": [],
        "python": [],
        "frontend": [],
        "config": [],
        "other": [],
    }

    for f in changed_files:
        if f.endswith((".md", ".mdx", ".rst")):
            categories["docs"].append(f)
        elif f.endswith(".py"):
            categories["python"].append(f)
        elif f.endswith((".tsx", ".ts", ".jsx", ".js")):
            categories["frontend"].append(f)
        elif f.endswith((".toml", ".yml", ".yaml", ".json", ".cfg")):
            categories["config"].append(f)
        else:
            categories["other"].append(f)

    return categories


def process_commit(client: anthropic.Anthropic | None) -> None:
    """Process the last commit for documentation updates."""
    changed_files = get_changed_files_last_commit()
    if not changed_files:
        print("No files changed in last commit.")
        return

    categories = analyze_changes(changed_files)

    print(f"\n{'='*60}")
    print("  UNCASE Doc Agent — Post-Commit Report")
    print(f"{'='*60}\n")

    # Report what changed
    for cat, files in categories.items():
        if files:
            print(f"  {cat.upper()} ({len(files)} files):")
            for f in files[:5]:
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            print()

    # Translate doc files if API key is available
    if categories["docs"] and client:
        print("  Translating documentation files...")
        for doc_file in categories["docs"]:
            filepath = PROJECT_ROOT / doc_file
            if not filepath.exists():
                continue
            try:
                # Determine if it needs en->es or es->en translation
                if "/en/" in doc_file or doc_file.startswith("en/"):
                    target = translate_markdown_file(client, filepath, "es")
                    print(f"    EN->ES: {doc_file} -> {target.relative_to(PROJECT_ROOT)}")
                elif "/es/" in doc_file or doc_file.startswith("es/"):
                    target = translate_markdown_file(client, filepath, "en")
                    print(f"    ES->EN: {doc_file} -> {target.relative_to(PROJECT_ROOT)}")
                else:
                    # Default: translate to Spanish (assume English source)
                    target = translate_markdown_file(client, filepath, "es")
                    print(f"    EN->ES: {doc_file} -> {target.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                print(f"    ERROR translating {doc_file}: {e}")
        print()

    # Suggest updates for code changes
    code_changes = categories["python"] + categories["frontend"]
    if code_changes:
        print("  Code changes detected — documentation may need updating:")
        for f in code_changes[:10]:
            print(f"    - {f}")
        if client:
            print("\n  Run `python scripts/doc-agent.py --update-docs` to auto-generate updates.")
        print()

    if not client:
        print("  Note: Set ANTHROPIC_API_KEY to enable automatic translation")
        print("  and changelog generation.\n")

    print(f"{'='*60}\n")


def translate_file_command(client: anthropic.Anthropic, filepath_str: str) -> None:
    """Translate a specific file to the other language."""
    filepath = Path(filepath_str).resolve()
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Determine target language
    target_lang = "en" if "/es/" in str(filepath) or filepath.parent.name == "es" else "es"

    target = translate_markdown_file(client, filepath, target_lang)
    print(f"Translated: {filepath.name} -> {target}")


def process_all(client: anthropic.Anthropic) -> None:
    """Process all documentation files."""
    doc_files = list(DOCS_DIR.rglob("*.md")) if DOCS_DIR.exists() else []
    print(f"Found {len(doc_files)} documentation files in docs/")

    for filepath in doc_files:
        rel = filepath.relative_to(PROJECT_ROOT)
        if "/en/" in str(filepath):
            try:
                target = translate_markdown_file(client, filepath, "es")
                print(f"  EN->ES: {rel} -> {target.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                print(f"  ERROR: {rel}: {e}")
        elif "/es/" in str(filepath):
            try:
                target = translate_markdown_file(client, filepath, "en")
                print(f"  ES->EN: {rel} -> {target.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                print(f"  ERROR: {rel}: {e}")
        else:
            # Standalone file — translate to both
            try:
                target_es = translate_markdown_file(client, filepath, "es")
                print(f"  ->ES: {rel} -> {target_es.relative_to(PROJECT_ROOT)}")
                target_en = translate_markdown_file(client, filepath, "en")
                print(f"  ->EN: {rel} -> {target_en.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                print(f"  ERROR: {rel}: {e}")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="UNCASE Doc Agent — Haiku-powered documentation assistant")
    parser.add_argument("--all", action="store_true", help="Process all documentation files")
    parser.add_argument("--translate", metavar="FILE", help="Translate a specific file")
    parser.add_argument("--changelog", action="store_true", help="Generate changelog from recent commits")
    args = parser.parse_args()

    # Initialize client if API key is available
    client = None
    api_key = get_api_key()
    if api_key and anthropic:
        client = anthropic.Anthropic(api_key=api_key)
    elif not anthropic:
        print("Warning: anthropic package not installed. Run: uv sync --extra dev")
    elif not api_key:
        print("Warning: ANTHROPIC_API_KEY not set. Translation features disabled.")

    if args.translate:
        if not client:
            print("Error: ANTHROPIC_API_KEY required for translation.")
            sys.exit(1)
        translate_file_command(client, args.translate)
    elif args.all:
        if not client:
            print("Error: ANTHROPIC_API_KEY required for --all processing.")
            sys.exit(1)
        process_all(client)
    elif args.changelog:
        if not client:
            print("Error: ANTHROPIC_API_KEY required for changelog generation.")
            sys.exit(1)
        commits = get_last_commits(10)
        entry = generate_changelog_entry(client, commits)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    else:
        process_commit(client)


if __name__ == "__main__":
    main()
