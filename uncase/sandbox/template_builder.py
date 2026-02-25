"""E2B template builder for creating custom sandbox templates.

A custom template pre-installs Python dependencies (litellm, pydantic)
so that sandbox boot time is faster — no pip install required per run.

Usage:
    python -m uncase.sandbox.template_builder

This creates a custom E2B template and prints the template ID to use
in E2B_TEMPLATE_ID.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

# Packages to pre-install in the custom template
TEMPLATE_PACKAGES = [
    "litellm>=1.55.0",
    "pydantic>=2.10.0",
]

DOCKERFILE_CONTENT = """FROM e2b/base:latest

# Install Python dependencies for the UNCASE sandbox worker
RUN pip install --no-cache-dir {packages}
""".format(packages=" ".join(f'"{p}"' for p in TEMPLATE_PACKAGES))


async def build_template(*, api_key: str) -> str:
    """Build and register a custom E2B template.

    Args:
        api_key: E2B API key.

    Returns:
        The template ID string.
    """
    logger.info("building_e2b_template", packages=TEMPLATE_PACKAGES)

    # Note: E2B template building is done via the e2b CLI or API.
    # For programmatic creation, use the E2B SDK when available.
    # For now, this provides the Dockerfile content for manual build.
    logger.info(
        "template_dockerfile",
        content=DOCKERFILE_CONTENT,
        instructions=(
            "To build the template, save the Dockerfile and run:\n"
            "  e2b template build --name uncase-worker --dockerfile Dockerfile\n"
            "Then set E2B_TEMPLATE_ID to the returned template ID."
        ),
    )

    return "base"


if __name__ == "__main__":
    print("E2B Template Dockerfile for UNCASE sandbox worker:")
    print("=" * 60)
    print(DOCKERFILE_CONTENT)
    print("=" * 60)
    print("\nTo build: e2b template build --name uncase-worker --dockerfile Dockerfile")
    print("Then set E2B_TEMPLATE_ID=<returned-id> in your .env")
