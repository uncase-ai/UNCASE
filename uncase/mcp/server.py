"""FastMCP server for UNCASE — exposes SCSF tools via MCP protocol.

Dual approach:
1. Custom @mcp.tool decorators for workflow-specific tools
2. Mountable as ASGI sub-application at /mcp
"""

from __future__ import annotations

import contextlib
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

    # -- Template tools -----------------------------------------------------

    @mcp.tool()
    def list_templates() -> dict[str, Any]:
        """List all available chat template formats for fine-tuning export."""
        from uncase.templates import get_template_registry, register_all_templates

        register_all_templates()
        registry = get_template_registry()
        templates = []
        for name in registry.list_names():
            t = registry.get(name)
            templates.append(
                {
                    "name": t.name,
                    "display_name": t.display_name,
                    "supports_tool_calls": t.supports_tool_calls,
                    "special_tokens": t.get_special_tokens(),
                }
            )
        return {"templates": templates, "count": len(templates)}

    @mcp.tool()
    def render_template(conversations_json: str, template_name: str) -> dict[str, Any]:
        """Render conversations using a specific chat template format.

        Args:
            conversations_json: JSON string with a list of conversations.
            template_name: Template name (e.g. 'chatml', 'llama', 'mistral').

        Returns:
            Rendered output for each conversation.
        """
        import json

        from uncase.schemas.conversation import Conversation
        from uncase.templates import get_template_registry, register_all_templates

        try:
            raw = json.loads(conversations_json)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}"}

        if not isinstance(raw, list):
            return {"error": "Expected a JSON array of conversations."}

        try:
            conversations = [Conversation.model_validate(item) for item in raw]
        except Exception as e:
            return {"error": f"Conversation validation failed: {e}"}

        register_all_templates()
        registry = get_template_registry()

        try:
            template = registry.get(template_name)
        except Exception as e:
            return {"error": str(e)}

        rendered: list[str] = []
        for conv in conversations:
            try:
                rendered.append(template.render(conv))
            except Exception as e:
                rendered.append(f"[render error: {e}]")

        return {
            "rendered": rendered,
            "template_name": template_name,
            "count": len(rendered),
        }

    # -- Evaluation tools ---------------------------------------------------

    @mcp.tool()
    def evaluate_conversation(conversation_json: str, seed_json: str) -> dict[str, Any]:
        """Evaluate a conversation's quality against its origin seed.

        Computes all 6 quality metrics (ROUGE-L, fidelity, diversity,
        coherence, privacy, memorization) and the composite score.

        Args:
            conversation_json: JSON string representing a Conversation.
            seed_json: JSON string representing the origin SeedSchema.

        Returns:
            Quality report with metrics, composite score, and pass/fail.
        """
        import asyncio
        import json

        from uncase.core.evaluator.evaluator import ConversationEvaluator
        from uncase.schemas.conversation import Conversation
        from uncase.schemas.seed import SeedSchema

        try:
            conv_data = json.loads(conversation_json)
            seed_data = json.loads(seed_json)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}"}

        try:
            conversation = Conversation.model_validate(conv_data)
            seed = SeedSchema.model_validate(seed_data)
        except Exception as e:
            return {"error": f"Validation failed: {e}"}

        evaluator = ConversationEvaluator()

        try:
            report = asyncio.run(evaluator.evaluate(conversation, seed))
        except RuntimeError:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                report = pool.submit(asyncio.run, evaluator.evaluate(conversation, seed)).result()

        return report.model_dump(mode="json")

    # -- Tool framework tools -----------------------------------------------

    @mcp.tool()
    def list_tools(domain: str = "") -> dict[str, Any]:
        """List registered tool definitions, optionally filtered by domain.

        Args:
            domain: Optional domain namespace to filter by (e.g. 'automotive.sales').
        """
        from uncase.tools import get_registry

        # Ensure builtins are loaded (side-effect import, already guarded).
        with contextlib.suppress(ImportError):
            import uncase.tools._builtin  # noqa: F401

        registry = get_registry()
        tools = registry.list_by_domain(domain) if domain else [registry.get(name) for name in registry.list_names()]

        tool_summaries = [
            {
                "name": t.name,
                "description": t.description,
                "domains": t.domains,
                "category": t.category,
                "execution_mode": t.execution_mode,
                "version": t.version,
            }
            for t in tools
        ]
        return {"tools": tool_summaries, "count": len(tool_summaries)}

    @mcp.tool()
    def simulate_tool(tool_name: str, arguments_json: str = "{}") -> dict[str, Any]:
        """Simulate execution of a registered tool with given arguments.

        Args:
            tool_name: Name of the tool to simulate.
            arguments_json: JSON string of arguments to pass to the tool.
        """
        import asyncio
        import json

        from uncase.tools import get_registry
        from uncase.tools.executor import SimulatedToolExecutor
        from uncase.tools.schemas import ToolCall

        try:
            arguments = json.loads(arguments_json)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid arguments JSON: {e}"}

        if not isinstance(arguments, dict):
            return {"error": "Arguments must be a JSON object."}

        tool_call = ToolCall(tool_name=tool_name, arguments=arguments)
        executor = SimulatedToolExecutor(registry=get_registry())

        try:
            result = asyncio.run(executor.execute(tool_call))
        except RuntimeError:
            # If an event loop is already running, use it directly.
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, executor.execute(tool_call)).result()

        return {
            "tool_call_id": result.tool_call_id,
            "tool_name": result.tool_name,
            "status": result.status,
            "result": result.result,
            "duration_ms": result.duration_ms,
        }

    return mcp


def create_mcp_app() -> Any:
    """Create the MCP ASGI application for mounting in FastAPI.

    Returns:
        Starlette-compatible ASGI app serving MCP over streamable HTTP.
    """
    mcp = create_mcp_server()
    return mcp.http_app(transport="streamable-http")
