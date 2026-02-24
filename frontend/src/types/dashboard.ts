import type { LucideIcon } from 'lucide-react'

// ─── Navigation ───
export interface NavItem {
  label: string
  href: string
  icon: LucideIcon
  badge?: string | number
  children?: NavItem[]
}

export interface NavGroup {
  label?: string
  items: NavItem[]
}

export interface BreadcrumbSegment {
  label: string
  href?: string
}

// ─── Pipeline ───
export type PipelineStage = 'seed' | 'import' | 'evaluate' | 'generate' | 'export'

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface PipelineJob {
  id: string
  stage: PipelineStage
  status: JobStatus
  progress: number
  label: string
  created_at: string
  started_at?: string
  completed_at?: string
  error?: string
  metadata?: Record<string, unknown>
}

// ─── Activity ───
export type ActivityType =
  | 'seed_created'
  | 'conversation_imported'
  | 'conversation_generated'
  | 'evaluation_completed'
  | 'dataset_exported'
  | 'tool_registered'
  | 'api_key_created'
  | 'template_rendered'

export interface ActivityEvent {
  id: string
  type: ActivityType
  title: string
  description?: string
  timestamp: string
  metadata?: Record<string, unknown>
}

// ─── Dashboard Stats ───
export interface DashboardStats {
  seeds: number
  conversations: number
  templates: number
  tools: number
  evaluations_passed: number
  evaluations_failed: number
  datasets_exported: number
}

// ─── Domain Info ───
export interface DomainInfo {
  key: string
  label: string
  description: string
  icon: string
  typical_roles: string[]
  tools: string[]
  color: string
}

// ─── Dataset Export ───
export interface DatasetExport {
  id: string
  name: string
  domain: string
  template: string
  conversation_count: number
  seed_count: number
  quality_score: number
  format: 'jsonl' | 'csv' | 'parquet'
  size_bytes: number
  created_at: string
  conversations: string[]
}

// ─── Sidebar State ───
export interface SidebarState {
  collapsed: boolean
  activeGroup?: string
}

// ─── UI Preferences ───
export type UIDensity = 'compact' | 'comfortable' | 'spacious'
export type UILocale = 'en' | 'es'

export interface UIPreferences {
  density: UIDensity
  locale: UILocale
  sidebarCollapsed: boolean
}
