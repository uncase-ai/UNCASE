import type {
  ProviderCreateRequest,
  ProviderListResponse,
  ProviderResponse,
  ProviderTestResponse,
  ProviderUpdateRequest
} from '@/types/api'

import { apiDelete, apiGet, apiPost, apiPut } from './client'

export function fetchProviders(activeOnly = true, signal?: AbortSignal) {
  return apiGet<ProviderListResponse>(`/api/v1/providers?active_only=${activeOnly}`, { signal })
}

export function fetchProvider(id: string, signal?: AbortSignal) {
  return apiGet<ProviderResponse>(`/api/v1/providers/${id}`, { signal })
}

export function createProvider(data: ProviderCreateRequest) {
  return apiPost<ProviderResponse>('/api/v1/providers', data)
}

export function updateProvider(id: string, data: ProviderUpdateRequest) {
  return apiPut<ProviderResponse>(`/api/v1/providers/${id}`, data)
}

export function deleteProvider(id: string) {
  return apiDelete(`/api/v1/providers/${id}`)
}

export function testProvider(id: string) {
  return apiPost<ProviderTestResponse>(`/api/v1/providers/${id}/test`)
}
