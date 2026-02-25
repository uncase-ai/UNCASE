import type { JobResponse } from '@/types/api'
import { apiGet, apiPost } from './client'

// ─── Job CRUD ───

export function fetchJobs(
  params?: { job_type?: string; status?: string; page?: number; page_size?: number },
  signal?: AbortSignal
) {
  const query = new URLSearchParams()

  if (params?.job_type) query.set('job_type', params.job_type)
  if (params?.status) query.set('status', params.status)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const qs = query.toString()

  return apiGet<JobResponse[]>(`/api/v1/jobs${qs ? `?${qs}` : ''}`, { signal })
}

export function fetchJob(jobId: string, signal?: AbortSignal) {
  return apiGet<JobResponse>(`/api/v1/jobs/${jobId}`, { signal })
}

export function cancelJob(jobId: string, signal?: AbortSignal) {
  return apiPost<JobResponse>(`/api/v1/jobs/${jobId}/cancel`, undefined, { signal })
}

// ─── Job status helpers ───

export function isJobTerminal(job: JobResponse): boolean {
  return ['completed', 'failed', 'cancelled'].includes(job.status)
}

export function getJobStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'text-green-600'
    case 'failed':
      return 'text-red-600'
    case 'running':
      return 'text-blue-600'
    case 'cancelled':
      return 'text-gray-500'
    default:
      return 'text-yellow-600'
  }
}

export function getJobStatusBadge(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'completed':
      return 'default'
    case 'failed':
      return 'destructive'
    case 'running':
      return 'secondary'
    default:
      return 'outline'
  }
}
