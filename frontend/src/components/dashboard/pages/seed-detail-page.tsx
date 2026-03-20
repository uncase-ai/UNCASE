'use client'

import { useCallback, useEffect, useState } from 'react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  BarChart3,
  Check,
  Clock,
  Copy,
  Database,
  Eye,
  Info,
  Loader2,
  Rocket,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react'

import type { Conversation, QualityReport, SeedSchema } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { generateConversations } from '@/lib/api/generate'
import { deleteSeedApi } from '@/lib/api/seeds'
import { isDemoMode } from '@/lib/demo'
import { generateDemoConversation, generateDemoQualityReport } from '@/lib/demo/generators'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Slider } from '@/components/ui/slider'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

import { PageHeader } from '../page-header'

// ─── Local Storage ───
const SEEDS_KEY = 'uncase-seeds'
const CONVERSATIONS_KEY = 'uncase-conversations'
const EVALUATIONS_KEY = 'uncase-evaluations'

function loadSeedById(id: string): SeedSchema | null {
  if (typeof window === 'undefined') return null

  try {
    const raw = localStorage.getItem(SEEDS_KEY)
    const seeds: SeedSchema[] = raw ? JSON.parse(raw) : []

    return seeds.find(s => s.seed_id === id) ?? null
  } catch {
    return null
  }
}

function loadConversationsForSeed(seedId: string): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY)
    const all: Conversation[] = raw ? JSON.parse(raw) : []

    return all.filter(c => c.seed_id === seedId)
  } catch {
    return []
  }
}

function loadEvaluationsForSeed(seedId: string): QualityReport[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(EVALUATIONS_KEY)
    const all: QualityReport[] = raw ? JSON.parse(raw) : []

    return all.filter(e => e.seed_id === seedId)
  } catch {
    return []
  }
}

const DOMAIN_LABELS: Record<string, string> = {
  'automotive.sales': 'Automotive',
  'medical.consultation': 'Medical',
  'legal.advisory': 'Legal',
  'finance.advisory': 'Finance',
  'industrial.support': 'Industrial',
  'education.tutoring': 'Education',
}

const QUALITY_THRESHOLD_LABELS: Record<string, { label: string; threshold: number }> = {
  rouge_l: { label: 'ROUGE-L', threshold: 0.20 },
  fidelidad_factual: { label: 'Factual Fidelity', threshold: 0.80 },
  diversidad_lexica: { label: 'Lexical Diversity (TTR)', threshold: 0.55 },
  coherencia_dialogica: { label: 'Dialogic Coherence', threshold: 0.65 },
  tool_call_validity: { label: 'Tool Call Validity', threshold: 0.80 },
  privacy_score: { label: 'Privacy Score', threshold: 0.00 },
}

interface SeedDetailPageProps {
  id: string
}

