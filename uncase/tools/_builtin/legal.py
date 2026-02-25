"""Built-in tool definitions for the **legal.advisory** domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. buscar_jurisprudencia
# ---------------------------------------------------------------------------

buscar_jurisprudencia = ToolDefinition(
    name="buscar_jurisprudencia",
    description=(
        "Search case law and judicial precedents by subject matter, court, and date range.\n\n"
        "WHEN_TO_USE: The client asks about prior court rulings, judicial criteria, "
        "binding precedents (jurisprudencia), or isolated theses related to their legal "
        "matter. Also useful when the advisor needs to support a legal argument with "
        "authoritative case law.\n\n"
        "CAPABILITIES:\n"
        "- Filter by search terms, subject matter (materia), court, and start date.\n"
        "- Returns matching precedents with case number, summary, and relevance score.\n"
        "- Supports partial searches (e.g. searching only by materia).\n"
        "- Results are ordered by relevance score descending.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"terminos": "despido injustificado", "materia": "laboral", '
        '"tribunal": "SCJN", "fecha_desde": "2023-01-01"}\n'
        '  Output: {"resultados": [{"expediente": "ADR-1234/2023", "materia": "laboral", '
        '"tribunal": "SCJN", "resumen": "...", "relevancia_score": 0.95}], "total_resultados": 3}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "terminos": {
                "type": "string",
                "description": "Free-text search terms describing the legal issue or topic.",
            },
            "materia": {
                "type": "string",
                "description": "Legal subject matter to filter by.",
                "enum": ["civil", "penal", "laboral", "mercantil", "administrativo", "familiar"],
            },
            "tribunal": {
                "type": "string",
                "description": "Name or abbreviation of the court (e.g. SCJN, TCC, tribunal colegiado).",
            },
            "fecha_desde": {
                "type": "string",
                "description": "Start date for the search range in ISO 8601 format (YYYY-MM-DD).",
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "expediente": {"type": "string"},
                        "materia": {"type": "string"},
                        "tribunal": {"type": "string"},
                        "fecha_resolucion": {"type": "string"},
                        "resumen": {"type": "string"},
                        "relevancia_score": {"type": "number"},
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["legal.advisory"],
    category="legal",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. consultar_expediente
# ---------------------------------------------------------------------------

consultar_expediente = ToolDefinition(
    name="consultar_expediente",
    description=(
        "Look up a specific case file by its identifier and retrieve its full status.\n\n"
        "WHEN_TO_USE: The client asks about the current status of their case, wants to "
        "know who the parties are, or needs details on recent court actions (actuaciones). "
        "Also used when the advisor needs to verify procedural state before recommending "
        "next steps.\n\n"
        "CAPABILITIES:\n"
        "- Retrieves case metadata: type, subject matter, court, procedural status, and parties.\n"
        "- Optionally includes the full timeline of court actions (actuaciones).\n"
        "- Returns start date and date of the most recent action.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"expediente_id": "EXP-2024/5678", "incluir_actuaciones": true}\n'
        '  Output: {"expediente_id": "EXP-2024/5678", "tipo_asunto": "juicio ordinario civil", '
        '"estado_procesal": "en instruccion", "partes": [{"nombre": "...", "rol": "actor"}], '
        '"actuaciones": [{"fecha": "2024-03-15", "tipo": "auto", "descripcion": "..."}]}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "expediente_id": {
                "type": "string",
                "description": "Unique case file identifier (e.g. EXP-2024/5678).",
            },
            "incluir_actuaciones": {
                "type": "boolean",
                "description": "Whether to include the full list of court actions in the response.",
            },
        },
        "required": ["expediente_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "expediente_id": {"type": "string"},
            "tipo_asunto": {"type": "string"},
            "materia": {"type": "string"},
            "juzgado": {"type": "string"},
            "estado_procesal": {"type": "string"},
            "partes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"},
                        "rol": {"type": "string"},
                    },
                },
            },
            "fecha_inicio": {"type": "string"},
            "ultima_actuacion": {"type": "string"},
            "actuaciones": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string"},
                        "tipo": {"type": "string"},
                        "descripcion": {"type": "string"},
                    },
                },
            },
        },
    },
    domains=["legal.advisory"],
    category="legal",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. verificar_plazos
# ---------------------------------------------------------------------------

verificar_plazos = ToolDefinition(
    name="verificar_plazos",
    description=(
        "Calculate and verify legal deadlines for a given procedural action.\n\n"
        "WHEN_TO_USE: The client or advisor needs to know the remaining time to file "
        "a motion, appeal, or any procedural action. Critical when a notification has "
        "been received and the clock is ticking on a legal deadline. Also useful for "
        "proactive alerts about upcoming or expired deadlines.\n\n"
        "CAPABILITIES:\n"
        "- Calculates the deadline date and remaining days based on notification date and action type.\n"
        "- Provides the legal basis (fundamentacion_legal) for the computed deadline.\n"
        "- Returns an alert status: vigente, proximo_a_vencer, or vencido.\n"
        "- Accounts for subject matter-specific deadline rules.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"expediente_id": "EXP-2024/5678", "tipo_accion": "apelacion", '
        '"fecha_notificacion": "2024-06-01", "materia": "civil"}\n'
        '  Output: {"tipo_accion": "apelacion", "plazo_dias": 9, "fecha_limite": "2024-06-12", '
        '"dias_restantes": 5, "fundamentacion_legal": "Art. 691 CPCDF", "alerta": "proximo_a_vencer"}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "expediente_id": {
                "type": "string",
                "description": "Case file identifier for context (e.g. EXP-2024/5678).",
            },
            "tipo_accion": {
                "type": "string",
                "description": "Type of procedural action (e.g. apelacion, contestacion, amparo, recurso de revision).",
            },
            "fecha_notificacion": {
                "type": "string",
                "description": "Date the notification was received, in ISO 8601 format (YYYY-MM-DD).",
            },
            "materia": {
                "type": "string",
                "description": "Legal subject matter for deadline calculation rules.",
                "enum": ["civil", "penal", "laboral", "mercantil", "administrativo", "familiar"],
            },
        },
        "required": ["tipo_accion", "fecha_notificacion"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "tipo_accion": {"type": "string"},
            "plazo_dias": {"type": "integer"},
            "fecha_limite": {"type": "string"},
            "dias_restantes": {"type": "integer"},
            "fundamentacion_legal": {"type": "string"},
            "alerta": {
                "type": "string",
                "enum": ["vigente", "proximo_a_vencer", "vencido"],
            },
        },
    },
    domains=["legal.advisory"],
    category="legal",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. buscar_legislacion
# ---------------------------------------------------------------------------

buscar_legislacion = ToolDefinition(
    name="buscar_legislacion",
    description=(
        "Search statutes, codes, and legislation by keywords, specific law name, or article number.\n\n"
        "WHEN_TO_USE: The client asks about what the law says on a particular topic, "
        "the advisor needs to cite a specific article, or a legal argument requires "
        "the exact text of a statutory provision. Also useful to check if legislation "
        "is still in force (vigente) or has been reformed.\n\n"
        "CAPABILITIES:\n"
        "- Search by free-text terms, specific law name, article number, or subject matter.\n"
        "- Returns the full text of matching articles along with publication date and reform history.\n"
        "- Indicates whether each article is currently in force (vigente).\n"
        "- Supports combined filters for precise lookups.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"ley": "Codigo Civil Federal", "articulo": "1916", "materia": "civil"}\n'
        '  Output: {"resultados": [{"ley": "Codigo Civil Federal", "articulo": "1916", '
        '"titulo": "Del dano moral", "texto": "...", "vigente": true}], "total_resultados": 1}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "terminos": {
                "type": "string",
                "description": "Free-text search terms describing the legal topic or concept.",
            },
            "ley": {
                "type": "string",
                "description": "Name of the specific law or code (e.g. Codigo Civil Federal, Ley Federal del Trabajo).",
            },
            "articulo": {
                "type": "string",
                "description": "Specific article number to look up (e.g. 123, 1916 Bis).",
            },
            "materia": {
                "type": "string",
                "description": "Legal subject matter to filter by.",
                "enum": ["civil", "penal", "laboral", "mercantil", "administrativo", "familiar"],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ley": {"type": "string"},
                        "articulo": {"type": "string"},
                        "titulo": {"type": "string"},
                        "texto": {"type": "string"},
                        "fecha_publicacion": {"type": "string"},
                        "vigente": {"type": "boolean"},
                        "ultima_reforma": {"type": "string"},
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["legal.advisory"],
    category="legal",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. calcular_honorarios
# ---------------------------------------------------------------------------

calcular_honorarios = ToolDefinition(
    name="calcular_honorarios",
    description=(
        "Estimate legal fees for a given type of service, subject matter, and case complexity.\n\n"
        "WHEN_TO_USE: The client asks how much legal representation or a specific service "
        "will cost. Also useful when the advisor needs to provide a transparent fee "
        "breakdown before engagement, or when comparing service costs across different "
        "legal matters.\n\n"
        "CAPABILITIES:\n"
        "- Calculates base fees, percentage surcharges based on case value (cuantia), and total with tax.\n"
        "- Adjusts estimates according to complexity level (baja, media, alta).\n"
        "- Provides the legal or professional basis for the fee calculation (fundamentacion).\n"
        "- Returns a detailed breakdown including IVA and additional notes.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"tipo_servicio": "juicio", "materia": "mercantil", '
        '"cuantia": 500000, "complejidad": "alta"}\n'
        '  Output: {"tipo_servicio": "juicio", "honorarios_base": 45000, '
        '"cuota_adicional_porcentaje": 10, "honorarios_estimados": 95000, '
        '"iva": 15200, "total_con_iva": 110200, "moneda": "MXN", ...}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "tipo_servicio": {
                "type": "string",
                "description": "Type of legal service requested.",
                "enum": ["consulta", "juicio", "amparo", "contrato", "mediacion", "arbitraje"],
            },
            "materia": {
                "type": "string",
                "description": "Legal subject matter for the service.",
                "enum": ["civil", "penal", "laboral", "mercantil", "administrativo", "familiar"],
            },
            "cuantia": {
                "type": "number",
                "description": "Monetary value of the case or matter in MXN, used to calculate percentage-based fees.",
            },
            "complejidad": {
                "type": "string",
                "description": "Estimated complexity level of the case, affects fee multiplier.",
                "enum": ["baja", "media", "alta"],
            },
        },
        "required": ["tipo_servicio", "materia"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "tipo_servicio": {"type": "string"},
            "honorarios_base": {"type": "number"},
            "cuota_adicional_porcentaje": {"type": "number"},
            "honorarios_estimados": {"type": "number"},
            "iva": {"type": "number"},
            "total_con_iva": {"type": "number"},
            "moneda": {"type": "string"},
            "notas": {"type": "string"},
            "fundamentacion": {"type": "string"},
        },
    },
    domains=["legal.advisory"],
    category="legal",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

LEGAL_TOOLS: list[ToolDefinition] = [
    buscar_jurisprudencia,
    consultar_expediente,
    verificar_plazos,
    buscar_legislacion,
    calcular_honorarios,
]
