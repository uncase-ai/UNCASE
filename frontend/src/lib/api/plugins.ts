import type { InstalledPluginListResponse, InstalledPluginResponse, PluginManifest } from '@/types/api'

import { apiDelete, apiGet, apiPost, apiPut } from './client'

export function fetchPlugins(
  params?: { domain?: string; tag?: string; source?: string },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.domain) query.set('domain', params.domain)
  if (params?.tag) query.set('tag', params.tag)
  if (params?.source) query.set('source', params.source)
  const qs = query.toString()

  return apiGet<PluginManifest[]>(`/api/v1/plugins${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchInstalledPlugins(signal?: AbortSignal) {
  return apiGet<InstalledPluginListResponse>('/api/v1/plugins/installed', { signal })
}

export function fetchPlugin(id: string, signal?: AbortSignal) {
  return apiGet<PluginManifest>(`/api/v1/plugins/${encodeURIComponent(id)}`, { signal })
}

export function installPlugin(id: string) {
  return apiPost<InstalledPluginResponse>(`/api/v1/plugins/${encodeURIComponent(id)}/install`)
}

export function uninstallPlugin(id: string) {
  return apiDelete(`/api/v1/plugins/${encodeURIComponent(id)}/install`)
}

export function updatePluginConfig(id: string, data: { config?: Record<string, unknown>; is_active?: boolean }) {
  return apiPut<InstalledPluginResponse>(`/api/v1/plugins/${encodeURIComponent(id)}/config`, data)
}

export function publishPlugin(manifest: PluginManifest) {
  return apiPost<PluginManifest>('/api/v1/plugins', manifest)
}
