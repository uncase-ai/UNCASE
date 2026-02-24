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
