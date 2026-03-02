// ─── HuggingFace dataset row parsers ───
// Auto-detects common HF dataset formats and converts rows into UNCASE Conversation[]

import type { Conversation, ConversationTurn } from '@/types/api'
import type { HFRowsResponse } from './huggingface'

// ─── Format Detection ───

export type HFDatasetFormat =
  | 'messages'        // messages: [{role, content}]
  | 'sharegpt'        // conversations: [{from, value}]
  | 'rlhf'            // chosen / rejected with Human:/Assistant: markers
  | 'prompt-response' // prompt + response or instruction + output
  | 'unknown'

export function detectFormat(features: HFRowsResponse['features'], sampleRow?: Record<string, unknown>): HFDatasetFormat {
  const names = new Set(features.map(f => f.name.toLowerCase()))

  if (names.has('messages')) return 'messages'
  if (names.has('conversations')) return 'sharegpt'
  if (names.has('chosen') && names.has('rejected')) return 'rlhf'
  if (names.has('prompt') && names.has('response')) return 'prompt-response'
  if (names.has('instruction') && (names.has('output') || names.has('response'))) return 'prompt-response'
  if (names.has('input') && names.has('output')) return 'prompt-response'
  if (names.has('question') && names.has('answer')) return 'prompt-response'

  // Fallback: check sample row for nested message arrays
  if (sampleRow) {
    for (const val of Object.values(sampleRow)) {
      if (Array.isArray(val) && val.length > 0 && val[0] && typeof val[0] === 'object') {
        const first = val[0] as Record<string, unknown>

        if ('role' in first && 'content' in first) return 'messages'
        if ('from' in first && 'value' in first) return 'sharegpt'
      }
    }
  }

  return 'unknown'
}

// ─── Parsers ───

function makeTurn(turno: number, rol: string, contenido: string): ConversationTurn {
  return { turno, rol, contenido, herramientas_usadas: [], metadata: {} }
}

function parseMessages(row: Record<string, unknown>): ConversationTurn[] {
  const messages = (row.messages ?? row.Messages) as Array<{ role?: string; content?: string }> | undefined

  if (!Array.isArray(messages)) return []

  return messages
    .filter(m => m.content?.trim())
    .map((m, i) => makeTurn(i + 1, m.role ?? 'unknown', m.content ?? ''))
}

function parseShareGPT(row: Record<string, unknown>): ConversationTurn[] {
  const conversations = (row.conversations ?? row.Conversations) as Array<{ from?: string; value?: string }> | undefined

  if (!Array.isArray(conversations)) return []

  return conversations
    .filter(m => m.value?.trim())
    .map((m, i) => {
      const role = m.from === 'human' ? 'user' : m.from === 'gpt' ? 'assistant' : (m.from ?? 'unknown')

      return makeTurn(i + 1, role, m.value ?? '')
    })
}

function parseAnthropicStyle(text: string): ConversationTurn[] {
  const turns: ConversationTurn[] = []
  const parts = text.split(/\n\n(?=Human:|Assistant:)/)

  for (const part of parts) {
    const trimmed = part.trim()

    if (!trimmed) continue

    if (trimmed.startsWith('Human:')) {
      turns.push(makeTurn(turns.length + 1, 'user', trimmed.replace(/^Human:\s*/, '')))
    } else if (trimmed.startsWith('Assistant:')) {
      turns.push(makeTurn(turns.length + 1, 'assistant', trimmed.replace(/^Assistant:\s*/, '')))
    }
  }

  return turns
}

function parseRLHF(row: Record<string, unknown>): ConversationTurn[] {
  // Prefer 'chosen' response
  const chosen = row.chosen as string | Array<{ role?: string; content?: string }> | undefined

  if (Array.isArray(chosen) && chosen.length > 0 && typeof chosen[0] === 'object') {
    return chosen
      .filter(m => m.content?.trim())
      .map((m, i) => makeTurn(i + 1, m.role ?? 'unknown', m.content ?? ''))
  }

  if (typeof chosen === 'string' && chosen.includes('Human:')) {
    return parseAnthropicStyle(chosen)
  }

  // Fall back to rejected
  const rejected = row.rejected as string | undefined

  if (typeof rejected === 'string' && rejected.includes('Human:')) {
    return parseAnthropicStyle(rejected)
  }

  return []
}

function parsePromptResponse(row: Record<string, unknown>): ConversationTurn[] {
  const prompt = (row.prompt ?? row.instruction ?? row.input ?? row.question ?? row.context) as string | undefined
  const response = (row.response ?? row.output ?? row.answer ?? row.completion) as string | undefined

  const turns: ConversationTurn[] = []

  // Check for system / instruction prefix
  const system = row.system as string | undefined

  if (system?.trim()) {
    turns.push(makeTurn(turns.length + 1, 'system', system.trim()))
  }

  if (prompt?.trim()) {
    turns.push(makeTurn(turns.length + 1, 'user', prompt.trim()))
  }

  if (response?.trim()) {
    turns.push(makeTurn(turns.length + 1, 'assistant', response.trim()))
  }

  return turns
}

function parseFallback(row: Record<string, unknown>): ConversationTurn[] {
  // Look for longest text field
  let bestKey = ''
  let bestLen = 0

  for (const [key, val] of Object.entries(row)) {
    if (typeof val === 'string' && val.length > bestLen) {
      bestKey = key
      bestLen = val.length
    }
  }

  if (bestKey && bestLen > 10) {
    return [makeTurn(1, 'user', row[bestKey] as string)]
  }

  // Stringify the whole row
  return [makeTurn(1, 'user', JSON.stringify(row))]
}

// ─── Main Parser ───

export interface ParseResult {
  conversations: Conversation[]
  format: HFDatasetFormat
  warnings: string[]
}

export function parseHFRowsToConversations(
  rowsResponse: HFRowsResponse,
  repoId: string,
  config: string
): ParseResult {
  const { features, rows } = rowsResponse
  const sampleRow = rows[0]?.row
  const format = detectFormat(features, sampleRow)
  const conversations: Conversation[] = []
  const warnings: string[] = []
  const timestamp = Date.now()

  if (format === 'unknown') {
    warnings.push('Could not detect a standard conversation format — using raw text fallback')
  }

  for (const { row_idx, row } of rows) {
    let turns: ConversationTurn[] = []

    switch (format) {
      case 'messages':
        turns = parseMessages(row)
        break
      case 'sharegpt':
        turns = parseShareGPT(row)
        break
      case 'rlhf':
        turns = parseRLHF(row)
        break
      case 'prompt-response':
        turns = parsePromptResponse(row)
        break
      default:
        turns = parseFallback(row)
    }

    if (turns.length === 0) {
      warnings.push(`Row ${row_idx}: no turns extracted`)
      continue
    }

    conversations.push({
      conversation_id: `hf-${repoId.replace('/', '-')}-${row_idx}-${timestamp}`,
      seed_id: 'hf-import',
      dominio: 'automotive.sales',
      idioma: 'en',
      turnos: turns,
      es_sintetica: false,
      created_at: new Date().toISOString(),
      metadata: {
        source: 'huggingface',
        repo_id: repoId,
        config,
        row_idx,
        detected_format: format,
      },
    })
  }

  return { conversations, format, warnings }
}
