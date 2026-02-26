import type { SeedSchema, SeedResponse, SeedListResponse } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { apiGet, apiPost, apiPut, apiDelete } from './client'

// ─── Client-side seed validation ───

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
      saludo_marca: '',
      nombre_asistente: '',
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

// ─── Backend seed CRUD ───

export function fetchSeeds(params?: { domain?: string; page?: number; page_size?: number }, signal?: AbortSignal) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<SeedListResponse>(`/api/v1/seeds${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchSeed(seedId: string, signal?: AbortSignal) {
  return apiGet<SeedResponse>(`/api/v1/seeds/${seedId}`, { signal })
}

export function createSeedApi(data: Record<string, unknown>, signal?: AbortSignal) {
  return apiPost<SeedResponse>('/api/v1/seeds', data, { signal })
}

export function updateSeedApi(seedId: string, data: Record<string, unknown>, signal?: AbortSignal) {
  return apiPut<SeedResponse>(`/api/v1/seeds/${seedId}`, data, { signal })
}

export function deleteSeedApi(seedId: string, signal?: AbortSignal) {
  return apiDelete(`/api/v1/seeds/${seedId}`, { signal })
}
