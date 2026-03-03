// ─── Layer 0 Agentic Extraction API client ───

import type {
  ProgressResponse,
  StartExtractionRequest,
  StartExtractionResponse,
  TurnRequest,
  TurnResponse,
} from '@/types/layer0'

import { apiDelete, apiGet, apiPost } from './client'

export function startExtraction(body: StartExtractionRequest) {
  return apiPost<StartExtractionResponse>('/api/v1/seeds/extract/start', body)
}

export function sendTurn(body: TurnRequest) {
  return apiPost<TurnResponse>('/api/v1/seeds/extract/turn', body)
}

export function getProgress(sessionId: string) {
  return apiGet<ProgressResponse>(`/api/v1/seeds/extract/${sessionId}/progress`)
}

export function endSession(sessionId: string) {
  return apiDelete(`/api/v1/seeds/extract/${sessionId}`)
}
