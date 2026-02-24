import type { ToolDefinition, ToolResult } from '@/types/api'
import { apiGet, apiPost } from './client'

export function fetchTools(params?: { domain?: string; category?: string }, signal?: AbortSignal) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.category) query.set('category', params.category)
  const qs = query.toString()

  return apiGet<ToolDefinition[]>(`/api/v1/tools${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchTool(name: string, signal?: AbortSignal) {
  return apiGet<ToolDefinition>(`/api/v1/tools/${encodeURIComponent(name)}`, { signal })
}

export function registerTool(tool: ToolDefinition, signal?: AbortSignal) {
  return apiPost<ToolDefinition>('/api/v1/tools', tool, { signal })
}

export function simulateTool(name: string, args: Record<string, unknown>, signal?: AbortSignal) {
  return apiPost<ToolResult>(`/api/v1/tools/${encodeURIComponent(name)}/simulate`, args, { signal })
}
