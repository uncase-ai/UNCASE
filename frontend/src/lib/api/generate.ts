import type { GenerateRequest, GenerateResponse } from '@/types/api'
import { apiPost } from './client'

export function generateConversations(request: GenerateRequest, signal?: AbortSignal) {
  return apiPost<GenerateResponse>('/api/v1/generate', request, { signal })
}
