import type {
  WebhookDeliveryListResponse,
  WebhookListResponse,
  WebhookSubscriptionCreate,
  WebhookSubscriptionCreatedResponse,
  WebhookSubscriptionResponse,
  WebhookSubscriptionUpdate
} from '@/types/api'
import { apiDelete, apiGet, apiPatch, apiPost } from './client'

export function createWebhookSubscription(data: WebhookSubscriptionCreate, signal?: AbortSignal) {
  return apiPost<WebhookSubscriptionCreatedResponse>('/api/v1/webhooks', data, { signal })
}

export function fetchWebhookSubscriptions(
  params?: { is_active?: boolean; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.is_active !== undefined) query.set('is_active', String(params.is_active))
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<WebhookListResponse>(`/api/v1/webhooks${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchWebhookSubscription(id: string, signal?: AbortSignal) {
  return apiGet<WebhookSubscriptionResponse>(`/api/v1/webhooks/${id}`, { signal })
}

export function updateWebhookSubscription(id: string, data: WebhookSubscriptionUpdate, signal?: AbortSignal) {
  return apiPatch<WebhookSubscriptionResponse>(`/api/v1/webhooks/${id}`, data, { signal })
}

export function deleteWebhookSubscription(id: string, signal?: AbortSignal) {
  return apiDelete(`/api/v1/webhooks/${id}`, { signal })
}

export function sendTestWebhook(id: string, signal?: AbortSignal) {
  return apiPost<{ status: string; message: string }>(`/api/v1/webhooks/${id}/test`, undefined, { signal })
}

export function fetchWebhookDeliveries(
  subscriptionId: string,
  params?: { status?: string; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.status) query.set('status', params.status)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<WebhookDeliveryListResponse>(
    `/api/v1/webhooks/${subscriptionId}/deliveries${qs ? `?${qs}` : ''}`,
    { signal }
  )
}

export function fetchWebhookEventTypes(signal?: AbortSignal) {
  return apiGet<string[]>('/api/v1/webhooks/meta/event-types', { signal })
}
