import type { SeedSchema } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'

// ─── Client-side seed validation ───
// Seeds are managed locally and through import; no dedicated CRUD endpoint yet

export function validateSeed(seed: Partial<SeedSchema>): string[] {
  const errors: string[] = []

  if (!seed.dominio) {
    errors.push('Domain (dominio) is required')
  } else if (!SUPPORTED_DOMAINS.includes(seed.dominio as (typeof SUPPORTED_DOMAINS)[number])) {
    errors.push(`Unsupported domain: ${seed.dominio}`)
  }

  if (!seed.roles || seed.roles.length < 2) {
    errors.push('At least 2 roles are required')
  }

  if (!seed.objetivo) {
    errors.push('Objective (objetivo) is required')
  }

  if (seed.pasos_turnos) {
    const { turnos_min, turnos_max } = seed.pasos_turnos

    if (turnos_min >= turnos_max) {
      errors.push('turnos_min must be less than turnos_max')
    }

    if (!seed.pasos_turnos.flujo_esperado?.length) {
      errors.push('Expected flow (flujo_esperado) must have at least 1 step')
    }
  } else {
    errors.push('Turn configuration (pasos_turnos) is required')
  }

  if (seed.privacidad) {
    if (seed.privacidad.nivel_confianza < 0 || seed.privacidad.nivel_confianza > 1) {
      errors.push('Confidence level must be between 0 and 1')
    }
  }

  return errors
}

export function createEmptySeed(): Partial<SeedSchema> {
  return {
    version: '1.0',
    dominio: '',
    idioma: 'es',
    etiquetas: [],
    roles: [],
    descripcion_roles: {},
    objetivo: '',
    tono: 'profesional',
    pasos_turnos: {
      turnos_min: 3,
      turnos_max: 10,
      flujo_esperado: []
    },
    parametros_factuales: {
      contexto: '',
      restricciones: [],
      herramientas: [],
      metadata: {}
    },
    privacidad: {
      pii_eliminado: true,
      metodo_anonimizacion: 'presidio',
      nivel_confianza: 0.85,
      campos_sensibles_detectados: []
    },
    metricas_calidad: {
      rouge_l_min: 0.65,
      fidelidad_min: 0.90,
      diversidad_lexica_min: 0.55,
      coherencia_dialogica_min: 0.85
    }
  }
}
