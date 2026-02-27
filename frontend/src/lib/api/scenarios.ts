import type {
  ScenarioListResponse,
  ScenarioPackDetail,
  ScenarioPackListResponse,
  SkillLevel
} from '@/types/api'
import { apiGet } from './client'

/**
 * Fetch all available scenario packs (lightweight summaries).
 */
export function fetchScenarioPacks(signal?: AbortSignal) {
  return apiGet<ScenarioPackListResponse>('/api/v1/scenarios/packs', { signal })
}

/**
 * Fetch a single scenario pack with full scenario templates.
 */
export function fetchScenarioPack(domain: string, signal?: AbortSignal) {
  return apiGet<ScenarioPackDetail>(`/api/v1/scenarios/packs/${encodeURIComponent(domain)}`, { signal })
}

/**
 * Fetch scenarios from a pack with optional filters.
 */
export function fetchScenarios(
  domain: string,
  params?: {
    skill_level?: SkillLevel
    edge_case?: boolean
    tag?: string
  },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.skill_level) query.set('skill_level', params.skill_level)
  if (params?.edge_case !== undefined) query.set('edge_case', String(params.edge_case))
  if (params?.tag) query.set('tag', params.tag)

  const qs = query.toString()

  return apiGet<ScenarioListResponse>(
    `/api/v1/scenarios/packs/${encodeURIComponent(domain)}/scenarios${qs ? `?${qs}` : ''}`,
    { signal }
  )
}
