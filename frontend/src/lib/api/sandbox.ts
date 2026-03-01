import type { Conversation, SeedSchema } from '@/types/api'
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
  conversations: Conversation[]
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
  started_at: string
}

// ─── Demo Sandbox ───

export interface DemoSandboxRequest {
  domain: string
  ttl_minutes?: number
  preload_seeds?: number
  language?: string
}

export interface SandboxJob {
  job_id: string
  template: string
  status: 'pending' | 'booting' | 'running' | 'exporting' | 'completed' | 'failed' | 'expired'
  organization_id: string | null
  sandbox_url: string | null
  api_url: string | null
  opik_url: string | null
  created_at: string
  expires_at: string | null
  error: string | null
  metadata: Record<string, string>
}

export interface DemoSandboxResponse {
  job: SandboxJob
  api_url: string
  docs_url: string
  expires_at: string
  preloaded_seeds: number
  domain: string
  fallback?: boolean
  demo_seeds?: unknown[]
}

// ─── Opik Evaluation ───

export interface OpikEvaluationRequest {
  conversations: Conversation[]
  seeds: SeedSchema[]
  experiment_name?: string
  model?: string
  provider_id?: string
  ttl_minutes?: number
  run_hallucination_check?: boolean
  run_coherence_check?: boolean
  run_relevance_check?: boolean
  export_before_destroy?: boolean
}

export interface OpikMetricResult {
  metric_name: string
  value: number
  reason: string | null
}

export interface OpikConversationResult {
  conversation_id: string
  seed_id: string
  metrics: OpikMetricResult[]
  uncase_composite_score: number
  opik_avg_score: number
}

export interface OpikEvaluationSummary {
  total_conversations: number
  avg_hallucination: number | null
  avg_coherence: number | null
  avg_relevance: number | null
  avg_uncase_composite: number
  avg_opik_score: number
  passed_uncase: number
  duration_seconds: number
}

export interface OpikEvaluationResponse {
  job: SandboxJob
  experiment_name: string
  results: OpikConversationResult[]
  summary: OpikEvaluationSummary
  opik_url: string | null
  exported: boolean
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
