#!/usr/bin/env python3
"""Generate a Homebrew formula for UNCASE from PyPI metadata.

Usage:
    python scripts/generate-homebrew-formula.py --version 0.1.0 --output Formula/uncase.rb

Requires: homebrew-pypi-poet (pip install homebrew-pypi-poet)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import textwrap
import urllib.request


def get_sdist_url_and_sha(package: str, version: str) -> tuple[str, str]:
    """Fetch the sdist URL and SHA256 from PyPI."""
    import json

    url = f"https://pypi.org/pypi/{package}/{version}/json"
    with urllib.request.urlopen(url) as resp:  # noqa: S310
        data = json.loads(resp.read())

    for file_info in data["urls"]:
        if file_info["packagetype"] == "sdist":
            return file_info["url"], file_info["digests"]["sha256"]

    raise RuntimeError(f"No sdist found for {package}=={version}")


def generate_resources(package: str, version: str) -> str:
    """Use poet to generate resource stanzas for dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = f"{tmpdir}/venv"
        subprocess.check_call(
            [sys.executable, "-m", "venv", venv_dir],
            stdout=subprocess.DEVNULL,
        )
        pip = f"{venv_dir}/bin/pip"
        subprocess.check_call(
            [pip, "install", f"{package}=={version}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # poet generates resource stanzas from installed packages
        result = subprocess.check_output(
            [f"{venv_dir}/bin/python", "-m", "poet", "--resources", package],
            text=True,
        )
    return result.strip()


def build_formula(version: str, url: str, sha256: str, resources: str) -> str:
    """Build the complete Homebrew formula."""
    return textwrap.dedent(f"""\
        class Uncase < Formula
          include Language::Python::Virtualenv

          desc "Framework for high-quality synthetic conversational data generation"
          homepage "https://github.com/uncase-ai/uncase"
          url "{url}"
          sha256 "{sha256}"
          license "Apache-2.0"

          depends_on "python@3.12"

        {textwrap.indent(resources, "  ")}

          def install
            virtualenv_install_with_resources
          end

          test do
            assert_match version.to_s, shell_output("#{{bin}}/uncase --version")
          end
        end
    """)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Homebrew formula for UNCASE")
    parser.add_argument("--version", required=True, help="Package version (e.g. 0.1.0)")
    parser.add_argument("--output", default="-", help="Output file (default: stdout)")
    args = parser.parse_args()

    print(f"Fetching PyPI metadata for uncase=={args.version}...", file=sys.stderr)
    url, sha256 = get_sdist_url_and_sha("uncase", args.version)

    print("Generating resource stanzas (this installs dependencies in a temp venv)...", file=sys.stderr)
    resources = generate_resources("uncase", args.version)

    formula = build_formula(args.version, url, sha256, resources)

    if args.output == "-":
        print(formula)
    else:
        with open(args.output, "w") as f:
            f.write(formula)
        print(f"Formula written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
