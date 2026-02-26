import type { ToolDefinition } from '@/types/api'

export const DEMO_TOOLS: ToolDefinition[] = [
  // ── Automotive (5) ──
  {
    name: 'buscar_inventario',
    description: 'Busca vehículos en el inventario por marca, modelo, año o rango de precio.',
    input_schema: { type: 'object', properties: { marca: { type: 'string' }, modelo: { type: 'string' }, anio: { type: 'integer' }, precio_max: { type: 'number' } } },
    output_schema: { type: 'array', items: { type: 'object' } },
    domains: ['automotive.sales'],
    category: 'query',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'cotizar_vehiculo',
    description: 'Genera cotización formal de un vehículo con opciones de financiamiento.',
    input_schema: { type: 'object', properties: { vehiculo_id: { type: 'string' }, incluir_seguro: { type: 'boolean' } } },
    output_schema: { type: 'object' },
    domains: ['automotive.sales'],
    category: 'calculation',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'verificar_disponibilidad',
    description: 'Verifica disponibilidad en tiempo real de un vehículo específico.',
    input_schema: { type: 'object', properties: { vehiculo_id: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['automotive.sales'],
    category: 'query',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'solicitar_financiamiento',
    description: 'Inicia solicitud de financiamiento vehicular con evaluación de crédito.',
    input_schema: { type: 'object', properties: { cliente_id: { type: 'string' }, monto: { type: 'number' }, plazo_meses: { type: 'integer' } } },
    output_schema: { type: 'object' },
    domains: ['automotive.sales'],
    category: 'action',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'agendar_servicio',
    description: 'Agenda cita de servicio o mantenimiento para un vehículo.',
    input_schema: { type: 'object', properties: { vehiculo_id: { type: 'string' }, tipo_servicio: { type: 'string' }, fecha: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['automotive.sales'],
    category: 'action',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },

  // ── Medical (5) ──
  {
    name: 'consultar_historial_medico',
    description: 'Consulta historial médico del paciente con filtros por especialidad o fecha.',
    input_schema: { type: 'object', properties: { paciente_id: { type: 'string' }, especialidad: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['medical.consultation'],
    category: 'query',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'buscar_medicamentos',
    description: 'Busca medicamentos por nombre, principio activo o indicación terapéutica.',
    input_schema: { type: 'object', properties: { nombre: { type: 'string' }, indicacion: { type: 'string' } } },
    output_schema: { type: 'array', items: { type: 'object' } },
    domains: ['medical.consultation'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'agendar_cita',
    description: 'Agenda cita médica con especialista verificando disponibilidad.',
    input_schema: { type: 'object', properties: { paciente_id: { type: 'string' }, especialidad: { type: 'string' }, fecha_preferida: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['medical.consultation'],
    category: 'action',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'verificar_laboratorio',
    description: 'Consulta resultados de laboratorio de un paciente.',
    input_schema: { type: 'object', properties: { paciente_id: { type: 'string' }, estudio: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['medical.consultation'],
    category: 'query',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'validar_seguro',
    description: 'Valida cobertura de seguro médico del paciente para procedimientos.',
    input_schema: { type: 'object', properties: { paciente_id: { type: 'string' }, procedimiento: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['medical.consultation'],
    category: 'validation',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },

  // ── Legal (5) ──
  {
    name: 'buscar_jurisprudencia',
    description: 'Busca jurisprudencia relevante por tema, tribunal o fecha.',
    input_schema: { type: 'object', properties: { tema: { type: 'string' }, tribunal: { type: 'string' } } },
    output_schema: { type: 'array', items: { type: 'object' } },
    domains: ['legal.advisory'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'consultar_expediente',
    description: 'Consulta expediente judicial con estado y movimientos recientes.',
    input_schema: { type: 'object', properties: { numero_expediente: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['legal.advisory'],
    category: 'query',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'verificar_plazos',
    description: 'Verifica plazos procesales vigentes para un expediente.',
    input_schema: { type: 'object', properties: { expediente_id: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['legal.advisory'],
    category: 'validation',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'buscar_legislacion',
    description: 'Busca legislación vigente por materia, jurisdicción o palabra clave.',
    input_schema: { type: 'object', properties: { materia: { type: 'string' }, jurisdiccion: { type: 'string' } } },
    output_schema: { type: 'array', items: { type: 'object' } },
    domains: ['legal.advisory'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'calcular_honorarios',
    description: 'Calcula honorarios estimados según tipo de caso y complejidad.',
    input_schema: { type: 'object', properties: { tipo_caso: { type: 'string' }, complejidad: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['legal.advisory'],
    category: 'calculation',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },

  // ── Finance (5) ──
  {
    name: 'consultar_portafolio',
    description: 'Consulta posiciones actuales del portafolio de inversión del cliente.',
    input_schema: { type: 'object', properties: { cliente_id: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['finance.advisory'],
    category: 'query',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'analizar_riesgo',
    description: 'Analiza perfil de riesgo del cliente según cuestionario y datos financieros.',
    input_schema: { type: 'object', properties: { cliente_id: { type: 'string' }, horizonte_anios: { type: 'integer' } } },
    output_schema: { type: 'object' },
    domains: ['finance.advisory'],
    category: 'calculation',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'consultar_mercado',
    description: 'Consulta datos de mercado en tiempo real para instrumentos financieros.',
    input_schema: { type: 'object', properties: { simbolo: { type: 'string' }, periodo: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['finance.advisory'],
    category: 'query',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'verificar_cumplimiento',
    description: 'Verifica cumplimiento regulatorio de una operación financiera propuesta.',
    input_schema: { type: 'object', properties: { operacion: { type: 'object' } } },
    output_schema: { type: 'object' },
    domains: ['finance.advisory'],
    category: 'validation',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'simular_inversion',
    description: 'Simula rendimiento de inversión con diferentes escenarios de mercado.',
    input_schema: { type: 'object', properties: { monto: { type: 'number' }, instrumento: { type: 'string' }, plazo_meses: { type: 'integer' } } },
    output_schema: { type: 'object' },
    domains: ['finance.advisory'],
    category: 'calculation',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },

  // ── Industrial (5) ──
  {
    name: 'diagnosticar_equipo',
    description: 'Ejecuta diagnóstico remoto de equipo industrial por ID o código de error.',
    input_schema: { type: 'object', properties: { equipo_id: { type: 'string' }, codigo_error: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['industrial.support'],
    category: 'query',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'consultar_inventario_partes',
    description: 'Consulta inventario de refacciones y partes de repuesto.',
    input_schema: { type: 'object', properties: { numero_parte: { type: 'string' }, equipo_id: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['industrial.support'],
    category: 'query',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'programar_mantenimiento',
    description: 'Programa orden de mantenimiento preventivo o correctivo.',
    input_schema: { type: 'object', properties: { equipo_id: { type: 'string' }, tipo: { type: 'string' }, prioridad: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['industrial.support'],
    category: 'action',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'buscar_manual_tecnico',
    description: 'Busca manuales técnicos y documentación de equipo por modelo o tema.',
    input_schema: { type: 'object', properties: { modelo: { type: 'string' }, seccion: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['industrial.support'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'registrar_incidencia',
    description: 'Registra incidencia o falla en equipo para seguimiento.',
    input_schema: { type: 'object', properties: { equipo_id: { type: 'string' }, descripcion: { type: 'string' }, severidad: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['industrial.support'],
    category: 'action',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },

  // ── Education (5) ──
  {
    name: 'buscar_curriculum',
    description: 'Busca contenido curricular por nivel, materia o competencia.',
    input_schema: { type: 'object', properties: { nivel: { type: 'string' }, materia: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['education.tutoring'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'evaluar_progreso',
    description: 'Evalúa progreso del estudiante en competencias específicas.',
    input_schema: { type: 'object', properties: { estudiante_id: { type: 'string' }, competencia: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['education.tutoring'],
    category: 'query',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'generar_ejercicio',
    description: 'Genera ejercicio adaptativo según nivel del estudiante.',
    input_schema: { type: 'object', properties: { materia: { type: 'string' }, nivel: { type: 'string' }, tipo: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['education.tutoring'],
    category: 'action',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'buscar_recurso_educativo',
    description: 'Busca recursos educativos (videos, documentos, interactivos) por tema.',
    input_schema: { type: 'object', properties: { tema: { type: 'string' }, formato: { type: 'string' } } },
    output_schema: { type: 'array', items: { type: 'object' } },
    domains: ['education.tutoring'],
    category: 'retrieval',
    requires_auth: false,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  },
  {
    name: 'programar_sesion',
    description: 'Programa sesión de tutoría con disponibilidad y preferencias.',
    input_schema: { type: 'object', properties: { estudiante_id: { type: 'string' }, materia: { type: 'string' }, fecha: { type: 'string' } } },
    output_schema: { type: 'object' },
    domains: ['education.tutoring'],
    category: 'action',
    requires_auth: true,
    execution_mode: 'simulated',
    version: '1.0.0',
    metadata: { builtin: true }
  }
]
