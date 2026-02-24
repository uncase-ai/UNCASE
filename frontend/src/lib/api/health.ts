import type { HealthDbResponse, HealthResponse } from '@/types/api'
import { apiGet } from './client'

export function fetchHealth(signal?: AbortSignal) {
  return apiGet<HealthResponse>('/health', { signal })
}

export function fetchHealthDb(signal?: AbortSignal) {
  return apiGet<HealthDbResponse>('/health/db', { signal })
}
