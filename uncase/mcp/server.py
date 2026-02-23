"""FastMCP server for UNCASE — exposes SCSF tools via MCP protocol.

Dual approach:
1. Custom @mcp.tool decorators for workflow-specific tools
2. Mountable as ASGI sub-application at /mcp
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from uncase._version import __version__
from uncase.schemas.seed import SUPPORTED_DOMAINS


def create_mcp_server() -> FastMCP:
    """Create and configure the UNCASE MCP server with custom tools."""
    mcp = FastMCP(
        name="UNCASE",
        instructions=(
            "UNCASE is a framework for generating high-quality synthetic conversational data "
            "for LoRA/QLoRA fine-tuning in regulated industries. "
            "Use the available tools to manage seeds, validate data, and check system health."
        ),
    )

    @mcp.tool()
    def check_health() -> dict[str, str]:
        """Check UNCASE API health status."""
        return {"status": "ok", "version": __version__}

    @mcp.tool()
    def list_domains() -> dict[str, Any]:
        """List all supported conversation domains."""
        return {
            "domains": sorted(SUPPORTED_DOMAINS),
            "count": len(SUPPORTED_DOMAINS),
        }

    @mcp.tool()
    def get_quality_thresholds() -> dict[str, float]:
        """Get the mandatory quality thresholds for synthetic conversations."""
        return {
            "rouge_l_min": 0.65,
            "fidelidad_factual_min": 0.90,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.85,
            "privacy_score_max": 0.00,
            "memorizacion_max": 0.01,
        }

    @mcp.tool()
    def validate_seed(seed_json: str) -> dict[str, Any]:
        """Validate a seed JSON against SeedSchema v1.

        Args:
            seed_json: JSON string representing a seed.

        Returns:
            Validation result with status and any errors.
        """
        import json

        from uncase.schemas.seed import SeedSchema

        try:
            data = json.loads(seed_json)
            seed = SeedSchema.model_validate(data)
            return {
                "valid": True,
                "seed_id": seed.seed_id,
                "dominio": seed.dominio,
                "roles": seed.roles,
            }
        except (json.JSONDecodeError, Exception) as e:
            return {
                "valid": False,
                "error": str(e),
            }

    @mcp.tool()
    def get_seed_template(domain: str) -> dict[str, Any]:
        """Get a seed template for a specific domain.

        Args:
            domain: Domain namespace (e.g. 'automotive.sales').

        Returns:
            Template seed structure for the requested domain.
        """
        if domain not in SUPPORTED_DOMAINS:
            return {"error": f"Unknown domain '{domain}'. Available: {sorted(SUPPORTED_DOMAINS)}"}

        return {
            "version": "1.0",
            "dominio": domain,
            "idioma": "es",
            "roles": ["role_1", "role_2"],
            "objetivo": "Describe the conversation objective",
            "tono": "profesional",
            "pasos_turnos": {
                "turnos_min": 6,
                "turnos_max": 20,
                "flujo_esperado": ["greeting", "needs_assessment", "resolution"],
            },
            "parametros_factuales": {
                "contexto": "Describe the factual context",
                "restricciones": [],
                "herramientas": [],
                "metadata": {},
            },
        }

    return mcp


def create_mcp_app() -> Any:
    """Create the MCP ASGI application for mounting in FastAPI.

    Returns:
        Starlette-compatible ASGI app serving MCP over streamable HTTP.
    """
    mcp = create_mcp_server()
    return mcp.http_app(transport="streamable-http")
