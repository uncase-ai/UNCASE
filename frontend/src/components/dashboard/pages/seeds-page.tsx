'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  ArrowUpDown,
  BarChart3,
  Check,
  Cloud,
  CloudOff,
  HelpCircle,
  Info,
  Layers,
  Loader2,
  Play,
  Plus,
  RefreshCw,
  Rocket,
  Sprout,
  Star,
  Trash2,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, QualityReport, ScenarioTemplate, SeedSchema, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { fetchScenarioPack } from '@/lib/api/scenarios'
import { generateConversations } from '@/lib/api/generate'
import { createEmptySeed, createSeedApi, deleteSeedApi, fetchSeeds, validateSeed } from '@/lib/api/seeds'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { EmptyState } from '../empty-state'
import { JsonViewer } from '../json-viewer'
import { PageHeader } from '../page-header'
import { SearchInput } from '../search-input'

// ─── Local Storage ───
const STORE_KEY = 'uncase-seeds'

function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveSeeds(seeds: SeedSchema[]) {
  localStorage.setItem(STORE_KEY, JSON.stringify(seeds))
}

const TONES_EN = ['professional', 'informal', 'technical', 'empathetic', 'friendly', 'formal', 'persuasive'] as const
const TONES_ES = ['profesional', 'informal', 'tecnico', 'empatico', 'amigable', 'formal', 'persuasivo'] as const
const LANGUAGES = ['es', 'en'] as const
const ANONYMIZATION_METHODS = ['presidio', 'regex', 'spacy', 'manual', 'none'] as const
const TOTAL_STEPS = 6

const OBJECTIVE_EXAMPLES: Record<string, { en: string; es: string }> = {
  'automotive.sales': {
    en: 'Customer negotiating a certified pre-owned SUV with financing options and trade-in evaluation',
    es: 'Cliente negociando una SUV seminueva certificada con opciones de financiamiento y avaluo de unidad'
  },
  'medical.consultation': {
    en: 'Patient describing recurring headaches; doctor orders lab work and discusses preventive measures',
    es: 'Paciente describiendo dolores de cabeza recurrentes; doctor ordena estudios y discute medidas preventivas'
  },
  'legal.advisory': {
    en: 'Client consulting about breach of contract claim — lawyer reviews evidence and explains litigation options',
    es: 'Cliente consultando sobre demanda por incumplimiento de contrato — abogado revisa evidencia y explica opciones'
  },
  'finance.advisory': {
    en: 'Client reviewing retirement portfolio rebalancing with risk assessment and tax implications',
    es: 'Cliente revisando rebalanceo de portafolio de retiro con evaluacion de riesgo e implicaciones fiscales'
  },
  'industrial.support': {
    en: 'Operator reporting error code E-47 on CNC machine; technician runs remote diagnostics and schedules maintenance',
    es: 'Operador reportando codigo de error E-47 en maquina CNC; tecnico ejecuta diagnostico remoto y agenda mantenimiento'
  },
  'education.tutoring': {
    en: 'Student struggling with quadratic equations — tutor uses step-by-step examples and adaptive exercises',
    es: 'Estudiante con dificultades en ecuaciones cuadraticas — tutor usa ejemplos paso a paso y ejercicios adaptativos'
  }
}

function loadProjectTools(): ToolDefinition[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem('uncase-tools')

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

async function syncProjectTools(): Promise<ToolDefinition[]> {
  try {
    const { fetchTools } = await import('@/lib/api/tools')
    const result = await fetchTools(undefined, AbortSignal.timeout(5_000))

    if (result.data && result.data.length > 0) {
      localStorage.setItem('uncase-tools', JSON.stringify(result.data))
      window.dispatchEvent(new StorageEvent('storage', { key: 'uncase-tools' }))

      return result.data
    }
  } catch {
    // API unavailable — use localStorage
  }

  return loadProjectTools()
}

const DOMAIN_LABELS: Record<string, string> = {
  'automotive.sales': 'Automotive',
  'medical.consultation': 'Medical',
  'legal.advisory': 'Legal',
  'finance.advisory': 'Finance',
  'industrial.support': 'Industrial',
  'education.tutoring': 'Education'
}

const FAVORITES_KEY = 'uncase-seed-favorites'

function loadFavorites(): Set<string> {
  if (typeof window === 'undefined') return new Set()

  try {
    const raw = localStorage.getItem(FAVORITES_KEY)

    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

function saveFavorites(ids: Set<string>) {
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...ids]))
}

