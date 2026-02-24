import type { Conversation, ImportResult } from '@/types/api'
import { apiUpload } from './client'

export function importCsv(file: File, signal?: AbortSignal) {
  return apiUpload<ImportResult>('/api/v1/import/csv', file, undefined, { signal })
}

export function importJsonl(file: File, sourceFormat?: string, signal?: AbortSignal) {
  const params = sourceFormat ? { source_format: sourceFormat } : undefined

  return apiUpload<ImportResult>('/api/v1/import/jsonl', file, params, { signal })
}

export function detectFormat(filename: string): 'csv' | 'jsonl' | 'unknown' {
  const ext = filename.split('.').pop()?.toLowerCase()

  if (ext === 'csv') return 'csv'
  if (ext === 'jsonl' || ext === 'ndjson') return 'jsonl'

  return 'unknown'
}

// ─── Client-side JSONL parser (fallback when API is unreachable) ───

function parseJsonlLine(line: string, lineNumber: number): { conversation: Conversation | null; error: string | null } {
  try {
    const obj = JSON.parse(line)

    // Accept UNCASE native format (has conversation_id + turnos)
    if (obj.conversation_id && Array.isArray(obj.turnos)) {
      return { conversation: obj as Conversation, error: null }
    }

    // Accept OpenAI/ShareGPT format (has "conversations" or "messages" array)
    const messages = obj.messages ?? obj.conversations

    if (Array.isArray(messages) && messages.length > 0) {
      const turns = messages.map((m: { role?: string; content?: string; from?: string; value?: string }, i: number) => ({
        turno: i + 1,
        rol: m.role ?? m.from ?? 'unknown',
        contenido: m.content ?? m.value ?? '',
        herramientas_usadas: [],
        metadata: {}
      }))

      const conv: Conversation = {
        conversation_id: obj.id ?? obj.conversation_id ?? `import-${Date.now()}-${lineNumber}`,
        seed_id: obj.seed_id ?? 'imported',
        dominio: obj.domain ?? obj.dominio ?? 'automotive.sales',
        idioma: obj.language ?? obj.idioma ?? 'es',
        turnos: turns,
        es_sintetica: obj.es_sintetica ?? obj.synthetic ?? false,
        created_at: obj.created_at ?? new Date().toISOString(),
        metadata: obj.metadata ?? {}
      }

      return { conversation: conv, error: null }
    }

    return { conversation: null, error: `Line ${lineNumber}: unrecognized conversation format` }
  } catch {
    return { conversation: null, error: `Line ${lineNumber}: invalid JSON` }
  }
}

export async function parseJsonlLocally(file: File): Promise<ImportResult> {
  const text = await file.text()
  const lines = text.split('\n').filter(l => l.trim().length > 0)

  const conversations: Conversation[] = []
  const errors: { line: number; error: string }[] = []

  for (let i = 0; i < lines.length; i++) {
    const { conversation, error } = parseJsonlLine(lines[i], i + 1)

    if (conversation) {
      conversations.push(conversation)
    } else if (error) {
      errors.push({ line: i + 1, error })
    }
  }

  return {
    conversations_imported: conversations.length,
    conversations_failed: errors.length,
    errors,
    conversations
  }
}
