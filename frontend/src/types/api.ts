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
  saludo_marca?: string
  nombre_asistente?: string
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
  rating?: number | null
  rating_count?: number
  run_count?: number
  avg_quality_score?: number | null
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
  status?: 'valid' | 'invalid'
  rating?: number
  tags?: string[]
  notes?: string
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
  tool_call_validity: number
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
  provider_id?: string
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
  tool_call_validity_min: number
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
  tool_call_validity: 0.90,
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

// ─── LLM Providers ───
export const PROVIDER_TYPES = ['anthropic', 'openai', 'google', 'ollama', 'vllm', 'groq', 'custom'] as const
export type ProviderType = (typeof PROVIDER_TYPES)[number]

export interface ProviderCreateRequest {
  name: string
  provider_type: ProviderType
  api_base?: string | null
  api_key?: string | null
  default_model: string
  max_tokens?: number
  temperature_default?: number
  is_default?: boolean
}

export interface ProviderUpdateRequest {
  name?: string
  api_base?: string | null
  api_key?: string | null
  default_model?: string
  max_tokens?: number
  temperature_default?: number
  is_active?: boolean
  is_default?: boolean
}

export interface ProviderResponse {
  id: string
  name: string
  provider_type: string
  api_base: string | null
  has_api_key: boolean
  default_model: string
  max_tokens: number
  temperature_default: number
  is_active: boolean
  is_default: boolean
  organization_id: string | null
  created_at: string
  updated_at: string
}

export interface ProviderTestResponse {
  provider_id: string
  provider_name: string
  status: 'ok' | 'error' | 'timeout'
  latency_ms: number | null
  model_tested: string
  error: string | null
}

export interface ProviderListResponse {
  items: ProviderResponse[]
  total: number
}

// ─── Custom Tools (persisted) ───
export interface CustomToolResponse extends ToolDefinition {
  id: string
  is_active: boolean
  is_builtin: boolean
  organization_id: string | null
  created_at: string
  updated_at: string
}

export interface CustomToolListResponse {
  items: CustomToolResponse[]
  total: number
  page: number
  page_size: number
}

export interface CustomToolCreateRequest {
  name: string
  description: string
  input_schema: Record<string, unknown>
  output_schema?: Record<string, unknown>
  domains?: string[]
  category?: string
  requires_auth?: boolean
  execution_mode?: 'simulated' | 'live' | 'mock'
  version?: string
  metadata?: Record<string, unknown>
}

export interface CustomToolUpdateRequest {
  description?: string
  input_schema?: Record<string, unknown>
  output_schema?: Record<string, unknown>
  domains?: string[]
  category?: string
  requires_auth?: boolean
  execution_mode?: 'simulated' | 'live' | 'mock'
  version?: string
  metadata?: Record<string, unknown>
  is_active?: boolean
}

// ─── Plugins ───
export interface PluginManifest {
  id: string
  name: string
  description: string
  version: string
  author: string
  domains: string[]
  tags: string[]
  tools: ToolDefinition[]
  icon: string
  license: string
  homepage: string | null
  source: 'official' | 'community'
  verified: boolean
  downloads: number
}

export interface InstalledPlugin {
  plugin_id: string
  name: string
  version: string
  tools_registered: string[]
  domains: string[]
}

export interface InstalledPluginResponse {
  id: string
  plugin_id: string
  plugin_name: string
  plugin_version: string
  plugin_source: 'official' | 'community'
  tools_registered: string[]
  domains: string[]
  config: Record<string, unknown> | null
  is_active: boolean
  organization_id: string | null
  created_at: string
  updated_at: string
}

export interface InstalledPluginListResponse {
  items: InstalledPluginResponse[]
  total: number
}

// ─── Template Config ───
export interface TemplateConfig {
  id: string
  organization_id: string | null
  default_template: string
  default_tool_call_mode: 'none' | 'inline'
  default_system_prompt: string | null
  preferred_templates: string[]
  export_format: string
  created_at: string
  updated_at: string
}

export interface TemplateConfigUpdateRequest {
  default_template?: string
  default_tool_call_mode?: 'none' | 'inline'
  default_system_prompt?: string | null
  preferred_templates?: string[]
  export_format?: string
}

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

// ─── Gateway / Chat ───
export interface ChatMessage {
  role: string
  content: string
}

export interface ChatTool {
  type: string
  function: { name: string; description?: string; parameters?: Record<string, unknown> }
}

