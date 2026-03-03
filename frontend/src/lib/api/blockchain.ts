import { apiGet, apiPost } from './client'
import type { AnchorSchedule, BatchBuildResponse, BlockchainStats, MerkleBatch, VerificationResponse } from '@/types/api'

export function fetchBlockchainStats(signal?: AbortSignal) {
  return apiGet<BlockchainStats>('/api/v1/blockchain/stats', { signal })
}

export function fetchVerification(reportId: string, signal?: AbortSignal) {
  return apiGet<VerificationResponse>(`/api/v1/blockchain/verify/${reportId}`, { signal })
}

export function fetchBatches(
  params?: { anchored?: boolean; limit?: number; offset?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.anchored !== undefined) query.set('anchored', String(params.anchored))
  if (params?.limit) query.set('limit', String(params.limit))
  if (params?.offset) query.set('offset', String(params.offset))

  const qs = query.toString()

  return apiGet<MerkleBatch[]>(`/api/v1/blockchain/batches${qs ? `?${qs}` : ''}`, { signal })
}

export function buildBatch(signal?: AbortSignal) {
  return apiPost<BatchBuildResponse>('/api/v1/blockchain/batch', {}, { signal })
}

export function retryAnchor(batchId: string, signal?: AbortSignal) {
  return apiPost<BatchBuildResponse>('/api/v1/blockchain/retry-anchor', { batch_id: batchId }, { signal })
}

export function fetchAnchorSchedule(signal?: AbortSignal) {
  return apiGet<AnchorSchedule>('/api/v1/blockchain/schedule', { signal })
}
