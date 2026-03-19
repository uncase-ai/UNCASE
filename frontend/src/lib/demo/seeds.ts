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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
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
      rouge_l_min: 0.20,
      fidelidad_min: 0.80,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.65
    },
    rating: 4.9,
    rating_count: 22,
    run_count: 58,
    avg_quality_score: 0.95,
    created_at: daysAgo(2),
    updated_at: daysAgo(1)
  }
]
