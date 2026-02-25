"""Built-in tool definitions for the **education.tutoring** domain.

Every tool follows the TREFA pattern (Tool-Rich Enhanced Function Augmentation):
descriptions include WHEN_TO_USE, CAPABILITIES, and EXAMPLE blocks so that
LLM generators can decide autonomously when and how to invoke them.

All five tools are registered automatically in the default ``ToolRegistry``
when this module is imported (side-effect import from ``_builtin/__init__``).
"""

from __future__ import annotations

from uncase.tools.schemas import ToolDefinition

# ---------------------------------------------------------------------------
# 1. buscar_curriculum
# ---------------------------------------------------------------------------

buscar_curriculum = ToolDefinition(
    name="buscar_curriculum",
    description=(
        "Search curriculum and syllabus content by subject, level, and topic.\n\n"
        "WHEN_TO_USE: The tutor or student needs to locate specific learning "
        "objectives, unit contents, or competencies within an official study plan. "
        "Useful when planning sessions, aligning exercises with curriculum goals, "
        "or answering questions about what a course covers.\n\n"
        "CAPABILITIES:\n"
        "- Filter by subject (materia), educational level, specific topic, and study plan.\n"
        "- Returns matching curriculum units with learning objectives, contents, "
        "estimated hours, competencies, and suggested resources.\n"
        "- Supports partial matches (e.g. searching only by subject and level).\n\n"
        "EXAMPLE:\n"
        '  Input:  {"materia": "Matemáticas", "nivel": "secundaria", "tema": "ecuaciones lineales"}\n'
        '  Output: {"resultados": [{"materia": "Matemáticas", "nivel": "secundaria", '
        '"unidad": "Álgebra I", "tema": "Ecuaciones lineales", ...}], "total_resultados": 3}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "materia": {
                "type": "string",
                "description": "Subject name to search (e.g. Matemáticas, Historia, Biología).",
            },
            "nivel": {
                "type": "string",
                "description": "Educational level.",
                "enum": ["primaria", "secundaria", "preparatoria", "universidad", "posgrado"],
            },
            "tema": {
                "type": "string",
                "description": "Specific topic or keyword within the curriculum (e.g. fracciones).",
            },
            "plan_estudios": {
                "type": "string",
                "description": "Official study plan identifier or name (e.g. SEP 2023, Plan Bolonia).",
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
                        "materia": {"type": "string"},
                        "nivel": {"type": "string"},
                        "unidad": {"type": "string"},
                        "tema": {"type": "string"},
                        "objetivos_aprendizaje": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "contenidos": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "horas_estimadas": {"type": "number"},
                        "competencias": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "recursos_sugeridos": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["education.tutoring"],
    category="education",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 2. evaluar_progreso
# ---------------------------------------------------------------------------

evaluar_progreso = ToolDefinition(
    name="evaluar_progreso",
    description=(
        "Retrieve and summarize a student's academic progress for a given subject and period.\n\n"
        "WHEN_TO_USE: The tutor needs to review a student's performance before a session, "
        "identify strengths and weaknesses, or provide a progress report to the student "
        "or their parents. Also useful when deciding which topics need reinforcement.\n\n"
        "CAPABILITIES:\n"
        "- Retrieves all evaluations (exams, homework, projects, participation) for the student.\n"
        "- Calculates average grade and identifies achieved competencies.\n"
        "- Detects performance trend (improving, stable, declining).\n"
        "- Lists specific areas for improvement to guide session planning.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"alumno_id": "ALU-1042", "materia": "Física", "periodo": "2026-1"}\n'
        '  Output: {"alumno_id": "ALU-1042", "nombre_alumno": "María López", '
        '"calificacion_promedio": 8.2, "tendencia": "mejorando", ...}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "alumno_id": {
                "type": "string",
                "description": "Unique student identifier in the tutoring system.",
            },
            "materia": {
                "type": "string",
                "description": "Subject to evaluate progress for (e.g. Matemáticas, Química).",
            },
            "periodo": {
                "type": "string",
                "description": "Academic period or date range (e.g. 2026-1, enero-junio 2026).",
            },
        },
        "required": ["alumno_id"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "alumno_id": {"type": "string"},
            "nombre_alumno": {"type": "string"},
            "materia": {"type": "string"},
            "periodo": {"type": "string"},
            "calificacion_promedio": {"type": "number"},
            "evaluaciones": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "evaluacion_id": {"type": "string"},
                        "tipo": {
                            "type": "string",
                            "enum": ["examen", "tarea", "proyecto", "participacion"],
                        },
                        "titulo": {"type": "string"},
                        "calificacion": {"type": "number"},
                        "calificacion_maxima": {"type": "number"},
                        "fecha": {"type": "string"},
                        "retroalimentacion": {"type": "string"},
                    },
                },
            },
            "competencias_logradas": {
                "type": "array",
                "items": {"type": "string"},
            },
            "areas_mejora": {
                "type": "array",
                "items": {"type": "string"},
            },
            "tendencia": {
                "type": "string",
                "enum": ["mejorando", "estable", "declinando"],
            },
        },
    },
    domains=["education.tutoring"],
    category="education",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 3. generar_ejercicio
