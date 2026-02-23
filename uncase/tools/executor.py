"""Simulated tool executor for the UNCASE SCSF pipeline.

Generates realistic mock responses for tool calls based on the tool's
output schema.  Used during synthetic conversation generation (Layer 3)
so that tool-augmented dialogues contain structurally valid payloads
without hitting real external services.
"""

from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING, Any

from uncase.tools.schemas import ToolCall, ToolResult

if TYPE_CHECKING:
    from uncase.tools.registry import ToolRegistry


class SimulatedToolExecutor:
    """Produces realistic mock responses for registered tools.

    The executor inspects the ``output_schema`` of the target tool and
    recursively generates plausible values for every declared property,
    using name-based heuristics to choose contextually appropriate data.

    Parameters
    ----------
    registry:
        Tool registry to resolve tool names.  When *None*, the module-level
        default registry is used.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        if registry is None:
            from uncase.tools import get_registry

            registry = get_registry()
        self._registry = registry

    # -- Public API ---------------------------------------------------------

    async def execute(
        self,
        tool_call: ToolCall,
        context: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Execute a tool call and return a simulated result.

        Parameters
        ----------
        tool_call:
            The tool invocation to execute.
        context:
            Optional context dict that may influence generated values
            (e.g. ``{"marca": "Toyota"}`` will appear in string fields
            whose name matches).

        Returns
        -------
        ToolResult
            A result with ``status="success"`` and a structurally valid
            payload, or ``status="error"`` if the tool is not registered.
        """
        if tool_call.tool_name not in self._registry:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                tool_name=tool_call.tool_name,
                result=f"Error: tool '{tool_call.tool_name}' not found in registry.",
                status="error",
                duration_ms=self._simulate_duration(),
            )

        tool = self._registry.get(tool_call.tool_name)

        # Merge tool_call arguments into context so generated values
        # can reference the caller's inputs.
        merged_context = {**(context or {}), **tool_call.arguments}

        output_schema = tool.output_schema
        if output_schema:
            result_data = self._generate_mock_value(
                "root",
                output_schema,
                merged_context,
            )
        else:
            result_data = {"ok": True, "message": "Operación completada exitosamente."}

        # Ensure the top-level result is always a dict for ToolResult.
        if not isinstance(result_data, dict):
            result_data = {"data": result_data}

        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            result=result_data,
            status="success",
            duration_ms=self._simulate_duration(),
        )

    # -- Mock value generation ----------------------------------------------

    def _generate_mock_value(
        self,
        name: str,
        schema: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Generate a single mock value guided by a JSON Schema fragment.

        Uses the property *name* and the schema *type* to produce
        contextually appropriate data.  Falls back to safe defaults
        when no heuristic matches.

        Parameters
        ----------
        name:
            Property name (used for heuristic matching).
        schema:
            JSON Schema fragment describing the expected type.
        context:
            Optional context for injecting caller-supplied values.
        """
        context = context or {}

        # If the schema declares an enum, pick one at random.
        if "enum" in schema:
            return random.choice(schema["enum"])  # noqa: S311

        schema_type = schema.get("type", "string")

        if schema_type == "object":
            return self._mock_object(schema, context)
        if schema_type == "array":
            return self._mock_array(name, schema, context)
        if schema_type == "string":
            return self._mock_string(name, context)
        if schema_type in ("number", "integer"):
            return self._mock_number(name, schema_type)
        if schema_type == "boolean":
            return True

        # Unknown type — return a placeholder string.
        return f"valor_simulado_{name}"

    # -- Type-specific helpers ----------------------------------------------

    def _mock_string(self, name: str, context: dict[str, Any]) -> str:
        """Return a context-aware string value."""
        lower = name.lower()

        # If the context already provides a value for this field, use it.
        if lower in context and isinstance(context[lower], str):
            return str(context[lower])

        # Name-based heuristics (automotive-first, extensible).
        heuristics: dict[str, str | list[str]] = {
            "id": uuid.uuid4().hex[:12],
            "vehiculo_id": f"VH-{random.randint(1000, 9999)}",  # noqa: S311
            "cliente_id": f"CL-{random.randint(1000, 9999)}",  # noqa: S311
            "marca": ["Toyota", "Honda", "Nissan", "Mazda", "Volkswagen", "Ford", "Chevrolet"],
            "modelo": ["Corolla", "Civic", "Sentra", "CX-5", "Jetta", "Escape", "Onix"],
            "color": ["Blanco", "Negro", "Plata", "Rojo", "Azul", "Gris"],
            "nombre": ["Carlos Pérez", "María López", "Juan García", "Ana Martínez"],
            "telefono": f"+52 {random.randint(55, 99)}{random.randint(10000000, 99999999)}",  # noqa: S311
            "email": f"cliente_{random.randint(100, 999)}@ejemplo.com",  # noqa: S311
            "tipo": ["sedan", "SUV", "pickup", "hatchback"],
            "estatus": ["disponible", "reservado", "vendido"],
            "vigencia": "2026-03-25",
            "fecha": "2026-02-23",
            "plan": ["Tradicional", "Smart", "Leasing"],
            "descripcion": "Valor generado por el simulador UNCASE.",
            "direccion": "Av. Insurgentes Sur 1234, Col. Del Valle, CDMX",
            "moneda": "MXN",
        }

        for key, value in heuristics.items():
            if key in lower:
                if isinstance(value, list):
                    return random.choice(value)  # noqa: S311
                return value

        return f"valor_simulado_{name}"

    def _mock_number(self, name: str, schema_type: str) -> int | float:
        """Return a contextually appropriate numeric value."""
        lower = name.lower()

        # Name-based numeric heuristics.
        ranges: dict[str, tuple[int, int]] = {
            "precio": (150_000, 850_000),
            "precio_base": (200_000, 750_000),
            "precio_final": (180_000, 800_000),
            "descuento": (5_000, 50_000),
            "monto": (100_000, 1_000_000),
            "mensualidad": (3_000, 25_000),
            "enganche": (20_000, 200_000),
            "plazo": (12, 72),
            "anio": (2020, 2026),
            "kilometraje": (0, 120_000),
            "tasa": (8, 18),
            "cat": (10, 25),
            "porcentaje": (5, 30),
            "cantidad": (1, 10),
            "total": (100_000, 900_000),
            "calificacion": (1, 10),
        }

        for key, (low, high) in ranges.items():
            if key in lower:
                if schema_type == "integer":
                    return random.randint(low, high)  # noqa: S311
                return round(random.uniform(low, high), 2)  # noqa: S311

        if schema_type == "integer":
            return random.randint(1, 100)  # noqa: S311
        return round(random.uniform(1.0, 100.0), 2)  # noqa: S311

    def _mock_array(
        self,
        name: str,
        schema: dict[str, Any],
        context: dict[str, Any],
    ) -> list[Any]:
        """Return a list with 1-3 mock items based on the array's items schema."""
        items_schema = schema.get("items", {"type": "string"})
        count = random.randint(1, 3)  # noqa: S311
        return [self._generate_mock_value(name, items_schema, context) for _ in range(count)]

    def _mock_object(
        self,
        schema: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Recursively generate a dict from the object's properties."""
        properties = schema.get("properties", {})
        if not properties:
            return {"valor": "objeto_simulado"}

        result: dict[str, Any] = {}
        for prop_name, prop_schema in properties.items():
            result[prop_name] = self._generate_mock_value(
                prop_name,
                prop_schema,
                context,
            )
        return result

    # -- Helpers ------------------------------------------------------------

    def _simulate_duration(self) -> int:
        """Return a random simulated execution duration in milliseconds."""
        return random.randint(50, 500)  # noqa: S311
