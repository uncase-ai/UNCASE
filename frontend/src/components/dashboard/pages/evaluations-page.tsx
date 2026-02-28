'use client'

import { useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  ShieldAlert,
  Target
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  Cell
} from 'recharts'

import type { QualityReport, QualityMetrics } from '@/types/api'
import { QUALITY_THRESHOLDS } from '@/types/api'
import { fetchEvaluationReports } from '@/lib/api/evaluations'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Local Storage ───
const EVALUATIONS_KEY = 'uncase-evaluations'

function loadEvaluations(): QualityReport[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(EVALUATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

// ─── Metric display config ───
const METRIC_CONFIG = [
  { key: 'rouge_l' as const, label: 'ROUGE-L', threshold: QUALITY_THRESHOLDS.rouge_l },
  { key: 'fidelidad_factual' as const, label: 'Fidelity', threshold: QUALITY_THRESHOLDS.fidelidad_factual },
  { key: 'diversidad_lexica' as const, label: 'TTR', threshold: QUALITY_THRESHOLDS.diversidad_lexica },
  { key: 'coherencia_dialogica' as const, label: 'Coherence', threshold: QUALITY_THRESHOLDS.coherencia_dialogica },
  { key: 'tool_call_validity' as const, label: 'Tool Validity', threshold: QUALITY_THRESHOLDS.tool_call_validity }
] as const

// ─── Score bucket helpers ───
const BUCKET_LABELS = [
  '0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
  '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'
]

function getBucketIndex(score: number): number {
  if (score >= 1.0) return 9

  return Math.floor(score * 10)
}

export function EvaluationsPage() {
  const [evaluations, setEvaluations] = useState<QualityReport[]>(() => loadEvaluations())
  const [error, setError] = useState<string | null>(null)

  // Sync with backend API on mount
  useEffect(() => {
    let cancelled = false

    fetchEvaluationReports({ page: 1, page_size: 100 })
      .then(res => {
        if (cancelled) return

        if (res.data && res.data.items.length > 0) {
          const apiReports: QualityReport[] = res.data.items.map(item => ({
            conversation_id: item.conversation_id,
            seed_id: item.seed_id ?? '',
            metrics: {
              rouge_l: item.rouge_l,
              fidelidad_factual: item.fidelidad_factual,
              diversidad_lexica: item.diversidad_lexica,
              coherencia_dialogica: item.coherencia_dialogica,
              tool_call_validity: item.tool_call_validity ?? 1.0,
              privacy_score: item.privacy_score,
              memorizacion: item.memorizacion
            } as QualityMetrics,
            composite_score: item.composite_score,
            passed: item.passed,
            failures: item.failures,
            evaluated_at: item.created_at
          }))

          // Merge: API data + localStorage-only reports
          const apiIds = new Set(apiReports.map(r => `${r.conversation_id}-${r.evaluated_at}`))

          const localOnly = loadEvaluations().filter(
            r => !apiIds.has(`${r.conversation_id}-${r.evaluated_at}`)
          )

          const merged = [...apiReports, ...localOnly]

          setEvaluations(merged)

          // Update localStorage with merged data
          try {
            localStorage.setItem(EVALUATIONS_KEY, JSON.stringify(merged))
          } catch {
            // Storage full — ignore
          }
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load evaluation reports')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  // ─── Summary stats ───
  const totalEvaluations = evaluations.length
  const passCount = useMemo(() => evaluations.filter(e => e.passed).length, [evaluations])
  const passRate = totalEvaluations > 0 ? Math.round((passCount / totalEvaluations) * 100) : 0

  const avgComposite = useMemo(() => {
    if (totalEvaluations === 0) return 0

    return Math.round(
      (evaluations.reduce((sum, e) => sum + e.composite_score, 0) / totalEvaluations) * 1000
    ) / 1000
  }, [evaluations, totalEvaluations])

  const privacyViolations = useMemo(
    () => evaluations.filter(e => e.metrics.privacy_score > 0).length,
    [evaluations]
  )

  // ─── Histogram data ───
  const histogramData = useMemo(() => {
    const buckets = Array.from({ length: 10 }, () => 0)

    for (const e of evaluations) {
      const idx = getBucketIndex(e.composite_score)

      buckets[idx]++
    }

    return BUCKET_LABELS.map((label, i) => ({
      bucket: label,
      count: buckets[i],
      passing: i >= 6 // >= 0.6 bucket (composite threshold ~0.65 rounded down for bucket)
    }))
  }, [evaluations])

  // ─── Radar data (metric averages) ───
  const radarData = useMemo(() => {
    if (totalEvaluations === 0) return []

    return METRIC_CONFIG.map(m => {
      const avg = evaluations.reduce((sum, e) => sum + (e.metrics[m.key] ?? 0), 0) / totalEvaluations

      return {
        metric: m.label,
        value: Math.round(avg * 1000) / 1000,
        threshold: m.threshold
      }
    })
  }, [evaluations, totalEvaluations])

  // ─── Failure analysis ───
  const failureAnalysis = useMemo(() => {
    const counts: Record<string, number> = {}

    for (const e of evaluations) {
      for (const f of e.failures) {
        counts[f] = (counts[f] || 0) + 1
      }
    }

    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([reason, count]) => ({ reason, count }))
  }, [evaluations])

  // ─── Table columns ───
  const columns: Column<QualityReport>[] = [
    {
      key: 'conversation',
      header: 'Conversation',
      cell: row => (
        <span className="font-mono text-xs">{row.conversation_id.slice(0, 12)}...</span>
      )
    },
    {
      key: 'composite',
      header: 'Composite',
      cell: row => (
        <div className="flex items-center gap-2">
          <Progress
            value={Math.round(row.composite_score * 100)}
            className={cn('h-2 w-16', row.composite_score === 0 && '[&>div]:bg-destructive')}
          />
          <span className="font-mono text-xs font-medium">
            {row.composite_score.toFixed(3)}
          </span>
        </div>
      )
    },
    {
      key: 'passed',
      header: 'Status',
      cell: row => (
        <StatusBadge variant={row.passed ? 'success' : 'error'}>
          {row.passed ? 'Passed' : 'Failed'}
        </StatusBadge>
      )
    },
    {
      key: 'rouge',
      header: 'ROUGE-L',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.rouge_l < QUALITY_THRESHOLDS.rouge_l ? 'text-destructive' : 'text-muted-foreground'
        )}>
          {row.metrics.rouge_l.toFixed(3)}
        </span>
      )
    },
    {
      key: 'fidelity',
      header: 'Fidelity',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.fidelidad_factual < QUALITY_THRESHOLDS.fidelidad_factual ? 'text-destructive' : 'text-muted-foreground'
        )}>
          {row.metrics.fidelidad_factual.toFixed(3)}
        </span>
      )
    },
    {
      key: 'ttr',
      header: 'TTR',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.diversidad_lexica < QUALITY_THRESHOLDS.diversidad_lexica ? 'text-destructive' : 'text-muted-foreground'
        )}>
          {row.metrics.diversidad_lexica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'coherence',
      header: 'Coherence',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.coherencia_dialogica < QUALITY_THRESHOLDS.coherencia_dialogica ? 'text-destructive' : 'text-muted-foreground'
        )}>
          {row.metrics.coherencia_dialogica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'tool_validity',
      header: 'Tool Valid.',
      cell: row => {
        const tcv = row.metrics.tool_call_validity ?? 1.0

        return (
          <span className={cn(
            'text-xs',
            tcv < QUALITY_THRESHOLDS.tool_call_validity ? 'text-destructive' : 'text-muted-foreground'
          )}>
            {tcv.toFixed(3)}
          </span>
        )
      }
    },
    {
      key: 'privacy',
      header: 'Privacy',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.privacy_score > 0 ? 'text-red-500 font-medium' : 'text-muted-foreground'
        )}>
          {row.metrics.privacy_score.toFixed(3)}
        </span>
      )
    },
    {
      key: 'memo',
      header: 'Memo',
      cell: row => (
        <span className={cn(
          'text-xs',
          row.metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion ? 'text-red-500 font-medium' : 'text-muted-foreground'
        )}>
          {row.metrics.memorizacion.toFixed(4)}
        </span>
      )
    }
  ]

  // ─── Empty state ───
  if (evaluations.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Evaluations Overview"
          description="Quality metrics and trends across all evaluations"
        />
        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-destructive text-sm">{error}</p>
          </div>
        )}
        <EmptyState
          icon={BarChart3}
          title="No evaluations yet"
          description="Run quality evaluations on your conversations to see metrics, distributions, and trends here."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/pipeline/evaluate">
                <FlaskConical className="mr-1.5 size-4" /> Go to Evaluate
              </Link>
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Evaluations Overview"
        description={`${totalEvaluations} quality evaluations analyzed`}
        actions={
          <Button asChild size="sm" variant="outline">
            <Link href="/dashboard/pipeline/evaluate">
              <FlaskConical className="mr-1.5 size-4" /> Run Evaluations
            </Link>
          </Button>
        }
      />

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
          <p className="text-destructive text-sm">{error}</p>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Evaluations"
          value={totalEvaluations}
          icon={FlaskConical}
          description="Quality reports"
        />
        <StatsCard
          title="Pass Rate"
          value={passRate}
          icon={CheckCircle2}
          description="Percentage passing all checks"
        />
        <StatsCard
          title="Avg Composite Score"
          value={Math.round(avgComposite * 100)}
          icon={Target}
          description={`Raw: ${avgComposite.toFixed(3)}`}
        />
        <StatsCard
          title="Privacy Violations"
          value={privacyViolations}
          icon={ShieldAlert}
          description="Evaluations with privacy_score > 0"
        />
      </div>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Composite Score Distribution */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Composite Score Distribution</CardTitle>
            <CardDescription className="text-xs">
              Histogram of composite scores across all evaluations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={histogramData} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="bucket"
                  tick={{ fontSize: 10 }}
                  className="fill-muted-foreground"
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  className="fill-muted-foreground"
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    fontSize: 12,
                    borderRadius: 8,
                    border: '1px solid hsl(var(--border))',
                    backgroundColor: 'hsl(var(--card))',
                    color: 'hsl(var(--card-foreground))'
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {histogramData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.passing
                        ? 'hsl(var(--primary))'
                        : 'hsl(var(--muted-foreground))'
                      }
                      fillOpacity={entry.passing ? 0.8 : 0.4}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-muted-foreground">
              <div className="flex items-center gap-1">
                <span className="inline-block size-2.5 rounded-sm bg-primary" />
                Passing (bucket &ge; 0.6)
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-block size-2.5 rounded-sm bg-muted-foreground/40" />
                Failing (bucket &lt; 0.6)
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Metric Averages Radar */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Metric Averages</CardTitle>
            <CardDescription className="text-xs">
              Average of each quality metric across all evaluations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="80%">
                <PolarGrid className="stroke-muted" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <Radar
                  name="Threshold"
                  dataKey="threshold"
                  stroke="hsl(var(--muted-foreground))"
                  fill="transparent"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                />
                <Radar
                  name="Average"
                  dataKey="value"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
            <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <span className="inline-block h-px w-4 border-t-2 border-dashed border-muted-foreground" />
                Threshold
              </div>
              <div className="flex items-center gap-1.5">
                <span className="inline-block h-px w-4 border-t-2 border-primary" />
                Average Score
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Failure Analysis */}
      {failureAnalysis.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="size-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium">Failure Analysis</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Most common failure reasons, sorted by frequency.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {failureAnalysis.map(({ reason, count }) => {
                const percentage = Math.round((count / totalEvaluations) * 100)

                return (
                  <div key={reason} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs">{reason}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[10px]">
                          {count} ({percentage}%)
                        </Badge>
                      </div>
                    </div>
                    <Progress
                      value={percentage}
                      className="h-1.5"
                    />
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Full Results Table */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold">All Evaluation Results</h3>
        <DataTable
          columns={columns}
          data={evaluations}
          rowKey={r => `${r.conversation_id}-${r.evaluated_at}`}
          emptyMessage="No evaluations found"
        />
      </div>
    </div>
  )
}