# ---------------------------------------------------------------------------

generar_ejercicio = ToolDefinition(
    name="generar_ejercicio",
    description=(
        "Generate exercises or quiz questions for a specific subject, topic, and difficulty level.\n\n"
        "WHEN_TO_USE: The tutor needs practice material for a session, wants to create a "
        "quick assessment to diagnose understanding, or the student requests extra exercises "
        "on a particular topic. Use after consulting the curriculum to ensure alignment.\n\n"
        "CAPABILITIES:\n"
        "- Generates exercises of various types: multiple choice, open-ended, true/false, "
        "matching columns, and fill-in-the-blank.\n"
        "- Each exercise includes the correct answer and an explanation.\n"
        "- Adjustable difficulty (basic, intermediate, advanced) and quantity.\n"
        "- Returns estimated completion time and the competency each exercise evaluates.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"materia": "Matemáticas", "tema": "fracciones", "nivel_dificultad": "intermedio", '
        '"tipo_ejercicio": "opcion_multiple", "cantidad": 5}\n'
        '  Output: {"ejercicios": [{"ejercicio_id": "EJ-0001", "tipo": "opcion_multiple", '
        '"enunciado": "¿Cuánto es 3/4 + 1/2?", ...}], "total_generados": 5, '
        '"tiempo_estimado_minutos": 15}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "materia": {
                "type": "string",
                "description": "Subject for the exercises (e.g. Matemáticas, Español, Ciencias).",
            },
            "tema": {
                "type": "string",
                "description": "Specific topic within the subject (e.g. fracciones, verbos irregulares).",
            },
            "nivel_dificultad": {
                "type": "string",
                "description": "Difficulty level of the generated exercises.",
                "enum": ["basico", "intermedio", "avanzado"],
            },
            "tipo_ejercicio": {
                "type": "string",
                "description": "Type of exercise to generate.",
                "enum": [
                    "opcion_multiple",
                    "abierta",
                    "verdadero_falso",
                    "relacion_columnas",
                    "completar",
                ],
            },
            "cantidad": {
                "type": "integer",
                "description": "Number of exercises to generate (default: 5).",
            },
        },
        "required": ["materia", "tema", "nivel_dificultad"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "ejercicios": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ejercicio_id": {"type": "string"},
                        "tipo": {"type": "string"},
                        "enunciado": {"type": "string"},
                        "opciones": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "respuesta_correcta": {"type": "string"},
                        "explicacion": {"type": "string"},
                        "nivel_dificultad": {"type": "string"},
                        "competencia_evaluada": {"type": "string"},
                        "puntos": {"type": "integer"},
                    },
                },
            },
            "total_generados": {"type": "integer"},
            "tiempo_estimado_minutos": {"type": "integer"},
        },
    },
    domains=["education.tutoring"],
    category="education",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 4. buscar_recurso_educativo
# ---------------------------------------------------------------------------

