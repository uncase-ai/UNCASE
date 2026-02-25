"""Built-in tool definitions for the **industrial.support** domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. diagnosticar_equipo
# ---------------------------------------------------------------------------

diagnosticar_equipo = ToolDefinition(
    name="diagnosticar_equipo",
    description=(
        "Run diagnostics on industrial equipment to identify faults and recommend actions.\n\n"
        "WHEN_TO_USE: An operator reports a malfunction, an error code appears on the "
        "control panel, a technician needs to assess equipment before maintenance, or "
        "predictive monitoring flags an anomaly.\n\n"
        "CAPABILITIES:\n"
        "- Diagnoses by symptom description, error code, or subsystem.\n"
        "- Returns fault code, severity, probable cause, and affected subsystem.\n"
        "- Recommends specific corrective actions with time estimates.\n"
        "- Indicates whether a production stop is required.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"equipo_id": "EQ-2201", "codigo_error": "E-4415", '
        '"subsistema": "hidraulico"}\n'
        '  Output: {"equipo_id": "EQ-2201", "diagnostico": {"codigo_falla": "HYD-F12", '
        '"severidad": "mayor", "causa_probable": "Fuga en cilindro principal"}, '
        '"requiere_paro": true}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "equipo_id": {
                "type": "string",
                "description": "Unique equipment identifier.",
            },
            "sintoma": {
                "type": "string",
                "description": "Symptom description reported by the operator.",
            },
            "codigo_error": {
                "type": "string",
                "description": "Error code displayed by the equipment.",
            },
            "subsistema": {
                "type": "string",
                "description": "Equipment subsystem to diagnose.",
                "enum": ["mecanico", "electrico", "hidraulico", "neumatico", "control"],
            },
        },
        "required": ["equipo_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "equipo_id": {"type": "string"},
            "modelo": {"type": "string"},
            "ubicacion": {"type": "string"},
            "diagnostico": {
                "type": "object",
                "properties": {
                    "codigo_falla": {"type": "string"},
                    "descripcion": {"type": "string"},
                    "severidad": {
                        "type": "string",
                        "enum": ["critico", "mayor", "menor", "informativo"],
                    },
                    "causa_probable": {"type": "string"},
                    "subsistema_afectado": {"type": "string"},
                },
            },
            "acciones_recomendadas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "accion": {"type": "string"},
                        "prioridad": {"type": "string"},
                        "tiempo_estimado_horas": {"type": "number"},
                    },
                },
            },
            "requiere_paro": {"type": "boolean"},
            "historial_fallas_similares": {"type": "integer"},
        },
    },
    domains=["industrial.support"],
    category="industrial",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. consultar_inventario_partes
# ---------------------------------------------------------------------------

consultar_inventario_partes = ToolDefinition(
    name="consultar_inventario_partes",
    description=(
        "Search the spare parts inventory by part number, description, or compatible equipment.\n\n"
        "WHEN_TO_USE: A technician needs a replacement part for maintenance, the support "
        "agent is checking part availability before scheduling work, or an inventory "
        "review is needed to plan procurement.\n\n"
        "CAPABILITIES:\n"
        "- Search by part number, description keyword, or compatible equipment.\n"
        "- Filter by category: mecanica, electrica, hidraulica, consumibles, seguridad.\n"
        "- Returns stock levels, warehouse location, pricing, and lead times.\n"
        "- Shows compatible equipment for each part.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"equipo_compatible": "EQ-2201", "categoria": "hidraulica"}\n'
        '  Output: {"partes": [{"numero_parte": "HYD-CYL-045", '
        '"descripcion": "Cilindro hidráulico principal", "cantidad_disponible": 3, '
        '"ubicacion_almacen": "A-12-03", "precio_unitario": 28500}], '
        '"total_resultados": 1}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "numero_parte": {
                "type": "string",
                "description": "Part number to search for.",
            },
            "descripcion": {
                "type": "string",
                "description": "Keyword in part description.",
            },
            "equipo_compatible": {
                "type": "string",
                "description": "Equipment ID to find compatible parts.",
            },
            "categoria": {
                "type": "string",
                "description": "Part category.",
                "enum": ["mecanica", "electrica", "hidraulica", "consumibles", "seguridad"],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "partes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "numero_parte": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "categoria": {"type": "string"},
                        "cantidad_disponible": {"type": "integer"},
                        "ubicacion_almacen": {"type": "string"},
                        "precio_unitario": {"type": "number"},
                        "proveedor": {"type": "string"},
                        "tiempo_reposicion_dias": {"type": "integer"},
                        "equipo_compatible": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["industrial.support"],
    category="industrial",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. programar_mantenimiento
# ---------------------------------------------------------------------------

programar_mantenimiento = ToolDefinition(
    name="programar_mantenimiento",
    description=(
        "Schedule a maintenance work order for equipment.\n\n"
        "WHEN_TO_USE: Preventive maintenance is due, a diagnostic indicates corrective "
        "action is needed, predictive analytics suggest upcoming failure, or the operator "
        "requests a maintenance intervention.\n\n"
        "CAPABILITIES:\n"
        "- Supports preventive, corrective, and predictive maintenance types.\n"
        "- Assigns a technician and estimates duration and cost.\n"
        "- Lists required spare parts with quantities.\n"
        "- Returns a work order ID for tracking.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"equipo_id": "EQ-2201", "tipo_mantenimiento": "correctivo", '
        '"prioridad": "alta", "descripcion_trabajo": "Reemplazo cilindro hidráulico"}\n'
        '  Output: {"orden_id": "OM-44821", "fecha_programada": "2026-02-27", '
        '"tecnico_asignado": "Ing. Torres", "duracion_estimada_horas": 6, '
        '"costo_estimado": 45200}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "equipo_id": {
                "type": "string",
                "description": "Unique equipment identifier.",
            },
            "tipo_mantenimiento": {
                "type": "string",
                "description": "Type of maintenance.",
                "enum": ["preventivo", "correctivo", "predictivo"],
            },
            "prioridad": {
                "type": "string",
                "description": "Priority level.",
                "enum": ["critica", "alta", "media", "baja"],
            },
            "fecha_sugerida": {
                "type": "string",
                "description": "Suggested date (ISO 8601 YYYY-MM-DD).",
            },
            "descripcion_trabajo": {
                "type": "string",
                "description": "Description of the work to be performed.",
            },
        },
        "required": ["equipo_id", "tipo_mantenimiento"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "orden_id": {"type": "string"},
            "equipo_id": {"type": "string"},
            "tipo_mantenimiento": {"type": "string"},
            "fecha_programada": {"type": "string"},
            "tecnico_asignado": {"type": "string"},
            "duracion_estimada_horas": {"type": "number"},
            "partes_requeridas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "numero_parte": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "cantidad": {"type": "integer"},
                    },
                },
            },
            "estatus": {"type": "string"},
            "costo_estimado": {"type": "number"},
        },
    },
    domains=["industrial.support"],
    category="industrial",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. buscar_manual_tecnico
# ---------------------------------------------------------------------------

buscar_manual_tecnico = ToolDefinition(
    name="buscar_manual_tecnico",
    description=(
        "Search technical documentation, manuals, and diagrams for equipment.\n\n"
        "WHEN_TO_USE: A technician needs operating procedures, the support agent "
        "looks up troubleshooting steps, safety procedures must be consulted, or "
        "a technical specification is required for decision-making.\n\n"
        "CAPABILITIES:\n"
        "- Search by equipment ID, keywords, or document type.\n"
        "- Supports manual types: operation, maintenance, diagrams, datasheets, safety.\n"
        "- Returns relevant document sections with summaries.\n"
        "- Includes revision dates and available languages.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"equipo_id": "EQ-2201", "tipo_documento": "manual_mantenimiento", '
        '"terminos": "cilindro hidráulico"}\n'
        '  Output: {"documentos": [{"documento_id": "DOC-M2201-03", '
        '"titulo": "Manual de mantenimiento - Prensa hidráulica HYD-500", '
        '"seccion": "5.3 Reemplazo de cilindros", '
        '"contenido_resumen": "Procedimiento paso a paso para..."}], '
        '"total_resultados": 1}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "equipo_id": {
                "type": "string",
                "description": "Equipment ID to find related documentation.",
            },
            "terminos": {
                "type": "string",
                "description": "Search keywords.",
            },
            "tipo_documento": {
                "type": "string",
                "description": "Type of technical document.",
                "enum": [
                    "manual_operacion",
                    "manual_mantenimiento",
                    "diagrama",
                    "ficha_tecnica",
                    "procedimiento_seguridad",
                ],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "documentos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "documento_id": {"type": "string"},
                        "titulo": {"type": "string"},
                        "tipo": {"type": "string"},
                        "equipo": {"type": "string"},
                        "seccion": {"type": "string"},
                        "contenido_resumen": {"type": "string"},
                        "pagina": {"type": "integer"},
                        "fecha_revision": {"type": "string"},
                        "idioma": {"type": "string"},
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["industrial.support"],
    category="industrial",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. registrar_incidencia
# ---------------------------------------------------------------------------

registrar_incidencia = ToolDefinition(
    name="registrar_incidencia",
    description=(
        "Register a safety incident or near-miss event in the EHS system.\n\n"
        "WHEN_TO_USE: An accident occurs, a near-miss is reported, an unsafe condition "
        "is detected, or an unsafe act is witnessed. Required by ISO 45001 and "
        "local safety regulations.\n\n"
        "CAPABILITIES:\n"
        "- Classifies incidents: accident, near-miss, unsafe condition, unsafe act.\n"
        "- Assesses potential severity: catastrophic, critical, marginal, negligible.\n"
        "- Generates immediate action recommendations.\n"
        "- Triggers notifications to safety personnel.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"tipo_incidencia": "cuasi_accidente", "area": "Línea de prensado", '
        '"descripcion": "Fuga de aceite hidráulico cerca de pasillo de tránsito", '
        '"severidad_potencial": "critica"}\n'
        '  Output: {"incidencia_id": "INC-8812", "investigacion_requerida": true, '
        '"acciones_inmediatas": ["Acordonar área", "Contener derrame"], '
        '"plazo_cierre_dias": 5}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "tipo_incidencia": {
                "type": "string",
                "description": "Type of safety incident.",
                "enum": [
                    "accidente",
                    "cuasi_accidente",
                    "condicion_insegura",
                    "acto_inseguro",
                ],
            },
            "area": {
                "type": "string",
                "description": "Plant area where the incident occurred.",
            },
            "descripcion": {
                "type": "string",
                "description": "Detailed description of the incident.",
            },
            "severidad_potencial": {
                "type": "string",
                "description": "Potential severity of the incident.",
                "enum": ["catastrofica", "critica", "marginal", "despreciable"],
            },
            "personas_involucradas": {
                "type": "integer",
                "description": "Number of people involved.",
            },
        },
        "required": ["tipo_incidencia", "area", "descripcion"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "incidencia_id": {"type": "string"},
            "fecha_registro": {"type": "string"},
            "tipo_incidencia": {"type": "string"},
            "area": {"type": "string"},
            "severidad_potencial": {"type": "string"},
            "acciones_inmediatas": {
                "type": "array",
                "items": {"type": "string"},
            },
            "investigacion_requerida": {"type": "boolean"},
            "notificaciones_enviadas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "destinatario": {"type": "string"},
                        "medio": {"type": "string"},
                    },
                },
            },
            "plazo_cierre_dias": {"type": "integer"},
            "normativa_aplicable": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    },
    domains=["industrial.support"],
    category="industrial",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

INDUSTRIAL_TOOLS: list[ToolDefinition] = [
    diagnosticar_equipo,
    consultar_inventario_partes,
    programar_mantenimiento,
    buscar_manual_tecnico,
    registrar_incidencia,
]

