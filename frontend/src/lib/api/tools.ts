import type { CustomToolCreateRequest, CustomToolListResponse, CustomToolResponse, CustomToolUpdateRequest, ToolDefinition, ToolResult } from '@/types/api'
import { apiDelete, apiGet, apiPost, apiPut } from './client'

export function fetchTools(params?: { domain?: string; category?: string }, signal?: AbortSignal) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.category) query.set('category', params.category)
  const qs = query.toString()

  return apiGet<ToolDefinition[]>(`/api/v1/tools${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchCustomTools(
  params?: { domain?: string; category?: string; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.category) query.set('category', params.category)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))
  const qs = query.toString()

  return apiGet<CustomToolListResponse>(`/api/v1/tools/custom${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchTool(name: string, signal?: AbortSignal) {
  return apiGet<ToolDefinition>(`/api/v1/tools/${encodeURIComponent(name)}`, { signal })
}

export function registerTool(tool: CustomToolCreateRequest, signal?: AbortSignal) {
  return apiPost<CustomToolResponse>('/api/v1/tools', tool, { signal })
}

export function updateTool(toolId: string, data: CustomToolUpdateRequest, signal?: AbortSignal) {
  return apiPut<CustomToolResponse>(`/api/v1/tools/${encodeURIComponent(toolId)}`, data, { signal })
}

export function deleteTool(toolId: string, signal?: AbortSignal) {
  return apiDelete(`/api/v1/tools/${encodeURIComponent(toolId)}`, { signal })
}

export function simulateTool(name: string, args: Record<string, unknown>, signal?: AbortSignal) {
  return apiPost<ToolResult>(`/api/v1/tools/${encodeURIComponent(name)}/simulate`, args, { signal })
}

export function resolveToolsForDomain(domain: string, signal?: AbortSignal) {
  return apiGet<ToolDefinition[]>(`/api/v1/tools/resolve/${encodeURIComponent(domain)}`, { signal })
}
