import type { SeedSchema } from '@/types/api'
import { apiGet, apiPost } from './client'

// ─── Types ───

export interface SandboxStatusResponse {
  enabled: boolean
  max_parallel: number
  template_id: string
}

export interface SandboxGenerateRequest {
  seeds: SeedSchema[]
  count_per_seed: number
  model?: string
  provider_id?: string
  temperature?: number
  language_override?: string
  evaluate_after?: boolean
  max_parallel?: number
}

export interface SandboxSeedResult {
  seed_id: string
  conversations: unknown[]
  reports: unknown[] | null
  passed_count: number
  error: string | null
  duration_seconds: number
}

export interface SandboxGenerationSummary {
  total_seeds: number
  total_conversations: number
  total_passed: number | null
  avg_composite_score: number | null
  failed_seeds: number
  model_used: string
  temperature: number
  max_parallel: number
  duration_seconds: number
  sandbox_mode: boolean
}

export interface SandboxGenerateResponse {
  results: SandboxSeedResult[]
  summary: SandboxGenerationSummary
}

export interface DemoSandboxRequest {
  domain: string
  ttl_minutes?: number
  preload_seeds?: boolean
}

export interface DemoSandboxResponse {
  sandbox_id: string
  api_url: string
  domain: string
  ttl_minutes: number
  seeds_loaded: number
  expires_at: string
}

export interface OpikEvaluationRequest {
  conversations: unknown[]
  experiment_name?: string
  provider_id?: string
  ttl_minutes?: number
}

export interface OpikEvaluationResponse {
  experiment_name: string
  total_evaluated: number
  results: unknown[]
  duration_seconds: number
}

// ─── API Functions ───

export function fetchSandboxStatus(signal?: AbortSignal) {
  return apiGet<SandboxStatusResponse>('/api/v1/sandbox/status', { signal })
}

export function sandboxGenerate(request: SandboxGenerateRequest, signal?: AbortSignal) {
  return apiPost<SandboxGenerateResponse>('/api/v1/sandbox', request, { signal })
}

export function createDemoSandbox(request: DemoSandboxRequest, signal?: AbortSignal) {
  return apiPost<DemoSandboxResponse>('/api/v1/sandbox/demo', request, { signal })
}

export function runOpikEvaluation(request: OpikEvaluationRequest, signal?: AbortSignal) {
  return apiPost<OpikEvaluationResponse>('/api/v1/sandbox/evaluate', request, { signal })
}
