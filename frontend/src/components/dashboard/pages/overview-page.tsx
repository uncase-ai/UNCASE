'use client'

import { useCallback, useMemo, useState } from 'react'

import Link from 'next/link'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BarChart3,
  BookOpen,
  ChevronRight,
  Database,
  FlaskConical,
  MessageSquare,
  PackageOpen,
  Puzzle,
  Rocket,
  Sprout
} from 'lucide-react'

import type { HealthDbResponse, TemplateInfo, ToolDefinition } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { fetchHealthDb } from '@/lib/api/health'
import { fetchTemplates } from '@/lib/api/templates'
import { fetchTools } from '@/lib/api/tools'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'

import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Pipeline Steps ───
const PIPELINE_STEPS = [
  {
    label: 'Seeds',
    href: '/dashboard/pipeline/seeds',
    icon: Sprout,
    description: 'Define knowledge structures'
  },
  {
    label: 'Import',
    href: '/dashboard/pipeline/import',
    icon: ArrowDownToLine,
    description: 'Ingest conversation data'
  },
  {
    label: 'Evaluate',
    href: '/dashboard/pipeline/evaluate',
    icon: FlaskConical,
    description: 'Run quality gates'
  },
  {
    label: 'Generate',
    href: '/dashboard/pipeline/generate',
    icon: Rocket,
    description: 'Synthesize conversations'
  },
  {
    label: 'Export',
    href: '/dashboard/pipeline/export',
    icon: PackageOpen,
    description: 'Output LoRA-ready data'
  }
]

export function OverviewPage() {
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

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overview"
        description="UNCASE synthetic data pipeline at a glance"
        actions={
          <Button asChild size="sm">
            <Link href="/dashboard/pipeline/seeds">
              <Sprout className="mr-1.5 size-4" />
              Start Pipeline
            </Link>
          </Button>
        }
      />

      {/* Stats Row */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard title="Templates" value={stats.templates} icon={BookOpen} description="Chat formats available" />
        <StatsCard title="Tools" value={stats.tools} icon={Puzzle} description="Registered tool definitions" />
        <StatsCard
          title="Conversations"
          value={localCounts.conversations}
          icon={MessageSquare}
          description="In local store"
        />
        <StatsCard
          title="Evaluations"
          value={localCounts.evaluations}
          icon={BarChart3}
          description="Quality reports"
        />
      </div>

      {/* Pipeline */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">Pipeline</CardTitle>
            <span className="text-xs text-muted-foreground">5 stages</span>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-5 gap-0">
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
                  <ChevronRight className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 size-3.5 text-muted-foreground/40" />
                )}
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Getting Started + System Health */}
      <div className="grid gap-3 lg:grid-cols-2">
        {/* Getting Started */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Getting Started</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-1">
              <Link
                href="/dashboard/pipeline/seeds"
                className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-md border">
                    <Sprout className="size-3.5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">Create your first seed</div>
                    <div className="text-xs text-muted-foreground">Define a knowledge structure for your domain</div>
                  </div>
                </div>
                <ArrowRight className="size-3.5 text-muted-foreground" />
              </Link>
              <Separator />
              <Link
                href="/dashboard/pipeline/import"
                className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-md border">
                    <ArrowDownToLine className="size-3.5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">Import conversation data</div>
                    <div className="text-xs text-muted-foreground">WhatsApp, JSON, CSV, or webhook</div>
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
                    <div className="font-medium">Browse templates</div>
                    <div className="text-xs text-muted-foreground">Pre-built formats for common use cases</div>
                  </div>
                </div>
                <ArrowRight className="size-3.5 text-muted-foreground" />
              </Link>
              <Separator />
              <Link
                href="/dashboard/tools"
                className="flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition-colors hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-md border">
                    <Puzzle className="size-3.5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">Register tools</div>
                    <div className="text-xs text-muted-foreground">Define callable tools for synthetic generation</div>
                  </div>
                </div>
                <ArrowRight className="size-3.5 text-muted-foreground" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {health.loading ? (
              <div className="space-y-3">
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-3/4" />
              </div>
            ) : health.error ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Activity className="size-4 text-muted-foreground" /> API Server
                  </span>
                  <StatusBadge variant="error">Unreachable</StatusBadge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Cannot connect to the UNCASE API. The backend may not be running or the dashboard is in local-only
                  mode.
                </p>
                <Button variant="outline" size="sm" onClick={() => health.retry()}>
                  Retry connection
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Activity className="size-4 text-muted-foreground" /> API Server
                  </span>
                  <StatusBadge variant={stats.apiOk ? 'success' : 'error'}>
                    {stats.apiOk ? 'Healthy' : 'Error'}
                  </StatusBadge>
                </div>
                <Separator />
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Database className="size-4 text-muted-foreground" /> Database
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