function loadConversationsForStats(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem('uncase-conversations')

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadEvaluationsForStats(): QualityReport[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem('uncase-evaluations')

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

type SortOption = 'newest' | 'oldest' | 'name' | 'runs' | 'quality' | 'favorites'

function timeAgo(date: string): string {
  const diff = Date.now() - new Date(date).getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)

  if (hours < 24) return `${hours}h ago`

  const days = Math.floor(hours / 24)

  if (days < 30) return `${days}d ago`

  return new Date(date).toLocaleDateString()
}

// ─── Tooltip helper ───
function FieldTooltip({ text }: { text: string }) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <HelpCircle className="size-3 text-muted-foreground" />
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-xs text-xs">
          {text}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export function SeedsPage() {
  const [seeds, setSeeds] = useState<SeedSchema[]>(() => loadSeeds())
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  const [favorites, setFavorites] = useState<Set<string>>(() => loadFavorites())

  // API connectivity state
  const [apiAvailable, setApiAvailable] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [syncError, setSyncError] = useState<string | null>(null)

  // Create dialog
  const [createOpen, setCreateOpen] = useState(false)
  const [step, setStep] = useState(1)
  const [draft, setDraft] = useState<Partial<SeedSchema>>(() => createEmptySeed())
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // Detail dialog
  const [selectedSeed, setSelectedSeed] = useState<SeedSchema | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)

  // Scenario selector
  const [domainScenarios, setDomainScenarios] = useState<ScenarioTemplate[]>([])
  const [scenariosLoading, setScenariosLoading] = useState(false)

  // Computed stats from localStorage
  function computeSeedStats() {
    const conversations = loadConversationsForStats()
    const evaluations = loadEvaluationsForStats()

    const runCounts: Record<string, number> = {}
    const qualityScores: Record<string, number[]> = {}

    for (const conv of conversations) {
      runCounts[conv.seed_id] = (runCounts[conv.seed_id] || 0) + 1
    }

    for (const ev of evaluations) {
      if (!qualityScores[ev.seed_id]) qualityScores[ev.seed_id] = []
      qualityScores[ev.seed_id].push(ev.composite_score)
    }

    const avgQuality: Record<string, number> = {}

    for (const [id, scores] of Object.entries(qualityScores)) {
      avgQuality[id] = scores.reduce((a, b) => a + b, 0) / scores.length
    }

    return { runCounts, avgQuality }
  }

  const [seedStats, setSeedStats] = useState(() => computeSeedStats())

  // Toggle favorite
  function toggleFavorite(e: React.MouseEvent, seedId: string) {
    e.stopPropagation()

    const next = new Set(favorites)

    if (next.has(seedId)) next.delete(seedId)
    else next.add(seedId)

    setFavorites(next)
    saveFavorites(next)
  }

  // ─── API Integration ───
  const loadFromApi = useCallback(async () => {
    setSyncing(true)
    setSyncError(null)
    const { data, error } = await fetchSeeds({ page_size: 100 })

    if (error) {
      setSyncError(error.message)
      setSyncing(false)

      return
    }

    if (data) {
      // Convert SeedResponse to SeedSchema format for compatibility
      const apiSeeds: SeedSchema[] = data.items.map(item => ({
        seed_id: item.id,
        version: item.version as '1.0',
        dominio: item.dominio,
        idioma: item.idioma,
        etiquetas: item.etiquetas,
        roles: item.roles,
        descripcion_roles: item.descripcion_roles,
        objetivo: item.objetivo,
        tono: item.tono,
        pasos_turnos: item.pasos_turnos,
        parametros_factuales: item.parametros_factuales,
        privacidad: item.privacidad,
        metricas_calidad: item.metricas_calidad,
        organization_id: item.organization_id ?? undefined,
        created_at: item.created_at,
        updated_at: item.updated_at
      }))


      // Merge: API seeds take precedence, add local-only seeds
      const localSeeds = loadSeeds()
      const apiIds = new Set(apiSeeds.map(s => s.seed_id))
      const localOnly = localSeeds.filter(s => !apiIds.has(s.seed_id))
      const merged = [...apiSeeds, ...localOnly]

      setSeeds(merged)
      saveSeeds(merged)
    }

    setSyncing(false)
  }, [])

  // Check API health on mount and load seeds if available
  useEffect(() => {
    let cancelled = false

    async function init() {
      const healthy = await checkApiHealth()

      if (cancelled) return
      setApiAvailable(healthy)

      if (healthy) {
        await Promise.all([loadFromApi(), syncProjectTools()])
      }
    }

    init()

    return () => { cancelled = true }
  }, [loadFromApi])

  // ─── Filtering & sorting ───
  const filtered = useMemo(() => {
    let result = seeds

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        s =>
          s.seed_id.toLowerCase().includes(q) ||
          s.objetivo.toLowerCase().includes(q) ||
          s.dominio.toLowerCase().includes(q) ||
          s.etiquetas.some(t => t.toLowerCase().includes(q)) ||
          s.roles.some(r => r.toLowerCase().includes(q))
      )
    }

    if (domainFilter !== 'all') {
      result = result.filter(s => s.dominio === domainFilter)
    }

    const sorted = [...result]

    switch (sortBy) {
      case 'newest':
        sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
      case 'oldest':
        sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'name':
        sorted.sort((a, b) => a.seed_id.localeCompare(b.seed_id))
        break
      case 'runs':
        sorted.sort((a, b) => (seedStats.runCounts[b.seed_id] || 0) - (seedStats.runCounts[a.seed_id] || 0))
        break
      case 'quality':
        sorted.sort((a, b) => (seedStats.avgQuality[b.seed_id] || 0) - (seedStats.avgQuality[a.seed_id] || 0))
        break
      case 'favorites':
        sorted.sort((a, b) => (favorites.has(b.seed_id) ? 1 : 0) - (favorites.has(a.seed_id) ? 1 : 0))
        break
    }

    return sorted
  }, [seeds, search, domainFilter, sortBy, seedStats, favorites])

  // ─── Create seed ───
  function resetCreate() {
    setStep(1)
    setDraft(createEmptySeed())
    setValidationErrors([])
  }

  function handleValidate() {
    const errors = validateSeed(draft)

    setValidationErrors(errors)

    return errors.length === 0
  }

  async function handleCreate() {
    if (!handleValidate()) return

    const now = new Date().toISOString()

    const draftScenarios = ((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[] | undefined) ?? null

    const newSeed: SeedSchema = {
      ...(draft as SeedSchema),
      seed_id: crypto.randomUUID().replace(/-/g, ''),
      scenarios: draftScenarios?.length ? draftScenarios : null,
      created_at: now,
      updated_at: now
    }

    // Try backend first
    if (apiAvailable) {
      const selectedScenarios = ((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[] | undefined) ?? null

      const { data, error } = await createSeedApi({
        dominio: newSeed.dominio,
        idioma: newSeed.idioma,
        version: newSeed.version,
        etiquetas: newSeed.etiquetas,
        objetivo: newSeed.objetivo,
        tono: newSeed.tono,
        roles: newSeed.roles,
        descripcion_roles: newSeed.descripcion_roles,
        pasos_turnos: newSeed.pasos_turnos,
        parametros_factuales: newSeed.parametros_factuales,
        privacidad: newSeed.privacidad,
        metricas_calidad: newSeed.metricas_calidad,
        ...(selectedScenarios?.length ? { scenarios: selectedScenarios } : {})
      })

      if (data) {
        // Use server-assigned ID
        newSeed.seed_id = data.id
      } else if (error) {
        setSyncError(`Failed to save to server: ${error.message}`)
      }
    }

    const updated = [newSeed, ...seeds]

    setSeeds(updated)
    saveSeeds(updated)
    setCreateOpen(false)
    resetCreate()
  }

  // ─── Delete seed ───
  async function handleDelete(seedId: string) {
    if (apiAvailable) {
      const { error } = await deleteSeedApi(seedId)

      if (error) {
        setSyncError(`Failed to delete from server: ${error.message}`)
      }
    }

    const updated = seeds.filter(s => s.seed_id !== seedId)

    setSeeds(updated)
    saveSeeds(updated)
    setDetailOpen(false)
    setSelectedSeed(null)
  }

  // ─── Generate & Evaluate ───
  const [generating, setGenerating] = useState<string | null>(null)
  const [generateResult, setGenerateResult] = useState<string | null>(null)

  async function handleGenerateAndEvaluate(seed: SeedSchema) {
    if (!apiAvailable) {
      setSyncError('API connection required for generation')

      return
    }

    setGenerating(seed.seed_id)
    setGenerateResult(null)

    const { data, error } = await generateConversations({
      seed,
      count: 3,
      temperature: 0.7,
      evaluate_after: true
    })

    setGenerating(null)

    if (error) {
      setSyncError(`Generation failed: ${error.message}`)

      return
    }

    if (data) {
      const summary = data.generation_summary
      const passed = summary.total_passed ?? 0
      const total = summary.total_generated

      setGenerateResult(
        `Generated ${total} conversations, ${passed}/${total} passed quality checks (avg score: ${(summary.avg_composite_score ?? 0).toFixed(2)})`
      )

      // Store generated conversations in localStorage for other pages
      const { appendConversations } = await import('./conversations-page')

      appendConversations(data.conversations)

      // Store evaluation reports
      if (data.reports) {
        try {
          const existing = JSON.parse(localStorage.getItem('uncase-evaluations') || '[]')
          const merged = [...existing, ...data.reports]

          localStorage.setItem('uncase-evaluations', JSON.stringify(merged))
        } catch {
          // Storage full
        }
      }

      // Update run stats
      setSeedStats(computeSeedStats())
    }
  }

  // ─── Load domain scenarios when entering step 4 ───
  useEffect(() => {
    if (step === 4 && draft.dominio && apiAvailable) {
      loadDomainScenarios(draft.dominio)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step])

  const loadDomainScenarios = useCallback(async (domain: string) => {
    if (!domain || !apiAvailable) {
      setDomainScenarios([])

      return
    }

    setScenariosLoading(true)

    try {
      const res = await fetchScenarioPack(domain)

      if (res.data) {
        setDomainScenarios(res.data.scenarios)
      } else {
        setDomainScenarios([])
      }
    } catch {
      setDomainScenarios([])
    } finally {
      setScenariosLoading(false)
    }
  }, [apiAvailable])

  // ─── Draft update helpers ───
  function updateDraft(patch: Partial<SeedSchema>) {
    setDraft(prev => ({ ...prev, ...patch }))
  }

  function updatePasosTurnos(patch: Partial<SeedSchema['pasos_turnos']>) {
    setDraft(prev => ({
      ...prev,
      pasos_turnos: { ...prev.pasos_turnos!, ...patch }
    }))
  }

  function updateParametros(patch: Partial<SeedSchema['parametros_factuales']>) {
    setDraft(prev => ({
      ...prev,
      parametros_factuales: { ...prev.parametros_factuales!, ...patch }
    }))
  }

  function updatePrivacidad(patch: Partial<SeedSchema['privacidad']>) {
    setDraft(prev => ({
      ...prev,
      privacidad: { ...prev.privacidad!, ...patch }
    }))
  }

  // ─── Role management ───
  function addRole() {
    const roles = [...(draft.roles || []), '']

    updateDraft({ roles })
  }

  function removeRole(index: number) {
    const roles = [...(draft.roles || [])]
    const removed = roles.splice(index, 1)[0]
    const descripcion_roles = { ...(draft.descripcion_roles || {}) }

    if (removed) delete descripcion_roles[removed]
    updateDraft({ roles, descripcion_roles })
  }

  function updateRole(index: number, value: string) {
    const roles = [...(draft.roles || [])]
    const oldName = roles[index]

    roles[index] = value
    const descripcion_roles = { ...(draft.descripcion_roles || {}) }

    if (oldName && oldName !== value) {
      descripcion_roles[value] = descripcion_roles[oldName] || ''
      delete descripcion_roles[oldName]
    }

    updateDraft({ roles, descripcion_roles })
  }

  function updateRoleDescription(role: string, description: string) {
    updateDraft({
      descripcion_roles: { ...(draft.descripcion_roles || {}), [role]: description }
    })
  }

  // ─── List helpers ───
  function addToList(field: 'flujo_esperado') {
    const list = [...(draft.pasos_turnos?.[field] || []), '']

    updatePasosTurnos({ [field]: list })
  }

  function removeFromList(field: 'flujo_esperado', index: number) {
    const list = [...(draft.pasos_turnos?.[field] || [])]

    list.splice(index, 1)
    updatePasosTurnos({ [field]: list })
  }

  function updateListItem(field: 'flujo_esperado', index: number, value: string) {
    const list = [...(draft.pasos_turnos?.[field] || [])]

    list[index] = value
    updatePasosTurnos({ [field]: list })
  }

  function addToParamList(field: 'restricciones' | 'herramientas') {
    const list = [...(draft.parametros_factuales?.[field] || []), '']

    updateParametros({ [field]: list })
  }

  function removeFromParamList(field: 'restricciones' | 'herramientas', index: number) {
    const list = [...(draft.parametros_factuales?.[field] || [])]

    list.splice(index, 1)
    updateParametros({ [field]: list })
  }

  function updateParamListItem(field: 'restricciones' | 'herramientas', index: number, value: string) {
    const list = [...(draft.parametros_factuales?.[field] || [])]

    list[index] = value
    updateParametros({ [field]: list })
  }

  // ─── Tag management ───
  const [tagInput, setTagInput] = useState('')

  function addTag() {
    const tag = tagInput.trim()

    if (tag && !(draft.etiquetas || []).includes(tag)) {
      updateDraft({ etiquetas: [...(draft.etiquetas || []), tag] })
      setTagInput('')
    }
  }

  function removeTag(index: number) {
    const tags = [...(draft.etiquetas || [])]

    tags.splice(index, 1)
    updateDraft({ etiquetas: tags })
  }

  // ─── Connection status indicator ───
  function renderSyncStatus() {
    return (
      <div className="flex items-center gap-1.5">
        {apiAvailable ? (
          <Badge variant="outline" className="gap-1 text-[10px]">
            <Cloud className="size-3" /> API Connected
          </Badge>
        ) : (
          <Badge variant="outline" className="gap-1 text-[10px]">
            <CloudOff className="size-3" /> Local Only
          </Badge>
        )}
        {syncing && <RefreshCw className="size-3 animate-spin text-muted-foreground" />}
      </div>
    )
  }

  // ─── Info banner ───
  function renderInfoBanner() {
    return (
      <Card className="bg-muted/40">
        <CardContent className="flex items-start gap-3 p-4 sm:p-5">
          <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground sm:size-5" />
          <div className="space-y-1 text-xs text-muted-foreground sm:text-sm">
            <p className="text-base font-semibold text-foreground sm:text-lg">What are Seeds?</p>
            <p>
              Seeds are structured templates that define the parameters for synthetic conversation generation.
              Each seed specifies the domain, roles, conversation flow, factual constraints, and privacy settings.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // ─── Sync error alert ───
  function renderSyncError() {
    if (!syncError) return null

    return (
      <Card className="bg-muted/40">
        <CardContent className="flex items-center gap-3 p-3">
          <AlertTriangle className="size-4 shrink-0 text-muted-foreground" />
          <p className="text-xs text-muted-foreground">{syncError}</p>
          <Button variant="ghost" size="sm" className="ml-auto h-6 text-xs" onClick={() => setSyncError(null)}>
            Dismiss
          </Button>
        </CardContent>
      </Card>
    )
  }

  // ─── Create dialog content (shared between empty and normal states) ───
  function renderCreateDialog() {
    return (
      <Dialog open={createOpen} onOpenChange={open => { setCreateOpen(open); if (!open) resetCreate() }}>
        <DialogTrigger asChild>
          <Button size="sm">
            <Plus className="mr-1.5 size-4" /> Create Seed
          </Button>
        </DialogTrigger>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Create Seed</DialogTitle>
            <DialogDescription>
              Step {step} of {TOTAL_STEPS} — Build a new seed schema for synthetic conversation generation.
            </DialogDescription>
          </DialogHeader>
          {renderStep()}
          <DialogFooter className="flex-row justify-between sm:justify-between">
            <Button
              variant="outline"
              size="sm"
              disabled={step === 1}
              onClick={() => setStep(s => s - 1)}
            >
              <ArrowLeft className="mr-1.5 size-4" /> Back
            </Button>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{step}/{TOTAL_STEPS}</span>
              {step < TOTAL_STEPS ? (
                <Button size="sm" onClick={() => setStep(s => s + 1)}>
                  Next <ArrowRight className="ml-1.5 size-4" />
                </Button>
              ) : (
                <Button size="sm" onClick={handleCreate} disabled={validationErrors.length > 0}>
                  Create Seed
                </Button>
              )}
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // ─── Step content renderer ───
  function renderStep() {
    switch (step) {
      case 1: {
        const lang = draft.idioma || 'es'
        const tones = lang === 'es' ? TONES_ES : TONES_EN

        const objectiveExample = draft.dominio
          ? (lang === 'es'
              ? OBJECTIVE_EXAMPLES[draft.dominio]?.es
              : OBJECTIVE_EXAMPLES[draft.dominio]?.en) || ''
          : lang === 'es'
            ? 'Cliente negociando una SUV seminueva con opciones de financiamiento'
            : 'Customer negotiating a certified pre-owned SUV with financing options'

        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 1: Basic Information</h3>
              <p className="text-xs text-muted-foreground">
                Choose the industry domain, define the conversation&apos;s objective, and set language/tone preferences.
              </p>
            </div>
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Domain
                <FieldTooltip text="The industry vertical this seed targets. Each domain has specific terminology, compliance requirements, and conversation patterns." />
              </Label>
              <Select value={draft.dominio || ''} onValueChange={v => updateDraft({ dominio: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select domain" />
                </SelectTrigger>
                <SelectContent>
                  {SUPPORTED_DOMAINS.map(d => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Objective
                <FieldTooltip text="A clear description of what the conversation should achieve. This guides the LLM during generation." />
              </Label>
              <Textarea
                value={draft.objetivo || ''}
                onChange={e => updateDraft({ objetivo: e.target.value })}
                placeholder={objectiveExample}
                className="min-h-[60px]"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label className="flex items-center gap-1">
                  Language
                  <FieldTooltip text="The primary language for generated conversations. Tone options will match the selected language." />
                </Label>
                <Select
                  value={lang}
                  onValueChange={v => {
                    const newTones = v === 'es' ? TONES_ES : TONES_EN
                    const currentToneIdx = (tones as readonly string[]).indexOf(draft.tono || '')
                    const newTone = currentToneIdx >= 0 ? newTones[currentToneIdx] : newTones[0]

                    updateDraft({ idioma: v, tono: newTone })
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGES.map(l => (
                      <SelectItem key={l} value={l}>{l === 'es' ? 'Spanish' : 'English'}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="flex items-center gap-1">
                  Tone
                  <FieldTooltip text="Sets the formality and communication style. Professional for regulated industries, informal for customer support." />
                </Label>
                <Select value={draft.tono || tones[0]} onValueChange={v => updateDraft({ tono: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {tones.map(t => (
                      <SelectItem key={t} value={t}>{t}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Tags</Label>
              <div className="flex gap-2">
                <Input
                  value={tagInput}
                  onChange={e => setTagInput(e.target.value)}
                  placeholder="Add a tag..."
                  onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag() } }}
                />
                <Button type="button" variant="outline" size="sm" onClick={addTag}>Add</Button>
              </div>
              {(draft.etiquetas || []).length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(draft.etiquetas || []).map((tag, i) => (
                    <Badge key={i} variant="secondary" className="gap-1 pr-1 text-xs">
                      {tag}
                      <button onClick={() => removeTag(i)} className="ml-0.5 rounded hover:bg-muted">
                        <X className="size-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        )
      }

      case 2:
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 2: Roles</h3>
              <p className="text-xs text-muted-foreground">
                Define at least 2 participants. Common patterns: user/assistant, patient/doctor, client/advisor.
              </p>
            </div>
            {(draft.roles || []).map((role, i) => (
              <div key={i} className="space-y-2 rounded-md border p-3">
                <div className="flex items-center gap-2">
                  <Input
                    value={role}
                    onChange={e => updateRole(i, e.target.value)}
                    placeholder={`Role ${i + 1} name`}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0"
                    onClick={() => removeRole(i)}
                  >
                    <Trash2 className="size-3.5 text-destructive" />
                  </Button>
                </div>
                {role && (
                  <div className="space-y-1">
                    <Label className="text-xs">Description for &ldquo;{role}&rdquo;</Label>
                    <Textarea
                      value={draft.descripcion_roles?.[role] || ''}
                      onChange={e => updateRoleDescription(role, e.target.value)}
                      placeholder={`Describe the ${role} role...`}
                      className="min-h-[60px]"
                    />
                  </div>
                )}
              </div>
            ))}
            <Button type="button" variant="outline" size="sm" onClick={addRole}>
              <Plus className="mr-1.5 size-4" /> Add Role
            </Button>
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 3: Turn Structure</h3>
              <p className="text-xs text-muted-foreground">
                Controls conversation length and flow. Min/max turns define the range, and expected flow provides step-by-step guidance to the generator.
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Min Turns</Label>
                <Input
                  type="number"
                  min={1}
                  value={draft.pasos_turnos?.turnos_min ?? 3}
                  onChange={e => updatePasosTurnos({ turnos_min: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label>Max Turns</Label>
                <Input
                  type="number"
                  min={2}
                  value={draft.pasos_turnos?.turnos_max ?? 10}
                  onChange={e => updatePasosTurnos({ turnos_max: Number(e.target.value) })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Expected Flow
                <FieldTooltip text="Ordered steps the conversation should follow. The generator uses these as structural guidelines." />
              </Label>
              <p className="text-xs text-muted-foreground">Define the expected sequence of conversation steps.</p>
              {(draft.pasos_turnos?.flujo_esperado || []).map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="w-6 text-center text-xs text-muted-foreground">{i + 1}</span>
                  <Input
                    value={item}
                    onChange={e => updateListItem('flujo_esperado', i, e.target.value)}
                    placeholder={`Step ${i + 1}`}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0"
                    onClick={() => removeFromList('flujo_esperado', i)}
                  >
                    <X className="size-3.5" />
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => addToList('flujo_esperado')}>
                <Plus className="mr-1.5 size-4" /> Add Step
              </Button>
            </div>
          </div>
        )

      case 4: {
        const allTools = loadProjectTools()
        const selectedDomain = draft.dominio || ''

        const domainTools = selectedDomain
          ? allTools.filter(t => t.domains.some(d => d === selectedDomain))
          : allTools

        const otherTools = selectedDomain
          ? allTools.filter(t => !t.domains.some(d => d === selectedDomain))
          : []

        const selectedTools = new Set(draft.parametros_factuales?.herramientas || [])

        function toggleTool(toolName: string) {
          const current = new Set(draft.parametros_factuales?.herramientas || [])

          if (current.has(toolName)) current.delete(toolName)
          else current.add(toolName)
          updateParametros({ herramientas: [...current] })
        }

        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 4: Context &amp; Tools</h3>
              <p className="text-xs text-muted-foreground">
                Domain-specific context, brand identity, constraints, and available tools for this seed.
              </p>
            </div>

            {/* Context */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Context
                <FieldTooltip text="Factual background the generator should know. Include industry specifics, product details, or scenario setup." />
              </Label>
              <Textarea
                value={draft.parametros_factuales?.contexto || ''}
                onChange={e => updateParametros({ contexto: e.target.value })}
                placeholder="Describe the factual context for the conversation..."
                className="min-h-[80px]"
              />
            </div>

            {/* Assistant Name */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Assistant Name
                <FieldTooltip text="The name the assistant will use to identify itself (e.g. 'Sofia', 'Dr. MediBot'). This prevents the name from being flagged as PII during generation." />
              </Label>
              <Input
                value={draft.parametros_factuales?.nombre_asistente || ''}
                onChange={e => updateParametros({ nombre_asistente: e.target.value })}
                placeholder={draft.idioma === 'es' ? 'Ej: Sofia, Asesor Virtual' : 'e.g. Sofia, Virtual Advisor'}
              />
            </div>

            {/* Brand Greeting */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Brand Greeting
                <FieldTooltip text="A mandatory opening line or greeting template the assistant must use. Include your brand name or slogan so it appears naturally in generated conversations." />
              </Label>
              <Textarea
                value={draft.parametros_factuales?.saludo_marca || ''}
                onChange={e => updateParametros({ saludo_marca: e.target.value })}
                placeholder={draft.idioma === 'es'
                  ? 'Ej: Bienvenido a AutoMax, soy Sofia, tu asesora virtual. ¿En que puedo ayudarte hoy?'
                  : 'e.g. Welcome to AutoMax! I\'m Sofia, your virtual advisor. How can I help you today?'}
                className="min-h-[60px]"
              />
            </div>

            {/* Restrictions */}
            <div className="space-y-2">
              <Label>Restrictions</Label>
              {(draft.parametros_factuales?.restricciones || []).map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Input
                    value={item}
                    onChange={e => updateParamListItem('restricciones', i, e.target.value)}
                    placeholder={`Restriction ${i + 1}`}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0"
                    onClick={() => removeFromParamList('restricciones', i)}
                  >
                    <X className="size-3.5" />
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => addToParamList('restricciones')}>
                <Plus className="mr-1.5 size-4" /> Add Restriction
              </Button>
            </div>

            {/* Tools — Selectable from project tools */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Tools
                <FieldTooltip text="Select tools the assistant can invoke during the conversation. Only selected tools will be available to the generator." />
              </Label>
              {allTools.length > 0 ? (
                <div className="space-y-2">
                  {domainTools.length > 0 && (
                    <div className="space-y-1.5">
                      {selectedDomain && (
                        <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                          {DOMAIN_LABELS[selectedDomain] || selectedDomain} tools
                        </p>
                      )}
                      <div className="max-h-40 space-y-1 overflow-y-auto rounded-md border p-2">
                        {domainTools.map(tool => (
                          <label
                            key={tool.name}
                            className={cn(
                              'flex cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 transition-colors hover:bg-muted/50',
                              selectedTools.has(tool.name) && 'bg-muted'
                            )}
                          >
                            <input
                              type="checkbox"
                              checked={selectedTools.has(tool.name)}
                              onChange={() => toggleTool(tool.name)}
                              className="mt-0.5 accent-primary"
                            />
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-1.5">
                                <span className="font-mono text-xs font-medium">{tool.name}</span>
                                <Badge variant="outline" className="text-[9px]">{tool.category}</Badge>
                              </div>
                              <p className="truncate text-[10px] text-muted-foreground">{tool.description}</p>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                  {otherTools.length > 0 && (
                    <div className="space-y-1.5">
                      <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Other domains</p>
                      <div className="max-h-32 space-y-1 overflow-y-auto rounded-md border p-2">
                        {otherTools.map(tool => (
                          <label
                            key={tool.name}
                            className={cn(
                              'flex cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 transition-colors hover:bg-muted/50',
                              selectedTools.has(tool.name) && 'bg-muted'
                            )}
                          >
                            <input
                              type="checkbox"
                              checked={selectedTools.has(tool.name)}
                              onChange={() => toggleTool(tool.name)}
                              className="mt-0.5 accent-primary"
                            />
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-1.5">
                                <span className="font-mono text-xs font-medium">{tool.name}</span>
                                <Badge variant="outline" className="text-[9px]">{tool.domains.join(', ')}</Badge>
                              </div>
                              <p className="truncate text-[10px] text-muted-foreground">{tool.description}</p>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedTools.size > 0 && (
                    <p className="text-[10px] text-muted-foreground">{selectedTools.size} tool{selectedTools.size > 1 ? 's' : ''} selected</p>
                  )}
                </div>
              ) : (
                <div className="rounded-md border border-dashed p-3 text-center">
                  <Wrench className="mx-auto mb-1 size-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">
                    No tools registered yet. Go to the Tools page to add tools, or they will be loaded from demo data.
                  </p>
                </div>
              )}
            </div>

            {/* Scenario Templates */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                <Layers className="size-3.5" />
                Scenario Templates
                <FieldTooltip text="Attach curated conversation archetypes from the built-in scenario pack for this domain. The generator will randomly select from these during batch generation." />
              </Label>
              {domainScenarios.length > 0 ? (
                <div className="space-y-2">
                  <div className="max-h-48 space-y-1 overflow-y-auto rounded-md border p-2">
                    {domainScenarios.map(sc => {
                      const attached = (draft as Record<string, unknown>)._scenarios as ScenarioTemplate[] | undefined
                      const isSelected = attached?.some(s => s.name === sc.name) ?? false

                      return (
                        <label
                          key={sc.name}
                          className={cn(
                            'flex cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 transition-colors hover:bg-muted/50',
                            isSelected && 'bg-muted'
                          )}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => {
                              const current = ((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[] | undefined) ?? []

                              if (isSelected) {
                                (draft as Record<string, unknown>)._scenarios = current.filter(s => s.name !== sc.name)
                              } else {
                                (draft as Record<string, unknown>)._scenarios = [...current, sc]
                              }

                              setDraft({ ...draft })
                            }}
                            className="mt-0.5 accent-primary"
                          />
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-medium">
                                {sc.name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                              </span>
                              <Badge variant="outline" className="text-[9px]">{sc.skill_level}</Badge>
                              {sc.edge_case && (
                                <Badge variant="outline" className="text-[9px] bg-orange-500/10 text-orange-600">edge</Badge>
                              )}
                            </div>
                            <p className="truncate text-[10px] text-muted-foreground">{sc.description}</p>
                          </div>
                        </label>
                      )
                    })}
                  </div>
                  {((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[] | undefined)?.length ? (
                    <p className="text-[10px] text-muted-foreground">
                      {((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[]).length} scenario{((draft as Record<string, unknown>)._scenarios as ScenarioTemplate[]).length > 1 ? 's' : ''} selected
                    </p>
                  ) : null}
                </div>
              ) : scenariosLoading ? (
                <div className="flex items-center gap-2 rounded-md border border-dashed p-3">
                  <Loader2 className="size-4 animate-spin text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Loading scenarios...</span>
                </div>
              ) : (
                <div className="rounded-md border border-dashed p-3 text-center">
                  <Layers className="mx-auto mb-1 size-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">
                    {draft.dominio
                      ? 'No scenario pack available for this domain, or API is offline.'
                      : 'Select a domain first to see available scenarios.'}
                  </p>
                </div>
              )}
            </div>
          </div>
        )
      }

      case 5:
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 5: Privacy Settings</h3>
              <p className="text-xs text-muted-foreground">
                PII detection and anonymization configuration. Privacy score must be 0.0 for generated data to pass quality checks.
              </p>
            </div>
            <div className="flex items-center justify-between rounded-md border p-3">
              <div>
                <Label>PII Removed</Label>
                <p className="text-xs text-muted-foreground">Enable PII removal for this seed</p>
              </div>
              <Switch
                checked={draft.privacidad?.pii_eliminado ?? true}
                onCheckedChange={v => updatePrivacidad({ pii_eliminado: v })}
              />
            </div>
            <div className="space-y-2">
              <Label>Anonymization Method</Label>
              <Select
                value={draft.privacidad?.metodo_anonimizacion || 'presidio'}
                onValueChange={v => updatePrivacidad({ metodo_anonimizacion: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ANONYMIZATION_METHODS.map(m => (
                    <SelectItem key={m} value={m}>{m}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Confidence Level</Label>
                <span className="text-sm font-medium">
                  {(draft.privacidad?.nivel_confianza ?? 0.85).toFixed(2)}
                </span>
              </div>
              <Slider
                value={[draft.privacidad?.nivel_confianza ?? 0.85]}
                onValueChange={([v]) => updatePrivacidad({ nivel_confianza: v })}
                min={0}
                max={1}
                step={0.01}
              />
              <div className="flex justify-between text-[10px] text-muted-foreground">
                <span>0.00</span>
                <span>1.00</span>
              </div>
            </div>
          </div>
        )

      case 6:
        return (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Step 6: Review</h3>
            <div className="space-y-3 rounded-md border p-4">
              <div className="grid gap-2 text-sm sm:grid-cols-2">
                <div>
                  <span className="text-xs text-muted-foreground">Domain</span>
                  <p className="font-medium">{draft.dominio || '-'}</p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Language</span>
                  <p className="font-medium">{draft.idioma || '-'}</p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Tone</span>
                  <p className="font-medium">{draft.tono || '-'}</p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Turns</span>
                  <p className="font-medium">
                    {draft.pasos_turnos?.turnos_min ?? '-'} - {draft.pasos_turnos?.turnos_max ?? '-'}
                  </p>
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Objective</span>
                <p className="text-sm">{draft.objetivo || '-'}</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Roles</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {(draft.roles || []).map((r, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{r || '(empty)'}</Badge>
                  ))}
                  {(!draft.roles || draft.roles.length === 0) && <span className="text-xs text-muted-foreground">No roles defined</span>}
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Tags</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {(draft.etiquetas || []).map((t, i) => (
                    <Badge key={i} variant="secondary" className="text-[10px]">{t}</Badge>
                  ))}
                  {(!draft.etiquetas || draft.etiquetas.length === 0) && <span className="text-xs text-muted-foreground">No tags</span>}
                </div>
              </div>
              {/* Brand identity */}
              {(draft.parametros_factuales?.nombre_asistente || draft.parametros_factuales?.saludo_marca) && (
                <div className="grid gap-2 text-sm sm:grid-cols-2">
                  {draft.parametros_factuales?.nombre_asistente && (
                    <div>
                      <span className="text-xs text-muted-foreground">Assistant Name</span>
                      <p className="font-medium">{draft.parametros_factuales.nombre_asistente}</p>
                    </div>
                  )}
                  {draft.parametros_factuales?.saludo_marca && (
                    <div className="sm:col-span-2">
                      <span className="text-xs text-muted-foreground">Brand Greeting</span>
                      <p className="text-xs italic">&ldquo;{draft.parametros_factuales.saludo_marca}&rdquo;</p>
                    </div>
                  )}
                </div>
              )}
              {/* Tools */}
              {(draft.parametros_factuales?.herramientas || []).length > 0 && (
                <div>
                  <span className="text-xs text-muted-foreground">Tools</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {(draft.parametros_factuales?.herramientas || []).map((t, i) => (
                      <Badge key={i} variant="outline" className="font-mono text-[10px]">
                        <Wrench className="mr-0.5 size-2.5" />{t}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <span className="text-xs text-muted-foreground">Expected Flow</span>
                <div className="mt-1">
                  {(draft.pasos_turnos?.flujo_esperado || []).length > 0 ? (
                    <ol className="list-inside list-decimal text-xs">
                      {(draft.pasos_turnos?.flujo_esperado || []).map((f, i) => (
                        <li key={i}>{f || '(empty)'}</li>
                      ))}
                    </ol>
                  ) : (
                    <span className="text-xs text-muted-foreground">No steps</span>
                  )}
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Privacy</span>
                <p className="text-xs">
                  PII removed: {draft.privacidad?.pii_eliminado ? 'Yes' : 'No'} |
                  Method: {draft.privacidad?.metodo_anonimizacion || '-'} |
                  Confidence: {(draft.privacidad?.nivel_confianza ?? 0).toFixed(2)}
                </p>
              </div>
            </div>

            <Button type="button" variant="outline" size="sm" onClick={handleValidate}>
              <Check className="mr-1.5 size-4" /> Validate
            </Button>

            {validationErrors.length > 0 && (
              <div className="rounded-md border border-destructive/50 bg-destructive/5 p-3">
                <p className="mb-1 text-xs font-semibold text-destructive">Validation Errors:</p>
                <ul className="space-y-0.5">
                  {validationErrors.map((err, i) => (
                    <li key={i} className="text-xs text-destructive">{err}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )

      default:
        return null
    }
  }

  // ─── Empty state ───
  if (seeds.length === 0 && !createOpen) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Seed Library"
          description="Create and manage conversation seeds for synthetic data generation"
          actions={
            <div className="flex items-center gap-3">
              {renderSyncStatus()}
              {renderCreateDialog()}
            </div>
          }
        />
        {renderInfoBanner()}
        {renderSyncError()}
        <EmptyState
          icon={Sprout}
          title="No seeds yet"
          description="Create your first seed to define the structure and parameters for synthetic conversation generation."
          action={
            <Button size="sm" onClick={() => setCreateOpen(true)}>
              <Plus className="mr-1.5 size-4" /> Create Seed
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Seed Library"
        description={`${seeds.length} seeds${apiAvailable ? ' (synced with API)' : ' in local store'}`}
        actions={
          <div className="flex items-center gap-3">
            {renderSyncStatus()}
            {renderCreateDialog()}
          </div>
        }
      />

      {/* Info banner */}
      {renderInfoBanner()}

      {/* Sync error alert */}
      {renderSyncError()}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <SearchInput value={search} onChange={setSearch} placeholder="Search seeds..." className="w-64" />
        <Select value={domainFilter} onValueChange={setDomainFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Domain" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Domains</SelectItem>
            {SUPPORTED_DOMAINS.map(d => (
              <SelectItem key={d} value={d}>{d.split('.').pop()}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-1.5">
              <ArrowUpDown className="size-3" />
              Sort
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={() => setSortBy('newest')}>
              {sortBy === 'newest' && <Check className="size-3" />} Newest first
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortBy('oldest')}>
              {sortBy === 'oldest' && <Check className="size-3" />} Oldest first
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortBy('name')}>
              {sortBy === 'name' && <Check className="size-3" />} Name
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortBy('runs')}>
              {sortBy === 'runs' && <Check className="size-3" />} Most runs
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortBy('quality')}>
              {sortBy === 'quality' && <Check className="size-3" />} Highest quality
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortBy('favorites')}>
              {sortBy === 'favorites' && <Check className="size-3" />} Favorites first
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <span className="ml-auto text-xs text-muted-foreground">{filtered.length} results</span>
      </div>

      {/* Seed cards grid */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={Sprout}
          title="No seeds match filters"
          description="Try adjusting your search or filter criteria."
          action={
            <Button variant="outline" size="sm" onClick={() => { setSearch(''); setDomainFilter('all') }}>
              Clear filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(seed => {
            const runs = seedStats.runCounts[seed.seed_id] || 0
            const avgQ = seedStats.avgQuality[seed.seed_id]
            const isFav = favorites.has(seed.seed_id)
            const author = (seed.parametros_factuales?.metadata?.author as string) || 'UNCASE'
            const tools = seed.parametros_factuales?.herramientas || []

            return (
              <Card
                key={seed.seed_id}
                className="cursor-pointer transition-colors hover:bg-muted/50"
                onClick={() => { setSelectedSeed(seed); setGenerateResult(null); setDetailOpen(true) }}
              >
                <CardContent className="space-y-2.5 p-4">
                  {/* Row 1: Favorite + ID + Domain badge */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={e => toggleFavorite(e, seed.seed_id)}
                      className="shrink-0 text-muted-foreground/40 transition-colors hover:text-foreground"
                    >
                      <Star className={cn('size-3.5', isFav && 'fill-foreground text-foreground')} />
                    </button>
                    <span className="min-w-0 truncate font-mono text-xs font-semibold">
                      {seed.seed_id}
                    </span>
                    <Badge variant="secondary" className="ml-auto shrink-0 text-[10px]">
                      {DOMAIN_LABELS[seed.dominio] || seed.dominio.split('.').pop()}
                    </Badge>
                  </div>

                  {/* Row 2: Objective */}
                  <p className="line-clamp-2 text-[12px] leading-snug text-muted-foreground">
                    {seed.objetivo}
                  </p>

                  {/* Row 3: Roles + Tags compact */}
                  <div className="flex flex-wrap gap-1">
                    {seed.roles.map(role => (
                      <Badge key={role} variant="outline" className="font-mono text-[9px]">
                        {role}
                      </Badge>
                    ))}
                    {seed.etiquetas.slice(0, 3).map(tag => (
                      <Badge key={tag} variant="secondary" className="text-[9px] font-normal">
                        {tag}
                      </Badge>
                    ))}
                    {seed.etiquetas.length > 3 && (
                      <span className="text-[9px] text-muted-foreground">+{seed.etiquetas.length - 3}</span>
                    )}
                  </div>

                  {/* Row 4: Technical specs */}
                  <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                    <span>{seed.pasos_turnos.turnos_min}-{seed.pasos_turnos.turnos_max} turns</span>
                    <span className="text-muted-foreground/30">|</span>
                    <span>{seed.tono}</span>
                    <span className="text-muted-foreground/30">|</span>
                    <span className="uppercase">{seed.idioma}</span>
                    {tools.length > 0 && (
                      <>
                        <span className="text-muted-foreground/30">|</span>
                        <span className="flex items-center gap-0.5">
                          <Wrench className="size-2.5" /> {tools.length}
                        </span>
                      </>
                    )}
                  </div>

                  {/* Row 5: Stats footer */}
                  <div className="flex items-center gap-3 border-t pt-2 text-[10px] text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Play className="size-2.5" />
                      <span className="font-medium text-foreground">{runs}</span> runs
                    </span>
                    {avgQ !== undefined && (
                      <span className="flex items-center gap-1">
                        <BarChart3 className="size-2.5" />
                        Avg <span className="font-mono font-medium text-foreground">{avgQ.toFixed(2)}</span>
                      </span>
                    )}
                    <span className="ml-auto">by <span className="font-medium">{author}</span></span>
                  </div>

                  {/* Row 6: Date */}
                  <div className="text-[10px] text-muted-foreground">
                    Created {timeAgo(seed.created_at)}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Detail dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-sm font-medium">
              Seed: {selectedSeed?.seed_id.slice(0, 20)}...
            </DialogTitle>
            <DialogDescription>
              Full seed schema details
            </DialogDescription>
          </DialogHeader>

          {selectedSeed && (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="text-xs">
                  {selectedSeed.dominio}
                </Badge>
                <Badge variant="outline" className="text-xs">{selectedSeed.idioma}</Badge>
                <Badge variant="outline" className="text-xs">{selectedSeed.tono}</Badge>
              </div>
              <JsonViewer data={selectedSeed} maxHeight="400px" />
            </div>
          )}

          {generateResult && selectedSeed && generating === null && (
            <div className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-xs text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-300">
              {generateResult}
            </div>
          )}

          <DialogFooter className="flex-row justify-between gap-2 sm:justify-between">
            <Button
              variant="destructive"
              size="sm"
              onClick={() => selectedSeed && handleDelete(selectedSeed.seed_id)}
            >
              <Trash2 className="mr-1.5 size-4" /> Delete Seed
            </Button>
            <div className="flex gap-2">
              <Button
                variant="default"
                size="sm"
                disabled={!apiAvailable || generating === selectedSeed?.seed_id}
                onClick={() => selectedSeed && handleGenerateAndEvaluate(selectedSeed)}
              >
                {generating === selectedSeed?.seed_id ? (
                  <>
                    <Loader2 className="mr-1.5 size-4 animate-spin" /> Generating...
                  </>
                ) : (
                  <>
                    <Rocket className="mr-1.5 size-4" /> Generate & Evaluate
                  </>
                )}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setDetailOpen(false)}>
                Close
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
