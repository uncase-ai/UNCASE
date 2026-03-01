import type { Conversation } from '@/types/api'
import { apiGet, apiPost, apiUpload } from './client'

// ─── Types ───

export interface ConnectorImportResponse {
  conversations: Conversation[]
  total_imported: number
  total_skipped: number
  total_pii_anonymized: number
  errors: string[]
  warnings: string[]
}

export interface WebhookPayload {
  conversations: Array<{
    turns: Array<{
      role: string
      content: string
    }>
  }>
  source?: string
}

export interface PIIEntity {
  category: string
  start: number
  end: number
  score: number
  source: string
}

export interface PIIScanResponse {
  text_length: number
  pii_found: boolean
  entity_count: number
  entities: PIIEntity[]
  anonymized_preview: string
  scanner_mode: string
}

export interface ConnectorInfo {
  name: string
  slug: string
  description: string
  supported_formats: string[]
  endpoint: string
  method: string
  accepts: string
}

// ─── Hugging Face Types ───

export interface HFDatasetInfo {
  repo_id: string
  description: string | null
  downloads: number
  likes: number
  tags: string[]
  last_modified: string
  size_bytes: number | null
}

export interface HFUploadRequest {
  conversation_ids: string[]
  repo_id: string
  token: string
  private: boolean
}

export interface HFUploadResult {
  repo_id: string
  url: string
  commit_hash: string
  files_uploaded: number
}

// ─── API Functions ───

export function listConnectors(signal?: AbortSignal) {
  return apiGet<ConnectorInfo[]>('/api/v1/connectors', { signal })
}

export function importWhatsApp(file: File, signal?: AbortSignal) {
  return apiUpload<ConnectorImportResponse>('/api/v1/connectors/whatsapp', file, undefined, { signal })
}

export function receiveWebhook(payload: WebhookPayload, signal?: AbortSignal) {
  return apiPost<ConnectorImportResponse>('/api/v1/connectors/webhook', payload, { signal })
}

export function scanTextForPii(text: string, signal?: AbortSignal) {
  return apiPost<PIIScanResponse>('/api/v1/connectors/scan-pii', text, { signal })
}

// ─── Hugging Face API Functions ───

export function searchHFDatasets(query: string, limit: number = 20, signal?: AbortSignal) {
  return apiGet<HFDatasetInfo[]>(`/api/v1/connectors/huggingface/search?query=${encodeURIComponent(query)}&limit=${limit}`, { signal })
}

export function importHFDataset(repoId: string, split: string = 'train', token?: string, signal?: AbortSignal) {
  const headers: Record<string, string> = {}

  if (token) headers['X-HF-Token'] = token

  return apiPost<ConnectorImportResponse>(
    `/api/v1/connectors/huggingface/import?repo_id=${encodeURIComponent(repoId)}&split=${encodeURIComponent(split)}`,
    undefined,
    { signal, headers }
  )
}

export function uploadToHF(request: HFUploadRequest, signal?: AbortSignal) {
  return apiPost<HFUploadResult>('/api/v1/connectors/huggingface/upload', request, { signal })
}

export function listHFRepos(token: string, limit: number = 20, signal?: AbortSignal) {
  return apiGet<HFDatasetInfo[]>(`/api/v1/connectors/huggingface/repos?limit=${limit}`, {
    signal,
    headers: { 'X-HF-Token': token },
  })
}
