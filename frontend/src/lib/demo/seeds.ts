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
      herramientas: [],
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
      herramientas: [],
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
      herramientas: [],
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
  },

  // ── Medical Consultation Seeds ──
  {
    seed_id: 'demo-seed-006',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'en',
    etiquetas: ['cardiology', 'initial-consultation', 'chest-pain'],
    roles: ['patient', 'physician'],
    descripcion_roles: {
      patient: 'Adult patient presenting with chest pain symptoms seeking initial cardiology evaluation',
      physician: 'Board-certified cardiologist with access to patient records and diagnostic tools'
    },
    objetivo: 'Conduct thorough cardiac evaluation including history of present illness, risk factor assessment, and determine appropriate diagnostic workup',
    tono: 'professional-empathetic',
    pasos_turnos: {
      turnos_min: 6,
      turnos_max: 10,
      flujo_esperado: [
        'Chief complaint and HPI',
        'Review of medical history and medications',
        'Risk factor assessment',
        'Physical examination findings',
        'Diagnostic plan and orders',
        'Patient education and follow-up'
      ]
    },
    parametros_factuales: {
      contexto: 'Outpatient cardiology clinic with access to EHR, lab results, and scheduling system',
      restricciones: [
        'Must review complete medical history before making recommendations',
        'All medication changes require allergy verification',
        'Insurance coverage must be verified for advanced imaging',
        'Emergency symptoms require immediate escalation protocol'
      ],
      herramientas: ['check_medical_history', 'search_medications', 'schedule_appointment', 'check_lab_results', 'verify_insurance'],
      metadata: { specialty: 'cardiology', visit_type: 'initial', avg_duration_min: 45 }
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
    rating: 4.7,
    rating_count: 14,
    run_count: 42,
    avg_quality_score: 0.92,
    created_at: daysAgo(12),
    updated_at: daysAgo(11)
  },
  {
    seed_id: 'demo-seed-007',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'en',
    etiquetas: ['pediatrics', 'wellness-visit', 'immunization'],
    roles: ['patient', 'physician'],
    descripcion_roles: {
      patient: 'Parent or guardian bringing a child for a routine wellness visit and immunization review',
      physician: 'Board-certified pediatrician with access to immunization records and growth charts'
    },
    objetivo: 'Complete pediatric wellness assessment including growth milestones, immunization schedule review, and parental counseling',
    tono: 'professional-reassuring',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Growth and development review',
        'Immunization history check',
        'Current concerns from parent',
        'Physical examination summary',
        'Immunization plan and anticipatory guidance',
        'Schedule follow-up'
      ]
    },
    parametros_factuales: {
      contexto: 'Pediatric outpatient clinic with access to immunization registry and growth databases',
      restricciones: [
        'Immunization recommendations must follow current CDC schedule',
        'Allergy history must be reviewed before any vaccine administration',
        'Growth percentiles must reference WHO/CDC standard charts',
        'Parent consent required for all immunizations'
      ],
      herramientas: [],
      metadata: { specialty: 'pediatrics', visit_type: 'wellness', avg_duration_min: 30 }
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
    rating: 4.3,
    rating_count: 9,
    run_count: 28,
    avg_quality_score: 0.88,
    created_at: daysAgo(10),
    updated_at: daysAgo(9)
  },
  {
    seed_id: 'demo-seed-008',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'en',
    etiquetas: ['dermatology', 'follow-up', 'chronic-condition'],
    roles: ['patient', 'physician'],
    descripcion_roles: {
      patient: 'Patient with chronic skin condition returning for follow-up evaluation and treatment adjustment',
      physician: 'Board-certified dermatologist with access to patient treatment history and medication databases'
    },
    objetivo: 'Evaluate treatment response for chronic dermatologic condition, adjust therapy as needed, and plan ongoing management',
    tono: 'professional-collaborative',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Treatment response assessment',
        'Symptom progression review',
        'Medication adherence check',
        'Lab results review if applicable',
        'Treatment plan adjustment',
        'Follow-up scheduling'
      ]
    },
    parametros_factuales: {
      contexto: 'Dermatology clinic with access to treatment history, lab results, and insurance verification',
      restricciones: [
        'Biologic medications require prior authorization verification',
        'Lab monitoring required for systemic medications',
        'Treatment changes must account for drug interactions',
        'Photo documentation should be referenced for comparison'
      ],
      herramientas: ['check_medical_history', 'search_medications', 'check_lab_results', 'verify_insurance'],
      metadata: { specialty: 'dermatology', visit_type: 'follow-up', avg_duration_min: 20 }
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
    rating: 4.5,
    rating_count: 11,
    run_count: 33,
    avg_quality_score: 0.90,
    created_at: daysAgo(8),
    updated_at: daysAgo(7)
  },
  {
    seed_id: 'demo-seed-009',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'en',
    etiquetas: ['mental-health', 'intake', 'anxiety'],
    roles: ['patient', 'therapist'],
    descripcion_roles: {
      patient: 'Adult patient seeking initial mental health evaluation for anxiety and stress-related symptoms',
      therapist: 'Licensed clinical psychologist conducting intake assessment with access to screening tools'
    },
    objetivo: 'Conduct comprehensive mental health intake assessment including symptom inventory, psychosocial history, risk assessment, and treatment planning',
    tono: 'professional-warm',
    pasos_turnos: {
      turnos_min: 6,
      turnos_max: 10,
      flujo_esperado: [
        'Presenting concerns and symptom onset',
        'Symptom inventory and severity',
        'Psychosocial and family history',
        'Current coping mechanisms and support system',
        'Safety screening',
        'Treatment recommendations and plan'
      ]
    },
    parametros_factuales: {
      contexto: 'Outpatient behavioral health clinic with access to patient records and insurance verification',
      restricciones: [
        'PHQ-9 and GAD-7 screening scores must be documented',
        'Safety assessment is mandatory at every intake',
        'Medication recommendations must defer to psychiatry referral',
        'Insurance must be verified for ongoing therapy sessions'
      ],
      herramientas: [],
      metadata: { specialty: 'psychology', visit_type: 'intake', avg_duration_min: 60 }
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
    rating_count: 16,
    run_count: 45,
    avg_quality_score: 0.93,
    created_at: daysAgo(7),
    updated_at: daysAgo(6)
  },
  {
    seed_id: 'demo-seed-010',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'en',
    etiquetas: ['endocrinology', 'chronic-disease', 'diabetes-t2'],
    roles: ['patient', 'physician'],
    descripcion_roles: {
      patient: 'Patient with Type 2 diabetes mellitus returning for quarterly follow-up and disease management review',
      physician: 'Board-certified endocrinologist managing chronic diabetes care with access to lab results and treatment history'
    },
    objetivo: 'Review glycemic control, assess for complications, adjust medications as needed, and reinforce lifestyle modifications',
    tono: 'professional-motivational',
    pasos_turnos: {
      turnos_min: 6,
      turnos_max: 10,
      flujo_esperado: [
        'Glycemic control review (HbA1c, glucose logs)',
        'Medication adherence and side effects',
        'Complication screening (renal, ophthalmologic, neuropathy)',
        'Lab results review',
        'Medication adjustment if needed',
        'Lifestyle counseling and follow-up plan'
      ]
    },
    parametros_factuales: {
      contexto: 'Endocrinology clinic with access to comprehensive lab results, medication history, and diabetes management tools',
      restricciones: [
        'HbA1c target must be individualized based on patient profile',
        'Renal function must be checked before metformin adjustments',
        'Annual ophthalmology and podiatry referrals are mandatory',
        'Insurance formulary must be checked for medication changes'
      ],
      herramientas: ['check_medical_history', 'check_lab_results', 'search_medications', 'verify_insurance', 'schedule_appointment'],
      metadata: { specialty: 'endocrinology', visit_type: 'follow-up', avg_duration_min: 30 }
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
    rating_count: 13,
    run_count: 39,
    avg_quality_score: 0.91,
    created_at: daysAgo(5),
    updated_at: daysAgo(4)
  },

  // ── Finance Advisory Seeds ──
  {
    seed_id: 'demo-seed-011',
    version: '1.0',
    dominio: 'finance.advisory',
    idioma: 'en',
    etiquetas: ['retirement', 'portfolio', 'rebalancing'],
    roles: ['client', 'financial_advisor'],
    descripcion_roles: {
      client: 'Pre-retiree client seeking portfolio review and retirement income strategy',
      financial_advisor: 'CFP-certified advisor with access to portfolio analytics and retirement projection tools'
    },
    objetivo: 'Review current retirement portfolio allocation, assess risk tolerance changes, and recommend rebalancing strategy aligned with 5-year retirement horizon',
    tono: 'professional-consultative',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Current portfolio review and performance summary',
        'Updated risk tolerance and retirement timeline assessment',
        'Market outlook and allocation analysis',
        'Rebalancing recommendations with tax implications',
        'Implementation plan and monitoring schedule'
      ]
    },
    parametros_factuales: {
      contexto: 'Wealth management firm with portfolio analytics, tax-loss harvesting tools, and retirement projection models',
      restricciones: [
        'Past performance does not guarantee future results',
        'All recommendations must align with client risk profile',
        'Tax implications must be disclosed for any proposed trades',
        'Regulatory compliance (FINRA/SEC) required for all advice'
      ],
      herramientas: ['credit_calculator'],
      metadata: { specialty: 'retirement-planning', avg_portfolio_size: 750000 }
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
    rating: 4.7,
    rating_count: 15,
    run_count: 41,
    avg_quality_score: 0.92,
    created_at: daysAgo(14),
    updated_at: daysAgo(12)
  },
  {
    seed_id: 'demo-seed-012',
    version: '1.0',
    dominio: 'finance.advisory',
    idioma: 'es',
    etiquetas: ['credito-hipotecario', 'primera-vivienda', 'simulacion'],
    roles: ['cliente', 'asesor_hipotecario'],
    descripcion_roles: {
      cliente: 'Comprador de primera vivienda buscando opciones de crédito hipotecario',
      asesor_hipotecario: 'Asesor hipotecario certificado con acceso a simuladores de crédito y tablas de tasas'
    },
    objetivo: 'Evaluar capacidad de endeudamiento, comparar opciones de crédito hipotecario y guiar al cliente hacia la pre-aprobación',
    tono: 'profesional',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Detección de necesidad y perfil del comprador',
        'Evaluación de capacidad de pago',
        'Comparativa de productos hipotecarios',
        'Simulación de crédito personalizada',
        'Documentos para pre-aprobación y siguientes pasos'
      ]
    },
    parametros_factuales: {
      contexto: 'Institución financiera con productos hipotecarios a tasa fija y variable, plazos de 10 a 20 años',
      restricciones: [
        'Enganche mínimo del 10% del valor de la propiedad',
        'Tasa sujeta a calificación crediticia del solicitante',
        'Seguro de vida y daños obligatorio',
        'No compartir tasas preferenciales de otros clientes'
      ],
      herramientas: ['credit_calculator'],
      metadata: { product_type: 'mortgage', avg_loan_amount: 2500000 }
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
    rating: 4.5,
    rating_count: 10,
    run_count: 29,
    avg_quality_score: 0.90,
    created_at: daysAgo(10),
    updated_at: daysAgo(8)
  },

  // ── Legal Advisory Seeds ──
  {
    seed_id: 'demo-seed-013',
    version: '1.0',
    dominio: 'legal.advisory',
    idioma: 'en',
    etiquetas: ['contract-dispute', 'breach', 'litigation'],
    roles: ['client', 'attorney'],
    descripcion_roles: {
      client: 'Business owner consulting about a breach of contract claim against a former supplier',
      attorney: 'Commercial litigation attorney with access to case law databases and contract review tools'
    },
    objetivo: 'Assess the merits of a breach of contract claim, review key evidence, and outline litigation strategy including timeline and estimated costs',
    tono: 'professional-authoritative',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Case intake and factual background',
        'Contract review and breach identification',
        'Damages assessment and evidence strength',
        'Legal strategy options (negotiation, mediation, litigation)',
        'Timeline, costs, and engagement terms'
      ]
    },
    parametros_factuales: {
      contexto: 'Commercial law firm with access to Westlaw/LexisNexis, contract analytics, and case management system',
      restricciones: [
        'Cannot guarantee specific litigation outcomes',
        'Attorney-client privilege must be established before disclosure',
        'Conflict of interest check required',
        'Statute of limitations must be verified before proceeding'
      ],
      herramientas: [],
      metadata: { practice_area: 'commercial-litigation', avg_case_value: 250000 }
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
    rating: 4.6,
    rating_count: 11,
    run_count: 35,
    avg_quality_score: 0.91,
    created_at: daysAgo(15),
    updated_at: daysAgo(13)
  },
  {
    seed_id: 'demo-seed-014',
    version: '1.0',
    dominio: 'legal.advisory',
    idioma: 'es',
    etiquetas: ['laboral', 'despido', 'indemnizacion'],
    roles: ['cliente', 'abogado_laboral'],
    descripcion_roles: {
      cliente: 'Trabajador que fue despedido y busca asesoría sobre sus derechos laborales e indemnización',
      abogado_laboral: 'Abogado especialista en derecho laboral con acceso a la Ley Federal del Trabajo y jurisprudencia'
    },
    objetivo: 'Evaluar las circunstancias del despido, determinar si fue justificado o injustificado, y calcular la indemnización correspondiente',
    tono: 'profesional',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Relato de hechos y circunstancias del despido',
        'Revisión de contrato y antigüedad laboral',
        'Determinación del tipo de despido (justificado/injustificado)',
        'Cálculo de liquidación e indemnización',
        'Opciones legales y próximos pasos'
      ]
    },
    parametros_factuales: {
      contexto: 'Despacho de abogados laborales con acceso a calculadoras de liquidación y base de datos de jurisprudencia',
      restricciones: [
        'No garantizar resultados específicos de juicio',
        'Plazos legales deben verificarse antes de proceder',
        'Honorarios deben ser transparentes desde el inicio',
        'Confidencialidad del caso es obligatoria'
      ],
      herramientas: [],
      metadata: { practice_area: 'labor-law', jurisdiction: 'Mexico' }
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
    rating: 4.4,
    rating_count: 8,
    run_count: 24,
    avg_quality_score: 0.89,
    created_at: daysAgo(11),
    updated_at: daysAgo(9)
  },

  // ── Industrial Support Seeds ──
  {
    seed_id: 'demo-seed-015',
    version: '1.0',
    dominio: 'industrial.support',
    idioma: 'en',
    etiquetas: ['cnc-machine', 'error-code', 'remote-diagnostic'],
    roles: ['operator', 'technician'],
    descripcion_roles: {
      operator: 'CNC machine operator reporting error code E-47 during production run',
      technician: 'Senior maintenance technician with remote diagnostic access and equipment manuals'
    },
    objetivo: 'Diagnose CNC error code E-47, guide operator through safe troubleshooting steps, and determine if on-site maintenance is required',
    tono: 'professional-technical',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Error code report and machine status',
        'Safety verification and lockout confirmation',
        'Remote diagnostic data review',
        'Guided troubleshooting steps',
        'Resolution or maintenance dispatch'
      ]
    },
    parametros_factuales: {
      contexto: 'Manufacturing plant with SCADA monitoring, remote diagnostic capabilities, and preventive maintenance scheduling system',
      restricciones: [
        'Safety lockout/tagout must be verified before any physical intervention',
        'Only certified personnel may access electrical panels',
        'All troubleshooting steps must be logged in CMMS',
        'Production impact must be reported to shift supervisor'
      ],
      herramientas: [],
      metadata: { equipment_type: 'CNC', facility: 'Plant-A', shift: '2nd' }
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
    rating: 4.3,
    rating_count: 7,
    run_count: 21,
    avg_quality_score: 0.88,
    created_at: daysAgo(16),
    updated_at: daysAgo(14)
  },
  {
    seed_id: 'demo-seed-016',
    version: '1.0',
    dominio: 'industrial.support',
    idioma: 'es',
    etiquetas: ['linea-produccion', 'mantenimiento-preventivo', 'programacion'],
    roles: ['supervisor_planta', 'coordinador_mantenimiento'],
    descripcion_roles: {
      supervisor_planta: 'Supervisor de planta solicitando programación de mantenimiento preventivo para línea de producción',
      coordinador_mantenimiento: 'Coordinador de mantenimiento con acceso al sistema CMMS y calendario de intervenciones'
    },
    objetivo: 'Programar mantenimiento preventivo para la línea de producción 3, coordinando ventanas de paro con el plan de producción semanal',
    tono: 'profesional',
    pasos_turnos: {
      turnos_min: 4,
      turnos_max: 7,
      flujo_esperado: [
        'Identificación de equipos y programa de mantenimiento',
        'Revisión de historial y últimas intervenciones',
        'Coordinación de ventana de paro con producción',
        'Asignación de técnicos y refacciones',
        'Confirmación de programa y notificaciones'
      ]
    },
    parametros_factuales: {
      contexto: 'Planta de manufactura con sistema CMMS, inventario de refacciones y calendario de producción',
      restricciones: [
        'Mantenimiento no debe exceder la ventana de paro autorizada',
        'Refacciones deben estar disponibles antes de programar',
        'Técnicos certificados obligatorios para equipos críticos',
        'Toda intervención debe documentarse en el sistema CMMS'
      ],
      herramientas: [],
      metadata: { facility: 'Planta-Norte', production_line: 'L3' }
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
    rating: 4.1,
    rating_count: 6,
    run_count: 17,
    avg_quality_score: 0.87,
    created_at: daysAgo(12),
    updated_at: daysAgo(10)
  },

  // ── Education Tutoring Seeds ──
  {
    seed_id: 'demo-seed-017',
    version: '1.0',
    dominio: 'education.tutoring',
    idioma: 'en',
    etiquetas: ['mathematics', 'algebra', 'quadratic-equations'],
    roles: ['student', 'tutor'],
    descripcion_roles: {
      student: 'High school student struggling with solving quadratic equations by factoring',
      tutor: 'Mathematics tutor with adaptive teaching methods and access to practice problem sets'
    },
    objetivo: 'Guide the student through understanding and solving quadratic equations using factoring, completing the square, and the quadratic formula',
    tono: 'professional-encouraging',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Identify specific difficulty and current understanding',
        'Explain the concept with visual examples',
        'Work through a guided example together',
        'Student attempts independent practice with hints',
        'Review, correct errors, and assign follow-up exercises'
      ]
    },
    parametros_factuales: {
      contexto: 'Online tutoring platform with interactive whiteboard, practice exercises, and curriculum-aligned content',
      restricciones: [
        'Never give direct answers — guide through the problem-solving process',
        'Adapt explanations to the student\'s demonstrated level',
        'Use positive reinforcement for effort, not just correct answers',
        'Suggest visual or alternative methods when standard approach fails'
      ],
      herramientas: [],
      metadata: { subject: 'mathematics', level: 'high-school', topic: 'quadratic-equations' }
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
    rating: 4.8,
    rating_count: 18,
    run_count: 52,
    avg_quality_score: 0.93,
    created_at: daysAgo(17),
    updated_at: daysAgo(15)
  },
  {
    seed_id: 'demo-seed-018',
    version: '1.0',
    dominio: 'education.tutoring',
    idioma: 'es',
    etiquetas: ['ciencias', 'biologia', 'celula'],
    roles: ['estudiante', 'tutor'],
    descripcion_roles: {
      estudiante: 'Estudiante de secundaria preparándose para examen de biología sobre la célula y sus organelos',
      tutor: 'Tutor de ciencias con materiales didácticos interactivos y banco de preguntas de examen'
    },
    objetivo: 'Repasar la estructura celular, funciones de los principales organelos, y diferencias entre célula animal y vegetal para preparación de examen',
    tono: 'amigable',
    pasos_turnos: {
      turnos_min: 5,
      turnos_max: 8,
      flujo_esperado: [
        'Evaluación de conocimientos previos',
        'Explicación de estructura celular con analogías',
        'Repaso de organelos y sus funciones',
        'Comparación célula animal vs vegetal',
        'Preguntas de práctica tipo examen y retroalimentación'
      ]
    },
    parametros_factuales: {
      contexto: 'Plataforma de tutoría en línea con recursos multimedia, diagramas interactivos y banco de preguntas',
      restricciones: [
        'Usar analogías cotidianas para conceptos abstractos',
        'No dar respuestas directas — guiar el razonamiento',
        'Adaptar complejidad al nivel del estudiante',
        'Reforzar con ejemplos de la vida diaria'
      ],
      herramientas: [],
      metadata: { subject: 'biology', level: 'middle-school', topic: 'cell-structure' }
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
    run_count: 36,
    avg_quality_score: 0.91,
    created_at: daysAgo(13),
    updated_at: daysAgo(11)
  }
]
