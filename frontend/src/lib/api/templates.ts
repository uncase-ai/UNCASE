import type { RenderRequest, RenderResponse, TemplateInfo } from '@/types/api'
import { apiGet, apiPost, API_BASE } from './client'

export function fetchTemplates(signal?: AbortSignal) {
  return apiGet<TemplateInfo[]>('/api/v1/templates', { signal })
}

export function renderTemplate(req: RenderRequest, signal?: AbortSignal) {
  return apiPost<RenderResponse>('/api/v1/templates/render', req, { signal })
}

export function exportTemplateUrl(): string {
  return `${API_BASE}/api/v1/templates/export`
}

export async function downloadExport(req: RenderRequest, signal?: AbortSignal): Promise<Blob | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/templates/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
      signal
    })

    if (!res.ok) return null

    return await res.blob()
  } catch {
    return null
  }
}
