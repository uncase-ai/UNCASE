"""Built-in tool definitions for the **automotive.sales** pilot domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

import uncase.tools as _tools_pkg
from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. buscar_inventario
# ---------------------------------------------------------------------------

buscar_inventario = ToolDefinition(
    name="buscar_inventario",
    description=(
        "Search the dealership vehicle inventory using optional filters.\n\n"
        "WHEN_TO_USE: The customer asks about available vehicles, specific brands, "
        "models, price ranges, or vehicle types. Also useful when the agent needs "
        "to verify stock before quoting.\n\n"
        "CAPABILITIES:\n"
        "- Filter by brand, model, year range, maximum price, and vehicle type.\n"
        "- Returns a list of matching vehicles with key specs and availability status.\n"
        "- Supports partial matches (e.g. searching only by brand).\n\n"
        "EXAMPLE:\n"
        '  Input:  {"marca": "Toyota", "tipo": "SUV", "precio_max": 600000}\n'
        '  Output: [{"vehiculo_id": "VH-4821", "marca": "Toyota", "modelo": "RAV4", ...}]'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "marca": {
                "type": "string",
                "description": "Vehicle brand to filter by (e.g. Toyota, Honda).",
            },
            "modelo": {
                "type": "string",
                "description": "Specific model name (e.g. Corolla, Civic).",
            },
            "anio_min": {
                "type": "integer",
                "description": "Minimum model year (inclusive).",
            },
            "anio_max": {
                "type": "integer",
                "description": "Maximum model year (inclusive).",
            },
            "precio_max": {
                "type": "number",
                "description": "Maximum price in MXN.",
            },
            "tipo": {
                "type": "string",
                "description": "Vehicle type.",
                "enum": ["sedan", "SUV", "pickup", "hatchback", "coupe", "minivan"],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "vehiculos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "vehiculo_id": {"type": "string"},
                        "marca": {"type": "string"},
                        "modelo": {"type": "string"},
                        "anio": {"type": "integer"},
                        "precio": {"type": "number"},
                        "color": {"type": "string"},
                        "tipo": {"type": "string"},
                        "kilometraje": {"type": "integer"},
                        "estatus": {"type": "string"},
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["automotive.sales"],
    category="automotive",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. cotizar_vehiculo
# ---------------------------------------------------------------------------

cotizar_vehiculo = ToolDefinition(
    name="cotizar_vehiculo",
    description=(
        "Generate a detailed price quote for a specific vehicle.\n\n"
        "WHEN_TO_USE: The customer has identified a vehicle of interest and wants "
        "to know the final price, available discounts, or accessory packages. "
        "Use after buscar_inventario has located the vehicle.\n\n"
        "CAPABILITIES:\n"
        "- Calculates precio_base, applicable descuentos, and precio_final.\n"
        "- Optionally includes accessory packages in the quote.\n"
        "- Can apply a specific financing plan to show adjusted pricing.\n"
        "- Returns quote validity date (vigencia).\n\n"
        "EXAMPLE:\n"
        '  Input:  {"vehiculo_id": "VH-4821", "incluir_accesorios": true}\n'
        '  Output: {"precio_base": 425000, "descuentos": 15000, "precio_final": 410000, ...}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "vehiculo_id": {
                "type": "string",
                "description": "Unique identifier of the vehicle to quote.",
            },
            "incluir_accesorios": {
                "type": "boolean",
                "description": "Whether to include accessory packages in the quote.",
            },
            "plan_financiamiento": {
                "type": "string",
                "description": "Financing plan to apply (e.g. Tradicional, Smart, Leasing).",
            },
        },
        "required": ["vehiculo_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "vehiculo_id": {"type": "string"},
            "precio_base": {"type": "number"},
            "descuentos": {"type": "number"},
            "accesorios": {"type": "number"},
            "precio_final": {"type": "number"},
            "moneda": {"type": "string"},
            "vigencia": {"type": "string"},
            "plan_financiamiento": {"type": "string"},
            "notas": {"type": "string"},
        },
    },
    domains=["automotive.sales"],
    category="automotive",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. consultar_financiamiento
# ---------------------------------------------------------------------------

consultar_financiamiento = ToolDefinition(
    name="consultar_financiamiento",
    description=(
        "Check available financing options for a given amount and term.\n\n"
        "WHEN_TO_USE: The customer asks about monthly payments, interest rates, "
        "down payment options, or financing plans. Typically used after cotizar_vehiculo "
        "has established the vehicle price.\n\n"
        "CAPABILITIES:\n"
        "- Returns one or more financing plans with tasa (interest rate), mensualidad "
        "(monthly payment), and CAT (total annual cost).\n"
        "- Supports different term lengths and down payment percentages.\n"
        "- Each plan includes a descriptive name and conditions.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"monto": 400000, "plazo_meses": 48, "enganche_porcentaje": 20}\n'
        '  Output: {"planes": [{"plan": "Tradicional", "tasa": 12.5, "mensualidad": 8450, ...}]}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "monto": {
                "type": "number",
                "description": "Total vehicle amount in MXN to finance.",
            },
            "plazo_meses": {
                "type": "integer",
                "description": "Financing term in months (e.g. 12, 24, 36, 48, 60, 72).",
            },
            "enganche_porcentaje": {
                "type": "number",
                "description": "Down payment as a percentage of the total amount (e.g. 20 for 20%).",
            },
        },
        "required": ["monto"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "monto_solicitado": {"type": "number"},
            "enganche": {"type": "number"},
            "monto_a_financiar": {"type": "number"},
            "planes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "plan": {"type": "string"},
                        "plazo_meses": {"type": "integer"},
                        "tasa": {"type": "number"},
                        "mensualidad": {"type": "number"},
                        "cat": {"type": "number"},
                        "total_a_pagar": {"type": "number"},
                    },
                },
            },
            "moneda": {"type": "string"},
        },
    },
    domains=["automotive.sales"],
    category="automotive",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. comparar_modelos
# ---------------------------------------------------------------------------

comparar_modelos = ToolDefinition(
    name="comparar_modelos",
    description=(
        "Compare two or more vehicle models side by side on selected criteria.\n\n"
        "WHEN_TO_USE: The customer is deciding between multiple vehicles and wants "
        "an objective comparison. Also useful when the agent proactively suggests "
        "alternatives.\n\n"
        "CAPABILITIES:\n"
        "- Accepts a list of model names and a list of comparison criteria.\n"
        "- Returns a structured comparison table with values for each criterion.\n"
        "- Default criteria: precio, rendimiento, equipamiento, garantia, espacio.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"modelos": ["Corolla", "Civic"], "criterios": ["precio", "rendimiento"]}\n'
        '  Output: {"comparacion": [{"modelo": "Corolla", "precio": 420000, ...}]}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "modelos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of model names to compare (2-5 models).",
            },
            "criterios": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Criteria for comparison (e.g. precio, rendimiento, equipamiento).",
            },
        },
        "required": ["modelos"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "comparacion": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "modelo": {"type": "string"},
                        "precio": {"type": "number"},
                        "rendimiento_km_l": {"type": "number"},
                        "garantia_anios": {"type": "integer"},
                        "calificacion_seguridad": {"type": "integer"},
                        "equipamiento": {"type": "string"},
                    },
                },
            },
            "recomendacion": {"type": "string"},
        },
    },
    domains=["automotive.sales"],
    category="automotive",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. consultar_crm
# ---------------------------------------------------------------------------

consultar_crm = ToolDefinition(
    name="consultar_crm",
    description=(
        "Look up a customer record in the CRM system.\n\n"
        "WHEN_TO_USE: The agent needs to identify a returning customer, check "
        "purchase history, verify contact details, or personalize the conversation "
        "with prior interaction data.\n\n"
        "CAPABILITIES:\n"
        "- Search by cliente_id, telefono, or email.\n"
        "- Returns customer profile including name, contact info, and interaction history.\n"
        "- Includes previous purchases and active quotes if available.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"telefono": "+52 5512345678"}\n'
        '  Output: {"cliente_id": "CL-2847", "nombre": "Carlos Pérez", ...}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "cliente_id": {
                "type": "string",
                "description": "Unique customer identifier in the CRM.",
            },
            "telefono": {
                "type": "string",
                "description": "Customer phone number.",
            },
            "email": {
                "type": "string",
                "description": "Customer email address.",
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "cliente_id": {"type": "string"},
            "nombre": {"type": "string"},
            "telefono": {"type": "string"},
            "email": {"type": "string"},
            "direccion": {"type": "string"},
            "historial_compras": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "vehiculo_id": {"type": "string"},
                        "modelo": {"type": "string"},
                        "fecha": {"type": "string"},
                        "precio_final": {"type": "number"},
                    },
                },
            },
            "cotizaciones_activas": {"type": "integer"},
            "ultima_interaccion": {"type": "string"},
        },
    },
    domains=["automotive.sales"],
    category="automotive",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

AUTOMOTIVE_TOOLS: list[ToolDefinition] = [
    buscar_inventario,
    cotizar_vehiculo,
    consultar_financiamiento,
    comparar_modelos,
    consultar_crm,
]

# ---------------------------------------------------------------------------
# Auto-registration into the default registry
# ---------------------------------------------------------------------------
# Access the module-level ``_default_registry`` directly to avoid a circular
# dependency: ``uncase.tools.__init__`` triggers this import *before*
# ``get_registry()`` is defined, but ``_default_registry`` is already
# instantiated at that point.

_registry = _tools_pkg._default_registry
for _tool in AUTOMOTIVE_TOOLS:
    if _tool.name not in _registry:
        _registry.register(_tool)
