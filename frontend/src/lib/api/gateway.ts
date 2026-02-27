import type { ChatRequest, ChatStreamChunk, ChatStreamComplete } from '@/types/api'
import { apiPost, getApiBase } from './client'

// ─── Types (re-exported from api.ts for convenience) ───

export type { ChatMessage, ChatRequest, ChatStreamChunk, ChatStreamComplete, ChatTool } from '@/types/api'

export interface ChatChoice {
  index: number
  message: { role: string; content: string }
  finish_reason: string
  tool_calls?: Record<string, unknown>[]
}

export interface PrivacyScanInfo {
  outbound_pii_found: number
  inbound_pii_found: number
  mode: string
  any_blocked: boolean
}

export interface ChatResponse {
  choices: ChatChoice[]
  model: string
  provider_name: string
  privacy: PrivacyScanInfo
}

// ─── Non-streaming ───

export function chatProxy(request: ChatRequest, signal?: AbortSignal) {
  return apiPost<ChatResponse>('/api/v1/gateway/chat', request, { signal })
}

// ─── Streaming (SSE) ───

export interface ChatStreamCallbacks {
  onToken: (chunk: ChatStreamChunk) => void
  onComplete: (data: ChatStreamComplete) => void
  onError: (error: string) => void
}

export async function chatProxyStream(
  request: ChatRequest,
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem('uncase-api-key') : null
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }

  if (apiKey) headers['X-API-Key'] = apiKey

  const res = await fetch(`${getApiBase()}/api/v1/gateway/chat/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify(request),
    signal
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Stream request failed' }))

    callbacks.onError(body.detail ?? `HTTP ${res.status}`)

    return
  }

  const reader = res.body?.getReader()

  if (!reader) {
    callbacks.onError('No response body')

    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')

      buffer = lines.pop() ?? ''

      let eventType = 'message'

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)

          try {
            const parsed = JSON.parse(jsonStr)

            if (eventType === 'done') {
              callbacks.onComplete(parsed as ChatStreamComplete)
            } else if (eventType === 'error') {
              callbacks.onError(parsed.error ?? 'Unknown stream error')
            } else {
              callbacks.onToken(parsed as ChatStreamChunk)
            }
          } catch {
            // Partial JSON, skip
          }

          eventType = 'message'
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
