import type {
  APIKeyCreate,
  APIKeyCreatedResponse,
  APIKeyResponse,
  OrganizationCreate,
  OrganizationResponse,
  OrganizationUpdate
} from '@/types/api'
import { apiDelete, apiGet, apiPost, apiPut } from './client'

// ─── Organizations ───
export function createOrganization(data: OrganizationCreate, signal?: AbortSignal) {
  return apiPost<OrganizationResponse>('/api/v1/organizations', data, { signal })
}

export function fetchOrganization(orgId: string, signal?: AbortSignal) {
  return apiGet<OrganizationResponse>(`/api/v1/organizations/${orgId}`, { signal })
}

export function updateOrganization(orgId: string, data: OrganizationUpdate, signal?: AbortSignal) {
  return apiPut<OrganizationResponse>(`/api/v1/organizations/${orgId}`, data, { signal })
}

// ─── API Keys ───
export function createApiKey(orgId: string, data: APIKeyCreate, signal?: AbortSignal) {
  return apiPost<APIKeyCreatedResponse>(`/api/v1/organizations/${orgId}/api-keys`, data, { signal })
}

export function fetchApiKeys(orgId: string, signal?: AbortSignal) {
  return apiGet<APIKeyResponse[]>(`/api/v1/organizations/${orgId}/api-keys`, { signal })
}

export function revokeApiKey(orgId: string, keyId: string, signal?: AbortSignal) {
  return apiDelete(`/api/v1/organizations/${orgId}/api-keys/${keyId}`, { signal })
}

export function rotateApiKey(orgId: string, keyId: string, signal?: AbortSignal) {
  return apiPost<APIKeyCreatedResponse>(`/api/v1/organizations/${orgId}/api-keys/${keyId}/rotate`, undefined, {
    signal
  })
}
