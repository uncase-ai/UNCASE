"""Financial advisory seed schema for agentic extraction.

Defines ``SeedFinance`` — a structured Pydantic model containing all the
fields an interview loop needs to capture for generating synthetic financial
advisory conversations.  The schema is organized into five nested categories,
each modeled as a separate ``BaseModel``, and is designed for regulated
financial markets (primarily the Mexican financial system: CNBV, CONDUSEF,
SAT, LFPDPPP).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from uncase.core.seed_engine.layer0.schemas.base import BaseSeedExtraction

# ── Category 1: Financial Client Profile ─────────────────────────────


class ClienteFinanciero(BaseModel):
    """Profile of the financial client participating in the conversation."""

    tipo_cliente: str | None = Field(
        default=None,
        description=(
            "Tipo de cliente financiero. "
            "Valores: 'persona_fisica', 'persona_moral', 'inversionista', 'pyme', 'corporativo'. Required."
        ),
    )
    perfil_riesgo: str | None = Field(
        default=None,
        description=(
            "Perfil de riesgo del cliente según su tolerancia a pérdidas y horizonte de inversión. "
            "Valores: 'conservador', 'moderado', 'agresivo'. Required."
        ),
    )
    nivel_conocimiento_financiero: str | None = Field(
        default=None,
        description=(
            "Nivel de alfabetización financiera del cliente para calibrar el lenguaje del asesor. "
            "Valores: 'basico', 'intermedio', 'avanzado'. Required."
        ),
    )
    rango_ingresos: str | None = Field(
        default=None,
        description=(
            "Rango de ingresos mensuales del cliente que determina productos elegibles. "
            "Valores: 'bajo', 'medio', 'alto', 'muy_alto'. Optional."
        ),
    )
    productos_actuales: list[str] | None = Field(
        default=None,
        description=(
            "Productos financieros que el cliente ya tiene contratados. "
            "Valores posibles: 'credito_hipotecario', 'tarjeta_credito', 'inversion', "
            "'ahorro', 'seguro', 'credito_automotriz', 'credito_personal', 'nomina', "
            "'afore', 'fondo_inversion'. Optional."
        ),
    )
    situacion_laboral: str | None = Field(
        default=None,
        description=(
            "Situación laboral actual del cliente, relevante para elegibilidad crediticia. "
            "Valores: 'asalariado', 'independiente', 'empresario', 'jubilado'. Optional."
        ),
    )
    historial_crediticio: str | None = Field(
        default=None,
        description=(
            "Estado del historial crediticio del cliente en buró de crédito. "
            "Valores: 'sin_historial', 'bueno', 'regular', 'malo'. Optional."
        ),
    )
    edad_rango: str | None = Field(
        default=None,
        description=(
            "Rango de edad del cliente, relevante para productos como AFORE y seguros de vida. "
            "Ejemplo: '25-35', '36-50', '51-65', '65+'. Optional."
        ),
    )
    tiene_dependientes: bool | None = Field(
        default=None,
        description="Si el cliente tiene dependientes económicos, relevante para seguros y planeación. Optional.",
    )


# ── Category 2: Financial Objective ──────────────────────────────────


class ObjetivoFinanciero(BaseModel):
    """Financial objective and product interest details."""

    tipo_servicio: str | None = Field(
        default=None,
        description=(
            "Tipo de servicio financiero que busca el cliente. "
            "Valores: 'credito', 'inversion', 'ahorro', 'seguro', 'planeacion_financiera', "
            "'reestructura_deuda', 'asesoria_fiscal'. Required."
        ),
    )
    objetivo_especifico: str | None = Field(
        default=None,
        description=(
            "Descripción en texto libre del objetivo financiero concreto del cliente. "
            "Ejemplo: 'Comprar casa en 2 años', 'Planear retiro a los 60', "
            "'Consolidar deudas de tarjetas'. Required."
        ),
    )
    monto_rango: str | None = Field(
        default=None,
        description=(
            "Rango del monto involucrado en la operación en MXN. "
            "Ejemplo: '50,000-200,000', '1,000,000-5,000,000'. Optional."
        ),
    )
    horizonte_temporal: str | None = Field(
        default=None,
        description=(
            "Horizonte de tiempo para alcanzar el objetivo financiero. "
            "Valores: 'corto_plazo' (< 1 año), 'mediano_plazo' (1-5 años), 'largo_plazo' (> 5 años). Required."
        ),
    )
    prioridad: str | None = Field(
        default=None,
        description=(
            "Nivel de prioridad o urgencia del objetivo financiero. "
            "Valores: 'urgente', 'importante', 'planeado'. Optional."
        ),
    )
    tiene_deuda_existente: bool | None = Field(
        default=None,
        description=(
            "Si el cliente tiene deudas vigentes que puedan afectar su capacidad de pago "
            "o que requieran reestructuración. Optional."
        ),
    )
    productos_existentes: list[str] | None = Field(
        default=None,
        description=(
            "Productos financieros que el cliente ya tiene y que son relevantes para el objetivo. "
            "Ejemplo: 'hipoteca_vigente', 'inversion_cetes', 'seguro_vida'. Optional."
        ),
    )
    tasa_referencia_esperada: str | None = Field(
        default=None,
        description=(
            "Tasa de interés o rendimiento de referencia que el cliente espera o ha visto en el mercado. "
            "Ejemplo: '11% anual', 'TIIE + 3 puntos'. Optional."
        ),
    )


# ── Category 3: Financial Context ───────────────────────────────────


class ContextoFinanciero(BaseModel):
    """Contextual metadata about the financial conversation channel and background."""

    canal: str | None = Field(
        default=None,
        description=(
            "Canal por el que se realiza la asesoría financiera. "
            "Valores: 'sucursal', 'telefono', 'banca_digital', 'whatsapp', 'videollamada'. Required."
        ),
    )
    tipo_institucion: str | None = Field(
        default=None,
        description=(
            "Tipo de institución financiera que brinda la asesoría. "
            "Valores: 'banco', 'fintech', 'casa_bolsa', 'aseguradora', 'cooperativa', "
            "'sofom', 'afore'. Optional."
        ),
    )
    entorno_regulatorio: str | None = Field(
        default=None,
        description=(
            "Marco regulatorio principal que aplica a la conversación. "
            "Valores: 'cnbv', 'condusef', 'sat', 'consar', 'cnsf'. Optional."
        ),
    )
    relacion_cliente: str | None = Field(
        default=None,
        description=(
            "Tipo de relación preexistente entre el cliente y la institución. "
            "Valores: 'nuevo', 'existente', 'reactivacion'. Optional."
        ),
    )
    fuente_referencia: str | None = Field(
        default=None,
        description=(
            "Cómo llegó el cliente a la asesoría. "
            "Valores: 'directo', 'recomendacion', 'campaña', 'cross_sell', 'renovacion_automatica'. Optional."
        ),
    )
    hora_contacto: str | None = Field(
        default=None,
        description=(
            "Momento del día en que ocurre el contacto, relevante para el tono y disponibilidad. "
            "Valores: 'horario_laboral', 'fuera_horario', 'fin_semana'. Optional."
        ),
    )
    idioma_preferido: str | None = Field(
        default=None,
        description=("Idioma preferido del cliente para la comunicación. Valores: 'es', 'en', 'bilingue'. Optional."),
    )


# ── Category 4: Financial Scenario ──────────────────────────────────


class EscenarioFinanciero(BaseModel):
    """Financial scenario configuration for the synthetic conversation."""

    tipo_escenario: str | None = Field(
        default=None,
        description=(
            "Tipo de escenario de asesoría financiera a simular. "
            "Valores: 'apertura_cuenta', 'solicitud_credito', 'asesoria_inversion', "
            "'reclamacion', 'reestructura', 'renovacion', 'educacion_financiera', "
            "'cobranza', 'prevencion_fraude'. Required."
        ),
    )
    complejidad: str | None = Field(
        default=None,
        description=(
            "Nivel de complejidad del escenario financiero. "
            "Valores: 'simple' (producto estándar), 'moderado' (comparación de opciones), "
            "'complejo' (productos estructurados o situaciones irregulares). Required."
        ),
    )
    tono: str | None = Field(
        default=None,
        description=(
            "Tono esperado para la conversación de asesoría. "
            "Valores: 'profesional', 'consultivo', 'educativo', 'empatico'. Required."
        ),
    )
    incluir_divulgacion_riesgo: bool = Field(
        default=True,
        description=(
            "Si se debe incluir la divulgación obligatoria de riesgos asociados al producto. "
            "Obligatoria para inversiones y créditos. Required."
        ),
    )
    incluir_comparacion: bool = Field(
        default=False,
        description=(
            "Si se debe incluir comparación de productos o instituciones para que el cliente "
            "tome una decisión informada. Optional."
        ),
    )
    incluir_simulacion: bool = Field(
        default=False,
        description=(
            "Si se debe incluir una simulación numérica (tabla de amortización, proyección "
            "de rendimientos, cálculo de primas). Optional."
        ),
    )
    incluir_divulgacion_regulatoria: bool = Field(
        default=True,
        description=(
            "Si se deben incluir las divulgaciones regulatorias obligatorias (CAT, GAT, "
            "comisiones, letra chica). Required."
        ),
    )
    incluir_educacion_financiera: bool = Field(
        default=False,
        description=(
            "Si se deben incluir explicaciones educativas sobre conceptos financieros "
            "para clientes con nivel básico. Optional."
        ),
    )


# ── Category 5: Financial Rules ─────────────────────────────────────


class ReglasFinancieras(BaseModel):
    """Domain-specific financial rules and regulatory constraints."""

    marco_cumplimiento: str | None = Field(
        default=None,
        description=(
            "Marco legal y regulatorio principal que rige la conversación. "
            "Valores: 'ley_bancos', 'ley_mercado_valores', 'ley_seguros', 'lfpdppp', "
            "'ley_ahorro_credito_popular', 'ley_fintech'. Optional."
        ),
    )
    nivel_kyc: str | None = Field(
        default=None,
        description=(
            "Nivel de conocimiento del cliente (Know Your Customer) requerido según "
            "el monto y tipo de operación. "
            "Valores: 'simplificado' (< $15,000 MXN), 'normal' (estándar), "
            "'ampliado' (operaciones relevantes > $500,000 MXN). Optional."
        ),
    )
    requiere_firma: bool | None = Field(
        default=None,
        description=(
            "Si la operación requiere firma del cliente (manuscrita, electrónica avanzada "
            "o firma autógrafa digitalizada). Optional."
        ),
    )
    restricciones_producto: list[str] | None = Field(
        default=None,
        description=(
            "Restricciones específicas del producto financiero. "
            "Ejemplos: 'monto_minimo_apertura', 'plazo_forzoso', 'penalizacion_retiro_anticipado', "
            "'solo_personas_fisicas', 'requiere_garantia', 'edad_minima_18'. Optional."
        ),
    )
    divulgacion_comisiones: str | None = Field(
        default=None,
        description=(
            "Nivel de divulgación de comisiones y costos al cliente. "
            "Valores: 'obligatoria' (regulada por CONDUSEF), 'opcional'. Optional."
        ),
    )
    contexto_tasa_interes: str | None = Field(
        default=None,
        description=(
            "Contexto sobre las tasas de interés aplicables al producto. "
            "Ejemplo: 'TIIE + 6 puntos, tasa fija a 12 meses', 'CAT promedio 45%', "
            "'GAT real 3.5% antes de impuestos'. Optional."
        ),
    )
    politica_cancelacion: str | None = Field(
        default=None,
        description=(
            "Política de cancelación o desistimiento del producto. "
            "Ejemplo: 'Cancelación sin penalización en primeros 10 días hábiles', "
            "'Penalización del 3% por liquidación anticipada'. Optional."
        ),
    )
    prevencion_lavado_dinero: str | None = Field(
        default=None,
        description=(
            "Contexto de prevención de lavado de dinero (PLD) aplicable. "
            "Ejemplo: 'Operación sujeta a reporte por monto', 'Requiere origen de recursos'. Optional."
        ),
    )
    proteccion_datos: str | None = Field(
        default=None,
        description=(
            "Aviso de privacidad y manejo de datos personales según LFPDPPP. "
            "Ejemplo: 'Aviso de privacidad integral entregado', 'Consentimiento datos sensibles'. Optional."
        ),
    )


# ── Root Seed Model ──────────────────────────────────────────────────


# Map of field dot-paths that are *required* for completion.
# The State Manager uses this to decide when the seed is ready.
REQUIRED_FIELDS_FINANCE: frozenset[str] = frozenset(
    {
        "cliente_financiero.tipo_cliente",
        "cliente_financiero.perfil_riesgo",
        "cliente_financiero.nivel_conocimiento_financiero",
        "objetivo_financiero.tipo_servicio",
        "objetivo_financiero.objetivo_especifico",
        "objetivo_financiero.horizonte_temporal",
        "contexto_financiero.canal",
        "escenario_financiero.tipo_escenario",
        "escenario_financiero.complejidad",
        "escenario_financiero.tono",
    }
)


class SeedFinance(BaseSeedExtraction):
    """Financial advisory seed schema for agentic extraction.

    Captures all the information needed to generate high-quality synthetic
    conversations for financial advisory assistant fine-tuning in regulated
    markets (Mexican financial system: CNBV, CONDUSEF, SAT).

    Organized in five categories that the Interviewer walks the user through:
    1. Financial client profile (``cliente_financiero``)
    2. Financial objective (``objetivo_financiero``)
    3. Financial context (``contexto_financiero``)
    4. Financial scenario (``escenario_financiero``)
    5. Financial rules (``reglas_financieras``)
    """

    cliente_financiero: ClienteFinanciero = Field(
        default_factory=ClienteFinanciero,
        description="Perfil del cliente financiero que participará en la conversación simulada.",
    )
    objetivo_financiero: ObjetivoFinanciero = Field(
        default_factory=ObjetivoFinanciero,
        description="Detalles sobre el objetivo financiero y producto de interés del cliente.",
    )
    contexto_financiero: ContextoFinanciero = Field(
        default_factory=ContextoFinanciero,
        description="Metadatos sobre el canal, institución y contexto de la asesoría.",
    )
    escenario_financiero: EscenarioFinanciero = Field(
        default_factory=EscenarioFinanciero,
        description="Configuración del escenario de asesoría para la conversación sintética.",
    )
    reglas_financieras: ReglasFinancieras = Field(
        default_factory=ReglasFinancieras,
        description="Reglas regulatorias y restricciones específicas del sector financiero.",
    )

    @classmethod
    def required_field_names(cls) -> frozenset[str]:
        """Return the set of dot-path field names that are required for completion."""
        return REQUIRED_FIELDS_FINANCE

    @classmethod
    def industry_name(cls) -> str:
        """Return the human-readable industry identifier."""
        return "finance"

    @classmethod
    def industry_display(cls, locale: str = "es") -> str:
        """Return localized display name for this industry."""
        names = {"es": "Asesoría Financiera", "en": "Financial Advisory"}
        return names.get(locale, names["en"])

    def to_seed_dict(self) -> dict[str, Any]:
        """Convert extracted financial parameters to a SeedSchema v1 dict.

        Maps the financial extraction fields into the canonical seed format
        used by the SCSF pipeline.  Generates objectives, roles, flow steps,
        constraints, and context tailored to regulated financial advisory
        conversations.
        """
        # ── Build objective from scenario + financial goal ────────────
        tipo_escenario = self.escenario_financiero.tipo_escenario or "asesoria_inversion"
        tipo_servicio = self.objetivo_financiero.tipo_servicio or "asesoria_general"
        objetivo_especifico = self.objetivo_financiero.objetivo_especifico or ""
        tipo_cliente = self.cliente_financiero.tipo_cliente or "persona_fisica"
        perfil_riesgo = self.cliente_financiero.perfil_riesgo or "moderado"

        objetivo = (
            f"Simular una conversación de {tipo_escenario} financiera "
            f"con un cliente {tipo_cliente} (perfil {perfil_riesgo}) "
            f"interesado en {tipo_servicio}"
        )
        if objetivo_especifico:
            objetivo += f": {objetivo_especifico}"

        # ── Build roles ───────────────────────────────────────────────
        nivel_financiero = self.cliente_financiero.nivel_conocimiento_financiero or "basico"
        horizonte = self.objetivo_financiero.horizonte_temporal or "mediano_plazo"
        canal = self.contexto_financiero.canal or "sucursal"

        roles = ["client", "financial_advisor"]
        descripcion_roles: dict[str, str] = {
            "client": (
                f"Cliente {tipo_cliente}, perfil de riesgo: {perfil_riesgo}, "
                f"conocimiento financiero: {nivel_financiero}, "
                f"horizonte: {horizonte}"
            ),
            "financial_advisor": (
                "Asesor financiero certificado con acceso a catálogo de productos, "
                "simuladores y herramientas de análisis de riesgo"
            ),
        }

        # ── Build flow steps ─────────────────────────────────────────
        flujo: list[str] = [
            "Saludo e identificación del cliente",
            "Diagnóstico de necesidades financieras",
        ]

        # Adapt flow based on scenario configuration
        if self.escenario_financiero.incluir_educacion_financiera:
            flujo.append("Educación financiera contextualizada")

        flujo.append("Presentación de producto/solución")

        if self.escenario_financiero.incluir_comparacion:
            flujo.append("Comparación de alternativas")

        if self.escenario_financiero.incluir_simulacion:
            flujo.append("Simulación numérica (amortización/rendimientos/primas)")

        if self.escenario_financiero.incluir_divulgacion_riesgo:
            flujo.append("Divulgación de riesgos asociados")

        if self.escenario_financiero.incluir_divulgacion_regulatoria:
            flujo.append("Divulgaciones regulatorias (CAT/GAT/comisiones)")

        flujo.extend(
            [
                "Documentación y requisitos",
                "Cierre y siguientes pasos",
            ]
        )

        # ── Build constraints from regulatory rules ──────────────────
        restricciones: list[str] = []

        if self.reglas_financieras.restricciones_producto:
            restricciones.extend(self.reglas_financieras.restricciones_producto)

        if self.reglas_financieras.marco_cumplimiento:
            restricciones.append(f"Cumplir con {self.reglas_financieras.marco_cumplimiento}")

        if self.reglas_financieras.divulgacion_comisiones == "obligatoria":
            restricciones.append("Divulgar todas las comisiones y costos asociados de forma transparente")

        if self.reglas_financieras.prevencion_lavado_dinero:
            restricciones.append(f"PLD: {self.reglas_financieras.prevencion_lavado_dinero}")

        if self.reglas_financieras.proteccion_datos:
            restricciones.append(f"Protección de datos: {self.reglas_financieras.proteccion_datos}")

        if self.escenario_financiero.incluir_divulgacion_riesgo:
            restricciones.append("Incluir advertencia obligatoria de riesgos")

        if self.escenario_financiero.incluir_divulgacion_regulatoria:
            restricciones.append("Incluir divulgaciones regulatorias (CAT, GAT, comisiones)")

        if not self.escenario_financiero.incluir_comparacion:
            restricciones.append("No comparar con productos de otras instituciones")

        if self.reglas_financieras.nivel_kyc:
            restricciones.append(f"Nivel KYC requerido: {self.reglas_financieras.nivel_kyc}")

        # ── Build context ────────────────────────────────────────────
        contexto_parts: list[str] = [f"Canal: {canal}"]

        if self.contexto_financiero.tipo_institucion:
            contexto_parts.append(f"Institución: {self.contexto_financiero.tipo_institucion}")

        if self.contexto_financiero.entorno_regulatorio:
            contexto_parts.append(f"Regulador: {self.contexto_financiero.entorno_regulatorio}")

        if self.contexto_financiero.relacion_cliente:
            contexto_parts.append(f"Relación: {self.contexto_financiero.relacion_cliente}")

        if self.contexto_financiero.fuente_referencia:
            contexto_parts.append(f"Fuente: {self.contexto_financiero.fuente_referencia}")

        if self.cliente_financiero.rango_ingresos:
            contexto_parts.append(f"Ingresos: {self.cliente_financiero.rango_ingresos}")

        if self.cliente_financiero.historial_crediticio:
            contexto_parts.append(f"Historial crediticio: {self.cliente_financiero.historial_crediticio}")

        if self.cliente_financiero.situacion_laboral:
            contexto_parts.append(f"Situación laboral: {self.cliente_financiero.situacion_laboral}")

        if self.cliente_financiero.productos_actuales:
            contexto_parts.append(f"Productos actuales: {', '.join(self.cliente_financiero.productos_actuales)}")

        if self.objetivo_financiero.monto_rango:
            contexto_parts.append(f"Monto: {self.objetivo_financiero.monto_rango}")

        if self.objetivo_financiero.tiene_deuda_existente is not None:
            contexto_parts.append(
                f"Deuda existente: {'sí' if self.objetivo_financiero.tiene_deuda_existente else 'no'}"
            )

        if self.reglas_financieras.contexto_tasa_interes:
            contexto_parts.append(f"Tasa referencia: {self.reglas_financieras.contexto_tasa_interes}")

        if self.reglas_financieras.politica_cancelacion:
            contexto_parts.append(f"Cancelación: {self.reglas_financieras.politica_cancelacion}")

        # ── Map tone ─────────────────────────────────────────────────
        tono = self.escenario_financiero.tono or "profesional"

        # ── Build tags ───────────────────────────────────────────────
        etiquetas = ["ai-extracted", "finance"]
        if self.escenario_financiero.complejidad:
            etiquetas.append(f"complexity:{self.escenario_financiero.complejidad}")
        if tipo_servicio:
            etiquetas.append(f"service:{tipo_servicio}")
        if perfil_riesgo:
            etiquetas.append(f"risk:{perfil_riesgo}")

        # ── Build herramientas (tools) ───────────────────────────────
        herramientas: list[str] = []
        if self.escenario_financiero.incluir_simulacion:
            herramientas.append("simulador_financiero")
        if self.escenario_financiero.incluir_comparacion:
            herramientas.append("comparador_productos")
        if self.reglas_financieras.nivel_kyc:
            herramientas.append("verificador_identidad")

        return {
            "version": "1.0",
            "dominio": "finance.advisory",
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
                "herramientas": herramientas,
                "metadata": {
                    "extracted_by": "ai-interview",
                    "scenario_type": tipo_escenario,
                    "complexity": self.escenario_financiero.complejidad or "moderado",
                    "client_type": tipo_cliente,
                    "risk_profile": perfil_riesgo,
                    "financial_literacy": nivel_financiero,
                    "service_type": tipo_servicio,
                    "time_horizon": horizonte,
                    "channel": canal,
                    "institution_type": self.contexto_financiero.tipo_institucion or "banco",
                    "regulatory_environment": self.contexto_financiero.entorno_regulatorio or "cnbv",
                    "kyc_level": self.reglas_financieras.nivel_kyc or "normal",
                    "compliance_framework": self.reglas_financieras.marco_cumplimiento or "ley_bancos",
                    "requires_signature": self.reglas_financieras.requiere_firma or False,
                    "has_existing_debt": self.objetivo_financiero.tiene_deuda_existente or False,
                    "risk_disclosure_included": self.escenario_financiero.incluir_divulgacion_riesgo,
                    "regulatory_disclosure_included": self.escenario_financiero.incluir_divulgacion_regulatoria,
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
