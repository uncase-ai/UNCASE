'use client'

import { useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import {
  AlertTriangle,
  ArrowDownToLine,
  CheckCircle2,
  Cloud,
  CloudOff,
  ExternalLink,
  FlaskConical,
  HelpCircle,
  Info,
  Loader2,
  Play,
  Shield,
  StopCircle,
  XCircle,
  X as XIcon
} from 'lucide-react'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer
} from 'recharts'

import type { Conversation, QualityMetrics, QualityReport, SeedSchema } from '@/types/api'
import { QUALITY_THRESHOLDS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { evaluateBatch } from '@/lib/api/evaluations'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import { Switch } from '@/components/ui/switch'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Local Storage Keys ───
const CONVERSATIONS_KEY = 'uncase-conversations'
const EVALUATIONS_KEY = 'uncase-evaluations'
const SEEDS_KEY = 'uncase-seeds'

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

function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(SEEDS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

// ─── Mock Evaluation Logic ───
function randomInRange(min: number, max: number): number {
  return Math.round((Math.random() * (max - min) + min) * 1000) / 1000
}

// Generates metrics that consistently pass thresholds (demo content is premium)
// ~85% of conversations pass; ~15% fail with clear, realistic failures
// Thresholds: rouge_l>=0.20, fidelidad>=0.80, TTR>=0.55, coherencia>=0.65,
//   tool_call>=0.80, privacy=0, memo<0.01, semantic>=0.60, drift>=0.30
function generateMockMetrics(): { metrics: QualityMetrics; shouldFail: boolean } {
  const shouldFail = Math.random() < 0.15

  if (shouldFail) {
    // Pick 1-2 metrics to fail for a realistic failure case
    const failType = Math.random()

    if (failType < 0.4) {
      // Lexical diversity failure — most common in synthetic data
      return {
        metrics: {
          rouge_l: randomInRange(0.25, 0.45),
          fidelidad_factual: randomInRange(0.82, 0.96),
          diversidad_lexica: randomInRange(0.38, 0.53),
          coherencia_dialogica: randomInRange(0.68, 0.92),
          tool_call_validity: 1.0,
          privacy_score: 0.0,
          memorizacion: randomInRange(0.001, 0.006),
          semantic_fidelity: randomInRange(0.65, 0.88),
          embedding_drift: randomInRange(0.35, 0.75),
        },
        shouldFail: true,
      }
    }

    if (failType < 0.7) {
      // Factual fidelity failure — hallucinated domain facts
      return {
        metrics: {
          rouge_l: randomInRange(0.22, 0.40),
          fidelidad_factual: randomInRange(0.62, 0.78),
          diversidad_lexica: randomInRange(0.58, 0.78),
          coherencia_dialogica: randomInRange(0.68, 0.90),
          tool_call_validity: 1.0,
          privacy_score: 0.0,
          memorizacion: randomInRange(0.001, 0.005),
          semantic_fidelity: randomInRange(0.55, 0.72),
          embedding_drift: randomInRange(0.32, 0.70),
        },
        shouldFail: true,
      }
    }

    // Memorization gate failure — extraction attack detected
    return {
      metrics: {
        rouge_l: randomInRange(0.28, 0.48),
        fidelidad_factual: randomInRange(0.85, 0.96),
        diversidad_lexica: randomInRange(0.60, 0.80),
        coherencia_dialogica: randomInRange(0.70, 0.92),
        tool_call_validity: 1.0,
        privacy_score: 0.0,
        memorizacion: randomInRange(0.012, 0.035),
        semantic_fidelity: randomInRange(0.70, 0.90),
        embedding_drift: randomInRange(0.40, 0.80),
      },
      shouldFail: true,
    }
  }

  // Passing case — all metrics above thresholds
  return {
    metrics: {
      rouge_l: randomInRange(0.25, 0.50),
      fidelidad_factual: randomInRange(0.82, 0.98),
      diversidad_lexica: randomInRange(0.58, 0.82),
      coherencia_dialogica: randomInRange(0.68, 0.95),
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: randomInRange(0.001, 0.007),
      semantic_fidelity: randomInRange(0.65, 0.93),
      embedding_drift: randomInRange(0.35, 0.85),
    },
    shouldFail: false,
  }
}

function computeCompositeScore(metrics: QualityMetrics): { composite: number; weightedMean: number } {
  if (metrics.privacy_score !== 0.0 || metrics.memorizacion >= 0.01) {
    return { composite: 0, weightedMean: 0 }
  }

  const coreValues = [
    metrics.rouge_l,
    metrics.fidelidad_factual,
    metrics.diversidad_lexica,
    metrics.coherencia_dialogica,
    metrics.tool_call_validity
  ]

  // Optional metrics only factor in when actually computed (not at neutral 0.5)
  const semComputed = metrics.semantic_fidelity != null && metrics.semantic_fidelity !== 0.5
  const embComputed = metrics.embedding_drift != null && metrics.embedding_drift !== 0.5

  if (semComputed) coreValues.push(metrics.semantic_fidelity!)
  if (embComputed) coreValues.push(metrics.embedding_drift!)

  const composite = Math.round(Math.min(...coreValues) * 1000) / 1000

  // Weighted mean (informational, mirrors backend weights)
  const pairs: [number, number][] = [
    [metrics.rouge_l, 0.15],
    [metrics.fidelidad_factual, 0.25],
    [metrics.diversidad_lexica, 0.10],
    [metrics.coherencia_dialogica, 0.20],
    [metrics.tool_call_validity, 0.10],
  ]
  if (semComputed) pairs.push([metrics.semantic_fidelity!, 0.10])
  if (embComputed) pairs.push([metrics.embedding_drift!, 0.10])

  const totalWeight = pairs.reduce((s, [, w]) => s + w, 0)
  const weightedMean = totalWeight > 0
    ? Math.round((pairs.reduce((s, [v, w]) => s + v * w, 0) / totalWeight) * 1000) / 1000
    : 0

  return { composite, weightedMean }
}

function evaluateConversationMock(conversation: Conversation): QualityReport {
  const { metrics } = generateMockMetrics()
  const { composite, weightedMean } = computeCompositeScore(metrics)

  const failures: string[] = []

  if (metrics.rouge_l < QUALITY_THRESHOLDS.rouge_l) failures.push(`rouge_l=${metrics.rouge_l.toFixed(3)} (min ${QUALITY_THRESHOLDS.rouge_l})`)
  if (metrics.fidelidad_factual < QUALITY_THRESHOLDS.fidelidad_factual) failures.push(`fidelidad_factual=${metrics.fidelidad_factual.toFixed(3)} (min ${QUALITY_THRESHOLDS.fidelidad_factual})`)
  if (metrics.diversidad_lexica < QUALITY_THRESHOLDS.diversidad_lexica) failures.push(`diversidad_lexica=${metrics.diversidad_lexica.toFixed(3)} (min ${QUALITY_THRESHOLDS.diversidad_lexica})`)
  if (metrics.coherencia_dialogica < QUALITY_THRESHOLDS.coherencia_dialogica) failures.push(`coherencia_dialogica=${metrics.coherencia_dialogica.toFixed(3)} (min ${QUALITY_THRESHOLDS.coherencia_dialogica})`)
  if (metrics.tool_call_validity < QUALITY_THRESHOLDS.tool_call_validity) failures.push(`tool_call_validity=${metrics.tool_call_validity.toFixed(3)} (min ${QUALITY_THRESHOLDS.tool_call_validity})`)
  if (metrics.privacy_score !== QUALITY_THRESHOLDS.privacy_score) failures.push(`privacy_score=${metrics.privacy_score} (must be 0.0)`)
  if (metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion) failures.push(`memorizacion=${metrics.memorizacion.toFixed(4)} (must be < ${QUALITY_THRESHOLDS.memorizacion})`)
  if (metrics.semantic_fidelity != null && metrics.semantic_fidelity !== 0.5 && metrics.semantic_fidelity < QUALITY_THRESHOLDS.semantic_fidelity) failures.push(`semantic_fidelity=${metrics.semantic_fidelity.toFixed(3)} (min ${QUALITY_THRESHOLDS.semantic_fidelity})`)
  if (metrics.embedding_drift != null && metrics.embedding_drift !== 0.5 && metrics.embedding_drift < QUALITY_THRESHOLDS.embedding_drift) failures.push(`embedding_drift=${metrics.embedding_drift.toFixed(3)} (min ${QUALITY_THRESHOLDS.embedding_drift})`)

  return {
    conversation_id: conversation.conversation_id,
    seed_id: conversation.seed_id,
    metrics,
    composite_score: composite,
    weighted_mean: weightedMean,
    passed: failures.length === 0,
    failures,
    evaluated_at: new Date().toISOString()
  }
}

// ─── Metric display config ───
const METRIC_CONFIG: {
  key: keyof QualityMetrics
  label: string
  description: string
  threshold: number
  tooltip: string
  optional?: boolean
}[] = [
  {
    key: 'rouge_l',
    label: 'ROUGE-L',
    description: 'Content coverage of seed',
    threshold: QUALITY_THRESHOLDS.rouge_l,
    tooltip: 'Recall-weighted F-beta (β=2) on content tokens after stopword filtering. Measures how well the generated conversation covers the seed\'s key concepts. Natural range: 0.15–0.50; threshold: 0.20.'
  },
  {
    key: 'fidelidad_factual',
    label: 'Factual Fidelity',
    description: 'Domain constraint adherence',
    threshold: QUALITY_THRESHOLDS.fidelidad_factual,
    tooltip: 'Checks that entities, procedures, terminology, and constraints from the seed\'s factual parameters appear correctly in the generated conversation. Threshold: 0.80.'
  },
  {
    key: 'diversidad_lexica',
    label: 'Lexical Diversity',
    description: 'Type-Token Ratio',
    threshold: QUALITY_THRESHOLDS.diversidad_lexica,
    tooltip: 'Type-Token Ratio (TTR) — measures vocabulary variety. Higher values indicate more diverse, natural-sounding language. Prevents repetitive or templated output. Threshold: 0.55.'
  },
  {
    key: 'coherencia_dialogica',
    label: 'Dialogic Coherence',
    description: 'Content-token Jaccard coherence',
    threshold: QUALITY_THRESHOLDS.coherencia_dialogica,
    tooltip: 'Content-token Jaccard similarity between consecutive turns. Measures inter-turn consistency of roles and context while filtering out stopwords. Threshold: 0.65.'
  },
  {
    key: 'tool_call_validity',
    label: 'Tool Validity',
    description: 'Tool call schema compliance',
    threshold: QUALITY_THRESHOLDS.tool_call_validity,
    tooltip: 'Validates that tool calls in the conversation use correct function names, parameters, and return types as defined in the seed. Defaults to 1.0 when no tools are present. Threshold: 0.80.'
  },
  {
    key: 'semantic_fidelity',
    label: 'Semantic Fidelity',
    description: 'LLM-as-Judge scoring',
    threshold: QUALITY_THRESHOLDS.semantic_fidelity,
    tooltip: 'LLM-as-Judge evaluation of semantic accuracy and intent preservation. Requires an LLM API — omitted from composite if unavailable (shown as 0.5). Threshold: 0.60.',
    optional: true
  },
  {
    key: 'embedding_drift',
    label: 'Embedding Drift',
    description: 'TF-IDF / embedding cosine similarity',
    threshold: QUALITY_THRESHOLDS.embedding_drift,
    tooltip: 'Cosine similarity between seed and generated conversation via TF-IDF (offline) or LLM embeddings (when API available). Detects semantic drift from the original intent. Threshold: 0.30.',
    optional: true
  }
]

export function EvaluatePage() {
  const [conversations] = useState<Conversation[]>(() => loadConversations())
  const [evaluations, setEvaluations] = useState<QualityReport[]>(() => loadEvaluations())
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [running, setRunning] = useState(false)
  const [selectedReport, setSelectedReport] = useState<QualityReport | null>(null)

  // ─── API integration state ───
  const [apiAvailable, setApiAvailable] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [evaluationError, setEvaluationError] = useState<string | null>(null)
  const [abortController, setAbortController] = useState<AbortController | null>(null)

  const [batchSummary, setBatchSummary] = useState<{
    total: number
    passed: number
    failed: number
    pass_rate: number
    avg_composite_score: number
    metric_averages: Record<string, number>
    failure_summary: Record<string, number>
  } | null>(null)

  // ─── Seeds for API pairing ───
  const [seeds] = useState<SeedSchema[]>(() => loadSeeds())

  const seedMap = useMemo(() => {
    const map = new Map<string, SeedSchema>()

    for (const s of seeds) map.set(s.seed_id, s)

    return map
  }, [seeds])

  // ─── API health check on mount ───
  useEffect(() => {
    let cancelled = false

    async function init() {
      const healthy = await checkApiHealth()

      if (!cancelled) {
        setApiAvailable(healthy)
        if (!healthy) setDemoMode(true)
      }
    }

    init()

    return () => { cancelled = true }
  }, [])

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

  // ─── Cancel handler ───
  function handleCancel() {
    abortController?.abort()
    setAbortController(null)
  }

  // ─── Run evaluation ───
  async function runEvaluation() {
    const targets = selected.size > 0
      ? conversations.filter(c => selected.has(c.conversation_id))
      : conversations

    if (targets.length === 0) return

    setRunning(true)
    setEvaluationError(null)
    setBatchSummary(null)

    const controller = new AbortController()

    setAbortController(controller)

    try {
      if (demoMode) {
        // Demo: use mock evaluator
        await new Promise(resolve => setTimeout(resolve, 800))
        const results = targets.map(c => evaluateConversationMock(c))
        const existingMap = new Map(evaluations.map(e => [e.conversation_id, e]))

        for (const r of results) existingMap.set(r.conversation_id, r)

        const updated = Array.from(existingMap.values())

        setEvaluations(updated)
        saveEvaluations(updated)
        if (results.length > 0) setSelectedReport(results[0])
      } else {
        // Real API: build pairs with seeds
        const pairs: Array<{ conversation: Conversation; seed: SeedSchema }> = []
        const unpaired: string[] = []

        for (const conv of targets) {
          const seed = seedMap.get(conv.seed_id)

          if (seed) {
            pairs.push({ conversation: conv, seed })
          } else {
            unpaired.push(conv.conversation_id.slice(0, 8))
          }
        }

        if (unpaired.length > 0) {
          setEvaluationError(
            `${unpaired.length} conversation(s) have no matching seed and were skipped: ${unpaired.join(', ')}...`
          )
        }

        if (pairs.length === 0) {
          setRunning(false)
          setAbortController(null)

          return
        }

        const { data, error } = await evaluateBatch(pairs, controller.signal)

        if (error) {
          if (error.status !== 0) {
            setEvaluationError(`Evaluation failed: ${error.message}`)
          }
        } else if (data) {
          // Merge reports
          const existingMap = new Map(evaluations.map(e => [e.conversation_id, e]))

          for (const r of data.reports) existingMap.set(r.conversation_id, r)

          const updated = Array.from(existingMap.values())

          setEvaluations(updated)
          saveEvaluations(updated)

          setBatchSummary({
            total: data.total,
            passed: data.passed,
            failed: data.failed,
            pass_rate: data.pass_rate,
            avg_composite_score: data.avg_composite_score,
            metric_averages: data.metric_averages,
            failure_summary: data.failure_summary
          })

          if (data.reports.length > 0) setSelectedReport(data.reports[0])
        }
      }
    } catch {
      // Cancelled or unexpected — silently handle
    }

    setRunning(false)
    setAbortController(null)
    clearSelection()
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

    return METRIC_CONFIG
      .filter(m => {
        if (!m.optional) return true

        const val = selectedReport.metrics[m.key]

        return val != null && val !== 0.5
      })
      .map(m => ({
        metric: m.label,
        value: selectedReport.metrics[m.key] ?? 0,
        threshold: m.threshold
      }))
  }, [selectedReport])

  // ─── Table columns ───
  const columns: Column<QualityReport>[] = [
    {
      key: 'conversation',
      header: 'Conversation',
      cell: row => (
        <div className="flex items-center gap-1.5">
          <button
            className="font-mono text-xs hover:underline"
            onClick={e => { e.stopPropagation(); setSelectedReport(row) }}
          >
            {row.conversation_id}
          </button>
          <Link
            href={`/dashboard/conversations?id=${encodeURIComponent(row.conversation_id)}`}
            onClick={e => e.stopPropagation()}
            title="Open conversation"
          >
            <ExternalLink className="size-3 text-muted-foreground hover:text-foreground" />
          </Link>
        </div>
      )
    },
    {
      key: 'composite',
      header: 'Score',
      cell: row => (
        <div>
          <span className="font-mono text-sm font-medium">
            {row.composite_score.toFixed(3)}
          </span>
          {row.weighted_mean != null && (
            <span className="ml-1.5 font-mono text-[10px] text-muted-foreground" title="Weighted mean">
              (w̄ {row.weighted_mean.toFixed(3)})
            </span>
          )}
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
        <span className={cn('text-xs', row.metrics.rouge_l < QUALITY_THRESHOLDS.rouge_l ? 'text-destructive' : 'text-muted-foreground')}>
          {row.metrics.rouge_l.toFixed(3)}
        </span>
      )
    },
    {
      key: 'fidelity',
      header: 'Fidelity',
      cell: row => (
        <span className={cn('text-xs', row.metrics.fidelidad_factual < QUALITY_THRESHOLDS.fidelidad_factual ? 'text-destructive' : 'text-muted-foreground')}>
          {row.metrics.fidelidad_factual.toFixed(3)}
        </span>
      )
    },
    {
      key: 'ttr',
      header: 'TTR',
      cell: row => (
        <span className={cn('text-xs', row.metrics.diversidad_lexica < QUALITY_THRESHOLDS.diversidad_lexica ? 'text-destructive' : 'text-muted-foreground')}>
          {row.metrics.diversidad_lexica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'coherence',
      header: 'Coherence',
      cell: row => (
        <span className={cn('text-xs', row.metrics.coherencia_dialogica < QUALITY_THRESHOLDS.coherencia_dialogica ? 'text-destructive' : 'text-muted-foreground')}>
          {row.metrics.coherencia_dialogica.toFixed(3)}
        </span>
      )
    },
    {
      key: 'tool_validity',
      header: 'Tools',
      cell: row => (
        <span className={cn('text-xs', row.metrics.tool_call_validity < QUALITY_THRESHOLDS.tool_call_validity ? 'text-destructive' : 'text-muted-foreground')}>
          {row.metrics.tool_call_validity.toFixed(3)}
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
    <TooltipProvider>
      <div className="space-y-4">
        <PageHeader
          title="Quality Evaluation"
          description={`${conversations.length} conversations available for evaluation`}
          actions={
            <div className="flex items-center gap-2">
              {running && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleCancel}
                >
                  <StopCircle className="mr-1.5 size-4" />
                  Cancel
                </Button>
              )}
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
            </div>
          }
        />

        {/* Info banner */}
        <Card className="bg-muted/40">
          <CardContent className="flex items-start gap-3 p-4">
            <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
            <div className="space-y-1 text-xs text-muted-foreground">
              <p className="text-[15px] font-semibold text-foreground">How Quality Evaluation Works</p>
              <p>
                Each conversation is evaluated against its origin seed using up to 9 quality metrics.
                Five core metrics (ROUGE-L &ge; 0.20, Fidelity &ge; 0.80, TTR &ge; 0.55, Coherence &ge; 0.65,
                Tool Validity &ge; 0.80), two gate metrics (Privacy = 0, Memorization {'<'} 1%), and two optional
                LLM-powered metrics (Semantic Fidelity &ge; 0.60, Embedding Drift &ge; 0.30).
              </p>
              <p>
                <strong>Composite score:</strong> Q = min(all computed metrics) when gates pass, else Q = 0.
                A <strong>weighted mean</strong> is also computed for informational purposes (not used for pass/fail).
              </p>
            </div>
          </CardContent>
        </Card>

        {/* API status and demo mode toggle */}
        <div className="flex items-center gap-4">
          <Badge variant="outline" className="gap-1 text-[10px]">
            {apiAvailable ? (
              <>
                <Cloud className="size-3" /> API Connected
              </>
            ) : (
              <>
                <CloudOff className="size-3" /> API Unavailable
              </>
            )}
          </Badge>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground">Demo Mode</span>
            <Switch checked={demoMode} onCheckedChange={setDemoMode} />
          </div>
        </div>

        {/* Error display */}
        {evaluationError && (
          <Card className="bg-muted/40">
            <CardContent className="flex items-center gap-3 p-3">
              <AlertTriangle className="size-4 shrink-0 text-muted-foreground" />
              <p className="flex-1 text-xs text-muted-foreground">{evaluationError}</p>
              <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => setEvaluationError(null)}>
                <XIcon className="size-3" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Batch summary from API */}
        {batchSummary && !running && (
          <Card className="border-l-4 border-l-foreground/20">
            <CardContent className="p-4">
              <p className="mb-2 text-sm font-semibold">Batch Evaluation Summary</p>
              <div className="grid grid-cols-4 gap-4 text-center text-xs">
                <div>
                  <p className="text-lg font-bold">{batchSummary.total}</p>
                  <p className="text-muted-foreground">Total</p>
                </div>
                <div>
                  <p className="text-lg font-bold">{batchSummary.passed}</p>
                  <p className="text-muted-foreground">Passed</p>
                </div>
                <div>
                  <p className="text-lg font-bold">{batchSummary.failed}</p>
                  <p className="text-muted-foreground">Failed</p>
                </div>
                <div>
                  <p className="text-lg font-bold">{batchSummary.avg_composite_score.toFixed(3)}</p>
                  <p className="text-muted-foreground">Avg Score</p>
                </div>
              </div>
              {Object.keys(batchSummary.failure_summary).length > 0 && (
                <div className="mt-3 rounded-md bg-muted/50 p-2">
                  <p className="mb-1 text-[10px] font-medium text-muted-foreground">Failure Breakdown</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(batchSummary.failure_summary).map(([metric, count]) => (
                      <Badge key={metric} variant="outline" className="text-[10px]">
                        {metric}: {count}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Quality Gate Summary */}
        {evaluations.length > 0 && (
          <Card className="border-l-4 border-l-foreground/20">
            <CardContent className="flex items-center gap-4 p-4">
              {passRate >= 80 ? (
                <CheckCircle2 className="size-8 text-muted-foreground" />
              ) : passRate >= 50 ? (
                <AlertTriangle className="size-8 text-muted-foreground" />
              ) : (
                <XCircle className="size-8 text-muted-foreground" />
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
                  <p className="text-lg font-bold">{passCount}</p>
                  <p className="text-[10px] text-muted-foreground">Passed</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold">{failCount}</p>
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
                        {conv.conversation_id}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {conv.dominio} | {conv.turnos.length} turns
                      </span>
                    </div>
                    {!seedMap.has(conv.seed_id) && !demoMode && (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <AlertTriangle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent className="text-xs">No matching seed found — cannot evaluate via API</TooltipContent>
                      </Tooltip>
                    )}
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
                  ? `Metrics for ${selectedReport.conversation_id}`
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
            {METRIC_CONFIG
              .filter(m => {
                if (!m.optional) return true

                const val = selectedReport.metrics[m.key]

                return val != null && val !== 0.5
              })
              .map(m => {
                const value = selectedReport.metrics[m.key] ?? 0
                const passed = value >= m.threshold
                const percentage = Math.min(Math.round((value / 1) * 100), 100)

                return (
                  <Card key={m.key}>
                    <CardContent className="p-4">
                      <div className="mb-2 flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-xs font-medium">
                          {m.label}
                          {m.optional && <Badge variant="outline" className="text-[8px]">optional</Badge>}
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <HelpCircle className="size-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs text-xs">{m.tooltip}</TooltipContent>
                          </Tooltip>
                        </span>
                        <span className={cn(
                          'text-sm font-bold',
                          !passed && 'text-destructive'
                        )}>
                          {value.toFixed(3)}
                        </span>
                      </div>
                      <Progress value={percentage} className={cn('h-2', !passed && '[&>div]:bg-destructive')} />
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
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="size-3 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs text-xs">
                        PII residual detection via Presidio. Must be exactly 0.0 — any detected PII immediately fails the conversation.
                      </TooltipContent>
                    </Tooltip>
                  </span>
                  <span className={cn(
                    'text-sm font-bold',
                    selectedReport.metrics.privacy_score !== 0.0 && 'text-destructive'
                  )}>
                    {selectedReport.metrics.privacy_score.toFixed(3)}
                  </span>
                </div>
                <Progress
                  value={selectedReport.metrics.privacy_score === 0.0 ? 100 : 0}
                  className={cn('h-2', selectedReport.metrics.privacy_score !== 0.0 && '[&>div]:bg-destructive')}
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
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="size-3 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs text-xs">
                        Extraction attack success rate. Measures if the model memorized training data. Must be below 1% for safety.
                      </TooltipContent>
                    </Tooltip>
                  </span>
                  <span className={cn(
                    'text-sm font-bold',
                    selectedReport.metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion && 'text-destructive'
                  )}>
                    {selectedReport.metrics.memorizacion.toFixed(4)}
                  </span>
                </div>
                <Progress
                  value={Math.min(Math.round((1 - selectedReport.metrics.memorizacion / 0.05) * 100), 100)}
                  className={cn('h-2', selectedReport.metrics.memorizacion >= QUALITY_THRESHOLDS.memorizacion && '[&>div]:bg-destructive')}
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
                Select conversations and click &ldquo;Evaluate&rdquo; to generate quality reports
                {demoMode ? ' with mock metrics.' : ' using the SCSF evaluation API.'}
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
    </TooltipProvider>
  )
}
