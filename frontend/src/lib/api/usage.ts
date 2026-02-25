import type { ApiResponse } from './client'
import { apiGet } from './client'

// ─── Types ───

export interface UsageSummaryItem {
  event_type: string
  total_count: number
  event_count: number
}

export interface UsageSummaryResponse {
  organization_id: string | null
  period_start: string
  period_end: string
  items: UsageSummaryItem[]
  total_events: number
}

export interface UsageTimelinePoint {
  period: string
  count: number
}

export interface UsageTimelineResponse {
  organization_id: string | null
  event_type: string
  granularity: string
  points: UsageTimelinePoint[]
}

// ─── API functions ───

export function fetchUsageSummary(
  params?: { organization_id?: string; period_start?: string; period_end?: string },
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<UsageSummaryResponse>> {
  const search = new URLSearchParams()

  if (params?.organization_id) search.set('organization_id', params.organization_id)
  if (params?.period_start) search.set('period_start', params.period_start)
  if (params?.period_end) search.set('period_end', params.period_end)

  const qs = search.toString()

  return apiGet<UsageSummaryResponse>(`/api/v1/usage/summary${qs ? `?${qs}` : ''}`, options)
}

export function fetchUsageTimeline(
  eventType: string,
  params?: { organization_id?: string; granularity?: string; period_start?: string; period_end?: string },
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<UsageTimelineResponse>> {
  const search = new URLSearchParams({ event_type: eventType })

  if (params?.organization_id) search.set('organization_id', params.organization_id)
  if (params?.granularity) search.set('granularity', params.granularity)
  if (params?.period_start) search.set('period_start', params.period_start)
  if (params?.period_end) search.set('period_end', params.period_end)

  return apiGet<UsageTimelineResponse>(`/api/v1/usage/timeline?${search}`, options)
}

export function fetchEventTypes(
  options?: { signal?: AbortSignal }
): Promise<ApiResponse<string[]>> {
  return apiGet<string[]>('/api/v1/usage/event-types', options)
}
