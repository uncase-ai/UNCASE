"""Automotive sales domain — 50 curated seed definitions.

Seeds cover the full spectrum of dealership interactions: vehicle inquiry,
test drives, financing, trade-ins, service appointments, warranty, parts,
fleet sales, insurance, and post-purchase follow-up.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

AUTOMOTIVE_SEEDS: list[dict[str, object]] = [
    # -------------------------------------------------------------------------
    # 1-5: New car inquiry / test drive scheduling
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor comercial de concesionaria",
            "Cliente": "Persona interesada en adquirir un vehículo nuevo",
        },
        "objetivo": "Cliente consulta disponibilidad y características de un sedán compacto nuevo modelo 2026",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Saludo y bienvenida",
                "Identificación de necesidades",
                "Presentación de opciones disponibles",
                "Discusión de características y equipamiento",
                "Propuesta de prueba de manejo",
                "Cierre y próximos pasos",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria de marca generalista con inventario de sedanes compactos 2026",
            "restricciones": [
                "No mencionar precios exactos sin consultar sistema",
                "Verificar disponibilidad en inventario antes de confirmar",
            ],
            "metadata": {
                "tipo_operacion": "venta_nuevo",
                "segmento": "sedan_compacto",
                "anio_modelo": "2026",
            },
        },
        "etiquetas": ["venta_nuevo", "sedan", "consulta_inicial", "inventario"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor comercial especializado en SUVs",
            "Cliente": "Familia buscando SUV de 7 pasajeros",
        },
        "objetivo": "Familia consulta opciones de SUV de 7 pasajeros para uso urbano y carretero",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Saludo y presentación",
                "Exploración de necesidades familiares",
                "Presentación de modelos SUV disponibles",
                "Comparación de versiones y equipamiento",
                "Discusión de espacio y seguridad",
                "Agenda de prueba de manejo",
                "Información de financiamiento preliminar",
                "Cierre con compromiso de seguimiento",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con gama completa de SUVs medianas y grandes",
            "restricciones": [
                "Enfatizar sistemas de seguridad para familias",
                "Ofrecer comparativo entre versiones",
            ],
            "metadata": {
                "tipo_operacion": "venta_nuevo",
                "segmento": "suv_7_pasajeros",
                "anio_modelo": "2026",
            },
        },
        "etiquetas": ["venta_nuevo", "suv", "familia", "7_pasajeros", "seguridad"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de ventas de piso",
            "Cliente": "Joven profesional interesado en su primer auto",
        },
        "objetivo": "Primer comprador solicita orientación sobre opciones de vehículo económico y confiable",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 16,
            "flujo_esperado": [
                "Bienvenida y primer contacto",
                "Evaluación de presupuesto y necesidades",
                "Explicación de categorías de vehículos",
                "Presentación de opciones económicas",
                "Discusión de costos de mantenimiento",
                "Propuesta de siguiente paso",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con línea de vehículos de entrada y subcompactos",
            "restricciones": [
                "Explicar terminología básica al ser primer comprador",
                "Incluir estimado de costos de mantenimiento anual",
            ],
            "metadata": {
                "tipo_operacion": "venta_nuevo",
                "segmento": "subcompacto",
                "perfil_cliente": "primer_comprador",
            },
        },
        "etiquetas": ["venta_nuevo", "primer_comprador", "economico", "orientacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de pruebas de manejo",
            "Cliente": "Interesado en probar pickup de trabajo",
        },
        "objetivo": "Agendar y preparar prueba de manejo para pickup doble cabina de uso mixto",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Confirmación de interés en prueba de manejo",
                "Verificación de licencia y requisitos",
                "Selección de modelo y versión a probar",
                "Explicación de la ruta de prueba",
                "Agenda de fecha y hora",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con área de prueba de manejo para pickups y vehículos de trabajo",
            "restricciones": [
                "Verificar licencia vigente antes de confirmar",
                "Confirmar disponibilidad de unidad demo",
            ],
            "metadata": {
                "tipo_operacion": "prueba_manejo",
                "segmento": "pickup",
                "uso": "mixto_trabajo_personal",
            },
        },
        "etiquetas": ["prueba_manejo", "pickup", "trabajo", "agenda"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Sales Advisor", "Customer"],
        "descripcion_roles": {
            "Sales Advisor": "Dealership sales consultant specializing in electric vehicles",
            "Customer": "Environmentally conscious buyer exploring EV options",
        },
        "objetivo": "Customer inquires about electric vehicle range, charging infrastructure, and incentives",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Greeting and introduction",
                "Understanding driving habits and range needs",
                "Presenting EV models and specifications",
                "Discussing charging options and infrastructure",
                "Explaining government incentives and tax credits",
                "Comparing total cost of ownership vs ICE",
                "Scheduling test drive",
                "Follow-up plan",
            ],
        },
        "parametros_factuales": {
            "contexto": "Dealership with full EV lineup including sedans, SUVs, and crossovers",
            "restricciones": [
                "Provide accurate range estimates based on EPA ratings",
                "Disclose current incentive programs without guarantees",
            ],
            "metadata": {
                "tipo_operacion": "venta_nuevo",
                "segmento": "electrico",
                "anio_modelo": "2026",
            },
        },
        "etiquetas": ["new_sale", "electric_vehicle", "ev", "incentives", "charging"],
    },
    # -------------------------------------------------------------------------
    # 6-10: Used car negotiation / trade-in valuation
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de vehículos seminuevos",
            "Cliente": "Comprador buscando auto usado certificado",
        },
        "objetivo": "Negociación de precio para vehículo seminuevo certificado con garantía extendida",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Presentación del vehículo y su historial",
                "Revisión del reporte de condición",
                "Discusión de precio de lista",
                "Negociación de descuento",
                "Presentación de garantía extendida",
                "Acuerdo preliminar",
                "Pasos para formalizar la compra",
            ],
        },
        "parametros_factuales": {
            "contexto": "Lote de seminuevos certificados con historial de servicio completo",
            "restricciones": [
                "Mostrar reporte de inspección de puntos antes de negociar",
                "Máximo de descuento autorizado sin aprobación gerencial es 5%",
            ],
            "metadata": {
                "tipo_operacion": "venta_seminuevo",
                "certificado": "si",
                "garantia_meses": "12",
            },
        },
        "etiquetas": ["seminuevo", "certificado", "negociacion", "garantia"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Valuador", "Cliente"],
        "descripcion_roles": {
            "Valuador": "Especialista en valuación de vehículos usados",
            "Cliente": "Propietario que desea conocer el valor de su auto actual",
        },
        "objetivo": "Valuación de auto usado para posible trade-in como enganche de unidad nueva",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Recepción de datos del vehículo a valuar",
                "Inspección visual y mecánica",
                "Consulta de libro azul y mercado",
                "Presentación de oferta de toma",
                "Explicación de factores de ajuste",
                "Decisión del cliente",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de valuaciones con acceso a guías de precios y mercado local",
            "restricciones": [
                "La valuación expira en 7 días hábiles",
                "Descontar por daños estéticos y mecánicos detectados",
            ],
            "metadata": {
                "tipo_operacion": "trade_in",
                "metodo_valuacion": "libro_azul_mas_mercado",
            },
        },
        "etiquetas": ["trade_in", "valuacion", "usado", "enganche"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de vehículos de segunda mano",
            "Cliente": "Comprador con presupuesto limitado buscando auto funcional",
        },
        "objetivo": "Asesoría para compra de vehículo usado económico con prioridad en confiabilidad",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Identificación de presupuesto y necesidades",
                "Presentación de opciones en rango de precio",
                "Revisión de historial de mantenimiento",
                "Explicación de condiciones de venta",
                "Discusión de formas de pago",
                "Cierre o reprogramación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Inventario de vehículos usados con rango de precios accesible",
            "restricciones": [
                "Todos los vehículos deben tener verificación vehicular vigente",
                "Informar sobre reporte de accidentes si existe",
            ],
            "metadata": {
                "tipo_operacion": "venta_usado",
                "rango_precio": "economico",
            },
        },
        "etiquetas": ["usado", "economico", "confiabilidad", "presupuesto_limitado"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor senior de seminuevos premium",
            "Cliente": "Comprador de vehículo de lujo en el mercado secundario",
        },
        "objetivo": "Venta de vehículo premium seminuevo con paquete de servicios exclusivos",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 22,
            "flujo_esperado": [
                "Recepción personalizada del cliente",
                "Identificación de preferencias de marca y modelo",
                "Presentación de unidades premium disponibles",
                "Recorrido detallado del vehículo seleccionado",
                "Revisión de historial y certificaciones",
                "Presentación de paquete de servicios exclusivos",
                "Negociación de precio y condiciones",
                "Acuerdo y proceso de entrega personalizada",
            ],
        },
        "parametros_factuales": {
            "contexto": "Sección premium de concesionaria con vehículos de lujo certificados",
            "restricciones": [
                "Cada unidad premium incluye inspección de 200 puntos",
                "Ofrecer entrega a domicilio sin costo adicional",
            ],
            "metadata": {
                "tipo_operacion": "venta_seminuevo",
                "segmento": "premium",
                "certificacion": "200_puntos",
            },
        },
        "etiquetas": ["seminuevo", "premium", "lujo", "servicio_exclusivo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Sales Advisor", "Customer"],
        "descripcion_roles": {
            "Sales Advisor": "Pre-owned vehicle specialist",
            "Customer": "Buyer looking to trade in current vehicle for an upgrade",
        },
        "objetivo": "Trade-in appraisal and upgrade negotiation for a mid-size SUV",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Welcome and trade-in vehicle details",
                "Walk-around inspection of trade-in",
                "Market value assessment presentation",
                "New vehicle selection and comparison",
                "Price difference negotiation",
                "Financing options for the balance",
                "Agreement on terms",
                "Paperwork scheduling",
            ],
        },
        "parametros_factuales": {
            "contexto": "Dealership with certified pre-owned program and trade-in appraisal center",
            "restricciones": [
                "Trade-in value valid for 5 business days",
                "Must disclose any prior accident history from Carfax equivalent",
            ],
            "metadata": {
                "tipo_operacion": "trade_in_upgrade",
                "segmento": "mid_size_suv",
            },
        },
        "etiquetas": ["trade_in", "upgrade", "negotiation", "pre_owned"],
    },
    # -------------------------------------------------------------------------
    # 11-15: Financing options discussion
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente Financiero", "Cliente"],
        "descripcion_roles": {
            "Gerente Financiero": "Responsable de planes de financiamiento en concesionaria",
            "Cliente": "Comprador que requiere financiamiento para vehículo nuevo",
        },
        "objetivo": "Presentación y comparación de planes de financiamiento para compra de auto nuevo",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Introducción y contexto de la compra",
                "Evaluación de perfil crediticio del cliente",
                "Presentación de opciones de crédito bancario",
                "Presentación de crédito de financiera cautiva",
                "Comparativo de tasas, plazos y mensualidades",
                "Discusión de enganche y seguros",
                "Selección de plan preferido",
                "Documentación requerida y siguientes pasos",
            ],
        },
        "parametros_factuales": {
            "contexto": "Área financiera con convenios con bancos y financiera de marca",
            "restricciones": [
                "Informar CAT (Costo Anual Total) en todas las opciones",
                "No comprometer aprobación sin pre-autorización bancaria",
            ],
            "metadata": {
                "tipo_operacion": "financiamiento",
                "tipo_credito": "automotriz",
                "plazos_disponibles": "12,24,36,48,60",
            },
        },
        "etiquetas": ["financiamiento", "credito", "tasas", "comparativo", "nuevo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente Financiero", "Cliente"],
        "descripcion_roles": {
            "Gerente Financiero": "Especialista en créditos automotrices",
            "Cliente": "Comprador que busca la mensualidad más baja posible",
        },
        "objetivo": "Estructuración de crédito con enganche alto para minimizar mensualidad",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 16,
            "flujo_esperado": [
                "Revisión de monto de enganche disponible",
                "Cálculo de diferentes escenarios de plazo",
                "Presentación de tabla de amortización simplificada",
                "Discusión de seguros incluidos vs opcionales",
                "Selección de esquema óptimo",
                "Preparación de solicitud",
            ],
        },
        "parametros_factuales": {
            "contexto": "Cliente con capacidad de enganche superior al 30% del valor del vehículo",
            "restricciones": [
                "Enganche mínimo aceptado es 10% del valor del auto",
                "Plazo máximo 60 meses sin penalización por pago anticipado",
            ],
            "metadata": {
                "tipo_operacion": "financiamiento",
                "estrategia": "minimizar_mensualidad",
                "enganche_porcentaje": "30_plus",
            },
        },
        "etiquetas": ["financiamiento", "enganche_alto", "mensualidad_baja", "amortizacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente Financiero", "Cliente"],
        "descripcion_roles": {
            "Gerente Financiero": "Asesor de planes de arrendamiento",
            "Cliente": "Profesionista que prefiere arrendar en lugar de comprar",
        },
        "objetivo": "Explicación y contratación de plan de arrendamiento puro para profesionista",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Exploración del perfil fiscal del cliente",
                "Explicación de arrendamiento puro vs financiero",
                "Beneficios fiscales para persona física con actividad empresarial",
                "Presentación de rentas mensuales y valor residual",
                "Discusión de kilometraje permitido y penalizaciones",
                "Opciones al término del contrato",
                "Documentación requerida",
                "Compromiso y firma de solicitud",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de arrendamiento puro con beneficios fiscales para empresarios",
            "restricciones": [
                "Deducibilidad máxima conforme a legislación fiscal vigente",
                "Kilometraje anual estándar de 20,000 km",
            ],
            "metadata": {
                "tipo_operacion": "arrendamiento",
                "tipo_arrendamiento": "puro",
                "plazo_meses": "36",
            },
        },
        "etiquetas": ["arrendamiento", "leasing", "fiscal", "profesionista"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente Financiero", "Cliente"],
        "descripcion_roles": {
            "Gerente Financiero": "Responsable de reestructuración de créditos",
            "Cliente": "Propietario con dificultades para cubrir mensualidades actuales",
        },
        "objetivo": "Reestructuración de crédito automotriz por dificultades económicas del cliente",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Escucha activa de la situación del cliente",
                "Revisión del estado actual del crédito",
                "Presentación de opciones de reestructuración",
                "Análisis de extensión de plazo",
                "Discusión de período de gracia",
                "Impacto en costo total del crédito",
                "Selección de opción y documentación",
                "Confirmación de nuevas condiciones",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de cobranza y reestructuración con políticas de apoyo al cliente",
            "restricciones": [
                "Reestructuración solo disponible para clientes con historial de pago de al menos 6 meses",
                "No se condona capital, solo se ajustan plazos e intereses",
            ],
            "metadata": {
                "tipo_operacion": "reestructuracion",
                "motivo": "dificultad_economica",
            },
        },
        "etiquetas": ["financiamiento", "reestructuracion", "cobranza", "apoyo_cliente"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Finance Manager", "Customer"],
        "descripcion_roles": {
            "Finance Manager": "Dealership F&I specialist",
            "Customer": "First-time buyer with limited credit history",
        },
        "objetivo": "Financing guidance for a first-time buyer with thin credit file",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Introduction and credit situation overview",
                "Explanation of credit score impact on rates",
                "First-time buyer programs available",
                "Co-signer option discussion",
                "Down payment strategies",
                "Pre-approval process explanation",
                "Document checklist",
                "Next steps and timeline",
            ],
        },
        "parametros_factuales": {
            "contexto": "Dealership with first-time buyer program through captive finance and partner banks",
            "restricciones": [
                "Minimum down payment for thin-file buyers is 15%",
                "Co-signer must have credit score above threshold defined by lender",
            ],
            "metadata": {
                "tipo_operacion": "financing",
                "program": "first_time_buyer",
                "credit_profile": "thin_file",
            },
        },
        "etiquetas": ["financing", "first_time_buyer", "credit", "down_payment"],
    },
    # -------------------------------------------------------------------------
    # 16-20: Service appointment booking
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Recepcionista del taller de servicio de concesionaria",
            "Cliente": "Propietario que necesita servicio de mantenimiento programado",
        },
        "objetivo": "Agendar servicio de mantenimiento de los 30,000 km para sedán",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Identificación del vehículo y cliente en sistema",
                "Revisión del historial de servicios",
                "Detalle de trabajos incluidos en servicio de 30k",
                "Cotización estimada y tiempo de entrega",
                "Selección de fecha y hora",
            ],
        },
        "parametros_factuales": {
            "contexto": "Taller de servicio autorizado con agenda de citas digitales",
            "restricciones": [
                "Servicios de mantenimiento deben seguir el programa del fabricante",
                "Informar costo estimado antes de confirmar cita",
            ],
            "metadata": {
                "tipo_servicio": "mantenimiento_programado",
                "kilometraje": "30000",
            },
        },
        "etiquetas": ["servicio", "mantenimiento", "cita", "30k"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Técnico recepcionista de taller",
            "Cliente": "Propietario que reporta falla mecánica inesperada",
        },
        "objetivo": "Diagnóstico inicial y programación de reparación correctiva por falla en transmisión",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 16,
            "flujo_esperado": [
                "Descripción de síntomas por parte del cliente",
                "Preguntas de diagnóstico inicial",
                "Explicación del proceso de diagnóstico electrónico",
                "Estimado de tiempo y costo del diagnóstico",
                "Programación de cita para diagnóstico",
                "Opciones de movilidad alternativa durante reparación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Taller con equipo de diagnóstico electrónico avanzado",
            "restricciones": [
                "Diagnóstico tiene costo independiente de la reparación",
                "No se inicia reparación sin autorización escrita del cliente",
            ],
            "metadata": {
                "tipo_servicio": "reparacion_correctiva",
                "sistema_afectado": "transmision",
            },
        },
        "etiquetas": ["servicio", "reparacion", "diagnostico", "transmision", "falla"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Coordinador de servicio express",
            "Cliente": "Propietario que necesita cambio de aceite rápido",
        },
        "objetivo": "Atención express para cambio de aceite y filtros sin cita previa",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 4,
            "turnos_max": 10,
            "flujo_esperado": [
                "Recepción sin cita y verificación de disponibilidad",
                "Confirmación de tipo de aceite y filtros requeridos",
                "Informar tiempo estimado y precio",
                "Entrega del vehículo y revisión de puntos básicos",
            ],
        },
        "parametros_factuales": {
            "contexto": "Bahía de servicio express con atención sin cita",
            "restricciones": [
                "Servicio express no aplica si se detectan fallas adicionales",
                "Tiempo máximo de espera ofrecido: 45 minutos",
            ],
            "metadata": {
                "tipo_servicio": "express",
                "trabajo": "cambio_aceite_filtros",
            },
        },
        "etiquetas": ["servicio", "express", "aceite", "sin_cita"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Coordinador de servicio de carrocería y pintura",
            "Cliente": "Propietario con daños estéticos menores tras incidente de estacionamiento",
        },
        "objetivo": "Cotización y programación de reparación de carrocería por golpe menor",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Inspección visual del daño",
                "Documentación fotográfica",
                "Cotización detallada de reparación",
                "Discusión de opciones: reparación vs reemplazo",
                "Coordinación con aseguradora si aplica",
                "Programación de ingreso al taller",
            ],
        },
        "parametros_factuales": {
            "contexto": "Taller de carrocería y pintura autorizado con cabina de pintura",
            "restricciones": [
                "Usar solo refacciones originales para mantener garantía",
                "Trabajo de pintura requiere mínimo 3 días hábiles",
            ],
            "metadata": {
                "tipo_servicio": "carroceria",
                "tipo_dano": "golpe_menor",
            },
        },
        "etiquetas": ["servicio", "carroceria", "pintura", "cotizacion", "estetico"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Service Advisor", "Customer"],
        "descripcion_roles": {
            "Service Advisor": "Dealership service department front desk",
            "Customer": "Vehicle owner scheduling routine tire rotation and brake inspection",
        },
        "objetivo": "Schedule tire rotation and brake inspection with multi-point vehicle check",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Greeting and vehicle identification",
                "Service history review",
                "Tire and brake service details and pricing",
                "Multi-point inspection add-on offer",
                "Appointment scheduling",
            ],
        },
        "parametros_factuales": {
            "contexto": "Full-service dealership with dedicated tire and brake department",
            "restricciones": [
                "Tire rotation included in maintenance package if applicable",
                "Brake inspection report provided within 1 hour",
            ],
            "metadata": {
                "tipo_servicio": "routine_maintenance",
                "trabajo": "tire_rotation_brake_inspection",
            },
        },
        "etiquetas": ["service", "tires", "brakes", "inspection", "appointment"],
    },
    # -------------------------------------------------------------------------
    # 21-25: Warranty claims / recall inquiries
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Especialista en reclamos de garantía",
            "Cliente": "Propietario con falla cubierta por garantía de fábrica",
        },
        "objetivo": "Gestión de reclamo de garantía por falla en sistema eléctrico de vehículo con 18 meses de uso",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Recepción y registro del reclamo",
                "Verificación de cobertura de garantía vigente",
                "Descripción detallada de la falla",
                "Diagnóstico técnico preliminar",
                "Apertura de orden de servicio en garantía",
                "Explicación del proceso y tiempos",
                "Ofrecimiento de auto sustituto",
                "Seguimiento y compromiso de comunicación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de garantías con sistema de gestión de reclamos del fabricante",
            "restricciones": [
                "Garantía de fábrica cubre 3 años o 60,000 km, lo que ocurra primero",
                "Reclamo debe registrarse en sistema del fabricante en 24 horas",
            ],
            "metadata": {
                "tipo_servicio": "garantia",
                "sistema_afectado": "electrico",
                "tiempo_uso_meses": "18",
            },
        },
        "etiquetas": ["garantia", "reclamo", "electrico", "falla", "cobertura"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Coordinador de campañas de recall",
            "Cliente": "Propietario notificado de campaña de seguridad en su vehículo",
        },
        "objetivo": "Programar corrección por campaña de recall relacionada con bolsas de aire",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Verificación de VIN y campaña aplicable",
                "Explicación de la naturaleza del recall",
                "Asegurar al cliente sobre la seguridad",
                "Detallar el trabajo correctivo a realizar",
                "Programar cita sin costo para el cliente",
                "Ofrecer transporte alternativo durante la reparación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Campaña de seguridad activa del fabricante para corrección sin costo",
            "restricciones": [
                "Toda reparación por recall es sin costo para el propietario",
                "Piezas de reemplazo deben ser del lote corregido",
            ],
            "metadata": {
                "tipo_servicio": "recall",
                "componente": "bolsas_de_aire",
                "severidad": "alta",
            },
        },
        "etiquetas": ["recall", "seguridad", "bolsas_aire", "campana", "sin_costo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Especialista en garantías extendidas",
            "Cliente": "Propietario cuya garantía de fábrica está próxima a vencer",
        },
        "objetivo": "Ofrecimiento de plan de garantía extendida antes del vencimiento de la garantía de fábrica",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Notificación de próximo vencimiento de garantía",
                "Presentación de planes de garantía extendida",
                "Comparación de coberturas y costos",
                "Explicación de exclusiones y condiciones",
                "Respuesta a dudas del cliente",
                "Decisión y proceso de contratación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de garantía extendida con cobertura de tren motriz y componentes mayores",
            "restricciones": [
                "Solo se puede contratar antes del vencimiento de garantía original",
                "Requiere inspección del vehículo para validar estado actual",
            ],
            "metadata": {
                "tipo_servicio": "garantia_extendida",
                "cobertura": "tren_motriz_plus",
            },
        },
        "etiquetas": ["garantia", "extendida", "vencimiento", "cobertura", "oferta"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente de Servicio", "Cliente"],
        "descripcion_roles": {
            "Gerente de Servicio": "Responsable de atención a quejas del taller",
            "Cliente": "Propietario insatisfecho con reparación previa en garantía",
        },
        "objetivo": "Resolución de queja por reparación deficiente realizada bajo garantía",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Escucha de la queja del cliente",
                "Revisión del historial de la reparación previa",
                "Disculpa y reconocimiento del problema",
                "Inspección técnica inmediata",
                "Propuesta de solución correctiva",
                "Ofrecimiento de compensación por las molestias",
                "Compromiso de seguimiento personalizado",
                "Encuesta de satisfacción post-resolución",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de calidad con protocolo de atención a quejas y escalamiento",
            "restricciones": [
                "Quejas en garantía requieren respuesta en máximo 48 horas",
                "Cualquier compensación debe ser aprobada por gerencia regional",
            ],
            "metadata": {
                "tipo_servicio": "queja_garantia",
                "prioridad": "alta",
            },
        },
        "etiquetas": ["queja", "garantia", "insatisfaccion", "resolucion", "calidad"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Service Advisor", "Customer"],
        "descripcion_roles": {
            "Service Advisor": "Recall campaign coordinator",
            "Customer": "Vehicle owner who received a recall notice by mail",
        },
        "objetivo": "Address customer concerns about a powertrain recall and schedule correction",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Verify VIN and confirm recall applicability",
                "Explain the recall issue and safety implications",
                "Reassure customer about interim driving safety",
                "Describe the corrective repair procedure",
                "Schedule no-cost appointment",
                "Provide loaner vehicle information",
            ],
        },
        "parametros_factuales": {
            "contexto": "Active manufacturer safety recall campaign for powertrain component",
            "restricciones": [
                "All recall repairs are at no charge to the customer",
                "Repair must use updated replacement parts from corrected batch",
            ],
            "metadata": {
                "tipo_servicio": "recall",
                "componente": "powertrain",
                "severidad": "medium",
            },
        },
        "etiquetas": ["recall", "powertrain", "safety", "no_charge", "appointment"],
    },
    # -------------------------------------------------------------------------
    # 26-30: Parts ordering / accessories
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Refacciones", "Cliente"],
        "descripcion_roles": {
            "Asesor de Refacciones": "Encargado del mostrador de refacciones originales",
            "Cliente": "Propietario que necesita refacciones para mantenimiento propio",
        },
        "objetivo": "Venta de kit de mantenimiento original (filtros, aceite, bujías) para auto de 3 años",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Identificación del vehículo por VIN o modelo",
                "Consulta de catálogo de refacciones compatibles",
                "Presentación de opciones originales vs alternativas",
                "Cotización del kit completo",
                "Verificación de existencia y tiempo de entrega",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de refacciones con catálogo electrónico de partes originales",
            "restricciones": [
                "Siempre ofrecer primero refacción original del fabricante",
                "Informar número de parte para referencia del cliente",
            ],
            "metadata": {
                "tipo_servicio": "refacciones",
                "tipo_producto": "kit_mantenimiento",
            },
        },
        "etiquetas": ["refacciones", "mantenimiento", "originales", "kit", "filtros"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Accesorios", "Cliente"],
        "descripcion_roles": {
            "Asesor de Accesorios": "Especialista en accesorios y personalización de vehículos",
            "Cliente": "Propietario que desea personalizar su SUV con accesorios off-road",
        },
        "objetivo": "Asesoría y venta de paquete de accesorios todoterreno para SUV",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Identificación del modelo y versión del SUV",
                "Exploración de uso y actividades del cliente",
                "Presentación de catálogo de accesorios off-road",
                "Recomendación de paquete personalizado",
                "Cotización total con instalación",
                "Programación de instalación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Centro de accesorios con instalación profesional y catálogo de productos aprobados",
            "restricciones": [
                "Solo instalar accesorios aprobados que no anulen garantía",
                "Tiempo de instalación varía según complejidad del paquete",
            ],
            "metadata": {
                "tipo_servicio": "accesorios",
                "categoria": "off_road",
            },
        },
        "etiquetas": ["accesorios", "off_road", "personalizacion", "instalacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Refacciones", "Cliente"],
        "descripcion_roles": {
            "Asesor de Refacciones": "Encargado de pedidos especiales de refacciones",
            "Cliente": "Propietario que necesita pieza descontinuada para modelo antiguo",
        },
        "objetivo": "Localización y pedido de refacción descontinuada para vehículo de más de 10 años",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Identificación de la pieza requerida",
                "Búsqueda en sistema de inventario nacional",
                "Consulta de disponibilidad en red de distribuidores",
                "Opciones alternativas si no hay original disponible",
                "Cotización y tiempo de entrega estimado",
                "Confirmación de pedido especial",
            ],
        },
        "parametros_factuales": {
            "contexto": "Red de distribución de refacciones con acceso a inventario nacional e importación",
            "restricciones": [
                "Piezas descontinuadas pueden requerir 15-30 días para localizar",
                "Informar al cliente si solo hay opción de pieza reconstruida",
            ],
            "metadata": {
                "tipo_servicio": "refacciones",
                "tipo_producto": "pieza_descontinuada",
                "antigüedad_vehiculo": "10_plus_anos",
            },
        },
        "etiquetas": ["refacciones", "descontinuada", "pedido_especial", "modelo_antiguo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Accesorios", "Cliente"],
        "descripcion_roles": {
            "Asesor de Accesorios": "Consultor de tecnología y entretenimiento vehicular",
            "Cliente": "Propietario interesado en actualizar sistema de infoentretenimiento",
        },
        "objetivo": "Actualización de sistema multimedia y conectividad en vehículo de modelo anterior",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Evaluación del sistema actual del vehículo",
                "Presentación de opciones de actualización compatibles",
                "Demostración de funcionalidades nuevas",
                "Cotización de equipo e instalación",
                "Discusión de compatibilidad con funciones existentes",
                "Programación de instalación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Centro de accesorios tecnológicos con opciones de upgrade de infoentretenimiento",
            "restricciones": [
                "Verificar compatibilidad eléctrica antes de confirmar upgrade",
                "Actualización no debe afectar funciones de seguridad del vehículo",
            ],
            "metadata": {
                "tipo_servicio": "accesorios",
                "categoria": "tecnologia",
                "producto": "infoentretenimiento",
            },
        },
        "etiquetas": ["accesorios", "tecnologia", "multimedia", "upgrade", "conectividad"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Parts Advisor", "Customer"],
        "descripcion_roles": {
            "Parts Advisor": "OEM parts counter specialist",
            "Customer": "DIY enthusiast ordering brake pads and rotors for weekend project",
        },
        "objetivo": "OEM brake components order with correct fitment verification",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Vehicle identification and brake system spec lookup",
                "Front vs rear brake component selection",
                "OEM vs aftermarket options and pricing",
                "Availability check and order placement",
                "Pickup or delivery arrangement",
            ],
        },
        "parametros_factuales": {
            "contexto": "Parts department with electronic catalog and real-time inventory system",
            "restricciones": [
                "Verify exact fitment by VIN to avoid returns",
                "Inform customer about core charges if applicable",
            ],
            "metadata": {
                "tipo_servicio": "parts",
                "tipo_producto": "brake_components",
                "canal": "counter_sale",
            },
        },
        "etiquetas": ["parts", "brakes", "oem", "diy", "fitment"],
    },
    # -------------------------------------------------------------------------
    # 31-35: Fleet sales / corporate accounts
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Ejecutivo de Flotillas", "Gerente de Compras"],
        "descripcion_roles": {
            "Ejecutivo de Flotillas": "Especialista en ventas corporativas y de flotilla",
            "Gerente de Compras": "Responsable de adquisición de vehículos para empresa de logística",
        },
        "objetivo": "Cotización de flotilla de 20 unidades pickup para empresa de distribución",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 10,
            "turnos_max": 24,
            "flujo_esperado": [
                "Presentación corporativa e identificación de necesidades",
                "Especificación técnica de unidades requeridas",
                "Revisión de configuraciones disponibles",
                "Presentación de precios de flotilla con descuento por volumen",
                "Opciones de personalización y rotulación",
                "Plan de entrega escalonada",
                "Programa de mantenimiento preventivo corporativo",
                "Condiciones de financiamiento especiales para flotilla",
                "Propuesta formal y proceso de aprobación",
                "Cierre y cronograma de implementación",
            ],
        },
        "parametros_factuales": {
            "contexto": "División de flotillas con precios especiales y programa de servicio corporativo",
            "restricciones": [
                "Descuento por volumen requiere mínimo 10 unidades",
                "Entrega escalonada máxima en 3 meses",
            ],
            "metadata": {
                "tipo_operacion": "venta_flotilla",
                "cantidad_unidades": "20",
                "segmento": "pickup_trabajo",
                "tipo_cliente": "empresa_logistica",
            },
        },
        "etiquetas": ["flotilla", "corporativo", "volumen", "pickup", "logistica"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Ejecutivo de Flotillas", "Director Administrativo"],
        "descripcion_roles": {
            "Ejecutivo de Flotillas": "Consultor de movilidad corporativa",
            "Director Administrativo": "Tomador de decisiones para renovación de flotilla ejecutiva",
        },
        "objetivo": "Propuesta de renovación de flotilla ejecutiva de 8 sedanes para dirección de empresa",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Presentación de propuesta de valor",
                "Diagnóstico de flotilla actual y ciclo de vida",
                "Presentación de modelos ejecutivos recomendados",
                "Análisis costo-beneficio de renovación vs mantenimiento",
                "Opciones de toma de unidades actuales",
                "Esquemas de arrendamiento vs compra",
                "Programa de servicio y mantenimiento incluido",
                "Presentación de propuesta económica integral",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de renovación de flotillas ejecutivas con trade-in y servicio integral",
            "restricciones": [
                "Unidades ejecutivas deben incluir paquete de seguridad completo",
                "Trade-in de flotilla actual valuada por lote, no individualmente",
            ],
            "metadata": {
                "tipo_operacion": "renovacion_flotilla",
                "segmento": "ejecutivo",
                "cantidad_unidades": "8",
            },
        },
        "etiquetas": ["flotilla", "ejecutivo", "renovacion", "trade_in", "arrendamiento"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Ejecutivo de Flotillas", "Coordinador de Operaciones"],
        "descripcion_roles": {
            "Ejecutivo de Flotillas": "Especialista en vehículos comerciales ligeros",
            "Coordinador de Operaciones": "Responsable de operaciones de empresa de servicios técnicos",
        },
        "objetivo": "Configuración de vans de carga para empresa de servicios técnicos domiciliarios",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Análisis de requerimientos operativos",
                "Selección de modelo base de van",
                "Diseño de configuración interior para herramientas",
                "Cotización de conversión y equipamiento",
                "Rotulación corporativa",
                "Plan de entrega y capacitación",
                "Programa de servicio y refacciones",
                "Acuerdo comercial y orden de compra",
            ],
        },
        "parametros_factuales": {
            "contexto": "Departamento de vehículos comerciales con servicio de conversión y equipamiento",
            "restricciones": [
                "Conversiones deben cumplir normativa de seguridad vehicular",
                "Peso de equipamiento no debe exceder capacidad de carga de la van",
            ],
            "metadata": {
                "tipo_operacion": "venta_flotilla",
                "segmento": "van_comercial",
                "conversion": "equipamiento_tecnico",
            },
        },
        "etiquetas": ["flotilla", "van", "comercial", "conversion", "equipamiento"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Ejecutivo de Flotillas", "Gerente de Recursos Humanos"],
        "descripcion_roles": {
            "Ejecutivo de Flotillas": "Consultor de programas de auto-beneficio",
            "Gerente de Recursos Humanos": "Responsable de beneficios de empleados en empresa tecnológica",
        },
        "objetivo": "Implementación de programa de auto-beneficio para empleados de empresa de tecnología",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Presentación del programa de auto-beneficio",
                "Estructura de descuentos corporativos para empleados",
                "Opciones de financiamiento preferencial",
                "Proceso de solicitud y aprobación",
                "Catálogo de modelos disponibles",
                "Beneficios adicionales: seguro, servicio, refacciones",
                "Implementación y comunicación interna",
                "Acuerdo marco y vigencia del programa",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de beneficios corporativos con precios preferenciales para empleados",
            "restricciones": [
                "Mínimo de 50 empleados elegibles para activar programa",
                "Descuento corporativo no acumulable con otras promociones",
            ],
            "metadata": {
                "tipo_operacion": "programa_beneficio",
                "tipo_cliente": "empresa_tecnologia",
                "modelo_negocio": "auto_beneficio",
            },
        },
        "etiquetas": ["corporativo", "beneficio_empleados", "descuento", "programa"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Fleet Manager", "Procurement Officer"],
        "descripcion_roles": {
            "Fleet Manager": "Corporate fleet sales specialist",
            "Procurement Officer": "Buyer for a rental car company expanding its fleet",
        },
        "objetivo": "Bulk order of 50 compact sedans for rental fleet with custom specifications",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 10,
            "turnos_max": 22,
            "flujo_esperado": [
                "Business introduction and fleet requirements",
                "Vehicle specification alignment",
                "Volume pricing negotiation",
                "Delivery schedule planning",
                "Fleet management software integration",
                "Maintenance and service contract",
                "Insurance and warranty packages",
                "Fleet branding and identification",
                "Contract terms and conditions",
                "Order confirmation and deposit",
            ],
        },
        "parametros_factuales": {
            "contexto": "National fleet program with volume discounts and dedicated support team",
            "restricciones": [
                "Minimum order of 25 units for fleet pricing",
                "Delivery in batches of 10 units per month",
            ],
            "metadata": {
                "tipo_operacion": "fleet_sale",
                "cantidad_unidades": "50",
                "segmento": "compact_sedan",
                "tipo_cliente": "rental_company",
            },
        },
        "etiquetas": ["fleet", "rental", "bulk_order", "corporate", "compact"],
    },
    # -------------------------------------------------------------------------
    # 36-40: Insurance discussion
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Seguros", "Cliente"],
        "descripcion_roles": {
            "Asesor de Seguros": "Agente de seguros dentro de la concesionaria",
            "Cliente": "Comprador que necesita contratar seguro para auto nuevo",
        },
        "objetivo": "Comparación y contratación de póliza de seguro para vehículo nuevo",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Identificación del vehículo a asegurar",
                "Perfil del conductor y uso del vehículo",
                "Presentación de coberturas disponibles",
                "Comparativo de aseguradoras y precios",
                "Explicación de deducibles y condiciones",
                "Selección de póliza y coberturas",
                "Proceso de contratación y documentos",
                "Entrega de póliza y guía de siniestros",
            ],
        },
        "parametros_factuales": {
            "contexto": "Agencia de seguros integrada en concesionaria con múltiples aseguradoras",
            "restricciones": [
                "Seguro de cobertura amplia requerido para vehículos financiados",
                "Presentar mínimo 3 cotizaciones de diferentes aseguradoras",
            ],
            "metadata": {
                "tipo_operacion": "seguro",
                "tipo_poliza": "cobertura_amplia",
                "vehiculo": "nuevo",
            },
        },
        "etiquetas": ["seguro", "poliza", "cobertura_amplia", "comparativo", "nuevo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Seguros", "Cliente"],
        "descripcion_roles": {
            "Asesor de Seguros": "Gestor de renovaciones de seguro automotriz",
            "Cliente": "Propietario con póliza próxima a vencer que busca mejor precio",
        },
        "objetivo": "Renovación de seguro automotriz con búsqueda de mejor tarifa",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Revisión de póliza actual y historial de siniestros",
                "Identificación de coberturas esenciales vs prescindibles",
                "Cotización de renovación con aseguradora actual",
                "Cotización comparativa con otras aseguradoras",
                "Análisis de ahorro por ajuste de coberturas",
                "Decisión de renovación y procesamiento",
            ],
        },
        "parametros_factuales": {
            "contexto": "Servicio de renovación con acceso a cotizador multi-aseguradora",
            "restricciones": [
                "Mantener cobertura amplia si hay crédito vigente",
                "Bonus de no siniestralidad puede reducir prima hasta 20%",
            ],
            "metadata": {
                "tipo_operacion": "seguro",
                "tipo_transaccion": "renovacion",
                "objetivo_cliente": "mejor_precio",
            },
        },
        "etiquetas": ["seguro", "renovacion", "comparativo", "ahorro", "tarifa"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Seguros", "Cliente"],
        "descripcion_roles": {
            "Asesor de Seguros": "Gestor de siniestros de seguro automotriz",
            "Cliente": "Propietario que sufrió un percance vial y necesita reportar siniestro",
        },
        "objetivo": "Guía para reporte de siniestro automotriz y activación de cobertura",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Verificación de bienestar del cliente",
                "Recolección de datos del siniestro",
                "Verificación de cobertura y vigencia de póliza",
                "Explicación del proceso de reclamación",
                "Documentación requerida para el reclamo",
                "Asignación de ajustador",
                "Opciones de taller para reparación",
                "Seguimiento y tiempos estimados",
            ],
        },
        "parametros_factuales": {
            "contexto": "Servicio de atención a siniestros con red de talleres autorizados",
            "restricciones": [
                "Siniestro debe reportarse dentro de las 72 horas del evento",
                "No mover el vehículo del lugar del percance sin instrucciones del ajustador",
            ],
            "metadata": {
                "tipo_operacion": "seguro",
                "tipo_transaccion": "siniestro",
                "tipo_percance": "colision",
            },
        },
        "etiquetas": ["seguro", "siniestro", "reclamo", "ajustador", "reparacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Seguros", "Cliente"],
        "descripcion_roles": {
            "Asesor de Seguros": "Especialista en seguros de robo automotriz",
            "Cliente": "Propietario preocupado por la seguridad de su vehículo de alta gama",
        },
        "objetivo": "Asesoría sobre cobertura de robo total y parcial con dispositivos de rastreo",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Evaluación del riesgo según modelo y zona de residencia",
                "Explicación de cobertura de robo total vs parcial",
                "Presentación de dispositivos de rastreo y recuperación",
                "Impacto del rastreo en la prima del seguro",
                "Recomendaciones de seguridad adicionales",
                "Contratación de póliza y dispositivo",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de seguridad vehicular con dispositivos de rastreo satelital",
            "restricciones": [
                "Vehículos de alta gama requieren dispositivo de rastreo para cobertura de robo",
                "Descuento en prima por instalación de rastreo certificado",
            ],
            "metadata": {
                "tipo_operacion": "seguro",
                "cobertura": "robo",
                "complemento": "rastreo_satelital",
            },
        },
        "etiquetas": ["seguro", "robo", "rastreo", "alta_gama", "seguridad"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Insurance Advisor", "Customer"],
        "descripcion_roles": {
            "Insurance Advisor": "In-dealership insurance specialist",
            "Customer": "New car buyer comparing comprehensive and liability-only coverage",
        },
        "objetivo": "Help customer understand coverage options and select appropriate insurance plan",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 16,
            "flujo_esperado": [
                "Greeting and vehicle details confirmation",
                "Driving profile and usage assessment",
                "Comprehensive coverage explanation",
                "Liability-only coverage explanation",
                "Deductible options and premium impact",
                "Gap insurance discussion for financed vehicles",
                "Quote comparison from partner insurers",
                "Policy selection and enrollment",
            ],
        },
        "parametros_factuales": {
            "contexto": "Dealership insurance desk with partnerships with major insurers",
            "restricciones": [
                "Financed vehicles require minimum comprehensive coverage",
                "Present at least two insurer quotes for comparison",
            ],
            "metadata": {
                "tipo_operacion": "insurance",
                "coverage_type": "comprehensive_vs_liability",
                "vehiculo": "new",
            },
        },
        "etiquetas": ["insurance", "comprehensive", "liability", "gap", "comparison"],
    },
    # -------------------------------------------------------------------------
    # 41-45: Vehicle comparison shopping
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de ventas con conocimiento multi-marca",
            "Cliente": "Comprador indeciso entre dos modelos de la misma marca",
        },
        "objetivo": "Comparación detallada entre dos versiones de SUV compacta de la misma marca",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Identificación de los modelos a comparar",
                "Comparativo de dimensiones y espacio interior",
                "Comparativo de motorización y rendimiento",
                "Comparativo de equipamiento y tecnología",
                "Comparativo de precio y valor residual",
                "Diferencias en costos de seguro y mantenimiento",
                "Recomendación personalizada según perfil",
                "Siguiente paso: prueba de manejo de ambas",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con herramienta digital de comparación de especificaciones",
            "restricciones": [
                "Comparar usando datos oficiales del fabricante",
                "No denigrar ningún modelo, resaltar diferencias objetivas",
            ],
            "metadata": {
                "tipo_operacion": "comparacion",
                "segmento": "suv_compacta",
                "tipo_comparacion": "misma_marca",
            },
        },
        "etiquetas": ["comparacion", "suv", "versiones", "decision", "especificaciones"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor especializado en vehículos híbridos y eléctricos",
            "Cliente": "Comprador evaluando híbrido vs eléctrico puro para uso urbano",
        },
        "objetivo": "Comparación entre vehículo híbrido enchufable y eléctrico puro para uso citadino",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Análisis de patrones de manejo del cliente",
                "Explicación de tecnologías híbrida y eléctrica",
                "Comparativo de autonomía y rendimiento",
                "Infraestructura de carga disponible",
                "Costos operativos comparados",
                "Incentivos gubernamentales aplicables",
                "Valor de reventa y tendencias de mercado",
                "Recomendación basada en perfil de uso",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con línea completa de vehículos electrificados",
            "restricciones": [
                "Usar datos de rendimiento en condiciones reales, no solo de laboratorio",
                "Informar sobre disponibilidad real de infraestructura de carga en la zona",
            ],
            "metadata": {
                "tipo_operacion": "comparacion",
                "tecnologias": "hibrido_vs_electrico",
                "uso": "urbano",
            },
        },
        "etiquetas": ["comparacion", "hibrido", "electrico", "urbano", "rendimiento"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de ventas de pickups",
            "Cliente": "Trabajador independiente decidiendo entre dos marcas de pickup",
        },
        "objetivo": "Comparación de capacidades de carga y remolque entre dos pickups de marcas diferentes",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Identificación de necesidades de carga y remolque",
                "Especificaciones de capacidad de ambos modelos",
                "Comparativo de motorización y torque",
                "Diferencias en equipamiento de trabajo",
                "Costos de mantenimiento comparados",
                "Disponibilidad y tiempos de entrega",
                "Prueba de carga en ambos modelos",
                "Resumen y recomendación",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria multi-marca con especialización en vehículos de trabajo",
            "restricciones": [
                "Capacidad de carga y remolque según especificaciones del fabricante",
                "Mencionar diferencias en garantía del tren motriz",
            ],
            "metadata": {
                "tipo_operacion": "comparacion",
                "segmento": "pickup",
                "tipo_comparacion": "multi_marca",
            },
        },
        "etiquetas": ["comparacion", "pickup", "carga", "remolque", "trabajo"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor comercial de sedanes",
            "Cliente": "Pareja joven que debate entre auto nuevo económico y seminuevo premium",
        },
        "objetivo": "Asesoría comparativa entre auto nuevo de gama baja y seminuevo de gama alta al mismo precio",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 18,
            "flujo_esperado": [
                "Entender presupuesto y prioridades de la pareja",
                "Presentar opción nueva: equipamiento y garantía",
                "Presentar opción seminueva: nivel de equipamiento superior",
                "Comparar costos de mantenimiento y seguro",
                "Comparar garantías disponibles",
                "Comparar valor de reventa a 3 y 5 años",
                "Financiamiento para cada opción",
                "Facilitar decisión informada",
            ],
        },
        "parametros_factuales": {
            "contexto": "Concesionaria con inventario nuevo y seminuevo en rango de precio similar",
            "restricciones": [
                "No presionar hacia ninguna opción, presentar hechos objetivos",
                "Incluir costos ocultos: seguro, tenencia, verificación",
            ],
            "metadata": {
                "tipo_operacion": "comparacion",
                "tipo_comparacion": "nuevo_vs_seminuevo",
                "rango_precio": "medio",
            },
        },
        "etiquetas": ["comparacion", "nuevo_vs_seminuevo", "pareja", "presupuesto"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Sales Advisor", "Customer"],
        "descripcion_roles": {
            "Sales Advisor": "Multi-brand comparison specialist",
            "Customer": "Tech-savvy buyer comparing infotainment and driver-assist features across brands",
        },
        "objetivo": "Technology-focused comparison of driver assistance and infotainment across three SUV models",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 20,
            "flujo_esperado": [
                "Identify key technology features important to customer",
                "Compare infotainment systems and connectivity",
                "Compare driver assistance suites",
                "Compare OTA update capabilities",
                "Evaluate mobile app integration",
                "Discuss technology subscription costs",
                "Hands-on demo of each system",
                "Technology-based recommendation",
            ],
        },
        "parametros_factuales": {
            "contexto": "Technology-forward dealership with demo units for hands-on comparison",
            "restricciones": [
                "Compare using current software versions only",
                "Disclose any features that require paid subscriptions",
            ],
            "metadata": {
                "tipo_operacion": "comparison",
                "focus": "technology",
                "segmento": "suv",
                "brands_compared": "3",
            },
        },
        "etiquetas": ["comparison", "technology", "infotainment", "adas", "suv"],
    },
    # -------------------------------------------------------------------------
    # 46-50: Post-purchase follow-up
    # -------------------------------------------------------------------------
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Asesor de postventa y fidelización",
            "Cliente": "Comprador reciente que recibe llamada de seguimiento a 7 días",
        },
        "objetivo": "Llamada de seguimiento post-entrega a los 7 días para verificar satisfacción",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Saludo y agradecimiento por la compra",
                "Consulta sobre experiencia con el vehículo nuevo",
                "Verificación de que todo funcione correctamente",
                "Resolución de dudas sobre funciones del auto",
                "Recordatorio de primer servicio programado",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de seguimiento postventa con llamadas a 7, 30 y 90 días",
            "restricciones": [
                "No intentar venta cruzada en primer contacto postventa",
                "Registrar cualquier incidencia para seguimiento inmediato",
            ],
            "metadata": {
                "tipo_operacion": "seguimiento",
                "etapa": "7_dias",
                "canal": "llamada_telefonica",
            },
        },
        "etiquetas": ["postventa", "seguimiento", "satisfaccion", "7_dias", "fidelizacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Asesor de Servicio", "Cliente"],
        "descripcion_roles": {
            "Asesor de Servicio": "Coordinador de primer servicio gratuito",
            "Cliente": "Propietario nuevo que asiste a su primer servicio de mantenimiento",
        },
        "objetivo": "Primer servicio de mantenimiento gratuito con explicación de programa de cuidado del vehículo",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Bienvenida y recepción del vehículo",
                "Explicación de los trabajos del primer servicio",
                "Revisión de puntos clave del vehículo",
                "Presentación del programa de mantenimiento completo",
                "Explicación de app de seguimiento de servicio",
                "Entrega del vehículo con reporte de inspección",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de primer servicio gratuito incluido en la compra del vehículo",
            "restricciones": [
                "Primer servicio es sin costo y no exceder los 5,000 km",
                "Registrar servicio en sistema para historial de garantía",
            ],
            "metadata": {
                "tipo_operacion": "primer_servicio",
                "costo": "gratuito",
                "kilometraje": "5000",
            },
        },
        "etiquetas": ["postventa", "primer_servicio", "gratuito", "mantenimiento"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Gerente de Relación", "Cliente"],
        "descripcion_roles": {
            "Gerente de Relación": "Responsable de programa de lealtad de la concesionaria",
            "Cliente": "Propietario con segundo auto comprado en la misma concesionaria",
        },
        "objetivo": "Activación de beneficios de programa de lealtad por segunda compra en la concesionaria",
        "tono": "formal",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Reconocimiento del cliente como comprador recurrente",
                "Presentación del programa de lealtad y sus niveles",
                "Beneficios específicos para clientes de segunda compra",
                "Descuentos en servicio, refacciones y accesorios",
                "Prioridad en citas y servicios",
                "Activación de membresía y entrega de beneficios",
            ],
        },
        "parametros_factuales": {
            "contexto": "Programa de lealtad con niveles según número de compras y antigüedad",
            "restricciones": [
                "Beneficios de lealtad no son transferibles",
                "Programa vigente mientras el cliente mantenga servicio en la red",
            ],
            "metadata": {
                "tipo_operacion": "fidelizacion",
                "nivel_lealtad": "segundo_compra",
                "programa": "club_propietarios",
            },
        },
        "etiquetas": ["postventa", "lealtad", "fidelizacion", "beneficios", "club"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["Vendedor", "Cliente"],
        "descripcion_roles": {
            "Vendedor": "Especialista en programas de referidos",
            "Cliente": "Propietario satisfecho que refirió a un familiar o amigo",
        },
        "objetivo": "Gestión de programa de referidos y entrega de bono por recomendación exitosa",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 5,
            "turnos_max": 12,
            "flujo_esperado": [
                "Agradecimiento por la referencia",
                "Confirmación de compra del referido",
                "Explicación del bono o incentivo obtenido",
                "Opciones de canje del bono",
                "Invitación a continuar refiriendo",
            ],
        },
        "parametros_factuales": {
            "contexto": (
                "Programa de referidos con bonos canjeables en servicio, accesorios o descuento en siguiente compra"
            ),
            "restricciones": [
                "Bono se activa solo cuando el referido concreta la compra",
                "Bono tiene vigencia de 12 meses desde la activación",
            ],
            "metadata": {
                "tipo_operacion": "referidos",
                "tipo_incentivo": "bono_canjeable",
                "vigencia_meses": "12",
            },
        },
        "etiquetas": ["postventa", "referidos", "bono", "recomendacion"],
    },
    {
        "dominio": "automotive.sales",
        "idioma": "en",
        "roles": ["Customer Relations Manager", "Customer"],
        "descripcion_roles": {
            "Customer Relations Manager": "Post-sale satisfaction coordinator",
            "Customer": "Buyer receiving 90-day follow-up call after purchase",
        },
        "objetivo": "90-day post-purchase satisfaction check and owner feedback collection",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Greeting and purpose of the call",
                "Overall ownership experience feedback",
                "Vehicle performance and comfort assessment",
                "Service department experience if applicable",
                "Address any outstanding concerns",
                "NPS score collection and closing",
            ],
        },
        "parametros_factuales": {
            "contexto": "Customer satisfaction program with structured follow-up at 7, 30, and 90 days",
            "restricciones": [
                "Focus on listening, not selling additional products",
                "Escalate any unresolved issues to management within 24 hours",
            ],
            "metadata": {
                "tipo_operacion": "follow_up",
                "etapa": "90_days",
                "canal": "phone_call",
                "metric": "nps",
            },
        },
        "etiquetas": ["post_purchase", "satisfaction", "follow_up", "nps", "90_days"],
    },
]
