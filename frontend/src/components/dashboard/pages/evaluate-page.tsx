'use client'

import { useMemo, useState } from 'react'

import Link from 'next/link'
import {
  AlertTriangle,
  ArrowDownToLine,
  CheckCircle2,
  FlaskConical,
  Loader2,
  Play,
  Shield,
  XCircle
} from 'lucide-react'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer
} from 'recharts'

import type { Conversation, QualityMetrics, QualityReport } from '@/types/api'
import { QUALITY_THRESHOLDS } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Local Storage Keys ───
const CONVERSATIONS_KEY = 'uncase-conversations'
const EVALUATIONS_KEY = 'uncase-evaluations'

function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadEvaluations(): QualityReport[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(EVALUATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveEvaluations(evaluations: QualityReport[]) {
  localStorage.setItem(EVALUATIONS_KEY, JSON.stringify(evaluations))
}

// ─── Mock Evaluation Logic ───
function randomInRange(min: number, max: number): number {
  return Math.round((Math.random() * (max - min) + min) * 1000) / 1000
}

function generateMockMetrics(): QualityMetrics {
  return {
    rouge_l: randomInRange(0.50, 0.95),
    fidelidad_factual: randomInRange(0.75, 0.98),
    diversidad_lexica: randomInRange(0.40, 0.85),
    coherencia_dialogica: randomInRange(0.70, 0.98),
    privacy_score: Math.random() < 0.9 ? 0.0 : randomInRange(0.0, 0.05),
    memorizacion: Math.random() < 0.85 ? randomInRange(0.0, 0.009) : randomInRange(0.01, 0.05)
  }
}

function computeCompositeScore(metrics: QualityMetrics): number {
  if (metrics.privacy_score !== 0.0 || metrics.memorizacion >= 0.01) {
    return 0
  }

  return Math.round(
    Math.min(
      metrics.rouge_l,
      metrics.fidelidad_factual,
      metrics.diversidad_lexica,
      metrics.coherencia_dialogica
    ) * 1000
  ) / 1000
}

function evaluateConversation(conversation: Conversation): QualityReport {
  const metrics = generateMockMetrics()
  const composite_score = computeCompositeScore(metrics)

  const failures: string[] = []

  if (metrics.rouge_l < QUALITY_THRESHOLDS.rouge_l) failures.push('ROUGE-L below threshold')
  if (metrics.fidelidad_factual < QUALITY_THRESHOLDS.fidelidad_factual) failures.push('Factual fidelity below threshold')
  if (metrics.diversidad_lexica < QUALITY_THRESHOLDS.diversidad_lexica) failures.push('Lexical diversity below threshold')
  if (metrics.coherencia_dialogica < QUALITY_THRESHOLDS.coherencia_dialogica) failures.push('Dialogic coherence below threshold')
  if (metrics.privacy_score !== QUALITY_THRESHOLDS.privacy_score) failures.push('Privacy score must be 0.0')
  if (metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion) failures.push('Memorization rate too high')

  return {
    conversation_id: conversation.conversation_id,
    seed_id: conversation.seed_id,
    metrics,
    composite_score,
    passed: failures.length === 0,
    failures,
    evaluated_at: new Date().toISOString()
  }
}

// ─── Metric display config ───
const METRIC_CONFIG = [
  { key: 'rouge_l' as const, label: 'ROUGE-L', description: 'Structural coherence with seed', threshold: QUALITY_THRESHOLDS.rouge_l },
  { key: 'fidelidad_factual' as const, label: 'Factual Fidelity', description: 'Domain fact accuracy', threshold: QUALITY_THRESHOLDS.fidelidad_factual },
  { key: 'diversidad_lexica' as const, label: 'Lexical Diversity', description: 'Type-Token Ratio', threshold: QUALITY_THRESHOLDS.diversidad_lexica },
  { key: 'coherencia_dialogica' as const, label: 'Dialogic Coherence', description: 'Inter-turn role consistency', threshold: QUALITY_THRESHOLDS.coherencia_dialogica }
] as const

export function EvaluatePage() {
  const [conversations] = useState<Conversation[]>(() => loadConversations())
  const [evaluations, setEvaluations] = useState<QualityReport[]>(() => loadEvaluations())
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [running, setRunning] = useState(false)
  const [selectedReport, setSelectedReport] = useState<QualityReport | null>(null)

  // ─── Selection ───
  function toggleSelection(id: string) {
    setSelected(prev => {
      const next = new Set(prev)

      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }

      return next
    })
  }

  function selectAll() {
    setSelected(new Set(conversations.map(c => c.conversation_id)))
  }

  function clearSelection() {
    setSelected(new Set())
  }

  // ─── Run evaluation ───
  async function runEvaluation() {
    const targets = selected.size > 0
      ? conversations.filter(c => selected.has(c.conversation_id))
      : conversations

    if (targets.length === 0) return

    setRunning(true)

    // Simulate async processing
    await new Promise(resolve => setTimeout(resolve, 800))

    const results = targets.map(c => evaluateConversation(c))

    // Merge with existing evaluations (replace if same conversation_id)
    const existingMap = new Map(evaluations.map(e => [e.conversation_id, e]))

    for (const r of results) {
      existingMap.set(r.conversation_id, r)
    }

    const updated = Array.from(existingMap.values())

    setEvaluations(updated)
    saveEvaluations(updated)
    setRunning(false)
    clearSelection()

    // Select first result for radar display
    if (results.length > 0) {
      setSelectedReport(results[0])
    }
  }

  // ─── Derived stats ───
  const passCount = useMemo(() => evaluations.filter(e => e.passed).length, [evaluations])
  const failCount = useMemo(() => evaluations.filter(e => !e.passed).length, [evaluations])

  const passRate = evaluations.length > 0
    ? Math.round((passCount / evaluations.length) * 100)
    : 0

  // ─── Radar chart data ───
  const radarData = useMemo(() => {
    if (!selectedReport) return []

    return METRIC_CONFIG.map(m => ({
      metric: m.label,
      value: selectedReport.metrics[m.key],
      threshold: m.threshold
    }))
  }, [selectedReport])

  // ─── Table columns ───
  const columns: Column<QualityReport>[] = [
    {
      key: 'conversation',
      header: 'Conversation',
      cell: row => (
        <button
          className="font-mono text-xs hover:underline"
          onClick={e => { e.stopPropagation(); setSelectedReport(row) }}
        >
          {row.conversation_id.slice(0, 12)}...
        </button>
      )
    },
    {
      key: 'composite',
      header: 'Score',
      cell: row => (
        <span
          className={cn(
            'font-mono text-sm font-medium',
            row.composite_score >= 0.55 ? 'text-emerald-600 dark:text-emerald-400' :
            row.composite_score > 0 ? 'text-amber-600 dark:text-amber-400' :
            'text-red-600 dark:text-red-400'
          )}
        >
          {row.composite_score.toFixed(3)}
        </span>
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
        <span className={cn('text-xs', row.metrics.rouge_l < QUALITY_THRESHOLDS.rouge_l ? 'text-red-500' : 'text-muted-foreground')}>
          {row.metrics.rouge_l.toFixed(3)}
        </span>
      )
    },
    {
      key: 'fidelity',
      header: 'Fidelity',
      cell: row => (
        <span className={cn('text-xs', row.metrics.fidelidad_factual < QUALITY_THRESHOLDS.fidelidad_factual ? 'text-red-500' : 'text-muted-foreground')}>
          {row.metrics.fidelidad_factual.toFixed(3)}
        </span>
      )
    },
    {
      key: 'ttr',
      header: 'TTR',
      cell: row => (
        <span className={cn('text-xs', row.metrics.diversidad_lexica < QUALITY_THRESHOLDS.diversidad_lexica ? 'text-red-500' : 'text-muted-foreground')}>
          {row.metrics.diversidad_lexica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'coherence',
      header: 'Coherence',
      cell: row => (
        <span className={cn('text-xs', row.metrics.coherencia_dialogica < QUALITY_THRESHOLDS.coherencia_dialogica ? 'text-red-500' : 'text-muted-foreground')}>
          {row.metrics.coherencia_dialogica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'failures',
      header: 'Failures',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {row.failures.length}
        </span>
      )
    }
  ]

  // ─── No conversations at all ───
  if (conversations.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Quality Evaluation" description="Run quality evaluations on imported conversations" />
        <EmptyState
          icon={FlaskConical}
          title="No conversations to evaluate"
          description="Import conversation data first, then come back to run quality evaluations."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/pipeline/import">
                <ArrowDownToLine className="mr-1.5 size-4" /> Import Data
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
        title="Quality Evaluation"
        description={`${conversations.length} conversations available for evaluation`}
        actions={
          <Button
            size="sm"
            onClick={runEvaluation}
            disabled={running}
          >
            {running ? (
              <Loader2 className="mr-1.5 size-4 animate-spin" />
            ) : (
              <Play className="mr-1.5 size-4" />
            )}
            {running ? 'Evaluating...' : selected.size > 0 ? `Evaluate (${selected.size})` : 'Evaluate All'}
          </Button>
        }
      />

      {/* Quality Gate Summary */}
      {evaluations.length > 0 && (
        <Card className={cn(
          'border-l-4',
          passRate >= 80 ? 'border-l-emerald-500' :
          passRate >= 50 ? 'border-l-amber-500' :
          'border-l-red-500'
        )}>
          <CardContent className="flex items-center gap-4 p-4">
            {passRate >= 80 ? (
              <CheckCircle2 className="size-8 text-emerald-500" />
            ) : passRate >= 50 ? (
              <AlertTriangle className="size-8 text-amber-500" />
            ) : (
              <XCircle className="size-8 text-red-500" />
            )}
            <div className="flex-1">
              <p className="text-sm font-semibold">
                Quality Gate: {passCount} of {evaluations.length} passed ({passRate}%)
              </p>
              <p className="text-xs text-muted-foreground">
                {passRate >= 80
                  ? 'Quality thresholds are being met across most conversations.'
                  : passRate >= 50
                    ? 'Some conversations are below quality thresholds. Review failures below.'
                    : 'Most conversations are failing quality checks. Review and adjust seeds or generation parameters.'}
              </p>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="text-center">
                <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{passCount}</p>
                <p className="text-[10px] text-muted-foreground">Passed</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-red-600 dark:text-red-400">{failCount}</p>
                <p className="text-[10px] text-muted-foreground">Failed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats row */}
      {evaluations.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Evaluations"
            value={evaluations.length}
            icon={FlaskConical}
            description="Quality reports generated"
          />
          <StatsCard
            title="Pass Rate"
            value={passRate}
            icon={CheckCircle2}
            description="Percentage passing all checks"
          />
          <StatsCard
            title="Passed"
            value={passCount}
            icon={CheckCircle2}
            description="Conversations meeting thresholds"
          />
          <StatsCard
            title="Failed"
            value={failCount}
            icon={XCircle}
            description="Conversations below thresholds"
          />
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Conversation selector */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Select Conversations</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={selectAll}>
                  Select All
                </Button>
                {selected.size > 0 && (
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={clearSelection}>
                    Clear
                  </Button>
                )}
              </div>
            </div>
            <CardDescription className="text-xs">
              Pick conversations to evaluate, or click &ldquo;Evaluate All&rdquo; to run on everything.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-[300px] space-y-1 overflow-y-auto">
              {conversations.map(conv => (
                <label
                  key={conv.conversation_id}
                  className="flex cursor-pointer items-center gap-3 rounded-md px-2 py-1.5 transition-colors hover:bg-muted"
                >
                  <Checkbox
                    checked={selected.has(conv.conversation_id)}
                    onCheckedChange={() => toggleSelection(conv.conversation_id)}
                  />
                  <div className="flex-1 overflow-hidden">
                    <span className="block truncate font-mono text-xs">
                      {conv.conversation_id.slice(0, 20)}...
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      {conv.dominio} | {conv.turnos.length} turns
                    </span>
                  </div>
                  {evaluations.find(e => e.conversation_id === conv.conversation_id) && (
                    <Badge variant="outline" className="text-[9px]">evaluated</Badge>
                  )}
                </label>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Radar chart */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Quality Radar</CardTitle>
            <CardDescription className="text-xs">
              {selectedReport
                ? `Metrics for ${selectedReport.conversation_id.slice(0, 16)}...`
                : 'Run an evaluation and click a result to view the radar chart.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedReport && radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="80%">
                  <PolarGrid />
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
                    name="Score"
                    dataKey="value"
                    stroke="hsl(var(--primary))"
                    fill="hsl(var(--primary))"
                    fillOpacity={0.15}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[260px] items-center justify-center text-sm text-muted-foreground">
                {evaluations.length === 0
                  ? 'No evaluations yet. Run an evaluation to see results.'
                  : 'Click a row in the results table to view its radar chart.'}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Metric detail cards */}
      {selectedReport && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {METRIC_CONFIG.map(m => {
            const value = selectedReport.metrics[m.key]
            const passed = value >= m.threshold
            const percentage = Math.min(Math.round((value / 1) * 100), 100)

            return (
              <Card key={m.key}>
                <CardContent className="p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-medium">{m.label}</span>
                    <span className={cn(
                      'text-sm font-bold',
                      passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
                    )}>
                      {value.toFixed(3)}
                    </span>
                  </div>
                  <Progress value={percentage} className={cn('h-2', !passed && '[&>div]:bg-red-500')} />
                  <div className="mt-1 flex items-center justify-between text-[10px] text-muted-foreground">
                    <span>{m.description}</span>
                    <span>Threshold: {m.threshold}</span>
                  </div>
                </CardContent>
              </Card>
            )
          })}

          {/* Privacy Score card */}
          <Card>
            <CardContent className="p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-medium">
                  <Shield className="size-3.5" /> Privacy Score
                </span>
                <span className={cn(
                  'text-sm font-bold',
                  selectedReport.metrics.privacy_score === 0.0
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-red-600 dark:text-red-400'
                )}>
                  {selectedReport.metrics.privacy_score.toFixed(3)}
                </span>
              </div>
              <Progress
                value={selectedReport.metrics.privacy_score === 0.0 ? 100 : 0}
                className={cn('h-2', selectedReport.metrics.privacy_score !== 0.0 && '[&>div]:bg-red-500')}
              />
              <div className="mt-1 flex items-center justify-between text-[10px] text-muted-foreground">
                <span>Zero PII residual required</span>
                <span>Must be 0.0</span>
              </div>
            </CardContent>
          </Card>

          {/* Memorization card */}
          <Card>
            <CardContent className="p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-medium">
                  <Shield className="size-3.5" /> Memorization
                </span>
                <span className={cn(
                  'text-sm font-bold',
                  selectedReport.metrics.memorizacion < QUALITY_THRESHOLDS.memorizacion
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-red-600 dark:text-red-400'
                )}>
                  {selectedReport.metrics.memorizacion.toFixed(4)}
                </span>
              </div>
              <Progress
                value={Math.min(Math.round((1 - selectedReport.metrics.memorizacion / 0.05) * 100), 100)}
                className={cn('h-2', selectedReport.metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion && '[&>div]:bg-red-500')}
              />
              <div className="mt-1 flex items-center justify-between text-[10px] text-muted-foreground">
                <span>Extraction attack success rate</span>
                <span>Must be {'<'} {QUALITY_THRESHOLDS.memorizacion}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Prompt to run evaluation */}
      {evaluations.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <FlaskConical className="mb-3 size-8 text-muted-foreground" />
            <p className="mb-1 text-sm font-medium">No evaluations run yet</p>
            <p className="mb-3 text-xs text-muted-foreground">
              Select conversations and click &ldquo;Evaluate&rdquo; to generate quality reports with mock metrics.
            </p>
            <Button size="sm" onClick={runEvaluation} disabled={running}>
              {running ? (
                <Loader2 className="mr-1.5 size-4 animate-spin" />
              ) : (
                <Play className="mr-1.5 size-4" />
              )}
              Evaluate All Conversations
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Results table */}
      {evaluations.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Evaluation Results</h3>
          <DataTable
            columns={columns}
            data={evaluations}
            rowKey={r => r.conversation_id}
            onRowClick={r => setSelectedReport(r)}
          />
        </div>
      )}
    </div>
  )
}
