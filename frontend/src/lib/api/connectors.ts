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
