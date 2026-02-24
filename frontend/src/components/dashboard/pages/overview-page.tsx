'use client'

import { useCallback, useMemo, useState } from 'react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BarChart3,
  BookOpen,
  Building2,
  ChevronRight,
  Database,
  ExternalLink,
  FlaskConical,
  HelpCircle,
  Key,
  Library,
  MessageSquare,
  PackageOpen,
  Play,
  Puzzle,
  Rocket,
  Server,
  Sprout
} from 'lucide-react'

import type { HealthDbResponse, TemplateInfo, ToolDefinition } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { useDemoMode } from '@/hooks/use-demo-mode'
import { activateDemo } from '@/lib/demo'
import { fetchHealthDb } from '@/lib/api/health'
import { fetchTemplates } from '@/lib/api/templates'
import { fetchTools } from '@/lib/api/tools'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Constants ───

const ORG_ID_KEY = 'uncase-org-id'

const PIPELINE_STEPS = [
  { label: 'Seeds', href: '/dashboard/pipeline/seeds', icon: Sprout, description: 'Define knowledge structures' },
  { label: 'Knowledge', href: '/dashboard/knowledge', icon: Library, description: 'Upload domain literature' },
  { label: 'Import', href: '/dashboard/pipeline/import', icon: ArrowDownToLine, description: 'Ingest conversation data' },
  { label: 'Evaluate', href: '/dashboard/pipeline/evaluate', icon: FlaskConical, description: 'Run quality gates' },
  { label: 'Generate', href: '/dashboard/pipeline/generate', icon: Rocket, description: 'Synthesize conversations' },
  { label: 'Export', href: '/dashboard/pipeline/export', icon: PackageOpen, description: 'Output LoRA-ready data' }
]

// ─── Setup Step Component ───

