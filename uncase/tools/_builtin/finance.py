"""Built-in tool definitions for the **finance.advisory** domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. consultar_portafolio
# ---------------------------------------------------------------------------

consultar_portafolio = ToolDefinition(
    name="consultar_portafolio",
    description=(
        "Look up a client's investment portfolio with current positions and performance.\n\n"
        "WHEN_TO_USE: The advisor needs to review a client's current holdings before "
        "making recommendations, the client asks about their portfolio performance, or "
        "a rebalancing analysis is needed.\n\n"
        "CAPABILITIES:\n"
        "- Filter by asset type: acciones, bonos, fondos, etf, or todos.\n"
        "- Returns each position with current price, total value, and return percentage.\n"
        "- Calculates total portfolio value and global return.\n"
        "- Includes the consultation timestamp.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"cliente_id": "CLI-4820", "tipo_activo": "acciones"}\n'
        '  Output: {"cliente_id": "CLI-4820", "portafolio": [{"activo_id": "AMZN", '
        '"nombre": "Amazon", "tipo": "acciones", "cantidad": 15, "precio_actual": 185.40, '
        '"valor_total": 2781.0, "rendimiento_porcentaje": 12.5}], '
        '"valor_total_portafolio": 2781.0, "rendimiento_global": 12.5}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "cliente_id": {
                "type": "string",
                "description": "Unique client identifier in the financial system.",
            },
            "tipo_activo": {
                "type": "string",
                "description": "Asset type to filter by.",
                "enum": ["acciones", "bonos", "fondos", "etf", "todos"],
            },
        },
        "required": ["cliente_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "cliente_id": {"type": "string"},
            "nombre_cliente": {"type": "string"},
            "portafolio": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "activo_id": {"type": "string"},
                        "nombre": {"type": "string"},
                        "tipo": {"type": "string"},
                        "cantidad": {"type": "number"},
                        "precio_actual": {"type": "number"},
                        "valor_total": {"type": "number"},
                        "rendimiento_porcentaje": {"type": "number"},
                        "moneda": {"type": "string"},
                    },
                },
            },
            "valor_total_portafolio": {"type": "number"},
            "rendimiento_global": {"type": "number"},
            "fecha_consulta": {"type": "string"},
        },
    },
    domains=["finance.advisory"],
    category="finance",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. analizar_riesgo
# ---------------------------------------------------------------------------

analizar_riesgo = ToolDefinition(
    name="analizar_riesgo",
    description=(
        "Perform a risk analysis and generate an asset allocation recommendation.\n\n"
        "WHEN_TO_USE: The client wants to invest a specific amount and needs a risk "
        "assessment, the advisor is building an investment proposal, or a periodic "
        "portfolio review requires updated risk metrics.\n\n"
        "CAPABILITIES:\n"
        "- Calculates risk score, Value-at-Risk (95%), and maximum drawdown.\n"
        "- Suggests asset allocation based on the investment profile.\n"
        "- Provides actionable recommendations.\n"
        "- Supports conservative, moderate, and aggressive profiles.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"perfil_inversion": "moderado", "monto_inversion": 500000, '
        '"horizonte_meses": 36}\n'
        '  Output: {"perfil_riesgo": "moderado", "score_riesgo": 5.2, '
        '"var_95": 42500, "distribucion_sugerida": {"renta_fija": 40, '
        '"renta_variable": 45, "alternativas": 10, "liquidez": 5}}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "cliente_id": {
                "type": "string",
                "description": "Client identifier for personalized analysis.",
            },
            "perfil_inversion": {
                "type": "string",
                "description": "Investment risk profile.",
                "enum": ["conservador", "moderado", "agresivo"],
            },
            "monto_inversion": {
                "type": "number",
                "description": "Total amount to invest in MXN.",
            },
            "horizonte_meses": {
                "type": "integer",
                "description": "Investment time horizon in months.",
            },
        },
        "required": ["perfil_inversion", "monto_inversion"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "perfil_riesgo": {"type": "string"},
            "score_riesgo": {"type": "number"},
            "var_95": {"type": "number"},
            "max_drawdown": {"type": "number"},
            "recomendaciones": {
                "type": "array",
                "items": {"type": "string"},
            },
            "distribucion_sugerida": {
                "type": "object",
                "properties": {
                    "renta_fija": {"type": "number"},
                    "renta_variable": {"type": "number"},
                    "alternativas": {"type": "number"},
                    "liquidez": {"type": "number"},
                },
            },
            "disclaimer": {"type": "string"},
        },
    },
    domains=["finance.advisory"],
    category="finance",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. consultar_mercado
# ---------------------------------------------------------------------------

consultar_mercado = ToolDefinition(
    name="consultar_mercado",
    description=(
        "Query real-time market data for a specific financial instrument.\n\n"
        "WHEN_TO_USE: The client asks about current prices, the advisor needs market "
        "data to support a recommendation, or a comparison of instruments is required.\n\n"
        "CAPABILITIES:\n"
        "- Returns current price, daily change, volume, and 52-week range.\n"
        "- Includes key indicators: P/E ratio, dividend yield, and market cap.\n"
        "- Supports BMV, NYSE, NASDAQ, and crypto markets.\n"
        "- Data types: real-time price, historical, or technical indicators.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"simbolo": "AMXL", "mercado": "bmv", "tipo_dato": "precio"}\n'
        '  Output: {"simbolo": "AMXL", "nombre": "América Móvil", "mercado": "bmv", '
        '"precio_actual": 14.85, "cambio_porcentaje": 1.23, "volumen": 15420000}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "simbolo": {
                "type": "string",
                "description": "Ticker symbol of the financial instrument.",
            },
            "mercado": {
                "type": "string",
                "description": "Market exchange.",
                "enum": ["bmv", "nyse", "nasdaq", "crypto"],
            },
            "tipo_dato": {
                "type": "string",
                "description": "Type of data to retrieve.",
                "enum": ["precio", "historico", "indicadores"],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "simbolo": {"type": "string"},
            "nombre": {"type": "string"},
            "mercado": {"type": "string"},
            "precio_actual": {"type": "number"},
            "cambio_porcentaje": {"type": "number"},
            "volumen": {"type": "integer"},
            "maximo_52s": {"type": "number"},
            "minimo_52s": {"type": "number"},
            "indicadores": {
                "type": "object",
                "properties": {
                    "pe_ratio": {"type": "number"},
                    "dividend_yield": {"type": "number"},
                    "market_cap": {"type": "number"},
                },
            },
            "ultima_actualizacion": {"type": "string"},
        },
    },
    domains=["finance.advisory"],
    category="finance",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. verificar_cumplimiento
# ---------------------------------------------------------------------------

verificar_cumplimiento = ToolDefinition(
    name="verificar_cumplimiento",
    description=(
        "Check regulatory compliance (KYC/AML) for a client operation.\n\n"
        "WHEN_TO_USE: Before processing a new account opening, investment order, "
        "international transfer, or profile change. Required by regulations for "
        "any significant financial operation.\n\n"
        "CAPABILITIES:\n"
        "- Verifies KYC (Know Your Customer) and PLD (anti-money laundering) status.\n"
        "- Returns risk level classification and pending documents.\n"
        "- Lists applicable regulations and whether authorization is required.\n"
        "- Flags any compliance alerts.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"cliente_id": "CLI-4820", "tipo_operacion": "inversion", '
        '"monto": 250000}\n'
        '  Output: {"cumple_kyc": true, "cumple_pld": true, '
        '"nivel_riesgo_pld": "bajo", "documentos_pendientes": [], '
        '"requiere_autorizacion": false}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "cliente_id": {
                "type": "string",
                "description": "Unique client identifier.",
            },
            "tipo_operacion": {
                "type": "string",
                "description": "Type of financial operation to verify.",
                "enum": [
                    "apertura_cuenta",
                    "inversion",
                    "transferencia_internacional",
                    "cambio_perfil",
                ],
            },
            "monto": {
                "type": "number",
                "description": "Operation amount in MXN for threshold evaluation.",
            },
        },
        "required": ["cliente_id", "tipo_operacion"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "cliente_id": {"type": "string"},
            "tipo_operacion": {"type": "string"},
            "cumple_kyc": {"type": "boolean"},
            "cumple_pld": {"type": "boolean"},
            "nivel_riesgo_pld": {
                "type": "string",
                "enum": ["bajo", "medio", "alto"],
            },
            "documentos_pendientes": {
                "type": "array",
                "items": {"type": "string"},
            },
            "alertas": {
                "type": "array",
                "items": {"type": "string"},
            },
            "requiere_autorizacion": {"type": "boolean"},
            "normativa_aplicable": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    },
    domains=["finance.advisory"],
    category="finance",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. simular_inversion
# ---------------------------------------------------------------------------

simular_inversion = ToolDefinition(
    name="simular_inversion",
    description=(
        "Simulate an investment over time with multiple scenarios.\n\n"
        "WHEN_TO_USE: The client wants to understand potential returns before committing, "
        "the advisor needs to illustrate different outcomes, or a financial plan requires "
        "projections for goal-based investing.\n\n"
        "CAPABILITIES:\n"
        "- Projects three scenarios: pessimistic, base, and optimistic.\n"
        "- Accounts for monthly contributions and estimated commissions.\n"
        "- Adjusts for inflation to show real purchasing power.\n"
        "- Supports conservative, moderate, and aggressive profiles.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"monto_inicial": 100000, "aportacion_mensual": 5000, '
        '"plazo_meses": 60, "perfil": "moderado"}\n'
        '  Output: {"escenarios": {"base": {"rendimiento_anual": 9.5, '
        '"monto_final": 524800, "ganancia": 124800}}, '
        '"poder_adquisitivo_real": 448200}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "monto_inicial": {
                "type": "number",
                "description": "Initial investment amount in MXN.",
            },
            "aportacion_mensual": {
                "type": "number",
                "description": "Monthly contribution amount in MXN.",
            },
            "plazo_meses": {
                "type": "integer",
                "description": "Investment term in months.",
            },
            "perfil": {
                "type": "string",
                "description": "Investment profile for return estimation.",
                "enum": ["conservador", "moderado", "agresivo"],
            },
            "instrumento": {
                "type": "string",
                "description": "Specific instrument to simulate (optional).",
            },
        },
        "required": ["monto_inicial", "plazo_meses", "perfil"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "monto_inicial": {"type": "number"},
            "aportacion_mensual": {"type": "number"},
            "plazo_meses": {"type": "integer"},
            "escenarios": {
                "type": "object",
                "properties": {
                    "pesimista": {
                        "type": "object",
                        "properties": {
                            "rendimiento_anual": {"type": "number"},
                            "monto_final": {"type": "number"},
                            "ganancia": {"type": "number"},
                            "rendimiento_total_porcentaje": {"type": "number"},
                        },
                    },
                    "base": {
                        "type": "object",
                        "properties": {
                            "rendimiento_anual": {"type": "number"},
                            "monto_final": {"type": "number"},
                            "ganancia": {"type": "number"},
                            "rendimiento_total_porcentaje": {"type": "number"},
                        },
                    },
                    "optimista": {
                        "type": "object",
                        "properties": {
                            "rendimiento_anual": {"type": "number"},
                            "monto_final": {"type": "number"},
                            "ganancia": {"type": "number"},
                            "rendimiento_total_porcentaje": {"type": "number"},
                        },
                    },
                },
            },
            "comisiones_estimadas": {"type": "number"},
            "inflacion_estimada": {"type": "number"},
            "poder_adquisitivo_real": {"type": "number"},
            "disclaimer": {"type": "string"},
        },
    },
    domains=["finance.advisory"],
    category="finance",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

FINANCE_TOOLS: list[ToolDefinition] = [
    consultar_portafolio,
    analizar_riesgo,
    consultar_mercado,
    verificar_cumplimiento,
    simular_inversion,
]
