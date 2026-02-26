import type { Conversation } from '@/types/api'
import { apiGet, apiPost, apiPatch, apiDelete } from './client'

// ─── Types ───

export interface ConversationResponse extends Conversation {
  id: string
  num_turnos: number
  organization_id: string | null
  updated_at: string
}

export interface ConversationListResponse {
  items: ConversationResponse[]
  total: number
  page: number
  page_size: number
}

export interface ConversationBulkCreateResponse {
  created: number
  skipped: number
  errors: string[]
}

// ─── API calls ───

export function fetchConversations(
  params?: { domain?: string; language?: string; status?: string; seed_id?: string; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.language) query.set('language', params.language)
  if (params?.status) query.set('status', params.status)
  if (params?.seed_id) query.set('seed_id', params.seed_id)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<ConversationListResponse>(`/api/v1/conversations${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchConversation(conversationId: string, signal?: AbortSignal) {
  return apiGet<ConversationResponse>(`/api/v1/conversations/${conversationId}`, { signal })
}

export function createConversationApi(data: Record<string, unknown>, signal?: AbortSignal) {
  return apiPost<ConversationResponse>('/api/v1/conversations', data, { signal })
}

export function bulkCreateConversations(conversations: Record<string, unknown>[], signal?: AbortSignal) {
  return apiPost<ConversationBulkCreateResponse>('/api/v1/conversations/bulk', { conversations }, { signal })
}

export function updateConversationApi(
  conversationId: string,
  data: { status?: string; rating?: number; tags?: string[]; notes?: string },
  signal?: AbortSignal
) {
  return apiPatch<ConversationResponse>(`/api/v1/conversations/${conversationId}`, data, { signal })
}

export function deleteConversationApi(conversationId: string, signal?: AbortSignal) {
  return apiDelete(`/api/v1/conversations/${conversationId}`, { signal })
}
