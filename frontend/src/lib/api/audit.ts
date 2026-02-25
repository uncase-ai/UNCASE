import { apiGet } from './client'
import type { AuditLogEntry } from '@/types/api'

export async function fetchAuditLogs(params?: {
  action?: string
  resource_type?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()

  if (params?.action) searchParams.set('action', params.action)
  if (params?.resource_type) searchParams.set('resource_type', params.resource_type)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  const query = searchParams.toString()
  const path = query ? `/api/v1/audit?${query}` : '/api/v1/audit'

  return apiGet<AuditLogEntry[]>(path)
}
