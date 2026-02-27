import type {
  BatchEvaluationResponse,
  Conversation,
  QualityReport,
  QualityThresholdsResponse,
  SeedSchema
} from '@/types/api'
import { apiGet, apiPost } from './client'

export interface EvaluateRequest {
  conversation: Conversation
  seed: SeedSchema
}

export interface EvaluateBatchRequest {
  pairs: Array<{ conversation: Conversation; seed: SeedSchema }>
}

export function evaluateConversation(conversation: Conversation, seed: SeedSchema, signal?: AbortSignal) {
  const body: EvaluateRequest = { conversation, seed }

  return apiPost<QualityReport>('/api/v1/evaluations', body, { signal })
}

export function evaluateBatch(
  pairs: Array<{ conversation: Conversation; seed: SeedSchema }>,
  signal?: AbortSignal
) {
  const body: EvaluateBatchRequest = { pairs }

  return apiPost<BatchEvaluationResponse>('/api/v1/evaluations/batch', body, { signal })
}

export function fetchThresholds(signal?: AbortSignal) {
  return apiGet<QualityThresholdsResponse>('/api/v1/evaluations/thresholds', { signal })
}

// ─── Persisted evaluation reports ───

export interface EvaluationReportResponse {
  id: string
  conversation_id: string
  seed_id: string | null
  rouge_l: number
  fidelidad_factual: number
  diversidad_lexica: number
  coherencia_dialogica: number
  privacy_score: number
  memorizacion: number
  tool_call_validity: number | null
  composite_score: number
  passed: boolean
  failures: string[]
  dominio: string | null
  organization_id: string | null
  created_at: string
}

export interface EvaluationReportListResponse {
  items: EvaluationReportResponse[]
  total: number
  page: number
  page_size: number
}

export function fetchEvaluationReports(
  params?: { domain?: string; passed?: boolean; seed_id?: string; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.passed !== undefined) query.set('passed', String(params.passed))
  if (params?.seed_id) query.set('seed_id', params.seed_id)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<EvaluationReportListResponse>(`/api/v1/evaluations/reports${qs ? `?${qs}` : ''}`, { signal })
}
