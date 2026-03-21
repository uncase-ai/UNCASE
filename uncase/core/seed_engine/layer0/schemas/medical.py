"""Medical consultation seed schema for agentic extraction.

Defines ``SeedMedical`` — a structured Pydantic model containing all the
fields an interview loop needs to capture for generating synthetic medical
consultation conversations.  The schema is organized into five nested
categories, each modeled as a separate ``BaseModel``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from uncase.core.seed_engine.layer0.schemas.base import BaseSeedExtraction

# ── Category 1: Patient Profile ─────────────────────────────────────


class PacientePerfil(BaseModel):
    """Profile of the patient participating in the consultation."""

    tipo_paciente: str | None = Field(
        default=None,
        description=(
            "Tipo de paciente según grupo etario. "
            "Valores posibles: 'adulto', 'pediatrico', 'geriatrico', 'prenatal'. Required."
        ),
    )
    severidad_condicion: str | None = Field(
        default=None,
        description=(
            "Severidad de la condición o padecimiento del paciente. "
            "Valores: 'leve', 'moderado', 'grave', 'crónico'. Required."
        ),
    )
    cobertura_medica: str | None = Field(
        default=None,
        description=(
            "Tipo de cobertura médica del paciente. "
            "Valores: 'particular', 'seguro_social', 'seguro_privado', 'sin_cobertura'. Required."
        ),
    )
    alergias_conocidas: list[str] | None = Field(
        default=None,
        description=(
            "Lista de alergias conocidas del paciente. Ejemplos: 'penicilina', 'sulfas', 'latex', 'mariscos'. Optional."
        ),
    )
    condiciones_cronicas: list[str] | None = Field(
        default=None,
        description=(
            "Lista de condiciones crónicas preexistentes del paciente. "
            "Ejemplos: 'diabetes_tipo_2', 'hipertension', 'asma', 'hipotiroidismo'. Optional."
        ),
    )
    medicamentos_actuales: list[str] | None = Field(
        default=None,
        description=(
            "Lista de medicamentos que el paciente toma actualmente. "
            "Ejemplos: 'metformina_850mg', 'losartan_50mg', 'levotiroxina_100mcg'. Optional."
        ),
    )
    estado_emocional: str | None = Field(
        default=None,
        description=(
            "Estado emocional predominante del paciente al momento de la consulta. "
            "Valores: 'tranquilo', 'ansioso', 'asustado', 'frustrado'. Optional."
        ),
    )


# ── Category 2: Consultation Reason ─────────────────────────────────


class MotivoConsulta(BaseModel):
    """Details about the reason for the medical consultation."""

    especialidad: str | None = Field(
        default=None,
        description=(
            "Especialidad médica de la consulta. "
            "Valores: 'general', 'cardiologia', 'dermatologia', 'pediatria', "
            "'ginecologia', 'traumatologia', 'neurologia', 'psiquiatria', "
            "'oftalmologia', 'otro'. Required."
        ),
    )
    motivo_principal: str | None = Field(
        default=None,
        description=(
            "Motivo principal de la consulta descrito por el paciente (texto libre). "
            "Ejemplo: 'dolor en el pecho al hacer esfuerzo', 'manchas en la piel que no desaparecen'. Required."
        ),
    )
    duracion_sintomas: str | None = Field(
        default=None,
        description=(
            "Duración o temporalidad de los síntomas. "
            "Valores: 'agudo' (< 2 semanas), 'subagudo' (2-6 semanas), 'crónico' (> 6 semanas). Required."
        ),
    )
    tratamientos_previos: list[str] | None = Field(
        default=None,
        description=(
            "Lista de tratamientos previos que el paciente ya intentó para este padecimiento. "
            "Ejemplos: 'automedicacion_ibuprofeno', 'antibiotico_previo', 'fisioterapia'. Optional."
        ),
    )
    es_seguimiento: bool | None = Field(
        default=None,
        description="Si la consulta es un seguimiento de un padecimiento previo ya atendido. Optional.",
    )
    fuente_referencia: str | None = Field(
        default=None,
        description=(
            "Cómo llegó el paciente a esta consulta. "
            "Valores: 'espontanea', 'referido' (por otro médico), 'urgencia' (derivado de urgencias). Optional."
        ),
    )


# ── Category 3: Clinical Context ────────────────────────────────────


class ContextoClinico(BaseModel):
    """Contextual metadata about the clinical setting and channel."""

    canal: str | None = Field(
        default=None,
        description=(
            "Canal o medio por el cual se realiza la consulta. "
            "Valores: 'presencial', 'telemedicina', 'telefono', 'chat_medico'. Required."
        ),
    )
    entorno: str | None = Field(
        default=None,
        description=(
            "Entorno donde se lleva a cabo la consulta. "
            "Valores: 'consultorio', 'hospital', 'clinica', 'domicilio', 'urgencias'. Required."
        ),
    )
    restriccion_tiempo: str | None = Field(
        default=None,
        description=(
            "Nivel de urgencia temporal de la consulta. "
            "Valores: 'normal' (consulta programada), 'urgente' (prioridad alta), "
            "'emergencia' (atención inmediata). Optional."
        ),
    )
    requiere_interprete: bool | None = Field(
        default=None,
        description=(
            "Si se necesita un intérprete por barrera lingüística o discapacidad auditiva del paciente. Optional."
        ),
    )
    acompanante: str | None = Field(
        default=None,
        description=("Si el paciente viene acompañado y por quién. Valores: 'solo', 'familiar', 'cuidador'. Optional."),
    )


# ── Category 4: Medical Scenario ────────────────────────────────────


class EscenarioMedico(BaseModel):
    """Medical scenario configuration for the synthetic consultation."""

    tipo_escenario: str | None = Field(
        default=None,
        description=(
            "Tipo de escenario clínico a simular. "
            "Valores: 'primera_consulta', 'seguimiento', 'segunda_opinion', "
            "'interconsulta', 'urgencia', 'resultado_estudios'. Required."
        ),
    )
    complejidad: str | None = Field(
        default=None,
        description=(
            "Nivel de complejidad clínica del escenario. "
            "Valores: 'simple' (diagnóstico evidente), 'moderado' (requiere estudios), "
            "'complejo' (diagnóstico diferencial amplio o comorbilidades). Required."
        ),
    )
    tono: str | None = Field(
        default=None,
        description=(
            "Tono comunicativo del médico en la conversación. "
            "Valores: 'profesional', 'empático', 'directo', 'didáctico'. Required."
        ),
    )
    incluir_exploracion: bool = Field(
        default=True,
        description="Si se debe incluir una fase de exploración física o revisión de signos vitales. Required.",
    )
    incluir_razonamiento_diagnostico: bool = Field(
        default=True,
        description=(
            "Si se debe incluir el razonamiento clínico del médico "
            "(diagnóstico diferencial, hipótesis, descarte). Required."
        ),
    )
    incluir_plan_tratamiento: bool = Field(
        default=True,
        description="Si se debe incluir un plan de tratamiento con indicaciones y prescripciones. Required.",
    )
    incluir_educacion_paciente: bool = Field(
        default=False,
        description=(
            "Si se debe incluir una fase de educación al paciente "
            "(explicación del padecimiento, medidas preventivas, signos de alarma). Optional."
        ),
    )


# ── Category 5: Clinical Rules ──────────────────────────────────────


class ReglasClinicas(BaseModel):
    """Domain-specific clinical rules and regulatory constraints."""

    nivel_confidencialidad: str | None = Field(
        default=None,
        description=(
            "Nivel de confidencialidad requerido para la información del paciente. "
            "Valores: 'standard' (expediente regular), 'alto' (datos sensibles como VIH, psiquiatría), "
            "'máximo' (menor de edad, violencia, protección especial). Optional."
        ),
    )
    requiere_consentimiento_informado: bool | None = Field(
        default=None,
        description=(
            "Si el escenario requiere obtención de consentimiento informado "
            "(procedimientos invasivos, estudios de riesgo, tratamiento experimental). Optional."
        ),
    )
    marco_regulatorio: str | None = Field(
        default=None,
        description=(
            "Marco regulatorio aplicable a la consulta. "
            "Valores: 'nom_mexicana' (NOM-004-SSA3, NOM-024-SSA3), "
            "'hipaa' (Health Insurance Portability and Accountability Act), "
            "'gdpr' (General Data Protection Regulation). Optional."
        ),
    )
    tipo_documentacion: str | None = Field(
        default=None,
        description=(
            "Tipo de documentación clínica que debe generarse. "
            "Valores: 'nota_medica', 'receta', 'referencia', 'incapacidad'. Optional."
        ),
    )
    contraindicaciones: list[str] | None = Field(
        default=None,
        description=(
            "Lista de contraindicaciones a considerar durante la consulta. "
            "Ejemplos: 'alergia_penicilina', 'embarazo', 'insuficiencia_renal', 'anticoagulantes'. Optional."
        ),
    )
    guias_clinicas: list[str] | None = Field(
        default=None,
        description=(
            "Guías de práctica clínica aplicables al caso. "
            "Ejemplos: 'gpc_diabetes_tipo2', 'gpc_hipertension_arterial', 'aha_heart_failure'. Optional."
        ),
    )


# ── Root Seed Model ─────────────────────────────────────────────────


# Map of field dot-paths that are *required* for completion.
# The State Manager uses this to decide when the seed is ready.
REQUIRED_FIELDS_MEDICAL: frozenset[str] = frozenset(
    {
        "paciente_perfil.tipo_paciente",
        "paciente_perfil.severidad_condicion",
        "paciente_perfil.cobertura_medica",
        "motivo_consulta.especialidad",
        "motivo_consulta.motivo_principal",
        "motivo_consulta.duracion_sintomas",
        "contexto_clinico.canal",
        "contexto_clinico.entorno",
        "escenario_medico.tipo_escenario",
        "escenario_medico.complejidad",
    }
)


class SeedMedical(BaseSeedExtraction):
    """Medical consultation seed schema for agentic extraction.

    Captures all the information needed to generate high-quality synthetic
    conversations for medical consultation assistant fine-tuning.

    Organized in five categories that the Interviewer walks the user through:
    1. Patient profile (``paciente_perfil``)
    2. Consultation reason (``motivo_consulta``)
    3. Clinical context (``contexto_clinico``)
    4. Medical scenario (``escenario_medico``)
    5. Clinical rules (``reglas_clinicas``)
    """

    paciente_perfil: PacientePerfil = Field(
        default_factory=PacientePerfil,
        description="Perfil del paciente que participará en la consulta simulada.",
    )
    motivo_consulta: MotivoConsulta = Field(
        default_factory=MotivoConsulta,
        description="Detalles sobre el motivo de la consulta médica.",
    )
    contexto_clinico: ContextoClinico = Field(
        default_factory=ContextoClinico,
        description="Metadatos sobre el canal, entorno y contexto clínico de la consulta.",
    )
    escenario_medico: EscenarioMedico = Field(
        default_factory=EscenarioMedico,
        description="Configuración del escenario clínico para la consulta sintética.",
    )
    reglas_clinicas: ReglasClinicas = Field(
        default_factory=ReglasClinicas,
        description="Reglas clínicas, regulatorias y restricciones específicas del dominio médico.",
    )

    @classmethod
    def required_field_names(cls) -> frozenset[str]:
        """Return the set of dot-path field names that are required for completion."""
        return REQUIRED_FIELDS_MEDICAL

    @classmethod
    def industry_name(cls) -> str:
        """Return the human-readable industry identifier."""
        return "medical"

    @classmethod
    def industry_display(cls, locale: str = "es") -> str:
        """Return localized display name for this industry."""
        names = {"es": "Consulta Médica", "en": "Medical Consultation"}
        return names.get(locale, names["en"])

    def to_seed_dict(self) -> dict[str, Any]:
        """Convert extracted medical parameters to a SeedSchema v1 dict.

        Maps the medical extraction fields into the canonical seed format
        used by the SCSF pipeline.
        """
        # Build objective from scenario + specialty + chief complaint
        scenario_type = self.escenario_medico.tipo_escenario or "primera_consulta"
        especialidad = self.motivo_consulta.especialidad or "general"
        motivo = self.motivo_consulta.motivo_principal or "consulta general"
        tipo_paciente = self.paciente_perfil.tipo_paciente or "adulto"
        objetivo = (
            f"Simular una consulta médica de {scenario_type} en {especialidad} "
            f"con paciente {tipo_paciente} por: {motivo}"
        )

        # Build roles
        severidad = self.paciente_perfil.severidad_condicion or "moderado"
        cobertura = self.paciente_perfil.cobertura_medica or "particular"
        estado_emocional = self.paciente_perfil.estado_emocional or "tranquilo"
        canal = self.contexto_clinico.canal or "presencial"
        entorno = self.contexto_clinico.entorno or "consultorio"

        roles = ["patient", "physician"]
        descripcion_roles: dict[str, str] = {
            "patient": (
                f"Paciente {tipo_paciente}, severidad: {severidad}, "
                f"cobertura: {cobertura}, estado emocional: {estado_emocional}"
            ),
            "physician": (f"Médico especialista en {especialidad} con acceso al expediente clínico"),
        }

        # Build flow steps
        flujo: list[str] = [
            "Saludo y presentación",
            "Interrogatorio (anamnesis)",
        ]
        if self.escenario_medico.incluir_exploracion:
            flujo.append("Exploración física / revisión de signos vitales")
        if self.escenario_medico.incluir_razonamiento_diagnostico:
            flujo.append("Razonamiento diagnóstico y diagnóstico diferencial")
        if self.escenario_medico.incluir_plan_tratamiento:
            flujo.append("Plan de tratamiento e indicaciones")
        if self.escenario_medico.incluir_educacion_paciente:
            flujo.append("Educación al paciente y medidas preventivas")
        flujo.append("Cierre y seguimiento")

        # Build constraints from clinical rules
        restricciones: list[str] = []
        if self.reglas_clinicas.contraindicaciones:
            restricciones.extend(f"Contraindicación: {c}" for c in self.reglas_clinicas.contraindicaciones)
        if self.reglas_clinicas.requiere_consentimiento_informado:
            restricciones.append("Requiere obtención de consentimiento informado")
        if self.reglas_clinicas.nivel_confidencialidad == "alto":
            restricciones.append("Información sensible — confidencialidad alta")
        elif self.reglas_clinicas.nivel_confidencialidad == "máximo":
            restricciones.append("Protección especial — confidencialidad máxima")
        if self.reglas_clinicas.marco_regulatorio:
            restricciones.append(f"Marco regulatorio: {self.reglas_clinicas.marco_regulatorio}")
        if self.reglas_clinicas.guias_clinicas:
            restricciones.extend(f"Seguir guía: {g}" for g in self.reglas_clinicas.guias_clinicas)
        if self.paciente_perfil.alergias_conocidas:
            restricciones.extend(f"Alergia conocida: {a}" for a in self.paciente_perfil.alergias_conocidas)

        # Build context from clinical context + patient profile
        contexto_parts: list[str] = [
            f"Canal: {canal}",
            f"Entorno: {entorno}",
        ]
        duracion = self.motivo_consulta.duracion_sintomas
        if duracion:
            contexto_parts.append(f"Duración de síntomas: {duracion}")
        if self.paciente_perfil.condiciones_cronicas:
            contexto_parts.append(f"Condiciones crónicas: {', '.join(self.paciente_perfil.condiciones_cronicas)}")
        if self.paciente_perfil.medicamentos_actuales:
            contexto_parts.append(f"Medicamentos actuales: {', '.join(self.paciente_perfil.medicamentos_actuales)}")
        if self.motivo_consulta.tratamientos_previos:
            contexto_parts.append(f"Tratamientos previos: {', '.join(self.motivo_consulta.tratamientos_previos)}")
        if self.motivo_consulta.es_seguimiento:
            contexto_parts.append("Consulta de seguimiento")
        if self.motivo_consulta.fuente_referencia:
            contexto_parts.append(f"Fuente de referencia: {self.motivo_consulta.fuente_referencia}")
        if self.contexto_clinico.restriccion_tiempo:
            contexto_parts.append(f"Restricción de tiempo: {self.contexto_clinico.restriccion_tiempo}")
        if self.contexto_clinico.requiere_interprete:
            contexto_parts.append("Se requiere intérprete")
        if self.contexto_clinico.acompanante and self.contexto_clinico.acompanante != "solo":
            contexto_parts.append(f"Acompañante: {self.contexto_clinico.acompanante}")

        # Map tone
        tono = self.escenario_medico.tono or "profesional"

        # Build tags
        etiquetas = ["ai-extracted", "medical"]
        if self.escenario_medico.complejidad:
            etiquetas.append(f"complexity:{self.escenario_medico.complejidad}")
        etiquetas.append(f"specialty:{especialidad}")
        if severidad in ("grave", "crónico"):
            etiquetas.append(f"severity:{severidad}")

        # Documentation type
        tipo_doc = self.reglas_clinicas.tipo_documentacion or "nota_medica"

        return {
            "version": "1.0",
            "dominio": "medical.consultation",
            "idioma": self.idioma,
            "etiquetas": etiquetas,
            "roles": roles,
            "descripcion_roles": descripcion_roles,
            "objetivo": objetivo,
            "tono": tono,
            "pasos_turnos": {
                "turnos_min": 6,
                "turnos_max": 14,
                "flujo_esperado": flujo,
            },
            "parametros_factuales": {
                "contexto": ". ".join(contexto_parts),
                "restricciones": restricciones,
                "herramientas": [],
                "metadata": {
                    "extracted_by": "ai-interview",
                    "scenario_type": scenario_type,
                    "complexity": self.escenario_medico.complejidad or "moderado",
                    "patient_type": tipo_paciente,
                    "severity": severidad,
                    "insurance": cobertura,
                    "specialty": especialidad,
                    "symptom_duration": duracion or "no_especificado",
                    "setting": entorno,
                    "channel": canal,
                    "emotional_state": estado_emocional,
                    "documentation_type": tipo_doc,
                    "includes_examination": self.escenario_medico.incluir_exploracion,
                    "includes_diagnostic_reasoning": self.escenario_medico.incluir_razonamiento_diagnostico,
                    "includes_treatment_plan": self.escenario_medico.incluir_plan_tratamiento,
                    "includes_patient_education": self.escenario_medico.incluir_educacion_paciente,
                },
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
        }
