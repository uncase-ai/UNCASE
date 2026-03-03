// ─── Layer 0 Agentic Extraction Types ───

export type FieldStatusValue = 'empty' | 'extracted' | 'confirmed' | 'ambiguous'

export interface FieldProgress {
  status: FieldStatusValue
  confidence: number
  is_required: boolean
}

export interface ExtractionProgress {
  turn: number
  max_turns: number
  total_fields: number
  filled_fields: number
  required_total: number
  required_filled: number
  is_complete: boolean
  fields: Record<string, FieldProgress>
}

export interface EngineMessage {
  type: 'question' | 'summary'
  content: string
  progress?: ExtractionProgress
  seed?: Record<string, unknown>
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  progress?: ExtractionProgress
}

export interface ExtractionSession {
  sessionId: string
  messages: ChatMessage[]
  progress: ExtractionProgress | null
  isComplete: boolean
  seed: Record<string, unknown> | null
}

// API payloads
export interface StartExtractionRequest {
  industry: string
  max_turns?: number
  locale?: string
}

export interface StartExtractionResponse {
  session_id: string
  message: EngineMessage
}

export interface TurnRequest {
  session_id: string
  user_message: string
}

export interface TurnResponse {
  session_id: string
  message: EngineMessage
  is_complete: boolean
}

export interface ProgressResponse {
  session_id: string
  progress: ExtractionProgress
}
