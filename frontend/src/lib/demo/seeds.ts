import type { SeedSchema } from '@/types/api'

function daysAgo(n: number): string {
  const d = new Date()

  d.setDate(d.getDate() - n)

  return d.toISOString()
}

export const DEMO_SEEDS: SeedSchema[] = [
  {
    seed_id: 'demo-seed-001',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: ['vehiculo-nuevo', 'suv', 'consulta-inicial'],
    roles: ['cliente', 'asesor_ventas'],
    descripcion_roles: {
      cliente: 'Cliente interesado en adquirir un SUV nuevo para uso familiar',
      asesor_ventas: 'Asesor de ventas certificado con conocimiento de inventario y financiamiento'
    },
    objetivo: 'Guiar al cliente a través de la exploración de opciones de SUV disponibles, presentar características y rangos de precio',
    tono: 'profesional-amigable',
    pasos_turnos: {
      turnos_min: 4,
      turnos_max: 8,
      flujo_esperado: [
        'Saludo y detección de necesidad',
        'Presentación de opciones disponibles',
        'Comparativa de modelos',
        'Cotización preliminar',
        'Siguiente paso (prueba de manejo o financiamiento)'
      ]
    },
    parametros_factuales: {
      contexto: 'Agencia automotriz premium con inventario de SUVs 2024-2025',
      restricciones: [
        'Solo mencionar vehículos del inventario actual',
        'Precios deben incluir IVA',
        'No prometer descuentos sin autorización del gerente'
      ],
      herramientas: ['inventory_lookup', 'price_calculator'],
      metadata: { segment: 'premium', avg_ticket: 850000 }
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio_v2',
      nivel_confianza: 0.98,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    },
    rating: 4.6,
    rating_count: 12,
    run_count: 38,
    avg_quality_score: 0.91,
    created_at: daysAgo(13),
    updated_at: daysAgo(13)
  },
  {
    seed_id: 'demo-seed-002',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: ['prueba-manejo', 'agenda', 'seguimiento'],
    roles: ['cliente', 'coordinador_pruebas'],
    descripcion_roles: {
      cliente: 'Cliente que desea agendar una prueba de manejo después de consulta inicial',
      coordinador_pruebas: 'Coordinador de pruebas de manejo con acceso a agenda y disponibilidad de unidades'
    },
    objetivo: 'Agendar prueba de manejo confirmando disponibilidad, documentos requeridos y horario',
    tono: 'profesional-eficiente',
    pasos_turnos: {
      turnos_min: 4,
      turnos_max: 6,
      flujo_esperado: [
        'Confirmación de interés en modelo específico',
        'Verificación de disponibilidad de unidad demo',
        'Selección de fecha y hora',
        'Documentos requeridos',
        'Confirmación de cita'
      ]
    },
    parametros_factuales: {
      contexto: 'Sistema de agendamiento de pruebas de manejo con disponibilidad en tiempo real',
      restricciones: [
        'Pruebas solo de lunes a sábado 9:00-18:00',
        'Requiere licencia de conducir vigente',
        'Máximo 30 minutos por prueba'
      ],
      herramientas: ['appointment_scheduler'],
      metadata: { conversion_rate: 0.35 }
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio_v2',
      nivel_confianza: 0.97,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    },
    rating: 4.2,
    rating_count: 8,
    run_count: 22,
    avg_quality_score: 0.88,
    created_at: daysAgo(11),
    updated_at: daysAgo(11)
  },
  {
    seed_id: 'demo-seed-003',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: ['trade-in', 'evaluacion', 'vehiculo-usado'],
    roles: ['cliente', 'valuador'],
    descripcion_roles: {
      cliente: 'Cliente que desea evaluar su vehículo actual como parte de pago',
      valuador: 'Valuador certificado con acceso a bases de datos de precios de mercado'
    },
    objetivo: 'Evaluar el vehículo del cliente para trade-in, proporcionar estimación de valor y explicar el proceso',
    tono: 'profesional-transparente',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Datos del vehículo actual',
        'Verificación VIN',
        'Estimación de valor de mercado',
        'Ajustes por condición',
        'Propuesta de trade-in',
        'Siguiente paso'
      ]
    },
    parametros_factuales: {
      contexto: 'Programa de trade-in con valuación basada en datos de mercado y condición del vehículo',
      restricciones: [
        'Valuación válida por 7 días',
        'Vehículos de hasta 10 años de antigüedad',
        'Sujeto a inspección física'
      ],
      herramientas: ['vin_decoder', 'trade_in_estimator'],
      metadata: { avg_trade_in_value: 280000 }
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio_v2',
      nivel_confianza: 0.99,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    },
    rating: 3.9,
    rating_count: 5,
    run_count: 15,
    avg_quality_score: 0.85,
    created_at: daysAgo(9),
    updated_at: daysAgo(8)
  },
  {
    seed_id: 'demo-seed-004',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: ['financiamiento', 'credito', 'cotizacion'],
    roles: ['cliente', 'asesor_financiero'],
    descripcion_roles: {
      cliente: 'Cliente interesado en opciones de financiamiento para compra de vehículo',
      asesor_financiero: 'Asesor financiero certificado con acceso a simuladores de crédito'
    },
    objetivo: 'Evaluar perfil crediticio del cliente y presentar opciones de financiamiento personalizadas',
    tono: 'profesional-consultivo',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Exploración de necesidades financieras',
        'Datos para pre-aprobación',
        'Simulación de crédito',
        'Comparativa de planes',
        'Selección de plan',
        'Documentos requeridos'
      ]
    },
    parametros_factuales: {
      contexto: 'Departamento de financiamiento con alianzas bancarias y arrendadoras',
      restricciones: [
        'Tasa sujeta a aprobación crediticia',
        'Enganche mínimo 10%',
        'Plazos de 12 a 60 meses',
        'No compartir tasas de otros clientes'
      ],
      herramientas: ['credit_calculator'],
      metadata: { avg_financing_amount: 650000, approval_rate: 0.72 }
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio_v2',
      nivel_confianza: 0.99,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    },
    rating: 4.8,
    rating_count: 19,
    run_count: 47,
    avg_quality_score: 0.94,
    created_at: daysAgo(6),
    updated_at: daysAgo(5)
  },
  {
    seed_id: 'demo-seed-005',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: ['servicio', 'postventa', 'mantenimiento'],
    roles: ['cliente', 'asesor_servicio'],
    descripcion_roles: {
      cliente: 'Cliente que requiere agendar servicio de mantenimiento para su vehículo',
      asesor_servicio: 'Asesor de servicio post-venta con acceso al sistema de citas y historial de mantenimiento'
    },
    objetivo: 'Agendar servicio de mantenimiento, informar sobre paquetes disponibles y costos estimados',
    tono: 'profesional-servicial',
    pasos_turnos: {
      turnos_min: 4,
      turnos_max: 6,
      flujo_esperado: [
        'Identificación de necesidad de servicio',
        'Revisión de historial',
        'Presentación de paquetes',
        'Agendamiento',
        'Confirmación'
      ]
    },
    parametros_factuales: {
      contexto: 'Centro de servicio autorizado con paquetes de mantenimiento preventivo y correctivo',
      restricciones: [
        'Citas de lunes a viernes 7:00-17:00, sábados 8:00-13:00',
        'Garantía aplica solo con servicio en red autorizada',
        'Refacciones originales únicamente'
      ],
      herramientas: ['service_scheduler'],
      metadata: { avg_service_ticket: 8500 }
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio_v2',
      nivel_confianza: 0.97,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    },
    rating: 4.4,
    rating_count: 7,
    run_count: 19,
    avg_quality_score: 0.89,
    created_at: daysAgo(3),
    updated_at: daysAgo(2)
  }
]
