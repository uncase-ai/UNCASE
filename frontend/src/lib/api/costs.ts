import { apiGet } from './client'
import type { CostSummary, DailyCost, JobCost } from '@/types/api'

export async function fetchCostSummary(periodDays = 30) {
  return apiGet<CostSummary>(`/api/v1/costs/summary?period_days=${periodDays}`)
}

export async function fetchJobCost(jobId: string) {
  return apiGet<JobCost>(`/api/v1/costs/job/${jobId}`)
}

export async function fetchDailyCosts(days = 30) {
  return apiGet<DailyCost[]>(`/api/v1/costs/daily?days=${days}`)
}
