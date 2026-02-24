import type { ImportResult } from '@/types/api'
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
