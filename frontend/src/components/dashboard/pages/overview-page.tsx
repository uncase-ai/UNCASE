'use client'

import { useCallback, useMemo, useState } from 'react'

import Link from 'next/link'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BarChart3,
  BookOpen,
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

import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Pipeline Steps ───
const PIPELINE_STEPS = [
  { label: 'Seeds', href: '/dashboard/pipeline/seeds', icon: Sprout, color: 'text-emerald-500' },
  { label: 'Import', href: '/dashboard/pipeline/import', icon: ArrowDownToLine, color: 'text-blue-500' },
  { label: 'Evaluate', href: '/dashboard/pipeline/evaluate', icon: FlaskConical, color: 'text-amber-500' },
  { label: 'Generate', href: '/dashboard/pipeline/generate', icon: Rocket, color: 'text-violet-500' },
  { label: 'Export', href: '/dashboard/pipeline/export', icon: PackageOpen, color: 'text-rose-500' }
]

const QUICK_ACTIONS = [
  { label: 'Import Data', href: '/dashboard/pipeline/import', icon: ArrowDownToLine },
  { label: 'Browse Templates', href: '/dashboard/templates', icon: BookOpen },
  { label: 'Manage Tools', href: '/dashboard/tools', icon: Puzzle },
  { label: 'Run Evaluation', href: '/dashboard/pipeline/evaluate', icon: FlaskConical }
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
      <PageHeader title="Overview" description="UNCASE synthetic data pipeline at a glance" />

      {/* Stats Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard title="Templates" value={stats.templates} icon={BookOpen} description="Chat formats available" />
        <StatsCard title="Tools" value={stats.tools} icon={Puzzle} description="Registered tool definitions" />
        <StatsCard title="Conversations" value={localCounts.conversations} icon={MessageSquare} description="In local store" />
        <StatsCard title="Evaluations" value={localCounts.evaluations} icon={BarChart3} description="Quality reports" />
      </div>

      {/* Pipeline Visual */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Pipeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-1 overflow-x-auto pb-2">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.label} className="flex items-center">
                <Link
                  href={step.href}
                  className="group flex flex-col items-center gap-1.5 rounded-lg px-4 py-3 transition-colors hover:bg-muted"
                >
                  <div
                    className={cn(
                      'flex size-10 items-center justify-center rounded-full border-2 border-muted transition-colors group-hover:border-current',
                      step.color
                    )}
                  >
                    <step.icon className="size-5" />
                  </div>
                  <span className="text-xs font-medium">{step.label}</span>
                </Link>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowRight className="mx-1 size-4 shrink-0 text-muted-foreground/40" />
                )}
              </div>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Seed → Import → Evaluate → Generate → Export. Click any stage to begin.
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2">
            {QUICK_ACTIONS.map(action => (
              <Button key={action.label} variant="outline" className="h-auto justify-start gap-2 px-3 py-2.5" asChild>
                <Link href={action.href}>
                  <action.icon className="size-4 text-muted-foreground" />
                  <span className="text-sm">{action.label}</span>
                </Link>
              </Button>
            ))}
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {health.loading ? (
              <div className="space-y-2">
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-3/4" />
              </div>
            ) : health.error ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Activity className="size-4" /> API Server
                  </span>
                  <StatusBadge variant="error">Unreachable</StatusBadge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Cannot connect to the UNCASE API. Make sure the backend is running.
                </p>
                <Button variant="outline" size="sm" onClick={() => health.retry()}>
                  Retry
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Activity className="size-4" /> API Server
                  </span>
                  <StatusBadge variant={stats.apiOk ? 'success' : 'error'}>
                    {stats.apiOk ? 'Healthy' : 'Error'}
                  </StatusBadge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <Database className="size-4" /> Database
                  </span>
                  <StatusBadge variant={stats.dbOk ? 'success' : 'warning'}>
                    {stats.dbOk ? 'Connected' : 'Disconnected'}
                  </StatusBadge>
                </div>
                {stats.version && (
                  <p className="text-xs text-muted-foreground">UNCASE API v{stats.version}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
