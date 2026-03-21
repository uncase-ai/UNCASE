"""Automotive industry seed schema for agentic extraction.

Defines ``SeedAutomotriz`` — a structured Pydantic model containing all the
fields an interview loop needs to capture for generating synthetic automotive
sales training conversations.  The schema is organized into five nested
categories, each modeled as a separate ``BaseModel``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from uncase.core.seed_engine.layer0.schemas.base import BaseSeedExtraction

# ── Category 1: Client Profile ──────────────────────────────────────


class ClientePerfil(BaseModel):
    """Profile of the customer participating in the conversation."""

    tipo_cliente: str | None = Field(
        default=None,
        description=("Tipo de cliente. Valores posibles: 'particular', 'flotilla', 'empresa', 'revendedor'. Required."),
    )
    nivel_experiencia_compra: str | None = Field(
        default=None,
        description=(
            "Nivel de experiencia del cliente comprando vehículos. "
            "Valores: 'primera_vez', 'ha_comprado_antes', 'comprador_frecuente'. Required."
        ),
    )
    urgencia: str | None = Field(
        default=None,
        description=("Nivel de urgencia de la compra. Valores: 'explorando', 'decidiendo', 'urgente'. Required."),
    )
    presupuesto_rango: str | None = Field(
        default=None,
        description="Rango de presupuesto en formato 'min-max' en MXN o USD. Optional.",
    )
    tiene_vehiculo_actual: bool | None = Field(
        default=None,
        description="Si el cliente tiene un vehículo actualmente. Optional.",
    )
    vehiculo_actual_descripcion: str | None = Field(
        default=None,
        description="Descripción del vehículo actual (marca/modelo/año) si aplica. Optional.",
    )
    forma_pago_preferida: str | None = Field(
        default=None,
        description=("Forma de pago preferida. Valores: 'contado', 'financiamiento', 'mixto'. Optional."),
    )
    rango_edad: str | None = Field(
        default=None,
        description=("Rango de edad del cliente. Valores: '18-25', '26-35', '36-45', '46-55', '56+'. Optional."),
    )
    estado_emocional: str | None = Field(
        default=None,
        description=(
            "Estado emocional predominante del cliente. "
            "Valores: 'entusiasta', 'indeciso', 'desconfiado', 'frustrado', 'racional'. Optional."
        ),
    )
    interes_trade_in: bool | None = Field(
        default=None,
        description="Si el cliente está interesado en dar su vehículo actual a cuenta (trade-in). Optional.",
    )


# ── Category 2: Purchase Intent ─────────────────────────────────────


class Intencion(BaseModel):
    """Purchase intent details."""

    tipo_vehiculo: str | None = Field(
        default=None,
        description=(
            "Tipo de vehículo deseado. "
            "Valores: 'sedan', 'suv', 'pickup', 'hatchback', 'van', 'deportivo', 'otro'. Optional."
        ),
    )
    condicion: str | None = Field(
        default=None,
        description=("Condición del vehículo. Valores: 'nuevo', 'seminuevo', 'certificado'. Optional."),
    )
    marca_preferida: str | None = Field(
        default=None,
        description="Marca preferida del vehículo. Optional.",
    )
    modelo_especifico: str | None = Field(
        default=None,
        description="Modelo específico de interés. Optional.",
    )
    anio_rango: str | None = Field(
        default=None,
        description="Rango de año del vehículo en formato 'min-max'. Optional.",
    )
    uso_principal: str | None = Field(
        default=None,
        description=(
            "Uso principal del vehículo. Valores: 'personal', 'trabajo', 'familia', 'negocio', 'mixto'. Required."
        ),
    )
    caracteristicas_importantes: list[str] | None = Field(
        default=None,
        description=(
            "Características importantes para el cliente. Ejemplos: 'rendimiento', 'seguridad', 'tecnología', "
            "'espacio', 'consumo_combustible', 'diseño'. Optional."
        ),
    )
    factores_decision: list[str] | None = Field(
        default=None,
        description=(
            "Factores decisivos de compra. Ejemplos: 'precio', 'garantía', 'reputación', "
            "'disponibilidad', 'financiamiento', 'valor_reventa'. Optional."
        ),
    )
    numero_pasajeros: int | None = Field(
        default=None,
        description="Número de pasajeros habituales. Optional.",
    )


# ── Category 3: Conversation Context ────────────────────────────────


class ContextoConversacion(BaseModel):
    """Contextual metadata about the conversation channel and background."""

    canal: str | None = Field(
        default=None,
        description=(
            "Canal de la conversación. "
            "Valores: 'presencial', 'whatsapp', 'telefono', 'web_chat', 'redes_sociales'. Required."
        ),
    )
    viene_de_otra_agencia: bool | None = Field(
        default=None,
        description="Si el cliente viene de otra agencia. Optional.",
    )
    motivo_cambio: str | None = Field(
        default=None,
        description="Razón por la que el cliente cambió de agencia (si aplica). Optional.",
    )
    objeciones_conocidas: list[str] | None = Field(
        default=None,
        description=(
            "Objeciones conocidas del cliente. Ejemplos: 'precio_alto', 'no_confia_en_usados', "
            "'tiempo_entrega', 'mal_servicio_previo'. Optional."
        ),
    )
    nivel_conocimiento_tecnico: str | None = Field(
        default=None,
        description=(
            "Nivel de conocimiento técnico del cliente sobre vehículos. Valores: 'bajo', 'medio', 'alto'. Optional."
        ),
    )
    horario_contacto: str | None = Field(
        default=None,
        description=(
            "Preferencia de horario de contacto. Valores: 'manana', 'tarde', 'noche', 'cualquier_hora'. Optional."
        ),
    )
    region_geografica: str | None = Field(
        default=None,
        description="Región o ciudad del cliente para contextualizar disponibilidad y precios. Optional.",
    )


# ── Category 4: Sales Scenario ──────────────────────────────────────


class Escenario(BaseModel):
    """Sales scenario configuration for the synthetic conversation."""

    tipo_escenario: str | None = Field(
        default=None,
        description=(
            "Tipo de escenario de ventas. "
            "Valores: 'venta_directa', 'seguimiento', 'recuperacion', 'cotizacion', 'postventa'. Required."
        ),
    )
    complejidad: str | None = Field(
        default=None,
        description=("Nivel de complejidad del escenario. Valores: 'simple', 'medio', 'complejo'. Required."),
    )
    tono_esperado: str | None = Field(
        default=None,
        description=(
            "Tono esperado para la conversación. Valores: 'formal', 'casual', 'tecnico', 'empático'. Required."
        ),
    )
    incluir_objeciones: bool = Field(
        default=True,
        description="Si se deben incluir objeciones del cliente en la conversación. Required.",
    )
    incluir_negociacion: bool = Field(
        default=False,
        description="Si se debe incluir una fase de negociación de precio. Required.",
    )
    incluir_comparacion_competencia: bool = Field(
        default=False,
        description="Si se debe incluir comparación con la competencia. Optional.",
    )


# ── Category 5: Business Rules ──────────────────────────────────────


class ReglasNegocio(BaseModel):
    """Domain-specific business rules and constraints."""

    politica_descuento: str | None = Field(
        default=None,
        description="Política de descuentos de la agencia (texto libre). Optional.",
    )
    condiciones_financiamiento: str | None = Field(
        default=None,
        description="Condiciones o requisitos de financiamiento. Optional.",
    )
    inventario_disponible_contexto: str | None = Field(
        default=None,
        description=("Contexto del inventario disponible. Ejemplo: 'solo SUVs y pickups disponibles'. Optional."),
    )
    restricciones: list[str] | None = Field(
        default=None,
        description=(
            "Restricciones de la conversación. Ejemplos: 'no_mencionar_competencia', 'no_prometer_fechas'. Optional."
        ),
    )
    garantia_info: str | None = Field(
        default=None,
        description="Información sobre la garantía ofrecida (duración, cobertura). Optional.",
    )
    proceso_entrega: str | None = Field(
        default=None,
        description="Descripción del proceso de entrega del vehículo. Optional.",
    )
    documentacion_requerida: list[str] | None = Field(
        default=None,
        description=(
            "Documentos que el cliente necesita presentar. "
            "Ejemplos: 'INE', 'comprobante_domicilio', 'estados_cuenta'. Optional."
        ),
    )


# ── Root Seed Model ─────────────────────────────────────────────────


# Map of field dot-paths that are *required* for completion.
# The State Manager uses this to decide when the seed is ready.
REQUIRED_FIELDS_AUTOMOTRIZ: frozenset[str] = frozenset(
    {
        "cliente_perfil.tipo_cliente",
        "cliente_perfil.nivel_experiencia_compra",
        "cliente_perfil.urgencia",
        "intencion.uso_principal",
        "contexto_conversacion.canal",
        "escenario.tipo_escenario",
        "escenario.complejidad",
        "escenario.tono_esperado",
    }
)


class SeedAutomotriz(BaseSeedExtraction):
    """Automotive industry seed schema for agentic extraction.

    Captures all the information needed to generate high-quality synthetic
    conversations for automotive sales assistant fine-tuning.

    Organized in five categories that the Interviewer walks the user through:
    1. Client profile (``cliente_perfil``)
    2. Purchase intent (``intencion``)
    3. Conversation context (``contexto_conversacion``)
    4. Sales scenario (``escenario``)
    5. Business rules (``reglas_negocio``)
    """

    cliente_perfil: ClientePerfil = Field(
        default_factory=ClientePerfil,
        description="Perfil del cliente que participará en la conversación simulada.",
    )
    intencion: Intencion = Field(
        default_factory=Intencion,
        description="Detalles sobre la intención de compra del cliente.",
    )
    contexto_conversacion: ContextoConversacion = Field(
        default_factory=ContextoConversacion,
        description="Metadatos sobre el canal y contexto de la conversación.",
    )
    escenario: Escenario = Field(
        default_factory=Escenario,
        description="Configuración del escenario de ventas para la conversación sintética.",
    )
    reglas_negocio: ReglasNegocio = Field(
        default_factory=ReglasNegocio,
        description="Reglas de negocio y restricciones específicas del dominio.",
    )

    @classmethod
    def required_field_names(cls) -> frozenset[str]:
        """Return the set of dot-path field names that are required for completion."""
        return REQUIRED_FIELDS_AUTOMOTRIZ

    @classmethod
    def industry_name(cls) -> str:
        """Return the human-readable industry identifier."""
        return "automotive"

    @classmethod
    def industry_display(cls, locale: str = "es") -> str:
        """Return localized display name for this industry."""
        names = {"es": "Ventas Automotrices", "en": "Automotive Sales"}
        return names.get(locale, names["en"])

    def to_seed_dict(self) -> dict[str, Any]:
        """Convert extracted automotive parameters to a SeedSchema v1 dict.

        Maps the automotive extraction fields into the canonical seed format
        used by the SCSF pipeline.
        """
        # Build objective from scenario + intent
        scenario_type = self.escenario.tipo_escenario or "venta_directa"
        uso = self.intencion.uso_principal or "general"
        tipo_cliente = self.cliente_perfil.tipo_cliente or "particular"
        condicion = self.intencion.condicion or "nuevo"
        vehiculo_desc = ""
        if self.intencion.marca_preferida:
            vehiculo_desc = f" de {self.intencion.marca_preferida}"
            if self.intencion.modelo_especifico:
                vehiculo_desc += f" {self.intencion.modelo_especifico}"
        tipo_veh = self.intencion.tipo_vehiculo or "vehículo"

        objetivo = (
            f"Simular una conversación de {scenario_type} automotriz "
            f"con un cliente {tipo_cliente} interesado en un {tipo_veh} "
            f"{condicion}{vehiculo_desc} para uso {uso}"
        )

        # Build roles based on client profile
        nivel = self.cliente_perfil.nivel_experiencia_compra or "primera_vez"
        urgencia = self.cliente_perfil.urgencia or "explorando"
        canal = self.contexto_conversacion.canal or "presencial"

        roles = ["customer", "sales_advisor"]

        # Rich customer description
        customer_parts = [f"Cliente {tipo_cliente}"]
        customer_parts.append(f"experiencia: {nivel}")
        customer_parts.append(f"urgencia: {urgencia}")
        if self.cliente_perfil.rango_edad:
            customer_parts.append(f"edad: {self.cliente_perfil.rango_edad}")
        if self.cliente_perfil.estado_emocional:
            customer_parts.append(f"estado emocional: {self.cliente_perfil.estado_emocional}")
        if self.cliente_perfil.forma_pago_preferida:
            customer_parts.append(f"pago: {self.cliente_perfil.forma_pago_preferida}")

        # Rich advisor description
        advisor_parts = ["Asesor de ventas certificado con acceso al inventario"]
        if self.reglas_negocio.garantia_info:
            advisor_parts.append(f"Garantía: {self.reglas_negocio.garantia_info}")
        if self.reglas_negocio.politica_descuento:
            advisor_parts.append(f"Descuentos: {self.reglas_negocio.politica_descuento}")

        descripcion_roles: dict[str, str] = {
            "customer": ", ".join(customer_parts),
            "sales_advisor": ". ".join(advisor_parts),
        }

        # Build flow steps based on scenario complexity
        complejidad = self.escenario.complejidad or "medio"
        flujo: list[str] = ["Saludo y bienvenida", "Detección de necesidades"]

        if self.cliente_perfil.tiene_vehiculo_actual or self.cliente_perfil.interes_trade_in:
            flujo.append("Evaluación de vehículo actual / trade-in")

        flujo.append("Presentación de opciones")

        if self.escenario.incluir_comparacion_competencia:
            flujo.append("Comparación con competencia")

        if self.escenario.incluir_objeciones:
            flujo.append("Manejo de objeciones")

        if self.escenario.incluir_negociacion:
            flujo.append("Negociación de precio y condiciones")

        flujo.append("Cotización formal")

        if self.reglas_negocio.condiciones_financiamiento:
            flujo.append("Opciones de financiamiento")

        flujo.append("Cierre y siguiente paso")

        # Build constraints
        restricciones: list[str] = list(self.reglas_negocio.restricciones or [])
        if not self.escenario.incluir_negociacion:
            restricciones.append("No incluir negociación de precios")
        if not self.escenario.incluir_comparacion_competencia:
            restricciones.append("No comparar con la competencia")

        # Build rich context
        contexto_parts: list[str] = [f"Canal: {canal}"]
        if self.intencion.tipo_vehiculo:
            contexto_parts.append(f"Tipo de vehículo: {self.intencion.tipo_vehiculo}")
        if self.intencion.condicion:
            contexto_parts.append(f"Condición: {self.intencion.condicion}")
        if self.intencion.marca_preferida:
            contexto_parts.append(f"Marca: {self.intencion.marca_preferida}")
        if self.intencion.modelo_especifico:
            contexto_parts.append(f"Modelo: {self.intencion.modelo_especifico}")
        if self.intencion.anio_rango:
            contexto_parts.append(f"Año: {self.intencion.anio_rango}")
        if self.intencion.numero_pasajeros:
            contexto_parts.append(f"Pasajeros: {self.intencion.numero_pasajeros}")
        if self.cliente_perfil.presupuesto_rango:
            contexto_parts.append(f"Presupuesto: {self.cliente_perfil.presupuesto_rango}")
        if self.cliente_perfil.vehiculo_actual_descripcion:
            contexto_parts.append(f"Vehículo actual: {self.cliente_perfil.vehiculo_actual_descripcion}")
        if self.reglas_negocio.inventario_disponible_contexto:
            contexto_parts.append(f"Inventario: {self.reglas_negocio.inventario_disponible_contexto}")
        if self.reglas_negocio.condiciones_financiamiento:
            contexto_parts.append(f"Financiamiento: {self.reglas_negocio.condiciones_financiamiento}")
        if self.contexto_conversacion.region_geografica:
            contexto_parts.append(f"Región: {self.contexto_conversacion.region_geografica}")
        if self.intencion.caracteristicas_importantes:
            contexto_parts.append(f"Prioridades: {', '.join(self.intencion.caracteristicas_importantes)}")
        if self.contexto_conversacion.objeciones_conocidas:
            contexto_parts.append(f"Objeciones previstas: {', '.join(self.contexto_conversacion.objeciones_conocidas)}")

        # Build tools list based on scenario
        herramientas: list[str] = ["consultar_inventario", "generar_cotizacion"]
        if self.reglas_negocio.condiciones_financiamiento:
            herramientas.append("calcular_financiamiento")
        if self.cliente_perfil.interes_trade_in:
            herramientas.append("evaluar_trade_in")
        if self.escenario.incluir_comparacion_competencia:
            herramientas.append("comparar_modelos")

        # Map tone
        tono = self.escenario.tono_esperado or "profesional"

        # Build tags
        etiquetas = ["ai-extracted", "automotive", f"scenario:{scenario_type}"]
        if complejidad:
            etiquetas.append(f"complexity:{complejidad}")
        if condicion != "nuevo":
            etiquetas.append(f"condition:{condicion}")

        # Adjust turn count based on complexity
        turnos_map = {"simple": (3, 6), "medio": (5, 10), "complejo": (8, 15)}
        turnos_min, turnos_max = turnos_map.get(complejidad, (5, 10))

        return {
            "version": "1.0",
            "dominio": "automotive.sales",
            "idioma": self.idioma,
            "etiquetas": etiquetas,
            "roles": roles,
            "descripcion_roles": descripcion_roles,
            "objetivo": objetivo,
            "tono": tono,
            "pasos_turnos": {
                "turnos_min": turnos_min,
                "turnos_max": turnos_max,
                "flujo_esperado": flujo,
            },
            "parametros_factuales": {
                "contexto": ". ".join(contexto_parts),
                "restricciones": restricciones,
                "herramientas": herramientas,
                "metadata": {
                    "extracted_by": "ai-interview",
                    "scenario_type": scenario_type,
                    "complexity": complejidad,
                    "client_type": tipo_cliente,
                    "experience_level": nivel,
                    "urgency": urgencia,
                    "channel": canal,
                    "vehicle_condition": condicion,
                    "vehicle_type": self.intencion.tipo_vehiculo,
                    "payment_method": self.cliente_perfil.forma_pago_preferida,
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