export interface ChatRequest {
  messages: ChatMessage[]
  provider_id?: string
  model?: string
  temperature?: number
  max_tokens?: number
  privacy_mode?: 'audit' | 'warn' | 'block'
  tools?: ChatTool[]
  tool_choice?: string
  bypass_words?: string[]
}

export interface ChatStreamChunk {
  delta: string
  index: number
  tool_calls?: Record<string, unknown>[]
}

export interface ChatStreamComplete {
  full_response: string
  finish_reason: string
  model: string
  provider_name: string
  privacy: {
    outbound_pii_found: number
    inbound_pii_found: number
    mode: string
    any_blocked: boolean
  }
  usage: { input_tokens: number; output_tokens: number }
}

// ─── Webhooks ───
export interface WebhookSubscriptionCreate {
  url: string
  events: string[]
  description?: string
}

export interface WebhookSubscriptionUpdate {
  url?: string
  events?: string[]
  description?: string
  is_active?: boolean
}

export interface WebhookSubscriptionResponse {
  id: string
  url: string
  events: string[]
  description: string | null
  is_active: boolean
  last_triggered_at: string | null
  created_at: string
  updated_at: string
}

export interface WebhookSubscriptionCreatedResponse extends WebhookSubscriptionResponse {
  secret: string
}

export interface WebhookDeliveryResponse {
  id: string
  subscription_id: string
  event_type: string
  status: 'pending' | 'delivered' | 'failed'
  http_status_code: number | null
  error_message: string | null
  attempts: number
  created_at: string
  delivered_at: string | null
}

export interface WebhookListResponse {
  items: WebhookSubscriptionResponse[]
  total: number
  page: number
  page_size: number
}

export interface WebhookDeliveryListResponse {
  items: WebhookDeliveryResponse[]
  total: number
  page: number
  page_size: number
}

// ─── Background Jobs ───
export interface JobResponse {
  id: string
  job_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_stage: string | null
  status_message: string | null
  config: Record<string, unknown>
  result: Record<string, unknown> | null
  error_message: string | null
  organization_id: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

// ─── Pipeline ───
export interface PipelineRunRequest {
  raw_conversations: string[]
  domain: string
  count?: number
  model?: string | null
  temperature?: number
  train_adapter?: boolean
  base_model?: string
  use_qlora?: boolean
  use_dp_sgd?: boolean
  dp_epsilon?: number
  async_mode?: boolean
}

export interface PipelineRunResponse {
  job_id: string
  status: string
  message: string
}

// ─── Auth / JWT ───
export interface LoginRequest {
  api_key: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  role: 'admin' | 'developer' | 'viewer'
  org_id: string
}

export interface TokenVerifyResponse {
  valid: boolean
  org_id: string | null
  role: string | null
  scopes: string | null
}

// ─── Cost Tracking ───
export interface CostSummary {
  organization_id: string
  period_days: number
  total_cost_usd: number
  total_tokens: number
  event_count: number
  cost_by_provider: Record<string, number>
  cost_by_event_type: Record<string, number>
}

export interface JobCost {
  job_id: string
  total_cost_usd: number
  total_tokens: number
  event_count: number
}

export interface DailyCost {
  date: string
  event_count: number
}

// ─── Scenario Templates ───
export type SkillLevel = 'basic' | 'intermediate' | 'advanced'

export interface ScenarioTemplate {
  name: string
  description: string
  domain: string
  intent: string
  skill_level: SkillLevel
  expected_tool_sequence: string[]
  flow_steps: string[]
  edge_case: boolean
  weight: number
  tags: string[]
}

export interface ScenarioPackSummary {
  id: string
  name: string
  description: string
  domain: string
  version: string
  scenario_count: number
  edge_case_count: number
  skill_levels: string[]
  tags: string[]
}

export interface ScenarioPackDetail extends ScenarioPackSummary {
  scenarios: ScenarioTemplate[]
}

export interface ScenarioPackListResponse {
  packs: ScenarioPackSummary[]
  total: number
}

export interface ScenarioListResponse {
  domain: string
  scenarios: ScenarioTemplate[]
  total: number
  filters_applied: Record<string, string>
}

// ─── Audit Logs ───
export interface AuditLogEntry {
  id: string
  action: string
  resource_type: string
  resource_id: string | null
  actor_type: string
  actor_id: string | null
  organization_id: string | null
  ip_address: string | null
  endpoint: string | null
  http_method: string | null
  detail: string | null
  extra_data: Record<string, unknown> | null
  status: string
  created_at: string
}
