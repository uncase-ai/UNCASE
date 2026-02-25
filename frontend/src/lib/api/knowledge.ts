import type { ApiResponse } from './client'
import { apiDelete, apiGet, apiPost } from './client'

// ─── Types ───

export interface KnowledgeUploadRequest {
  filename: string
  content: string
  domain: string
  type: string
  tags?: string[]
  chunk_size?: number
  chunk_overlap?: number
}

export interface KnowledgeChunkResponse {
  id: string
  document_id: string
  content: string
  type: string
  domain: string
  tags: string[]
  source: string
  order: number
  created_at: string
}

export interface KnowledgeDocumentResponse {
  id: string
  filename: string
  domain: string
  type: string
  chunk_count: number
  size_bytes: number | null
  organization_id: string | null
  metadata: Record<string, unknown> | null
  chunks: KnowledgeChunkResponse[]
  created_at: string
  updated_at: string
}

export interface KnowledgeDocumentSummary {
  id: string
  filename: string
  domain: string
  type: string
  chunk_count: number
  size_bytes: number | null
  organization_id: string | null
  metadata: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface KnowledgeListResponse {
  items: KnowledgeDocumentSummary[]
  total: number
  page: number
  page_size: number
}

export interface KnowledgeSearchResult {
  chunk_id: string
  document_id: string
  filename: string
  content: string
  type: string
  domain: string
  tags: string[]
  order: number
}

export interface KnowledgeSearchResponse {
  query: string
  results: KnowledgeSearchResult[]
  total: number
}

// ─── API functions ───

export function uploadKnowledgeDocument(
  data: KnowledgeUploadRequest,
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<KnowledgeDocumentResponse>> {
  return apiPost<KnowledgeDocumentResponse>('/api/v1/knowledge', data, options)
}

export function fetchKnowledgeDocuments(
  params?: { domain?: string; type?: string; page?: number; page_size?: number },
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<KnowledgeListResponse>> {
  const search = new URLSearchParams()

  if (params?.domain) search.set('domain', params.domain)
  if (params?.type) search.set('type', params.type)
  if (params?.page) search.set('page', String(params.page))
  if (params?.page_size) search.set('page_size', String(params.page_size))

  const qs = search.toString()

  return apiGet<KnowledgeListResponse>(`/api/v1/knowledge${qs ? `?${qs}` : ''}`, options)
}

export function fetchKnowledgeDocument(
  docId: string,
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<KnowledgeDocumentResponse>> {
  return apiGet<KnowledgeDocumentResponse>(`/api/v1/knowledge/${docId}`, options)
}

export function deleteKnowledgeDocument(
  docId: string,
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<void>> {
  return apiDelete(`/api/v1/knowledge/${docId}`, options)
}

export function searchKnowledgeChunks(
  query: string,
  params?: { domain?: string; type?: string; limit?: number },
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<KnowledgeSearchResponse>> {
  const search = new URLSearchParams({ q: query })

  if (params?.domain) search.set('domain', params.domain)
  if (params?.type) search.set('type', params.type)
  if (params?.limit) search.set('limit', String(params.limit))

  return apiGet<KnowledgeSearchResponse>(`/api/v1/knowledge/search?${search}`, options)
}
