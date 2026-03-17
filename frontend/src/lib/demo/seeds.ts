import type { SeedSchema } from '@/types/api'

function daysAgo(n: number): string {
  const d = new Date()

  d.setDate(d.getDate() - n)

  return d.toISOString()
}

export const DEMO_SEEDS: SeedSchema[] = [
  // ── Featured Seeds — 6 premium seeds (1 per industry, all Spanish) ──

  // Automotive: Extracted from Mariana (Autos TREFA) conversation patterns —
  // full purchase funnel: greeting → discovery → inventory search → vehicle detail →
  // comparison → financing simulation → trade-in → lead capture.
  {
    seed_id: 'featured-auto-001',
    version: '1.0',
    dominio: 'automotive.sales',
    idioma: 'es',
    etiquetas: [
      'flujo-completo',
      'descubrimiento',
      'comparacion',
      'financiamiento',
      'intercambio',
      'cierre'
    ],
    roles: ['cliente', 'asesora_virtual'],
    descripcion_roles: {
      cliente:
        'Persona buscando un auto seminuevo para uso familiar, con presupuesto limitado y necesidad de financiamiento. Tiene un auto actual que podría dar a cuenta.',
      asesora_virtual:
        'Asistente virtual de agencia de autos seminuevos con acceso a inventario en tiempo real, simulador de financiamiento, comparador de vehículos y sistema de registro de prospectos. Tono cálido, profesional, español mexicano.'
    },
    objetivo:
      'Guiar al cliente desde la exploración inicial hasta la conversión: descubrir necesidades, buscar en inventario, comparar opciones, simular financiamiento con opción de intercambio, y registrar datos de contacto para seguimiento por un asesor humano',
    tono: 'profesional-amigable',
    pasos_turnos: {
      turnos_min: 8,
      turnos_max: 16,
      flujo_esperado: [
        'Saludo y bienvenida cálida',
        'Descubrimiento de necesidades (máximo 2 preguntas)',
        'Búsqueda en inventario con filtros del cliente',
        'Presentación de 2-3 opciones con precio, enganche y mensualidad',
        'Detalle completo del vehículo de interés',
        'Comparación lado a lado si el cliente duda entre dos opciones',
        'Simulación de financiamiento personalizada (enganche, plazo, mensualidad)',
        'Exploración de programa de intercambio si aplica',
        'Captura de datos de contacto y cierre con compromiso de seguimiento'
      ]
    },
    parametros_factuales: {
      contexto:
        'Agencia de autos seminuevos con presencia en 4 ciudades del noreste de México. Inventario de 80-100 vehículos, modelos 2018-2025. Financiamiento con múltiples instituciones bancarias.',
      restricciones: [
        'Siempre usar herramientas para consultar inventario real — nunca inventar datos',
        'Sin resultados exactos, buscar alternativas antes de decir que no hay opciones',
        'Incluir siempre información financiera: precio, enganche mínimo, mensualidad estimada',
        'Nunca compartir IDs internos, slugs técnicos ni nombres de herramientas',
        'Formato de precios: $XXX,XXX MXN',
        'No negociar precios — son finales',
        'No garantizar aprobación de crédito — siempre sujeto a evaluación',
        'No dar consejos legales, fiscales ni mecánicos — referir al asesor',
        'Enganche mínimo 20%, plazos 12-60 meses',
        'Programa de intercambio: autos 2015+, máximo 120,000 km',
        'Política de devolución: 7 días o 500 km'
      ],
      herramientas: [
        'buscar_vehiculos',
        'obtener_vehiculo',
        'comparar_vehiculos',
        'calcular_financiamiento',
        'obtener_info_negocio',
        'solicitar_datos_contacto'
      ],
      metadata: {
        tipo_operacion: 'venta_seminuevo',
        segmento: 'suv_familiar',
        rango_precios: '250000-520000',
        sucursales: 'Monterrey, Guadalupe, Saltillo, Reynosa',
        garantia: '3 meses / 5,000 km'
      }
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
    rating: 4.9,
    rating_count: 24,
    run_count: 63,
    avg_quality_score: 0.95,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // Medical: Consulta de medicina interna — paciente con síntomas gastrointestinales
  {
    seed_id: 'featured-med-001',
    version: '1.0',
    dominio: 'medical.consultation',
    idioma: 'es',
    etiquetas: [
      'medicina-interna',
      'gastroenterologia',
      'consulta-inicial',
      'diagnostico-diferencial',
      'laboratorios'
    ],
    roles: ['paciente', 'medico_internista'],
    descripcion_roles: {
      paciente:
        'Adulto de 42 años que acude a consulta por dolor abdominal recurrente, distensión y alteración del hábito intestinal de 3 meses de evolución. Sin antecedentes quirúrgicos, hipertenso controlado.',
      medico_internista:
        'Médico internista certificado con acceso a expediente clínico electrónico, sistema de órdenes de laboratorio e imagen, y base de datos de medicamentos con interacciones.'
    },
    objetivo:
      'Realizar historia clínica completa enfocada en aparato digestivo, elaborar diagnóstico diferencial entre síndrome de intestino irritable, enfermedad celíaca y patología orgánica, solicitar estudios pertinentes y establecer plan de manejo inicial',
    tono: 'profesional-empatico',
    pasos_turnos: {
      turnos_min: 8,
      turnos_max: 14,
      flujo_esperado: [
        'Motivo de consulta y padecimiento actual (cronología, características del dolor, factores desencadenantes)',
        'Interrogatorio por aparatos y sistemas relevantes (pérdida de peso, sangrado, fiebre)',
        'Antecedentes personales patológicos y medicamentos actuales',
        'Antecedentes heredofamiliares relevantes (cáncer colorrectal, enfermedad celíaca)',
        'Exploración física dirigida (abdomen, signos vitales)',
        'Diagnóstico diferencial razonado con explicación al paciente',
        'Solicitud de estudios de laboratorio e imagen con justificación',
        'Plan terapéutico inicial y medidas higiénico-dietéticas',
        'Signos de alarma y plan de seguimiento'
      ]
    },
    parametros_factuales: {
      contexto:
        'Consultorio de medicina interna en clínica privada con acceso a expediente electrónico, laboratorio clínico y gabinete de imagen.',
      restricciones: [
        'Revisar historial de alergias antes de prescribir cualquier medicamento',
        'Verificar interacciones con medicamentos actuales del paciente',
        'No emitir diagnóstico definitivo sin estudios confirmatorios',
        'Signos de alarma (sangrado, pérdida de peso >10%, obstrucción) requieren protocolo de urgencia',
        'Verificar cobertura del seguro para estudios de imagen avanzados',
        'Consentimiento informado obligatorio para procedimientos invasivos'
      ],
      herramientas: [
        'consultar_expediente',
        'buscar_medicamentos',
        'ordenar_laboratorios',
        'verificar_seguro',
        'agendar_cita'
      ],
      metadata: {
        especialidad: 'medicina_interna',
        tipo_visita: 'consulta_inicial',
        duracion_promedio_min: 40,
        contexto_clinico: 'dolor_abdominal_cronico'
      }
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
    rating_count: 21,
    run_count: 55,
    avg_quality_score: 0.94,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // Legal: Asesoría sobre registro de marca en México (IMPI)
  {
    seed_id: 'featured-legal-001',
    version: '1.0',
    dominio: 'legal.advisory',
    idioma: 'es',
    etiquetas: [
      'propiedad-intelectual',
      'registro-marca',
      'IMPI',
      'pyme',
      'estrategia-proteccion'
    ],
    roles: ['cliente', 'abogado_pi'],
    descripcion_roles: {
      cliente:
        'Dueño de una pequeña empresa de alimentos que quiere registrar su marca comercial y logotipo antes de expandirse a nuevos estados. Sin experiencia previa en propiedad intelectual.',
      abogado_pi:
        'Abogado especialista en propiedad intelectual con experiencia ante el IMPI, acceso a la base de datos MARCANET para búsquedas de anterioridades y conocimiento de la Ley Federal de Protección a la Propiedad Industrial.'
    },
    objetivo:
      'Evaluar la viabilidad de registro de marca, realizar búsqueda de anterioridades, explicar el proceso ante el IMPI con tiempos y costos, recomendar clases de Niza aplicables, y definir estrategia de protección integral',
    tono: 'profesional-didactico',
    pasos_turnos: {
      turnos_min: 7,
      turnos_max: 12,
      flujo_esperado: [
        'Entendimiento del negocio, marca y productos/servicios que ampara',
        'Búsqueda de anterioridades en MARCANET — verificar disponibilidad',
        'Explicación de clases de Niza aplicables al giro del cliente',
        'Descripción del proceso de registro ante el IMPI (etapas, tiempos, costos)',
        'Evaluación de riesgo de oposición y estrategia ante posibles conflictos',
        'Recomendación sobre protección complementaria (aviso comercial, imagen comercial)',
        'Documentos necesarios y plan de acción con calendario',
        'Honorarios, costos oficiales y próximos pasos'
      ]
    },
    parametros_factuales: {
      contexto:
        'Despacho de propiedad intelectual con acceso a MARCANET (base de marcas del IMPI), sistema de gestión de expedientes y calendario de plazos legales.',
      restricciones: [
        'No garantizar aprobación del registro — sujeta a examen de fondo del IMPI',
        'Verificar conflictos de interés antes de iniciar la representación',
        'Plazos legales del IMPI deben respetarse estrictamente (oposición: 1 mes post-publicación)',
        'Honorarios y costos oficiales deben ser transparentes desde el inicio',
        'Confidencialidad sobre la estrategia comercial del cliente',
        'Tiempo estimado de registro: 4-6 meses sin oposición'
      ],
      herramientas: [],
      metadata: {
        area_practica: 'propiedad_intelectual',
        jurisdiccion: 'Mexico',
        organismo: 'IMPI',
        clasificacion: 'Niza'
      }
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
    rating_count: 17,
    run_count: 44,
    avg_quality_score: 0.93,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // Finance: Asesoría de inversión para emprendedor post-ronda de capital
  {
    seed_id: 'featured-fin-001',
    version: '1.0',
    dominio: 'finance.advisory',
    idioma: 'es',
    etiquetas: [
      'tesoreria',
      'inversion',
      'startup',
      'gestion-capital',
      'optimizacion-fiscal'
    ],
    roles: ['cliente', 'asesor_financiero'],
    descripcion_roles: {
      cliente:
        'Fundador de startup tecnológica que acaba de cerrar una ronda seed de $2M USD y necesita estructurar la tesorería, invertir el capital no operativo a corto plazo, y optimizar la carga fiscal.',
      asesor_financiero:
        'Asesor financiero certificado especializado en startups y venture capital, con acceso a simuladores de inversión, proyecciones de flujo de caja y conocimiento de régimen fiscal mexicano para empresas tecnológicas.'
    },
    objetivo:
      'Diseñar estrategia de tesorería post-ronda: definir runway operativo, recomendar instrumentos de inversión a corto plazo para capital no operativo, estructurar la entidad fiscal óptima, y establecer controles de gasto alineados con métricas de la ronda',
    tono: 'profesional-consultivo',
    pasos_turnos: {
      turnos_min: 7,
      turnos_max: 12,
      flujo_esperado: [
        'Contexto de la ronda: monto, valuación, términos relevantes y runway objetivo',
        'Análisis de flujo de caja proyectado y burn rate mensual',
        'Separación de capital operativo vs. excedente invertible',
        'Presentación de instrumentos de inversión a corto plazo (CETES, fondos de deuda, mesa de dinero)',
        'Simulación de rendimientos con diferentes escenarios de runway',
        'Estrategia fiscal: régimen aplicable, deducciones, RESICO vs. general, PTU',
        'Controles de tesorería y reporteo para inversionistas',
        'Plan de acción con calendario y próximos pasos'
      ]
    },
    parametros_factuales: {
      contexto:
        'Firma de asesoría financiera con especialización en empresas tecnológicas en etapa temprana. Acceso a plataformas de inversión institucional y simuladores de proyección financiera.',
      restricciones: [
        'Rendimientos pasados no garantizan rendimientos futuros',
        'Recomendaciones deben alinearse con el perfil de riesgo del emprendedor y los términos de la ronda',
        'Implicaciones fiscales deben considerar régimen actual y proyecciones de crecimiento',
        'No recomendar instrumentos con horizonte mayor al runway proyectado',
        'Cumplimiento con regulación CNBV/SAT obligatorio',
        'Transparencia total en comisiones y costos de los instrumentos'
      ],
      herramientas: ['simulador_inversion', 'proyeccion_flujo_caja', 'calculadora_fiscal'],
      metadata: {
        tipo_cliente: 'startup_seed',
        monto_ronda: '2000000_usd',
        horizonte_inversion: '18-24_meses',
        jurisdiccion: 'Mexico'
      }
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
    run_count: 48,
    avg_quality_score: 0.94,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // Industrial: Diagnóstico remoto de falla en sistema de refrigeración industrial
  {
    seed_id: 'featured-ind-001',
    version: '1.0',
    dominio: 'industrial.support',
    idioma: 'es',
    etiquetas: [
      'refrigeracion-industrial',
      'diagnostico-remoto',
      'alarma-temperatura',
      'soporte-tecnico',
      'cadena-frio'
    ],
    roles: ['operador_planta', 'ingeniero_soporte'],
    descripcion_roles: {
      operador_planta:
        'Operador del turno nocturno en planta de alimentos que reporta alarma de alta temperatura en el sistema de refrigeración de la cámara de producto terminado. Línea de producción en riesgo de paro.',
      ingeniero_soporte:
        'Ingeniero de soporte técnico remoto con acceso al sistema SCADA, manuales de equipo, historial de mantenimiento en CMMS, e inventario de refacciones. Certificado en sistemas de refrigeración industrial con amoniaco.'
    },
    objetivo:
      'Diagnosticar la causa de la alarma de alta temperatura, guiar al operador de forma segura a través del protocolo de diagnóstico, determinar si se puede resolver remotamente o requiere despacho de técnico, y proteger la cadena de frío del producto',
    tono: 'profesional-tecnico',
    pasos_turnos: {
      turnos_min: 7,
      turnos_max: 12,
      flujo_esperado: [
        'Recepción del reporte de alarma: equipo afectado, código de error, lecturas actuales de temperatura y presión',
        'Verificación de seguridad: protocolos de amoniaco, EPP del operador, ventilación de la zona',
        'Consulta remota de parámetros SCADA: temperaturas, presiones, estado de compresores y válvulas',
        'Revisión de historial de mantenimiento del equipo en CMMS',
        'Diagnóstico guiado: pasos de verificación física que el operador puede realizar de forma segura',
        'Determinación de causa raíz (fuga de refrigerante, falla de compresor, válvula de expansión, sensor)',
        'Acción correctiva inmediata o despacho de técnico con refacciones necesarias',
        'Protocolo de protección de producto: transferencia a cámara alternativa si aplica',
        'Documentación del evento en CMMS y notificación al supervisor de turno'
      ]
    },
    parametros_factuales: {
      contexto:
        'Planta de manufactura de alimentos con sistema de refrigeración industrial por amoniaco. Monitoreo SCADA 24/7, sistema CMMS para mantenimiento, e inventario de refacciones críticas.',
      restricciones: [
        'Protocolos de seguridad con amoniaco son prioridad absoluta — evacuar zona si se detecta fuga',
        'Solo personal certificado puede intervenir en el circuito de refrigerante',
        'Procedimiento de bloqueo/etiquetado (LOTO) obligatorio antes de cualquier intervención física',
        'Toda intervención debe documentarse en CMMS con fotos y lecturas',
        'Cadena de frío no debe romperse: activar protocolo de transferencia de producto si temperatura supera límite crítico',
        'Notificar al jefe de turno y al supervisor de calidad si hay riesgo de pérdida de producto',
        'Impacto en producción debe reportarse en formato de tiempo muerto'
      ],
      herramientas: [],
      metadata: {
        tipo_equipo: 'sistema_refrigeracion_amoniaco',
        planta: 'Planta-Alimentos-Norte',
        turno: 'nocturno',
        criticidad: 'alta',
        producto_afectado: 'camara_producto_terminado'
      }
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
    rating: 4.7,
    rating_count: 15,
    run_count: 39,
    avg_quality_score: 0.93,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // Education: Tutoría de redacción de ensayo argumentativo universitario
  {
    seed_id: 'featured-edu-001',
    version: '1.0',
    dominio: 'education.tutoring',
    idioma: 'es',
    etiquetas: [
      'redaccion-academica',
      'ensayo-argumentativo',
      'universidad',
      'pensamiento-critico',
      'metodologia'
    ],
    roles: ['estudiante', 'tutor_redaccion'],
    descripcion_roles: {
      estudiante:
        'Estudiante universitario de tercer semestre que necesita escribir un ensayo argumentativo de 2,000 palabras para su clase de Comunicación. Tiene el tema pero no sabe cómo estructurar argumentos sólidos ni citar fuentes correctamente.',
      tutor_redaccion:
        'Tutor especializado en redacción académica y pensamiento crítico, con acceso a rúbricas de evaluación, banco de ejemplos de ensayos y guías de estilo APA/MLA. Metodología socrática: guía mediante preguntas, nunca da respuestas directas.'
    },
    objetivo:
      'Guiar al estudiante paso a paso en la construcción de su ensayo argumentativo: desde la formulación de una tesis clara, pasando por la estructura de argumentos con evidencia, manejo de contraargumentos, hasta la revisión final con formato APA',
    tono: 'amigable-motivador',
    pasos_turnos: {
      turnos_min: 8,
      turnos_max: 14,
      flujo_esperado: [
        'Exploración del tema y lo que el estudiante ya sabe o ha investigado',
        'Formulación de la tesis: convertir el tema en una postura argumentable',
        'Estructura del ensayo: introducción, desarrollo (3 argumentos), contraargumento, conclusión',
        'Desarrollo del primer argumento con evidencia — ejercicio guiado',
        'Enseñar a integrar citas y parafrasear sin plagiar (formato APA)',
        'Trabajo con contraargumentos: anticipar objeciones y refutarlas',
        'Revisión de coherencia, transiciones y voz académica',
        'Checklist final: formato, bibliografía, extensión, rúbrica del profesor'
      ]
    },
    parametros_factuales: {
      contexto:
        'Plataforma de tutoría académica en línea con pizarra colaborativa, banco de recursos de redacción, y acceso a guías de estilo APA 7a edición.',
      restricciones: [
        'Nunca escribir el ensayo ni párrafos completos por el estudiante — solo guiar el proceso',
        'Usar preguntas socráticas para que el estudiante llegue a sus propias conclusiones',
        'Adaptar las explicaciones al nivel demostrado del estudiante',
        'Reforzar el esfuerzo y el proceso, no solo el resultado',
        'Si el estudiante comete error de lógica, señalarlo con pregunta, no con corrección directa',
        'Toda cita debe verificarse como real — no inventar fuentes',
        'Respetar los lineamientos específicos del profesor si el estudiante los comparte'
      ],
      herramientas: [],
      metadata: {
        materia: 'comunicacion',
        nivel: 'universidad_3er_semestre',
        tipo_trabajo: 'ensayo_argumentativo',
        extension: '2000_palabras',
        formato_citas: 'APA_7'
      }
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
    rating: 4.9,
    rating_count: 22,
    run_count: 58,
    avg_quality_score: 0.95,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  },

  // ── Original Demo Seeds ──
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
