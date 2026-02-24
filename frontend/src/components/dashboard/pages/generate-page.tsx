'use client'

import { useCallback, useEffect, useState } from 'react'

import Link from 'next/link'
import {
  AlertTriangle,
  Clock,
  Cloud,
  CloudOff,
  HelpCircle,
  History,
  Info,
  Loader2,
  Rocket,
  Sparkles,
  StopCircle,
  X,
  Zap
} from 'lucide-react'

import type { SeedSchema, Conversation, ConversationTurn, QualityReport } from '@/types/api'
import { cn } from '@/lib/utils'
import { checkApiHealth } from '@/lib/api/client'
import { generateConversations } from '@/lib/api/generate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

// ─── Local Storage Keys ───
const SEEDS_KEY = 'uncase-seeds'
const CONVERSATIONS_KEY = 'uncase-conversations'
const HISTORY_KEY = 'uncase-generation-history'

// ─── Types ───
interface GenerationRun {
  id: string
  timestamp: string
  seed_count: number
  conversations_per_seed: number
  conversation_count: number
  temperature: number
  language_override: string | null
  seed_ids: string[]
  mode: 'demo' | 'api'
}

// ─── Storage helpers ───
function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(SEEDS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveConversations(conversations: Conversation[]) {
  localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations))
}

