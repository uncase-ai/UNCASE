"""E2B template builder for creating custom sandbox templates (v2 SDK).

A custom template pre-installs Python dependencies (litellm, pydantic)
so that sandbox boot time is ~5s instead of ~60s.

Usage:
    python -m uncase.sandbox.template_builder          # build dev template
    python -m uncase.sandbox.template_builder --prod    # build production template
"""

from __future__ import annotations

import sys

import structlog

logger = structlog.get_logger(__name__)

TEMPLATE_PACKAGES = [
    "litellm>=1.55.0",
    "pydantic>=2.10.0",
]

TEMPLATE_TAG_DEV = "uncase-worker-dev"
TEMPLATE_TAG_PROD = "uncase-worker"


def _build_template() -> None:
    """Define and build the UNCASE sandbox template using E2B v2 SDK."""
    try:
        from dotenv import load_dotenv
        from e2b import Template, default_build_logger
    except ImportError:
        print(
            "Missing dependencies. Install with:\n"
            '  pip install "e2b>=1.0.0" python-dotenv\n'
            "Or:\n"
            "  uv sync --extra sandbox"
        )
        sys.exit(1)

    load_dotenv()

    template = (
        Template()
        .from_python_image("3.12")
        .pip_install(TEMPLATE_PACKAGES)
        .set_envs({"UNCASE_SANDBOX": "true"})
    )

    is_prod = "--prod" in sys.argv
    tag = TEMPLATE_TAG_PROD if is_prod else TEMPLATE_TAG_DEV
    env_label = "production" if is_prod else "development"

    logger.info("building_e2b_template", tag=tag, env=env_label, packages=TEMPLATE_PACKAGES)
    print(f"Building E2B template '{tag}' ({env_label})...")

    Template.build(
        template,
        tag,
        cpu_count=1,
        memory_mb=1024,
        on_build_logs=default_build_logger(),
    )

    print(f"\nTemplate built successfully: {tag}")
    print(f"Set in your .env: E2B_TEMPLATE_ID={tag}")


if __name__ == "__main__":
    _build_template()
