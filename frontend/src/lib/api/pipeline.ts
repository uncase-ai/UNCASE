import type { PipelineRunRequest, PipelineRunResponse } from '@/types/api'
import { apiPost } from './client'

// ─── Pipeline API ───

export function submitPipelineRun(data: PipelineRunRequest, signal?: AbortSignal) {
  return apiPost<PipelineRunResponse>('/api/v1/pipeline/run', data, { signal })
}