export function SeedDetailPage({ id }: SeedDetailPageProps) {
  const router = useRouter()
  const [seed, setSeed] = useState<SeedSchema | null>(null)
  const [notFound, setNotFound] = useState(false)

  // Generation state
  const [count, setCount] = useState(3)
  const [temperature, setTemperature] = useState(0.7)
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)

  const [generationResult, setGenerationResult] = useState<{
    total: number
    passed: number
    avgScore: number
  } | null>(null)

  const [generationError, setGenerationError] = useState<string | null>(null)

  // Generated conversations for this session
  const [sessionConversations, setSessionConversations] = useState<Conversation[]>([])
  const [sessionReports, setSessionReports] = useState<QualityReport[]>([])

  // Seed metrics (all-time)
  const [allConversations, setAllConversations] = useState<Conversation[]>([])
  const [allEvaluations, setAllEvaluations] = useState<QualityReport[]>([])

  // API state
  const [apiAvailable, setApiAvailable] = useState(false)

  // Load seed
  useEffect(() => {
    const s = loadSeedById(id)

    if (s) {
      setSeed(s)
    } else {
      setNotFound(true)
    }
  }, [id])

  // Load existing conversations/evaluations for this seed
  const refreshMetrics = useCallback(() => {
    setAllConversations(loadConversationsForSeed(id))
    setAllEvaluations(loadEvaluationsForSeed(id))
  }, [id])

  useEffect(() => {
    refreshMetrics()
  }, [refreshMetrics])

  // Check API health
  useEffect(() => {
    let cancelled = false

    checkApiHealth().then(healthy => {
      if (!cancelled) setApiAvailable(healthy)
    })

    return () => { cancelled = true }
  }, [])

  // ─── Generation handler ───
  async function handleGenerate() {
    if (!seed) return

    setGenerating(true)
    setProgress(0)
    setGenerationResult(null)
    setGenerationError(null)
    setSessionConversations([])
    setSessionReports([])

    if (isDemoMode() || !apiAvailable) {
      // Demo mode — generate locally
      const conversations: Conversation[] = []
      const reports: QualityReport[] = []

      for (let i = 0; i < count; i++) {
        await new Promise(resolve => setTimeout(resolve, 80 + Math.random() * 120))

        const conv = generateDemoConversation(seed)
        const report = generateDemoQualityReport(conv, seed)

        conversations.push(conv)
        reports.push(report)
        setProgress(Math.round(((i + 1) / count) * 100))
      }

      const passed = reports.filter(r => r.passed).length
      const avgScore = reports.reduce((s, r) => s + r.composite_score, 0) / reports.length

      setGenerationResult({ total: count, passed, avgScore })
      setSessionConversations(conversations)
      setSessionReports(reports)

      // Persist to localStorage
      const { appendConversations } = await import('./conversations-page')

      appendConversations(conversations)

      try {
        const existing = JSON.parse(localStorage.getItem(EVALUATIONS_KEY) || '[]')

        localStorage.setItem(EVALUATIONS_KEY, JSON.stringify([...existing, ...reports]))
      } catch { /* storage full */ }

      refreshMetrics()
      setGenerating(false)

      return
    }

    // API mode
    const { data, error } = await generateConversations({
      seed,
      count,
      temperature,
      evaluate_after: true,
    })

    setGenerating(false)

    if (error) {
      setGenerationError(`Generation failed: ${error.message}`)

      return
    }

    if (data) {
      const summary = data.generation_summary
      const passed = summary.total_passed ?? 0
      const total = summary.total_generated

      setGenerationResult({
        total,
        passed,
        avgScore: summary.avg_composite_score ?? 0,
      })
      setSessionConversations(data.conversations)

      if (data.reports) {
        setSessionReports(data.reports)

        try {
          const existing = JSON.parse(localStorage.getItem(EVALUATIONS_KEY) || '[]')

          localStorage.setItem(EVALUATIONS_KEY, JSON.stringify([...existing, ...data.reports]))
        } catch { /* storage full */ }
      }

      const { appendConversations } = await import('./conversations-page')

      appendConversations(data.conversations)
      refreshMetrics()
    }
  }

  // ─── Delete handler ───
  async function handleDelete() {
    if (!seed) return

    if (apiAvailable) {
      await deleteSeedApi(seed.seed_id)
    }

    try {
      const raw = localStorage.getItem(SEEDS_KEY)
      const seeds: SeedSchema[] = raw ? JSON.parse(raw) : []
      const updated = seeds.filter(s => s.seed_id !== seed.seed_id)

      localStorage.setItem(SEEDS_KEY, JSON.stringify(updated))
    } catch { /* ignore */ }

    router.push('/dashboard/pipeline/seeds')
  }

  // ─── Add to dataset handler ───
  function handleAddToDataset(conversationIds: string[]) {
    try {
      const raw = localStorage.getItem(CONVERSATIONS_KEY)
      const all: Conversation[] = raw ? JSON.parse(raw) : []

      const updated = all.map(c => {
        if (conversationIds.includes(c.conversation_id)) {
          return { ...c, tags: [...(c.tags ?? []), 'dataset'].filter((v, i, a) => a.indexOf(v) === i) }
        }

        return c
      })

      localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(updated))
    } catch { /* ignore */ }
  }

  // ─── Not found ───
  if (notFound) {
    return (
      <div className="space-y-6">
        <PageHeader title="Seed Not Found" />
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <X className="size-12 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">The seed with ID &quot;{id}&quot; was not found.</p>
            <Button asChild variant="outline" size="sm">
              <Link href="/dashboard/pipeline/seeds">
                <ArrowLeft className="mr-1.5 size-4" /> Back to Seeds
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!seed) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  // ─── Computed ───
  const totalConvs = allConversations.length

  const avgQuality = allEvaluations.length > 0
    ? allEvaluations.reduce((s, e) => s + e.composite_score, 0) / allEvaluations.length
    : null

  const passRate = allEvaluations.length > 0
    ? allEvaluations.filter(e => e.passed).length / allEvaluations.length
    : null

  const lastGen = allConversations.length > 0
    ? allConversations.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at
    : null

  const hasConversations = totalConvs > 0
  const hasEvaluations = allEvaluations.length > 0
  const hasPassingConversations = allEvaluations.some(e => e.passed)

  // Pipeline guidance
  let guidanceMessage = ''
  let guidanceIcon = Info

  if (!hasConversations) {
    guidanceMessage = 'Generate synthetic conversations from this seed to start evaluating quality.'
    guidanceIcon = Sparkles
  } else if (!hasEvaluations) {
    guidanceMessage = 'Your conversations are ready. Run quality evaluation to check compliance.'
    guidanceIcon = BarChart3
  } else if (hasPassingConversations) {
    guidanceMessage = 'Conversations passed quality checks. Add them to a dataset for fine-tuning.'
    guidanceIcon = Database
  }

  const flowSteps = seed.pasos_turnos?.flujo_esperado ?? []
  const constraints = seed.parametros_factuales?.restricciones ?? []
  const tools = seed.parametros_factuales?.herramientas ?? []

  const GuidanceIcon = guidanceIcon

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title={seed.objetivo}
        description={seed.seed_id}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/pipeline/seeds">
                <ArrowLeft className="mr-1.5 size-4" /> Back
              </Link>
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link href={`/dashboard/pipeline/seeds/new?from=${seed.seed_id}`}>
                <Copy className="mr-1.5 size-4" /> Duplicate
              </Link>
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDelete}>
              <Trash2 className="mr-1.5 size-4" /> Delete
            </Button>
          </div>
        }
      />

      {/* Domain & status badges */}
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="secondary">{DOMAIN_LABELS[seed.dominio] ?? seed.dominio}</Badge>
        <Badge variant="outline">{seed.idioma.toUpperCase()}</Badge>
        <Badge variant="outline">{seed.tono}</Badge>
        {seed.version && <Badge variant="outline">v{seed.version}</Badge>}
        {hasPassingConversations && (
          <Badge className="bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300">
            <Check className="mr-1 size-3" /> Quality Passed
          </Badge>
        )}
      </div>

      {/* Pipeline guidance banner */}
      {guidanceMessage && (
        <Card className="bg-muted/40">
          <CardContent className="flex items-center gap-3 p-4">
            <GuidanceIcon className="size-5 shrink-0 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">{guidanceMessage}</p>
          </CardContent>
        </Card>
      )}

      {/* Seed info — two-column grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Left: Seed details */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Seed Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-xs text-muted-foreground">Objective</Label>
              <p className="mt-1 text-sm">{seed.objetivo}</p>
            </div>

            {(seed.roles ?? []).length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Roles</Label>
                <div className="mt-1 flex flex-wrap gap-1">
                  {seed.roles.map(role => (
                    <Badge key={role} variant="outline" className="font-mono text-xs">{role}</Badge>
                  ))}
                </div>
                {Object.keys(seed.descripcion_roles ?? {}).length > 0 && (
                  <div className="mt-2 space-y-1">
                    {Object.entries(seed.descripcion_roles).map(([role, desc]) => (
                      <p key={role} className="text-xs text-muted-foreground">
                        <span className="font-medium">{role}:</span> {desc}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div>
              <Label className="text-xs text-muted-foreground">Turns</Label>
              <p className="mt-1 text-sm">
                {seed.pasos_turnos?.turnos_min ?? 0}–{seed.pasos_turnos?.turnos_max ?? 0} turns per conversation
              </p>
            </div>

            {constraints.length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Constraints</Label>
                <ul className="mt-1 list-inside list-disc space-y-0.5 text-xs text-muted-foreground">
                  {constraints.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}

            {flowSteps.length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Expected Flow</Label>
                <ol className="mt-1 list-inside list-decimal space-y-0.5 text-xs text-muted-foreground">
                  {flowSteps.map((step, i) => <li key={i}>{step}</li>)}
                </ol>
              </div>
            )}

            {tools.length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Tools</Label>
                <div className="mt-1 flex flex-wrap gap-1">
                  {tools.map(t => (
                    <Link key={t} href={`/dashboard/tools/${encodeURIComponent(t)}`}>
                      <Badge variant="outline" className="cursor-pointer font-mono text-xs transition-colors hover:bg-muted">
                        {t}
                      </Badge>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {(seed.etiquetas ?? []).length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Tags</Label>
                <div className="mt-1 flex flex-wrap gap-1">
                  {seed.etiquetas.map(tag => (
                    <Badge key={tag} variant="secondary" className="text-xs font-normal">{tag}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right: Quality thresholds + Seed metrics */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Quality Thresholds</CardTitle>
              <CardDescription className="text-xs">Minimum scores required for conversations to pass</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(QUALITY_THRESHOLD_LABELS).map(([key, { label, threshold }]) => {
                  const seedThreshold = seed.metricas_calidad?.[key as keyof typeof seed.metricas_calidad]

                  return (
                    <div key={key} className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{label}</span>
                      <span className="font-mono font-medium">
                        {key === 'privacy_score' ? '= ' : '>= '}
                        {seedThreshold != null ? String(seedThreshold) : String(threshold)}
                      </span>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Seed metrics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Seed Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">Conversations</p>
                  <p className="text-lg font-bold">{totalConvs}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Avg Quality</p>
                  <p className="text-lg font-bold font-mono">
                    {avgQuality != null ? avgQuality.toFixed(2) : '—'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Pass Rate</p>
                  <p className="text-lg font-bold">
                    {passRate != null ? `${Math.round(passRate * 100)}%` : '—'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Last Generated</p>
                  <p className="flex items-center gap-1 text-sm font-medium">
                    {lastGen ? (
                      <>
                        <Clock className="size-3 text-muted-foreground" />
                        {new Date(lastGen).toLocaleDateString()}
                      </>
                    ) : '—'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Generation section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Generate Conversations</CardTitle>
          <CardDescription className="text-xs">
            Create synthetic conversations from this seed and evaluate their quality
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="text-xs">Number of conversations</Label>
              <div className="flex items-center gap-3">
                <Slider
                  value={[count]}
                  onValueChange={([v]) => setCount(v)}
                  min={1}
                  max={10}
                  step={1}
                  className="flex-1"
                />
                <span className="w-8 text-right font-mono text-sm font-medium">{count}</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Temperature</Label>
              <div className="flex items-center gap-3">
                <Slider
                  value={[temperature]}
                  onValueChange={([v]) => setTemperature(Math.round(v * 100) / 100)}
                  min={0}
                  max={1}
                  step={0.05}
                  className="flex-1"
                />
                <span className="w-8 text-right font-mono text-sm font-medium">{temperature}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              onClick={handleGenerate}
              disabled={generating}
            >
              {generating ? (
                <>
                  <Loader2 className="mr-1.5 size-4 animate-spin" /> Generating...
                </>
              ) : (
                <>
                  <Rocket className="mr-1.5 size-4" /> Generate Conversations
                </>
              )}
            </Button>
            {(isDemoMode() || !apiAvailable) && (
              <Badge variant="outline" className="text-xs">Demo Mode</Badge>
            )}
          </div>

          {generating && (
            <div className="space-y-1">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-muted-foreground">{progress}% complete</p>
            </div>
          )}

          {generationError && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
              {generationError}
            </div>
          )}

          {generationResult && !generating && (
            <div className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-xs text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-300">
              Generated {generationResult.total} conversations, {generationResult.passed}/{generationResult.total} passed quality checks (avg score: {generationResult.avgScore.toFixed(2)})
            </div>
          )}
        </CardContent>
      </Card>

      {/* Generated conversations table */}
      {sessionConversations.length > 0 && (
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle className="text-sm">Generated Conversations</CardTitle>
              <CardDescription className="text-xs">{sessionConversations.length} conversations from this generation run</CardDescription>
            </div>
            {sessionReports.filter(r => r.passed).length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const passingIds = sessionReports.filter(r => r.passed).map(r => r.conversation_id)

                  handleAddToDataset(passingIds)
                }}
              >
                <Database className="mr-1.5 size-4" /> Add All Passing to Dataset
              </Button>
            )}
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-xs">ID</TableHead>
                  <TableHead className="text-xs">Turns</TableHead>
                  <TableHead className="text-xs">Quality Score</TableHead>
                  <TableHead className="text-xs">Status</TableHead>
                  <TableHead className="text-right text-xs">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sessionConversations.map(conv => {
                  const report = sessionReports.find(r => r.conversation_id === conv.conversation_id)

                  return (
                    <TableRow
                      key={conv.conversation_id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => router.push(`/dashboard/conversations/${conv.conversation_id}`)}
                    >
                      <TableCell className="font-mono text-xs">
                        {conv.conversation_id.slice(0, 12)}...
                      </TableCell>
                      <TableCell className="text-xs">{conv.turnos.length}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {report ? report.composite_score.toFixed(3) : '—'}
                      </TableCell>
                      <TableCell>
                        {report ? (
                          report.passed ? (
                            <Badge className={cn(
                              'text-xs',
                              'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300'
                            )}>
                              <Check className="mr-0.5 size-3" /> Passed
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="text-xs">
                              <X className="mr-0.5 size-3" /> Failed
                            </Badge>
                          )
                        ) : (
                          <Badge variant="outline" className="text-xs">Pending</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1" onClick={e => e.stopPropagation()}>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => router.push(`/dashboard/conversations/${conv.conversation_id}`)}
                          >
                            <Eye className="mr-1 size-3" /> View
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => handleAddToDataset([conv.conversation_id])}
                          >
                            <Database className="mr-1 size-3" /> Add
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