buscar_recurso_educativo = ToolDefinition(
    name="buscar_recurso_educativo",
    description=(
        "Search for educational resources such as videos, documents, simulations, and readings.\n\n"
        "WHEN_TO_USE: The tutor wants to recommend supplementary material, the student "
        "needs additional resources for self-study, or the session plan requires specific "
        "media types (e.g. an interactive simulation for a science topic).\n\n"
        "CAPABILITIES:\n"
        "- Filter by topic, resource type, educational level, and language.\n"
        "- Returns resources with metadata including author, rating, usage count, and tags.\n"
        "- Supports multiple resource types: video, document, interactive, simulation, reading.\n"
        "- Results are sorted by relevance and community rating.\n\n"
        "EXAMPLE:\n"
        '  Input:  {"tema": "sistema solar", "tipo_recurso": "video", "nivel": "secundaria", '
        '"idioma": "es"}\n'
        '  Output: {"recursos": [{"recurso_id": "REC-3201", "titulo": "El Sistema Solar en 10 min", '
        '"tipo": "video", "calificacion_promedio": 4.7, ...}], "total_resultados": 12}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "tema": {
                "type": "string",
                "description": "Topic or keyword to search for (e.g. sistema solar, gramática inglesa).",
            },
            "tipo_recurso": {
                "type": "string",
                "description": "Type of educational resource.",
                "enum": ["video", "documento", "interactivo", "simulacion", "lectura"],
            },
            "nivel": {
                "type": "string",
                "description": "Educational level.",
                "enum": ["primaria", "secundaria", "preparatoria", "universidad", "posgrado"],
            },
            "idioma": {
                "type": "string",
                "description": "Language of the resource (ISO code, e.g. es, en, fr).",
            },
        },
        "required": [],
    },
    output_schema={
        "type": "object",
        "properties": {
            "recursos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "recurso_id": {"type": "string"},
                        "titulo": {"type": "string"},
                        "tipo": {"type": "string"},
                        "autor": {"type": "string"},
                        "url": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "nivel": {"type": "string"},
                        "idioma": {"type": "string"},
                        "duracion_minutos": {"type": "integer"},
                        "calificacion_promedio": {"type": "number"},
                        "veces_utilizado": {"type": "integer"},
                        "etiquetas": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "total_resultados": {"type": "integer"},
        },
    },
    domains=["education.tutoring"],
    category="education",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# 5. programar_sesion
# ---------------------------------------------------------------------------

programar_sesion = ToolDefinition(
    name="programar_sesion",
    description=(
        "Schedule a tutoring session for a student, optionally assigning a tutor and suggesting topics.\n\n"
        "WHEN_TO_USE: The student or parent requests a tutoring session, the tutor needs "
        "to book the next appointment, or the system recommends a session based on detected "
        "areas for improvement. Typically used after evaluar_progreso to align session "
        "topics with the student's needs.\n\n"
        "CAPABILITIES:\n"
        "- Schedules a session with date, duration, and modality (in-person, virtual, hybrid).\n"
        "- Auto-assigns a tutor if none is specified, based on subject and availability.\n"
        "- Suggests topics and preparation materials based on the student's progress data.\n"
        "- Returns platform information for virtual sessions (e.g. Zoom, Google Meet).\n\n"
        "EXAMPLE:\n"
        '  Input:  {"alumno_id": "ALU-1042", "materia": "Física", "fecha_preferida": "2026-03-05", '
        '"duracion_minutos": 60, "modalidad": "virtual"}\n'
        '  Output: {"sesion_id": "SES-8834", "tutor_asignado": "Prof. García", '
        '"plataforma": "Zoom", "temas_sugeridos": ["Leyes de Newton", "Fricción"], ...}'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "alumno_id": {
                "type": "string",
                "description": "Unique student identifier in the tutoring system.",
            },
            "tutor_id": {
                "type": "string",
                "description": "Preferred tutor identifier. If omitted, one is auto-assigned.",
            },
            "materia": {
                "type": "string",
                "description": "Subject for the tutoring session (e.g. Matemáticas, Inglés).",
            },
            "fecha_preferida": {
                "type": "string",
                "description": "Preferred date for the session (ISO format, e.g. 2026-03-05).",
            },
            "duracion_minutos": {
                "type": "integer",
                "description": "Desired session duration in minutes (e.g. 30, 45, 60, 90, 120).",
            },
            "modalidad": {
                "type": "string",
                "description": "Session modality.",
                "enum": ["presencial", "virtual", "hibrida"],
            },
        },
        "required": ["alumno_id", "materia"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "sesion_id": {"type": "string"},
            "alumno_id": {"type": "string"},
            "tutor_asignado": {"type": "string"},
            "materia": {"type": "string"},
            "fecha_hora": {"type": "string"},
            "duracion_minutos": {"type": "integer"},
            "modalidad": {"type": "string"},
            "plataforma": {"type": "string"},
            "temas_sugeridos": {
                "type": "array",
                "items": {"type": "string"},
            },
            "materiales_preparar": {
                "type": "array",
                "items": {"type": "string"},
            },
            "estatus": {"type": "string"},
        },
    },
    domains=["education.tutoring"],
    category="education",
    execution_mode="simulated",
    version="1.0",
)

# ---------------------------------------------------------------------------
# Public collection
# ---------------------------------------------------------------------------

EDUCATION_TOOLS: list[ToolDefinition] = [
    buscar_curriculum,
    evaluar_progreso,
    generar_ejercicio,
    buscar_recurso_educativo,
    programar_sesion,
]
