// ─── UNCASE API TypeScript Interfaces ───
// Mirrors backend Pydantic schemas exactly

// ─── Health ───
export interface HealthResponse {
  status: string
  version: string
}

export interface HealthDbResponse extends HealthResponse {
  database: 'connected' | 'disconnected'
}

// ─── Seed Schema v1 ───
export interface PasosTurnos {
  turnos_min: number
  turnos_max: number
  flujo_esperado: string[]
}

export interface ParametrosFactuales {
  contexto: string
  restricciones: string[]
  herramientas: string[]
  herramientas_definidas?: ToolDefinition[]
  metadata: Record<string, unknown>
}

export interface Privacidad {
  pii_eliminado: boolean
  metodo_anonimizacion: string
  nivel_confianza: number
  campos_sensibles_detectados: string[]
}

export interface MetricasCalidad {
  rouge_l_min: number
  fidelidad_min: number
  diversidad_lexica_min: number
  coherencia_dialogica_min: number
}

export interface SeedSchema {
  seed_id: string
  version: '1.0'
  dominio: string
  idioma: string
  etiquetas: string[]
  roles: string[]
  descripcion_roles: Record<string, string>
  objetivo: string
  tono: string
  pasos_turnos: PasosTurnos
  parametros_factuales: ParametrosFactuales
  privacidad: Privacidad
  metricas_calidad: MetricasCalidad
  organization_id?: string
  created_at: string
  updated_at: string
}

// ─── Tools ───
export interface ToolDefinition {
  name: string
  description: string
  input_schema: Record<string, unknown>
  output_schema?: Record<string, unknown>
  domains: string[]
  category: string
  requires_auth: boolean
  execution_mode: 'simulated' | 'live' | 'mock'
  version: string
  metadata: Record<string, unknown>
}

export interface ToolCall {
  tool_call_id: string
  tool_name: string
  arguments: Record<string, unknown>
}

export interface ToolResult {
  tool_call_id: string
  tool_name: string
  result: Record<string, unknown> | string
  status: 'success' | 'error' | 'timeout'
  duration_ms?: number
}

// ─── Conversations ───
export interface ConversationTurn {
  turno: number
  rol: string
  contenido: string
  herramientas_usadas: string[]
  tool_calls?: ToolCall[]
  tool_results?: ToolResult[]
  metadata: Record<string, unknown>
}

export interface Conversation {
  conversation_id: string
  seed_id: string
  dominio: string
  idioma: string
  turnos: ConversationTurn[]
  es_sintetica: boolean
  created_at: string
  metadata: Record<string, unknown>
}

// ─── Templates ───
export interface TemplateInfo {
  name: string
  display_name: string
  supports_tool_calls: boolean
  special_tokens: string[]
}

export interface RenderRequest {
  conversations: Conversation[]
  template_name: string
  tool_call_mode?: 'none' | 'inline'
  system_prompt?: string
}

export interface RenderResponse {
  rendered: string[]
  template_name: string
  count: number
}

// ─── Import ───
export interface ImportErrorDetail {
  line: number
  error: string
}

export interface ImportResult {
  conversations_imported: number
  conversations_failed: number
  errors: ImportErrorDetail[]
  conversations: Conversation[]
}

// ─── Organizations ───
export interface OrganizationCreate {
  name: string
  slug?: string
  description?: string
}

export interface OrganizationUpdate {
  name?: string
  description?: string
  is_active?: boolean
}

export interface OrganizationResponse {
  id: string
  name: string
  slug: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

// ─── API Keys ───
export interface APIKeyCreate {
  name: string
  scopes?: string
}

export interface APIKeyResponse {
  id: string
  key_id: string
  key_prefix: string
  name: string
  scopes: string
  is_active: boolean
  expires_at: string | null
  last_used_at: string | null
  created_at: string
}

export interface APIKeyCreatedResponse {
  id: string
  key_id: string
  key_prefix: string
  name: string
  scopes: string
  plain_key: string
  created_at: string
}

// ─── Quality ───
export interface QualityMetrics {
  rouge_l: number
  fidelidad_factual: number
  diversidad_lexica: number
  coherencia_dialogica: number
  privacy_score: number
  memorizacion: number
}

export interface QualityReport {
  conversation_id: string
  seed_id: string
  metrics: QualityMetrics
  composite_score: number
  passed: boolean
  failures: string[]
  evaluated_at: string
}

// ─── Validation ───
export interface ValidationCheck {
  name: string
  passed: boolean
  severity: 'error' | 'warning' | 'info'
  message: string
}

export interface ValidationReport {
  target_id: string
  target_type: string
  checks: ValidationCheck[]
  validated_at: string
}

// ─── Seed CRUD ───
export interface SeedResponse {
  id: string
  dominio: string
  idioma: string
  version: string
  etiquetas: string[]
  objetivo: string
  tono: string
  roles: string[]
  descripcion_roles: Record<string, string>
  pasos_turnos: PasosTurnos
  parametros_factuales: ParametrosFactuales
  privacidad: Privacidad
  metricas_calidad: MetricasCalidad
  organization_id: string | null
  created_at: string
  updated_at: string
}

export interface SeedListResponse {
  items: SeedResponse[]
  total: number
  page: number
  page_size: number
}

// ─── Generation ───
export interface GenerateRequest {
  seed: SeedSchema
  count: number
  temperature: number
  model?: string
  language_override?: string
  evaluate_after: boolean
}

export interface GenerationSummary {
  total_generated: number
  total_passed: number | null
  avg_composite_score: number | null
  model_used: string
  temperature: number
  duration_seconds: number
}

export interface GenerateResponse {
  conversations: Conversation[]
  reports: QualityReport[] | null
  generation_summary: GenerationSummary
}

// ─── Batch Evaluation ───
export interface BatchEvaluationResponse {
  total: number
  passed: number
  failed: number
  pass_rate: number
  avg_composite_score: number
  metric_averages: Record<string, number>
  failure_summary: Record<string, number>
  reports: QualityReport[]
}

export interface QualityThresholdsResponse {
  rouge_l_min: number
  fidelidad_min: number
  diversidad_lexica_min: number
  coherencia_dialogica_min: number
  privacy_score_max: number
  memorizacion_max: number
  formula: string
}

// ─── Quality Thresholds (constants) ───
export const QUALITY_THRESHOLDS = {
  rouge_l: 0.65,
  fidelidad_factual: 0.90,
  diversidad_lexica: 0.55,
  coherencia_dialogica: 0.85,
  privacy_score: 0.0,
  memorizacion: 0.01
} as const

export const SUPPORTED_DOMAINS = [
  'automotive.sales',
  'medical.consultation',
  'legal.advisory',
  'finance.advisory',
  'industrial.support',
  'education.tutoring'
] as const

export type SupportedDomain = (typeof SUPPORTED_DOMAINS)[number]

// ─── Knowledge Base ───
export type KnowledgeType = 'facts' | 'procedures' | 'terminology' | 'reference'

export interface KnowledgeChunk {
  id: string
  document_id: string
  content: string
  type: KnowledgeType
  domain: string
  tags: string[]
  source: string
  order: number
}

export interface KnowledgeDocument {
  id: string
  filename: string
  domain: string
  type: KnowledgeType
  chunk_count: number
  chunks: KnowledgeChunk[]
  uploaded_at: string
  metadata: Record<string, unknown>
}
