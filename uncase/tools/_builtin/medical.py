"""Built-in tool definitions for the **medical.consultation** domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. consultar_historial_medico
# ---------------------------------------------------------------------------

consultar_historial_medico = ToolDefinition(
    name="consultar_historial_medico",
    description=(
        "Look up a patient's medical history including past consultations, "
        "studies, prescriptions, allergies, and current medications.\n\n"
        "WHEN_TO_USE: The physician needs to review a patient's background "
        "before a consultation, check previous diagnoses, verify known allergies, "
        "or review current medication before prescribing. Essential at the start "
        "of any medical encounter to ensure continuity of care.\n\n"
        "CAPABILITIES:\n"
        "- Filter history records by type: consultas, estudios, recetas, or todos.\n"
        "- Returns chronological history entries with CIE-10 diagnosis codes.\n"
        "- Includes active allergies and current medication lists.\n"
        "- Each record shows the attending physician and date.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"paciente_id": "PAC-10234", "tipo_registro": "consultas"}\n'
        '  Output: {"paciente_id": "PAC-10234", "nombre": "María López", '
        '"historial": [{"fecha": "2025-11-15", "tipo": "consulta", '
        '"descripcion": "Control diabetes tipo 2", "medico": "Dr. Ramírez", '
        '"diagnostico_cie10": "E11.9"}], "alergias": ["penicilina"], '
        '"medicamentos_actuales": ["metformina 850mg"]}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "paciente_id": {
                "type": "string",
                "description": "Unique patient identifier in the medical system.",
            },
            "tipo_registro": {
                "type": "string",
                "description": "Type of medical record to retrieve.",
                "enum": ["consultas", "estudios", "recetas", "todos"],
            },
        },
        "required": ["paciente_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "paciente_id": {"type": "string"},
            "nombre": {"type": "string"},
            "historial": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string"},
                        "tipo": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "medico": {"type": "string"},
                        "diagnostico_cie10": {"type": "string"},
                    },
                },
            },
            "alergias": {
                "type": "array",
                "items": {"type": "string"},
            },
            "medicamentos_actuales": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    },
    domains=["medical.consultation"],
    category="medical",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. buscar_medicamentos
# ---------------------------------------------------------------------------

buscar_medicamentos = ToolDefinition(
    name="buscar_medicamentos",
    description=(
        "Search the medication database by commercial name, active ingredient, "
        "or route of administration.\n\n"
        "WHEN_TO_USE: The physician needs to look up a drug to prescribe, verify "
        "contraindications before prescribing, check available presentations, or "
        "find alternative medications with the same active ingredient.\n\n"
        "CAPABILITIES:\n"
        "- Search by commercial name, active ingredient, or administration route.\n"
        "- Returns matching medications with full details including contraindications.\n"
        "- Lists known drug interactions for each result.\n"
        "- Supports partial name matching for flexible searches.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"nombre": "metformina", "via_administracion": "oral"}\n'
        '  Output: {"medicamentos": [{"nombre_comercial": "Glucophage", '
        '"principio_activo": "metformina", "presentacion": "tabletas 850mg x 30", '
        '"contraindicaciones": "insuficiencia renal severa", '
        '"interacciones": ["alcohol", "medios de contraste yodados"]}], '
        '"total_resultados": 1}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "Commercial or generic medication name to search for.",
            },
            "principio_activo": {
                "type": "string",
                "description": "Active pharmaceutical ingredient (e.g. metformina, omeprazol).",
            },
            "via_administracion": {
                "type": "string",
                "description": "Route of administration to filter by.",
                "enum": ["oral", "intravenosa", "topica", "inhalada", "subcutanea"],
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "medicamentos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nombre_comercial": {"type": "string"},
                        "principio_activo": {"type": "string"},
                        "presentacion": {"type": "string"},
                        "via_administracion": {"type": "string"},
                        "contraindicaciones": {"type": "string"},
                        "interacciones": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["medical.consultation"],
    category="medical",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. agendar_cita
# ---------------------------------------------------------------------------

agendar_cita = ToolDefinition(
    name="agendar_cita",
    description=(
        "Schedule a medical appointment for a patient with a specific specialty.\n\n"
        "WHEN_TO_USE: The physician refers the patient to a specialist, the patient "
        "requests a follow-up appointment, or the consultation concludes with a need "
        "for a subsequent visit.\n\n"
        "CAPABILITIES:\n"
        "- Schedule appointments by specialty or specific physician.\n"
        "- Supports urgency levels: rutina, urgente, or seguimiento.\n"
        "- Returns confirmed date, time, office location, and pre-appointment instructions.\n"
        "- Automatically finds the next available slot when no preferred date is given.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"paciente_id": "PAC-10234", "especialidad": "cardiología", '
        '"urgencia": "seguimiento"}\n'
        '  Output: {"cita_id": "CIT-88412", "medico": "Dra. Fernanda Ríos", '
        '"fecha_hora": "2026-03-10T10:30:00", "consultorio": "204-B", '
        '"estatus": "confirmada"}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "paciente_id": {
                "type": "string",
                "description": "Unique patient identifier.",
            },
            "especialidad": {
                "type": "string",
                "description": "Medical specialty for the appointment.",
            },
            "medico_id": {
                "type": "string",
                "description": "Specific physician identifier, if preferred.",
            },
            "fecha_preferida": {
                "type": "string",
                "description": "Preferred date (ISO 8601 format YYYY-MM-DD).",
            },
            "urgencia": {
                "type": "string",
                "description": "Urgency level of the appointment.",
                "enum": ["rutina", "urgente", "seguimiento"],
            },
        },
        "required": ["paciente_id", "especialidad"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "cita_id": {"type": "string"},
            "paciente_id": {"type": "string"},
            "medico": {"type": "string"},
            "especialidad": {"type": "string"},
            "fecha_hora": {"type": "string"},
            "consultorio": {"type": "string"},
            "instrucciones_previas": {"type": "string"},
            "estatus": {"type": "string"},
        },
    },
    domains=["medical.consultation"],
    category="medical",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. consultar_resultados_lab
# ---------------------------------------------------------------------------

consultar_resultados_lab = ToolDefinition(
    name="consultar_resultados_lab",
    description=(
        "Retrieve laboratory and diagnostic study results for a patient.\n\n"
        "WHEN_TO_USE: The physician needs to review lab results during a consultation, "
        "check whether pending studies are ready, or verify if any parameter is outside "
        "the reference range. Critical for informed clinical decisions.\n\n"
        "CAPABILITIES:\n"
        "- Filter by specific study ID, date range, or study type.\n"
        "- Returns detailed parameters with values, units, and reference ranges.\n"
        "- Flags out-of-range values with a boolean indicator.\n"
        "- Supports blood work, urinalysis, imaging, biopsy, and other study types.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"paciente_id": "PAC-10234", "tipo_estudio": "sangre"}\n'
        '  Output: {"resultados": [{"estudio_id": "LAB-55210", "tipo": "sangre", '
        '"parametros": [{"nombre": "glucosa", "valor": 142, "unidad": "mg/dL", '
        '"rango_referencia": "70-110", "fuera_rango": true}], '
        '"estatus": "completado"}]}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "paciente_id": {
                "type": "string",
                "description": "Unique patient identifier.",
            },
            "estudio_id": {
                "type": "string",
                "description": "Specific study identifier to retrieve a single result.",
            },
            "fecha_desde": {
                "type": "string",
                "description": "Start date to filter results (ISO 8601 YYYY-MM-DD).",
            },
            "tipo_estudio": {
                "type": "string",
                "description": "Type of study.",
                "enum": ["sangre", "orina", "imagen", "biopsia", "otros"],
            },
        },
        "required": ["paciente_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "paciente_id": {"type": "string"},
            "resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "estudio_id": {"type": "string"},
                        "tipo": {"type": "string"},
                        "fecha": {"type": "string"},
                        "parametros": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "nombre": {"type": "string"},
                                    "valor": {"type": "number"},
                                    "unidad": {"type": "string"},
                                    "rango_referencia": {"type": "string"},
                                    "fuera_rango": {"type": "boolean"},
                                },
                            },
                        },
                        "medico_solicitante": {"type": "string"},
                        "estatus": {"type": "string"},
                    },
                },
            },
        },
    },
    domains=["medical.consultation"],
    category="medical",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. consultar_cobertura_seguro
# ---------------------------------------------------------------------------

consultar_cobertura_seguro = ToolDefinition(
    name="consultar_cobertura_seguro",
    description=(
        "Verify a patient's insurance coverage, deductibles, copays, and covered procedures.\n\n"
        "WHEN_TO_USE: The physician or staff needs to verify whether a procedure is covered "
        "before ordering it, or when the patient asks about costs and coverage limits.\n\n"
        "CAPABILITIES:\n"
        "- Look up coverage by patient ID, policy number, or procedure code.\n"
        "- Returns coverage percentage, deductible, and copay amounts.\n"
        "- Lists covered procedures and annual cap information.\n"
        "- Shows how much of the annual cap has been utilized.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"paciente_id": "PAC-10234", "procedimiento_codigo": "MED-CT-001"}\n'
        '  Output: {"poliza_numero": "POL-992847", "aseguradora": "GNP Seguros", '
        '"cobertura_porcentaje": 80, "deducible": 5000, "copago": 500, '
        '"tope_anual": 500000, "monto_utilizado": 125000}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "paciente_id": {
                "type": "string",
                "description": "Unique patient identifier.",
            },
            "poliza_numero": {
                "type": "string",
                "description": "Insurance policy number.",
            },
            "procedimiento_codigo": {
                "type": "string",
                "description": "Procedure code to check specific coverage.",
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "poliza_numero": {"type": "string"},
            "aseguradora": {"type": "string"},
            "vigencia_hasta": {"type": "string"},
            "cobertura_porcentaje": {"type": "number"},
            "deducible": {"type": "number"},
            "copago": {"type": "number"},
            "procedimientos_cubiertos": {
                "type": "array",
                "items": {"type": "string"},
            },
            "tope_anual": {"type": "number"},
            "monto_utilizado": {"type": "number"},
        },
    },
    domains=["medical.consultation"],
    category="medical",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

MEDICAL_TOOLS: list[ToolDefinition] = [
    consultar_historial_medico,
    buscar_medicamentos,
    agendar_cita,
    consultar_resultados_lab,
    consultar_cobertura_seguro,
]