function SetupStep({
  step,
  title,
  description,
  done,
  action,
  actionLabel,
}: {
  step: number
  title: string
  description: string
  done: boolean
  action: string | (() => void)
  actionLabel: string
  icon: React.ElementType
}) {
  const content = (
    <div
      className={cn(
        'flex items-start gap-4 rounded-lg border px-4 py-3.5 transition-colors',
        done ? 'border-muted bg-muted/30' : 'hover:bg-muted/50'
      )}
    >
      <div
        className={cn(
          'flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold',
          done ? 'bg-foreground text-background' : 'border-2 border-foreground/20 text-muted-foreground'
        )}
      >
        {done ? <span className="text-[10px]">&#10003;</span> : step}
      </div>
      <div className="flex-1 space-y-0.5">
        <div className={cn('text-sm font-medium', done && 'text-muted-foreground line-through')}>{title}</div>
        <div className="text-xs text-muted-foreground">{description}</div>
      </div>
      {!done && (
        <Button variant="outline" size="sm" className="shrink-0 text-xs" asChild={typeof action === 'string'}>
          {typeof action === 'string' ? (
            <Link href={action}>
              {actionLabel}
              <ChevronRight className="ml-1 size-3" />
            </Link>
          ) : (
            <span onClick={action}>
              {actionLabel}
              <ChevronRight className="ml-1 size-3" />
            </span>
          )}
        </Button>
      )}
    </div>
  )

  if (typeof action === 'string' && !done) {
    return <Link href={action} className="block">{content}</Link>
  }

  return content
}

// ─── Main Component ───

export function OverviewPage() {
  const router = useRouter()
  const { active: demoActive } = useDemoMode()

  const healthFetcher = useCallback((signal: AbortSignal) => fetchHealthDb(signal), [])
  const templatesFetcher = useCallback((signal: AbortSignal) => fetchTemplates(signal), [])
  const toolsFetcher = useCallback((signal: AbortSignal) => fetchTools(undefined, signal), [])

  const health = useApi<HealthDbResponse>(healthFetcher)
  const templates = useApi<TemplateInfo[]>(templatesFetcher)
  const tools = useApi<ToolDefinition[]>(toolsFetcher)

  const [localCounts] = useState(() => {
    if (typeof window === 'undefined') return { conversations: 0, evaluations: 0 }

    try {
      const convs = JSON.parse(localStorage.getItem('uncase-conversations') ?? '[]')
      const evals = JSON.parse(localStorage.getItem('uncase-evaluations') ?? '[]')

      return { conversations: convs.length, evaluations: evals.length }
    } catch {
      return { conversations: 0, evaluations: 0 }
    }
  })

  const [hasOrg] = useState(() => {
    if (typeof window === 'undefined') return false

    return !!localStorage.getItem(ORG_ID_KEY)
  })

  const stats = useMemo(
    () => ({
      templates: templates.data?.length ?? null,
      tools: tools.data?.length ?? null,
      apiOk: health.data?.status === 'ok',
      dbOk: health.data?.database === 'connected',
      version: health.data?.version ?? null
    }),
    [templates.data, tools.data, health.data]
  )

  const setupComplete = hasOrg && stats.apiOk

  const handleStartDemo = async () => {
    await activateDemo()
    router.refresh()
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overview"
        description="UNCASE synthetic data pipeline"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href="https://github.com/uncase-ai/UNCASE" target="_blank" rel="noopener noreferrer">
                <HelpCircle className="mr-1.5 size-3.5" />
                Docs
                <ExternalLink className="ml-1 size-3" />
              </Link>
            </Button>
            <Button size="sm" asChild>
              <Link href="/dashboard/pipeline/seeds">
                <Sprout className="mr-1.5 size-3.5" />
                Start Pipeline
              </Link>
            </Button>
          </div>
        }
      />

      {/* Setup / Onboarding — shown when not fully configured and not in demo mode */}
      {!setupComplete && !demoActive && (
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Setup</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1.5 text-xs text-muted-foreground"
                onClick={handleStartDemo}
              >
                <Play className="size-3" />
                Try with demo data instead
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 pt-0">
            <SetupStep
              step={1}
              title="Create your organization"
              description="Set up your workspace to manage seeds, API keys, and team access."
              done={hasOrg}
              action="/dashboard/settings"
              actionLabel="Set up"
              icon={Building2}
            />
            <SetupStep
              step={2}
              title="Generate an API key"
              description="Authenticate requests to the UNCASE API from your applications."
              done={false}
              action="/dashboard/settings"
              actionLabel="Create key"
              icon={Key}
            />
            <SetupStep
              step={3}
              title="Configure an LLM provider"
              description="Connect Claude, GPT, Gemini, or any LiteLLM-compatible provider for synthetic generation."
              done={false}
              action="/dashboard/settings"
              actionLabel="Add provider"
              icon={Server}
            />
          </CardContent>
        </Card>
      )}

      {/* Stats Row */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard title="Templates" value={stats.templates} icon={BookOpen} description="Chat formats available" />
        <StatsCard title="Tools" value={stats.tools} icon={Puzzle} description="Registered definitions" />
        <StatsCard title="Conversations" value={localCounts.conversations} icon={MessageSquare} description="In local store" />
        <StatsCard title="Evaluations" value={localCounts.evaluations} icon={BarChart3} description="Quality reports" />
      </div>

      {/* Pipeline */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">Pipeline</CardTitle>
            <span className="text-[11px] text-muted-foreground">6 stages</span>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-6 gap-0">
            {PIPELINE_STEPS.map((step, i) => (
              <Link
                key={step.label}
                href={step.href}
                className={cn(
                  'group relative flex flex-col items-center gap-2 py-4 transition-colors hover:bg-muted/50',
                  i === 0 && 'rounded-l-lg',
                  i === PIPELINE_STEPS.length - 1 && 'rounded-r-lg'
                )}
              >
                <div className="flex size-9 items-center justify-center rounded-lg border bg-background transition-colors group-hover:border-foreground/20">
                  <step.icon className="size-4 text-muted-foreground transition-colors group-hover:text-foreground" />
                </div>
                <div className="text-center">
                  <div className="text-xs font-medium">{step.label}</div>
                  <div className="hidden text-[10px] text-muted-foreground lg:block">{step.description}</div>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ChevronRight className="absolute right-0 top-1/2 size-3.5 -translate-y-1/2 translate-x-1/2 text-muted-foreground/40" />
                )}
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions + System */}
      <div className="grid gap-3 lg:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 pt-0">
            <Link
              href="/dashboard/pipeline/import"
              className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
            >
              <div className="flex items-center gap-3">
                <div className="flex size-8 items-center justify-center rounded-md border">
                  <ArrowDownToLine className="size-3.5 text-muted-foreground" />
                </div>
                <div>
                  <div className="text-sm font-medium">Import data</div>
                  <div className="text-xs text-muted-foreground">WhatsApp, JSON, CSV, or webhook</div>
                </div>
              </div>
              <ArrowRight className="size-3.5 text-muted-foreground" />
            </Link>
            <Separator />
            <Link
              href="/dashboard/pipeline/seeds"
              className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
            >
              <div className="flex items-center gap-3">
                <div className="flex size-8 items-center justify-center rounded-md border">
                  <Sprout className="size-3.5 text-muted-foreground" />
                </div>
                <div>
                  <div className="text-sm font-medium">Create a seed</div>
                  <div className="text-xs text-muted-foreground">Define a knowledge structure for your domain</div>
                </div>
              </div>
              <ArrowRight className="size-3.5 text-muted-foreground" />
            </Link>
            <Separator />
            <Link
              href="/dashboard/templates"
              className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
            >
              <div className="flex items-center gap-3">
                <div className="flex size-8 items-center justify-center rounded-md border">
                  <BookOpen className="size-3.5 text-muted-foreground" />
                </div>
                <div>
                  <div className="text-sm font-medium">Browse templates</div>
                  <div className="text-xs text-muted-foreground">Pre-built formats for common use cases</div>
                </div>
              </div>
              <ArrowRight className="size-3.5 text-muted-foreground" />
            </Link>
            <Separator />
            <Link
              href="/docs"
              className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
            >
              <div className="flex items-center gap-3">
                <div className="flex size-8 items-center justify-center rounded-md border">
                  <HelpCircle className="size-3.5 text-muted-foreground" />
                </div>
                <div>
                  <div className="text-sm font-medium">Documentation</div>
                  <div className="text-xs text-muted-foreground">Guides, API reference, and whitepaper</div>
                </div>
              </div>
              <ExternalLink className="size-3.5 text-muted-foreground" />
            </Link>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 pt-0">
            {health.loading ? (
              <div className="space-y-3">
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-3/4" />
              </div>
            ) : health.error ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Activity className="size-4" /> API Server
                  </span>
                  <StatusBadge variant="error">Unreachable</StatusBadge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Cannot connect to the UNCASE API. The backend may not be running, or the dashboard is in local-only
                  mode with demo data.
                </p>
                <Button variant="outline" size="sm" onClick={() => health.retry()}>
                  Retry connection
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Activity className="size-4" /> API Server
                  </span>
                  <StatusBadge variant={stats.apiOk ? 'success' : 'error'}>
                    {stats.apiOk ? 'Healthy' : 'Error'}
                  </StatusBadge>
                </div>
                <Separator />
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Database className="size-4" /> Database
                  </span>
                  <StatusBadge variant={stats.dbOk ? 'success' : 'warning'}>
                    {stats.dbOk ? 'Connected' : 'Disconnected'}
                  </StatusBadge>
                </div>
                {stats.version && (
                  <>
                    <Separator />
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Version</span>
                      <span className="font-mono text-xs">{stats.version}</span>
                    </div>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