function loadHistory(): GenerationRun[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(HISTORY_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveHistory(history: GenerationRun[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
}

// ─── Mock generation ───
function generateMockConversation(seed: SeedSchema, languageOverride?: string): Conversation {
  const numTurns = seed.pasos_turnos.turnos_min +
    Math.floor(Math.random() * (seed.pasos_turnos.turnos_max - seed.pasos_turnos.turnos_min + 1))

  const roles = seed.roles.length >= 2 ? seed.roles : ['usuario', 'asistente']
  const idioma = languageOverride || seed.idioma

  const turnos: ConversationTurn[] = Array.from({ length: numTurns }, (_, i) => ({
    turno: i + 1,
    rol: roles[i % roles.length],
    contenido: `Generated turn ${i + 1} content for ${seed.dominio} — ${seed.objetivo}`,
    herramientas_usadas: [],
    metadata: {}
  }))

  return {
    conversation_id: crypto.randomUUID(),
    seed_id: seed.seed_id,
    dominio: seed.dominio,
    idioma,
    turnos,
    es_sintetica: true,
    created_at: new Date().toISOString(),
    metadata: {
      generated_by: 'uncase-mock-generator',
      source_seed: seed.seed_id
    }
  }
}

// ─── Domain Colors ───
const DOMAIN_COLORS: Record<string, string> = {
  'automotive.sales': 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  'medical.consultation': 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  'legal.advisory': 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
  'finance.advisory': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300',
  'industrial.support': 'bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300',
  'education.tutoring': 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-300'
}

const LANGUAGES = [
  { value: '', label: 'Use seed default' },
  { value: 'es', label: 'Spanish' },
  { value: 'en', label: 'English' }
] as const

export function GeneratePage() {
  const [seeds] = useState<SeedSchema[]>(() => loadSeeds())
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [conversationsPerSeed, setConversationsPerSeed] = useState(5)
  const [temperature, setTemperature] = useState(0.7)
  const [languageOverride, setLanguageOverride] = useState('')
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [lastRunCount, setLastRunCount] = useState<number | null>(null)
  const [history, setHistory] = useState<GenerationRun[]>(() => loadHistory())

  // API integration state
  const [apiAvailable, setApiAvailable] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [evaluateAfter, setEvaluateAfter] = useState(true)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)

  const [qualityResults, setQualityResults] = useState<{
    total: number
    passed: number
    avgScore: number | null
  } | null>(null)

  // ─── Check API health on mount ───
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

    return () => {
      cancelled = true
    }
  }, [])

  // ─── Selection ───
  function toggleSeed(seedId: string) {
    setSelected(prev => {
      const next = new Set(prev)

      if (next.has(seedId)) {
        next.delete(seedId)
      } else {
        next.add(seedId)
      }

      return next
    })
  }

  function selectAll() {
    setSelected(new Set(seeds.map(s => s.seed_id)))
  }

  const clearSelection = useCallback(() => {
    setSelected(new Set())
  }, [])

  // ─── Cancel handler ───
  function handleCancel() {
    abortController?.abort()
    setAbortController(null)
  }

  // ─── Generation ───
  async function handleGenerate() {
    const selectedSeeds = seeds.filter(s => selected.has(s.seed_id))

    if (selectedSeeds.length === 0) return

    setGenerating(true)
    setProgress(0)
    setLastRunCount(null)
    setGenerationError(null)
    setQualityResults(null)

    const controller = new AbortController()

    setAbortController(controller)

    const totalConversations = selectedSeeds.length * conversationsPerSeed
    const generated: Conversation[] = []
    const allReports: QualityReport[] = []
    let completed = 0

    try {
      if (demoMode) {
        // Demo: use mock generator
        for (const seed of selectedSeeds) {
          for (let i = 0; i < conversationsPerSeed; i++) {
            if (controller.signal.aborted) break
            await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100))

            const conversation = generateMockConversation(seed, languageOverride || undefined)

            generated.push(conversation)
            completed++
            setProgress(Math.round((completed / totalConversations) * 100))
          }

          if (controller.signal.aborted) break
        }
      } else {
        // Real API: one call per seed
        for (const seed of selectedSeeds) {
          if (controller.signal.aborted) break

          const { data, error } = await generateConversations(
            {
              seed,
              count: conversationsPerSeed,
              temperature,
              language_override: languageOverride || undefined,
              evaluate_after: evaluateAfter
            },
            controller.signal
          )

          if (error) {
            if (error.status === 0 && error.message === 'Request cancelled') break
            setGenerationError(
              `Generation failed for seed ${seed.seed_id.slice(0, 8)}: ${error.message}`
            )
            break
          }

          if (data) {
            generated.push(...data.conversations)

            if (data.reports) allReports.push(...data.reports)

            completed += data.generation_summary.total_generated
            setProgress(Math.round((completed / totalConversations) * 100))
          }
        }
      }
    } catch {
      // Cancelled or unexpected
    }

    if (generated.length > 0) {
      // Save to localStorage
      const existing = loadConversations()

      saveConversations([...existing, ...generated])

      // Quality results
      if (allReports.length > 0) {
        const passedCount = allReports.filter(r => r.passed).length

        const avgScore =
          allReports.reduce((sum, r) => sum + r.composite_score, 0) / allReports.length

        setQualityResults({
          total: allReports.length,
          passed: passedCount,
          avgScore: Math.round(avgScore * 1000) / 1000
        })
      }

      // Save history
      const run: GenerationRun = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        seed_count: selectedSeeds.length,
        conversations_per_seed: conversationsPerSeed,
        conversation_count: generated.length,
        temperature,
        language_override: languageOverride || null,
        seed_ids: selectedSeeds.map(s => s.seed_id),
        mode: demoMode ? 'demo' : 'api'
      }

      const updatedHistory = [run, ...history]

      setHistory(updatedHistory)
      saveHistory(updatedHistory)
    }

    setLastRunCount(generated.length)
    setGenerating(false)
    setProgress(100)
    setAbortController(null)
    clearSelection()
  }

  // ─── Computed ───
  const selectedCount = selected.size
  const totalToGenerate = selectedCount * conversationsPerSeed

  // ─── Empty state ───
  if (seeds.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Synthetic Generation"
          description="Generate synthetic conversations from seeds"
        />
        <EmptyState
          icon={Rocket}
          title="No seeds available"
          description="Create seeds in the Seed Library first, then come back to generate synthetic conversations."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/seeds">
                <Sparkles className="mr-1.5 size-4" /> Go to Seed Library
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
        title="Synthetic Generation"
        description={`${seeds.length} seeds available for generation`}
        actions={
          <div className="flex items-center gap-2">
            {generating && (
              <Button variant="outline" size="sm" onClick={handleCancel}>
                <StopCircle className="mr-1.5 size-4" /> Cancel
              </Button>
            )}
            <Button
              size="sm"
              onClick={handleGenerate}
              disabled={generating || selectedCount === 0}
            >
              {generating ? (
                <Loader2 className="mr-1.5 size-4 animate-spin" />
              ) : (
                <Zap className="mr-1.5 size-4" />
              )}
              {generating
                ? 'Generating...'
                : selectedCount > 0
                  ? `Generate ${totalToGenerate} Conversations`
                  : 'Select Seeds to Generate'}
            </Button>
          </div>
        }
      />

      {/* Info banner */}
      <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/30">
        <CardContent className="flex items-start gap-3 p-4">
          <Info className="mt-0.5 size-4 shrink-0 text-blue-600 dark:text-blue-400" />
          <div className="space-y-1 text-xs text-blue-800 dark:text-blue-300">
            <p className="font-medium">How Synthetic Generation Works</p>
            <p>
              Select one or more seeds and configure generation parameters. The SCSF engine uses your seed&apos;s
              domain context, role definitions, and conversation flow to generate realistic synthetic conversations
              via LLM. Each generated conversation is optionally evaluated against 6 quality metrics to ensure
              it meets the required thresholds.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Progress bar during generation */}
      {generating && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Generating conversations...</span>
                <span className="text-muted-foreground">{progress}%</span>
              </div>
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground">
                Processing {selectedCount} seed{selectedCount !== 1 ? 's' : ''} x {conversationsPerSeed} conversation{conversationsPerSeed !== 1 ? 's' : ''} each
                {!demoMode && ' (API mode)'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error display */}
      {generationError && (
        <Card className="border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/30">
          <CardContent className="flex items-center gap-3 p-3">
            <AlertTriangle className="size-4 shrink-0 text-amber-600" />
            <p className="flex-1 text-xs text-amber-800 dark:text-amber-300">{generationError}</p>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs"
              onClick={() => setGenerationError(null)}
            >
              <X className="size-3" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Success banner */}
      {lastRunCount !== null && !generating && (
        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                Successfully generated {lastRunCount} conversation{lastRunCount !== 1 ? 's' : ''}
              </p>
              <p className="text-xs text-muted-foreground">
                Conversations have been saved to the local store.
              </p>
            </div>
            <Button asChild size="sm" variant="outline">
              <Link href="/dashboard/conversations">
                View Conversations
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Quality evaluation results */}
      {qualityResults && !generating && (
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-4">
            <p className="mb-2 text-sm font-semibold">Quality Evaluation Results</p>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-lg font-bold">{qualityResults.total}</p>
                <p className="text-[10px] text-muted-foreground">Evaluated</p>
              </div>
              <div>
                <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                  {qualityResults.passed}
                </p>
                <p className="text-[10px] text-muted-foreground">Passed</p>
              </div>
              <div>
                <p className="text-lg font-bold">
                  {qualityResults.avgScore?.toFixed(3) ?? 'N/A'}
                </p>
                <p className="text-[10px] text-muted-foreground">Avg Score</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Seed selection */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">Select Seeds</CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={selectAll}>
                    Select All
                  </Button>
                  {selectedCount > 0 && (
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={clearSelection}>
                      Clear ({selectedCount})
                    </Button>
                  )}
                </div>
              </div>
              <CardDescription className="text-xs">
                Pick one or more seeds to generate synthetic conversations from.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-[400px] space-y-1.5 overflow-y-auto">
                {seeds.map(seed => (
                  <label
                    key={seed.seed_id}
                    className={cn(
                      'flex cursor-pointer items-start gap-3 rounded-md border px-3 py-2.5 transition-colors hover:bg-muted',
                      selected.has(seed.seed_id) && 'border-primary bg-primary/5'
                    )}
                  >
                    <Checkbox
                      checked={selected.has(seed.seed_id)}
                      onCheckedChange={() => toggleSeed(seed.seed_id)}
                      className="mt-0.5"
                    />
                    <div className="flex-1 overflow-hidden">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-mono text-xs font-medium">
                          {seed.seed_id.slice(0, 16)}...
                        </span>
                        <Badge
                          variant="secondary"
                          className={cn('shrink-0 text-[10px]', DOMAIN_COLORS[seed.dominio])}
                        >
                          {seed.dominio.split('.').pop()}
                        </Badge>
                        <Badge variant="outline" className="shrink-0 text-[10px]">
                          {seed.idioma}
                        </Badge>
                      </div>
                      <p className="mt-0.5 truncate text-xs text-muted-foreground">
                        {seed.objetivo}
                      </p>
                      <div className="mt-1 flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>{seed.roles.join(', ')}</span>
                        <span>|</span>
                        <span>{seed.pasos_turnos.turnos_min}-{seed.pasos_turnos.turnos_max} turns</span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Generation config */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Generation Config</CardTitle>
              <CardDescription className="text-xs">
                Configure parameters for synthetic conversation generation.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* API Status & Demo Mode */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Demo Mode
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          In demo mode, conversations are generated locally with placeholder content.
                          When connected to the API, real LLM-powered generation is used.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Switch checked={demoMode} onCheckedChange={setDemoMode} />
                </div>
                <div className="flex items-center gap-1.5 text-[10px]">
                  {apiAvailable ? (
                    <>
                      <Cloud className="size-3 text-emerald-500" />
                      <span className="text-emerald-600 dark:text-emerald-400">API connected</span>
                    </>
                  ) : (
                    <>
                      <CloudOff className="size-3 text-amber-500" />
                      <span className="text-amber-600 dark:text-amber-400">
                        API unavailable — demo mode active
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Evaluate After toggle (API mode only) */}
              {!demoMode && (
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Evaluate After
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          Automatically run quality evaluation on each generated conversation.
                          Checks ROUGE-L, factual fidelity, lexical diversity, coherence, privacy,
                          and memorization.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Switch checked={evaluateAfter} onCheckedChange={setEvaluateAfter} />
                </div>
              )}

              {/* Conversations per seed */}
              <div className="space-y-2">
                <Label className="text-xs">Conversations per Seed</Label>
                <Input
                  type="number"
                  min={1}
                  max={50}
                  value={conversationsPerSeed}
                  onChange={e => {
                    const v = Math.max(1, Math.min(50, Number(e.target.value) || 1))

                    setConversationsPerSeed(v)
                  }}
                />
                <p className="text-[10px] text-muted-foreground">
                  Range: 1-50. Will generate {totalToGenerate > 0 ? totalToGenerate : '...'} total.
                </p>
              </div>

              {/* Temperature */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Temperature
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          Controls randomness in LLM output. Lower values (0.0-0.3) produce more
                          deterministic, consistent conversations. Higher values (0.7-1.5) increase
                          creativity and diversity. Default 0.7 is recommended for balanced output.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <span className="text-xs font-medium">{temperature.toFixed(1)}</span>
                </div>
                <Slider
                  value={[temperature]}
                  onValueChange={([v]) => setTemperature(Math.round(v * 10) / 10)}
                  min={0}
                  max={2}
                  step={0.1}
                />
                <div className="flex justify-between text-[10px] text-muted-foreground">
                  <span>0.0 (deterministic)</span>
                  <span>2.0 (creative)</span>
                </div>
              </div>

              {/* Language override */}
              <div className="space-y-2">
                <Label className="flex items-center gap-1 text-xs">
                  Language Override
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="size-3 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent side="left" className="max-w-xs text-xs">
                        Override the seed&apos;s default language for all generated conversations.
                        Useful for generating multilingual datasets from the same seed.
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </Label>
                <Select value={languageOverride} onValueChange={setLanguageOverride}>
                  <SelectTrigger>
                    <SelectValue placeholder="Use seed default" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGES.map(lang => (
                      <SelectItem key={lang.value || '__default'} value={lang.value || '__default'}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Summary */}
              {selectedCount > 0 && (
                <div className="rounded-md border bg-muted/50 p-3">
                  <p className="text-xs font-medium">Generation Summary</p>
                  <ul className="mt-1 space-y-0.5 text-[11px] text-muted-foreground">
                    <li>Seeds selected: <strong className="text-foreground">{selectedCount}</strong></li>
                    <li>Conversations per seed: <strong className="text-foreground">{conversationsPerSeed}</strong></li>
                    <li>Total to generate: <strong className="text-foreground">{totalToGenerate}</strong></li>
                    <li>Temperature: <strong className="text-foreground">{temperature.toFixed(1)}</strong></li>
                    <li>Language: <strong className="text-foreground">{languageOverride || 'seed default'}</strong></li>
                    <li>Mode: <strong className="text-foreground">{demoMode ? 'Demo' : 'API'}</strong></li>
                    {!demoMode && (
                      <li>Evaluate: <strong className="text-foreground">{evaluateAfter ? 'Yes' : 'No'}</strong></li>
                    )}
                    <li>
                      Est. time:{' '}
                      <strong className="text-foreground">
                        {demoMode ? '< 5s' : `~${Math.ceil(selectedCount * conversationsPerSeed * 8)}s`}
                      </strong>
                    </li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Generation History */}
      {history.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <History className="size-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium">Generation History</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Past generation runs stored locally.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map(run => (
                <div
                  key={run.id}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <div className="flex items-center gap-3">
                    <Clock className="size-3.5 text-muted-foreground" />
                    <div>
                      <p className="text-xs font-medium">
                        {run.conversation_count} conversation{run.conversation_count !== 1 ? 's' : ''} from{' '}
                        {run.seed_count} seed{run.seed_count !== 1 ? 's' : ''}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {new Date(run.timestamp).toLocaleString()} | temp: {run.temperature} | lang: {run.language_override || 'default'}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px]">
                    {run.mode === 'api' ? 'API' : 'Demo'} | {run.conversations_per_seed}/seed
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
