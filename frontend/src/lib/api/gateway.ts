import { apiPost } from './client'

// ─── Types ───

export interface ChatMessage {
  role: string
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  provider_id?: string
  model?: string
  temperature?: number
  max_tokens?: number
  privacy_mode?: 'audit' | 'warn' | 'block'
}

export interface PrivacyScanInfo {
  outbound_pii_found: number
  inbound_pii_found: number
  mode: string
  any_blocked: boolean
}

export interface ChatChoice {
  index: number
  message: ChatMessage
  finish_reason: string
}

export interface ChatResponse {
  choices: ChatChoice[]
  model: string
  provider_name: string
  privacy: PrivacyScanInfo
}

// ─── API Functions ───

export function chatProxy(request: ChatRequest, signal?: AbortSignal) {
  return apiPost<ChatResponse>('/api/v1/gateway/chat', request, { signal })
}
