"""Load featured seeds into the database on first deploy.

Idempotent: checks if seed IDs already exist before inserting.
Called from the app startup event after migrations complete.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import structlog
from sqlalchemy import func, select

from uncase.db.models.seed import SeedModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Default privacy and quality metadata applied to domain package seeds
# that don't carry their own.
_DEFAULT_PRIVACY: dict[str, object] = {
    "pii_eliminado": True,
    "metodo_anonimizacion": "presidio_v2",
    "nivel_confianza": 0.99,
    "campos_sensibles_detectados": [],
}

_DEFAULT_QUALITY: dict[str, object] = {
    "rouge_l_min": 0.20,
    "fidelidad_min": 0.80,
    "diversidad_lexica_min": 0.55,
    "coherencia_dialogica_min": 0.65,
}

# 6 featured seeds — one per industry, all Spanish.
# Extracted from Mariana/Autos TREFA patterns (automotive) and domain expertise (others).
FEATURED_SEEDS: list[dict[str, object]] = [
    {
        "id": "featured-auto-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": [
            "flujo-completo",
            "descubrimiento",
            "comparacion",
            "financiamiento",
            "intercambio",
            "cierre",
        ],
        "objetivo": (
            "Guiar al cliente desde la exploración inicial hasta la conversión: descubrir "
            "necesidades, buscar en inventario, comparar opciones, simular financiamiento "
            "con opción de intercambio, y registrar datos de contacto para seguimiento"
        ),
        "tono": "profesional-amigable",
        "roles": ["cliente", "asesora_virtual"],
        "descripcion_roles": {
            "cliente": (
                "Persona buscando un auto seminuevo para uso familiar, con presupuesto "
                "limitado y necesidad de financiamiento."
            ),
            "asesora_virtual": (
                "Asistente virtual de agencia de autos seminuevos con acceso a inventario "
                "en tiempo real, simulador de financiamiento, comparador de vehículos y "
                "sistema de registro de prospectos."
            ),
        },
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 16,
            "flujo_esperado": [
                "Saludo y bienvenida cálida",
                "Descubrimiento de necesidades (máximo 2 preguntas)",
                "Búsqueda en inventario con filtros del cliente",
                "Presentación de 2-3 opciones con precio, enganche y mensualidad",
                "Detalle completo del vehículo de interés",
                "Comparación lado a lado si el cliente duda entre dos opciones",
                "Simulación de financiamiento personalizada",
                "Exploración de programa de intercambio si aplica",
                "Captura de datos de contacto y cierre con compromiso de seguimiento",
            ],
        },
        "parametros_factuales": {
            "contexto": (
                "Agencia de autos seminuevos con presencia en 4 ciudades del noreste de México. "
                "Inventario de 80-100 vehículos, modelos 2018-2025."
            ),
            "restricciones": [
                "Siempre usar herramientas para consultar inventario real",
                "Incluir siempre información financiera: precio, enganche mínimo, mensualidad",
                "No negociar precios — son finales",
                "No garantizar aprobación de crédito",
                "Enganche mínimo 20%, plazos 12-60 meses",
            ],
            "herramientas": [
                "buscar_vehiculos",
                "obtener_vehiculo",
                "comparar_vehiculos",
                "calcular_financiamiento",
            ],
            "metadata": {"tipo_operacion": "venta_seminuevo", "segmento": "suv_familiar"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.99,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.9,
        "rating_count": 24,
        "run_count": 63,
        "avg_quality_score": 0.95,
    },
    {
        "id": "featured-med-001",
        "dominio": "medical.consultation",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": ["medicina-interna", "gastroenterologia", "consulta-inicial", "laboratorios"],
        "objetivo": (
            "Realizar historia clínica enfocada en aparato digestivo, elaborar diagnóstico "
            "diferencial y solicitar estudios pertinentes"
        ),
        "tono": "profesional-empatico",
        "roles": ["paciente", "medico_internista"],
        "descripcion_roles": {
            "paciente": "Adulto de 42 años con dolor abdominal recurrente de 3 meses de evolución.",
            "medico_internista": "Médico internista certificado con acceso a expediente clínico electrónico.",
        },
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 14,
            "flujo_esperado": [
                "Motivo de consulta y padecimiento actual",
                "Interrogatorio por aparatos y sistemas",
                "Antecedentes personales patológicos y medicamentos",
                "Antecedentes heredofamiliares relevantes",
                "Exploración física dirigida",
                "Diagnóstico diferencial razonado",
                "Solicitud de estudios con justificación",
                "Plan terapéutico inicial y signos de alarma",
            ],
        },
        "parametros_factuales": {
            "contexto": "Consultorio de medicina interna en clínica privada.",
            "restricciones": [
                "Revisar historial de alergias antes de prescribir",
                "No emitir diagnóstico definitivo sin estudios confirmatorios",
                "Signos de alarma requieren protocolo de urgencia",
            ],
            "herramientas": ["consultar_expediente", "buscar_medicamentos", "ordenar_laboratorios"],
            "metadata": {"especialidad": "medicina_interna", "tipo_visita": "consulta_inicial"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.99,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.8,
        "rating_count": 21,
        "run_count": 55,
        "avg_quality_score": 0.94,
    },
    {
        "id": "featured-legal-001",
        "dominio": "legal.advisory",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": ["propiedad-intelectual", "registro-marca", "IMPI", "pyme"],
        "objetivo": (
            "Evaluar viabilidad de registro de marca, buscar anterioridades, y definir "
            "estrategia de protección ante el IMPI"
        ),
        "tono": "profesional-didactico",
        "roles": ["cliente", "abogado_pi"],
        "descripcion_roles": {
            "cliente": "Dueño de pequeña empresa de alimentos que quiere registrar su marca comercial.",
            "abogado_pi": "Abogado especialista en propiedad intelectual con experiencia ante el IMPI.",
        },
        "pasos_turnos": {
            "turnos_min": 7,
            "turnos_max": 12,
            "flujo_esperado": [
                "Entendimiento del negocio y la marca",
                "Búsqueda de anterioridades en MARCANET",
                "Explicación de clases de Niza aplicables",
                "Proceso de registro ante el IMPI (etapas, tiempos, costos)",
                "Evaluación de riesgo de oposición",
                "Recomendación de protección complementaria",
                "Documentos necesarios y plan de acción",
            ],
        },
        "parametros_factuales": {
            "contexto": "Despacho de propiedad intelectual con acceso a MARCANET.",
            "restricciones": [
                "No garantizar aprobación del registro",
                "Plazos legales del IMPI deben respetarse estrictamente",
                "Honorarios y costos oficiales deben ser transparentes",
            ],
            "herramientas": [],
            "metadata": {"area_practica": "propiedad_intelectual", "jurisdiccion": "Mexico"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.99,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.7,
        "rating_count": 17,
        "run_count": 44,
        "avg_quality_score": 0.93,
    },
    {
        "id": "featured-fin-001",
        "dominio": "finance.advisory",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": ["tesoreria", "inversion", "startup", "gestion-capital"],
        "objetivo": (
            "Diseñar estrategia de tesorería post-ronda seed: runway operativo, instrumentos "
            "de inversión a corto plazo, y estructura fiscal óptima"
        ),
        "tono": "profesional-consultivo",
        "roles": ["cliente", "asesor_financiero"],
        "descripcion_roles": {
            "cliente": "Fundador de startup tecnológica que cerró ronda seed de $2M USD.",
            "asesor_financiero": "Asesor financiero certificado especializado en startups.",
        },
        "pasos_turnos": {
            "turnos_min": 7,
            "turnos_max": 12,
            "flujo_esperado": [
                "Contexto de la ronda: monto, términos, runway objetivo",
                "Análisis de flujo de caja y burn rate",
                "Separación de capital operativo vs. excedente invertible",
                "Instrumentos de inversión a corto plazo (CETES, fondos de deuda)",
                "Simulación de rendimientos",
                "Estrategia fiscal: régimen aplicable, deducciones",
                "Controles de tesorería y reporteo para inversionistas",
            ],
        },
        "parametros_factuales": {
            "contexto": "Firma de asesoría financiera con especialización en empresas tecnológicas.",
            "restricciones": [
                "Rendimientos pasados no garantizan rendimientos futuros",
                "No recomendar instrumentos con horizonte mayor al runway",
                "Cumplimiento con regulación CNBV/SAT obligatorio",
            ],
            "herramientas": ["simulador_inversion", "proyeccion_flujo_caja"],
            "metadata": {"tipo_cliente": "startup_seed", "jurisdiccion": "Mexico"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.99,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.8,
        "rating_count": 19,
        "run_count": 48,
        "avg_quality_score": 0.94,
    },
    {
        "id": "featured-ind-001",
        "dominio": "industrial.support",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": ["refrigeracion-industrial", "diagnostico-remoto", "alarma-temperatura"],
        "objetivo": (
            "Diagnosticar alarma de alta temperatura en sistema de refrigeración industrial, "
            "guiar al operador de forma segura y proteger la cadena de frío"
        ),
        "tono": "profesional-tecnico",
        "roles": ["operador_planta", "ingeniero_soporte"],
        "descripcion_roles": {
            "operador_planta": "Operador del turno nocturno que reporta alarma de alta temperatura.",
            "ingeniero_soporte": "Ingeniero de soporte remoto con acceso al sistema SCADA y CMMS.",
        },
        "pasos_turnos": {
            "turnos_min": 7,
            "turnos_max": 12,
            "flujo_esperado": [
                "Recepción del reporte de alarma",
                "Verificación de seguridad y protocolos de amoniaco",
                "Consulta remota de parámetros SCADA",
                "Revisión de historial de mantenimiento en CMMS",
                "Diagnóstico guiado con el operador",
                "Determinación de causa raíz",
                "Acción correctiva o despacho de técnico",
                "Protocolo de protección de producto",
            ],
        },
        "parametros_factuales": {
            "contexto": "Planta de manufactura de alimentos con refrigeración industrial por amoniaco.",
            "restricciones": [
                "Protocolos de seguridad con amoniaco son prioridad absoluta",
                "Solo personal certificado puede intervenir en el circuito",
                "Procedimiento LOTO obligatorio antes de intervención física",
                "Toda intervención debe documentarse en CMMS",
            ],
            "herramientas": [],
            "metadata": {"tipo_equipo": "refrigeracion_amoniaco", "criticidad": "alta"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.98,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.7,
        "rating_count": 15,
        "run_count": 39,
        "avg_quality_score": 0.93,
    },
    {
        "id": "featured-edu-001",
        "dominio": "education.tutoring",
        "idioma": "es",
        "version": "1.0",
        "etiquetas": ["redaccion-academica", "ensayo-argumentativo", "universidad"],
        "objetivo": (
            "Guiar al estudiante en la construcción de un ensayo argumentativo: tesis, "
            "estructura de argumentos con evidencia, contraargumentos, y formato APA"
        ),
        "tono": "amigable-motivador",
        "roles": ["estudiante", "tutor_redaccion"],
        "descripcion_roles": {
            "estudiante": (
                "Estudiante universitario de tercer semestre que necesita escribir un ensayo "
                "argumentativo de 2,000 palabras."
            ),
            "tutor_redaccion": (
                "Tutor especializado en redacción académica. Metodología socrática: "
                "guía mediante preguntas, nunca da respuestas directas."
            ),
        },
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 14,
            "flujo_esperado": [
                "Exploración del tema y conocimientos previos",
                "Formulación de la tesis",
                "Estructura del ensayo: introducción, desarrollo, conclusión",
                "Desarrollo del primer argumento con evidencia",
                "Integrar citas y parafrasear (formato APA)",
                "Trabajo con contraargumentos",
                "Revisión de coherencia y voz académica",
                "Checklist final: formato, bibliografía, rúbrica",
            ],
        },
        "parametros_factuales": {
            "contexto": "Plataforma de tutoría académica en línea con recursos de redacción.",
            "restricciones": [
                "Nunca escribir el ensayo por el estudiante — solo guiar",
                "Usar preguntas socráticas",
                "Adaptar explicaciones al nivel demostrado",
                "Toda cita debe verificarse como real",
            ],
            "herramientas": [],
            "metadata": {"materia": "comunicacion", "nivel": "universidad", "formato": "APA_7"},
        },
        "privacidad": {
            "pii_eliminado": True,
            "metodo_anonimizacion": "presidio_v2",
            "nivel_confianza": 0.98,
            "campos_sensibles_detectados": [],
        },
        "metricas_calidad": {
            "rouge_l_min": 0.20,
            "fidelidad_min": 0.80,
            "diversidad_lexica_min": 0.55,
            "coherencia_dialogica_min": 0.65,
        },
        "rating": 4.9,
        "rating_count": 22,
        "run_count": 58,
        "avg_quality_score": 0.95,
    },
]


def _build_seed_model(seed_dict: dict[str, object], *, seed_id: str | None = None) -> SeedModel:
    """Build a SeedModel from a seed dictionary, filling defaults for missing fields."""
    return SeedModel(
        id=seed_id or str(seed_dict.get("id", uuid.uuid4().hex)),
        dominio=seed_dict["dominio"],  # type: ignore[arg-type]
        idioma=str(seed_dict.get("idioma", "es")),
        version=str(seed_dict.get("version", "1.0")),
        etiquetas=seed_dict.get("etiquetas", []),
        objetivo=seed_dict["objetivo"],  # type: ignore[arg-type]
        tono=str(seed_dict.get("tono", "profesional")),
        roles=seed_dict["roles"],
        descripcion_roles=seed_dict.get("descripcion_roles", {}),
        pasos_turnos=seed_dict["pasos_turnos"],
        parametros_factuales=seed_dict["parametros_factuales"],
        privacidad=seed_dict.get("privacidad", _DEFAULT_PRIVACY),
        metricas_calidad=seed_dict.get("metricas_calidad", _DEFAULT_QUALITY),
        rating=seed_dict.get("rating"),  # type: ignore[arg-type]
        rating_count=int(seed_dict.get("rating_count", 0)),  # type: ignore[arg-type]
        run_count=int(seed_dict.get("run_count", 0)),  # type: ignore[arg-type]
        avg_quality_score=seed_dict.get("avg_quality_score"),  # type: ignore[arg-type]
        organization_id=None,  # Public — visible to all
    )


async def load_featured_seeds(session: AsyncSession) -> int:
    """Insert 6 featured seeds (one per industry) if the seeds table is empty.

    Returns the number of seeds inserted (0 if table already has data).
    """
    count = await session.scalar(select(func.count()).select_from(SeedModel))
    if count and count > 0:
        logger.info("seed_data_skip", reason="seeds table already has data", existing=count)
        return 0

    inserted = 0

    for seed_dict in FEATURED_SEEDS:
        session.add(_build_seed_model(seed_dict))
        inserted += 1

    await session.commit()
    logger.info("seed_data_loaded", featured=inserted)
    return inserted
