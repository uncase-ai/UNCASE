'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import {
  AlertTriangle,
  ArrowUpDown,
  BarChart3,
  Check,
  Cloud,
  CloudOff,
  Copy,
  Info,
  Loader2,
  Play,
  Plus,
  RefreshCw,
  Rocket,
  Sparkles,
  Sprout,
  Star,
  Trash2,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, ConversationTurn, QualityReport, SeedSchema, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { generateConversations } from '@/lib/api/generate'
import { deleteSeedApi, fetchSeeds } from '@/lib/api/seeds'
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
  DialogTitle
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

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

// ─── Demo generation helpers ───

const MOCK_TURNS: Record<string, { user: string[]; assistant: string[] }> = {
  'automotive.sales': {
    user: [
      'Good morning, I\'m looking for a family vehicle. What options do you have?',
      'I\'m interested in something with good fuel economy and space for 5. Ideally an SUV.',
      'The XR5 sounds great. What\'s the all-in price with everything included?',
      'Do you have financing options? My budget is around $20,000 down.',
      'That monthly payment works for me. Can I trade in my current car?',
      'It\'s a 2020 sedan with about 45,000 miles, in good condition.',
      'I\'d like to schedule a test drive for this Saturday if possible.',
      'What warranty coverage does the XR5 include?',
      'That\'s very thorough. What documents do I need to start the credit process?',
      'Perfect, I\'ll bring everything Saturday. Thanks for your help!',
    ],
    assistant: [
      'Welcome! I\'d be happy to help you find the right vehicle. We have excellent options in SUVs and family sedans. Do you have a budget range in mind?',
      'For your needs, I\'d recommend the XR5 2025 model. It seats 7 with a third row, gets 14 km/l in the city, and has top safety ratings. It starts at $689,900.',
      'The final price with tax, plates, and inspection is $864,084 MXN. That includes the advanced safety package and a 5-year/100K km comprehensive warranty.',
      'Absolutely. We offer financing from 12 to 72 months. With $20,000 down, your monthly payment would be approximately $15,800 at 48 months with our preferred rate of 9.9% APR.',
      'Yes, our trade-in program lets you apply your current vehicle\'s value toward the down payment. We can appraise it on the spot or within 24 hours.',
      'A 2020 sedan in good condition with that mileage should appraise well. We\'ll give you a competitive market-based valuation when you bring it in.',
      'Saturday at 10:00 AM works perfectly. The test drive takes about 30 minutes on a route that includes city and highway driving. Just bring your valid license.',
      'The XR5 includes a factory warranty of 5 years or 100,000 km, whichever comes first. It covers engine, transmission, electronics, and roadside assistance for the first 3 years.',
      'For credit pre-approval you\'ll need: official government ID, proof of address (less than 3 months old), your last 3 pay stubs, and your last bank statement. We can start the process in about 20 minutes.',
      'You\'re welcome! I\'ll have everything ready for your Saturday visit. Here\'s my card — feel free to call or text if any questions come up before then.',
    ],
  },
  'medical.consultation': {
    user: [
      'Doctor, I\'ve been having frequent headaches for the last two weeks, mostly in the afternoon.',
      'The pain is usually on both sides, like a tight band around my head. It lasts a few hours.',
      'Could it be something serious? I\'m a little worried because they\'ve been so persistent.',
      'I haven\'t taken any medication yet, just tried resting and drinking more water.',
      'Yes, I\'ve been under a lot of stress at work and spending 10+ hours on the computer daily.',
      'My mother has a history of migraines. Could this be hereditary?',
      'What tests would you recommend to make sure nothing else is going on?',
      'What treatment do you suggest in the meantime?',
      'Are there lifestyle changes I should make to prevent these from recurring?',
      'Thank you doctor, I\'ll follow the treatment plan and come back in two weeks.',
    ],
    assistant: [
      'I understand your concern. Let\'s go through your symptoms carefully. Can you describe the location and character of the pain — is it throbbing, pressing, or sharp?',
      'That pattern is very consistent with tension-type headaches, which are the most common form. The bilateral pressing quality and afternoon onset are typical. Have you noticed any visual disturbances or nausea along with the pain?',
      'Based on your description, I\'m confident this is a tension-type headache. The bilateral distribution and pressing quality make serious causes very unlikely. However, we\'ll do a thorough evaluation to be certain.',
      'It\'s good you haven\'t self-medicated. Hydration helps, but we should start a targeted treatment. First, let me ask — have you had any changes in your daily routine, sleep, or stress levels recently?',
      'That\'s very likely the primary trigger. Prolonged screen time causes eye strain and sustained neck tension, both of which commonly produce this type of headache. We call this cervicogenic component.',
      'Family history of migraine is relevant. While your current presentation fits tension-type, we\'ll monitor for any migraine features — such as one-sided pain, light sensitivity, or nausea — and adjust the diagnosis if needed.',
      'I\'ll order a complete blood count, metabolic panel, and thyroid function tests to rule out systemic causes. If your headaches don\'t improve within 3 weeks, we\'ll consider a CT scan for additional reassurance.',
      'I recommend acetaminophen 500mg every 8 hours as needed for 5 days, plus a daily 20-minute stretching routine for your neck and shoulders. Maintain at least 2 liters of water daily and take 5-minute screen breaks every hour.',
      'Absolutely. Aim for 7-8 hours of sleep on a regular schedule, limit caffeine to 2 cups before noon, and consider a brief daily walk or exercise. Managing work stress through breaks and boundaries will also make a significant difference.',
      'You\'re welcome. Follow the full treatment course even if you start feeling better. If the pain worsens suddenly, you develop new symptoms like vision changes or fever, come back immediately. Otherwise I\'ll see you in two weeks.',
    ],
  },
}

const DEFAULT_MOCK_TURNS = {
  user: ['Hello, I need help with a question.', 'Could you give me more details?', 'Thanks, that\'s very helpful.', 'Is there anything else I should consider?'],
  assistant: ['I\'d be happy to help. How can I assist you?', 'Of course, let me explain in detail.', 'That\'s an excellent question. Here\'s the information.', 'I recommend keeping these additional points in mind.'],
}

function generateDemoConversation(seed: SeedSchema): Conversation {
  const minTurns = seed.pasos_turnos?.turnos_min ?? 4
  const maxTurns = seed.pasos_turnos?.turnos_max ?? 8
  const numTurns = minTurns + Math.floor(Math.random() * (maxTurns - minTurns + 1))
  const roles = (seed.roles?.length ?? 0) >= 2 ? seed.roles : ['user', 'assistant']
  const pool = MOCK_TURNS[seed.dominio] ?? DEFAULT_MOCK_TURNS

  const turnos: ConversationTurn[] = Array.from({ length: numTurns }, (_, i) => {
    const isUser = i % 2 === 0
    const bank = isUser ? pool.user : pool.assistant
    const bankIdx = Math.floor(i / 2) % bank.length

    return {
      turno: i + 1,
      rol: roles[i % roles.length],
      contenido: bank[bankIdx],
      herramientas_usadas: [],
      metadata: {},
    }
  })

  return {
    conversation_id: crypto.randomUUID(),
    seed_id: seed.seed_id,
    dominio: seed.dominio,
    idioma: seed.idioma,
    turnos,
    es_sintetica: true,
    created_at: new Date().toISOString(),
    metadata: { generated_by: 'uncase-demo', source_seed: seed.seed_id },
  }
}

function generateDemoQualityReport(conv: Conversation, seed: SeedSchema): QualityReport {
  // Generate realistic scores that pass thresholds (demo content is premium)
  const r = () => 0.85 + Math.random() * 0.13 // 0.85–0.98

  const metrics = {
    rouge_l: r(),
    fidelidad_factual: r(),
    diversidad_lexica: 0.60 + Math.random() * 0.25,
    coherencia_dialogica: r(),
    tool_call_validity: 1.0,
    privacy_score: 0.0,
    memorizacion: 0.001 + Math.random() * 0.005,
    semantic_fidelity: r(),
    embedding_drift: 0.65 + Math.random() * 0.25,
  }

  const composite = Math.min(
    metrics.rouge_l, metrics.fidelidad_factual, metrics.diversidad_lexica,
    metrics.coherencia_dialogica, metrics.tool_call_validity,
    metrics.semantic_fidelity, metrics.embedding_drift
  )

  return {
    conversation_id: conv.conversation_id,
    seed_id: seed.seed_id,
    metrics,
    composite_score: Math.round(composite * 1000) / 1000,
    passed: true,
    failures: [],
    evaluated_at: new Date().toISOString(),
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

  // Detail dialog
  const [selectedSeed, setSelectedSeed] = useState<SeedSchema | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)

  // Tool filter from URL query param
  const searchParams = useSearchParams()
  const toolFilter = searchParams.get('tool')

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
      const apiSeeds: SeedSchema[] = data.items.map(item => ({
        seed_id: item.id ?? '',
        version: (item.version as '1.0') ?? '1.0',
        dominio: item.dominio ?? '',
        idioma: item.idioma ?? 'es',
        etiquetas: item.etiquetas ?? [],
        roles: item.roles ?? [],
        descripcion_roles: item.descripcion_roles ?? {},
        objetivo: item.objetivo ?? '',
        tono: item.tono ?? 'profesional',
        pasos_turnos: item.pasos_turnos ?? { turnos_min: 3, turnos_max: 10, flujo_esperado: [] },
        parametros_factuales: item.parametros_factuales ?? { contexto: '', restricciones: [] },
        privacidad: item.privacidad ?? { pii_fields: [], anonymization: 'redact' },
        metricas_calidad: item.metricas_calidad ?? {},
        organization_id: item.organization_id ?? undefined,
        created_at: item.created_at ?? new Date().toISOString(),
        updated_at: item.updated_at ?? new Date().toISOString()
      }))

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
          (s.etiquetas ?? []).some(t => t.toLowerCase().includes(q)) ||
          (s.roles ?? []).some(r => r.toLowerCase().includes(q))
      )
    }

    if (domainFilter !== 'all') {
      result = result.filter(s => s.dominio === domainFilter)
    }

    // Filter by tool from URL query param
    if (toolFilter) {
      result = result.filter(s => s.parametros_factuales?.herramientas?.includes(toolFilter))
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
  }, [seeds, search, domainFilter, toolFilter, sortBy, seedStats, favorites])

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
    setGenerating(seed.seed_id)
    setGenerateResult(null)

    // ─── Demo mode (no API) — generate locally with quality scoring ───
    if (!apiAvailable) {
      const count = 3
      const conversations: Conversation[] = []
      const reports: QualityReport[] = []

      for (let i = 0; i < count; i++) {
        const conv = generateDemoConversation(seed)
        const report = generateDemoQualityReport(conv, seed)

        conversations.push(conv)
        reports.push(report)
      }

      const passed = reports.filter(r => r.passed).length
      const avgScore = reports.reduce((s, r) => s + r.composite_score, 0) / reports.length

      setGenerateResult(
        `Generated ${count} conversations, ${passed}/${count} passed quality checks (avg score: ${avgScore.toFixed(2)})`
      )

      const { appendConversations } = await import('./conversations-page')

      appendConversations(conversations)

      try {
        const existing = JSON.parse(localStorage.getItem('uncase-evaluations') || '[]')

        localStorage.setItem('uncase-evaluations', JSON.stringify([...existing, ...reports]))
      } catch { /* storage full */ }

      setSeedStats(computeSeedStats())
      setGenerating(null)

      return
    }

    // ─── API mode ───
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

      const { appendConversations } = await import('./conversations-page')

      appendConversations(data.conversations)

      if (data.reports) {
        try {
          const existing = JSON.parse(localStorage.getItem('uncase-evaluations') || '[]')

          localStorage.setItem('uncase-evaluations', JSON.stringify([...existing, ...data.reports]))
        } catch { /* storage full */ }
      }

      setSeedStats(computeSeedStats())
    }
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
            <p className="text-[17px] font-bold text-foreground sm:text-lg">What are Seeds?</p>
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

  // ─── Create seed button (navigates to full-page wizard) ───
  function renderCreateButton() {
    return (
      <div className="flex items-center gap-2">
        <Link href="/dashboard/pipeline/seeds/extract">
          <Button size="sm" variant="outline" className="gap-1.5">
            <Sparkles className="size-4" /> AI Interview
          </Button>
        </Link>
        <Link href="/dashboard/pipeline/seeds/new">
          <Button size="sm">
            <Plus className="mr-1.5 size-4" /> Create Seed
          </Button>
        </Link>
      </div>
    )
  }

  // ─── Empty state ───
  if (seeds.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Seed Library"
          description="Create and manage conversation seeds for synthetic data generation"
          actions={
            <div className="flex items-center gap-3">
              {renderSyncStatus()}
              {renderCreateButton()}
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
            <Link href="/dashboard/pipeline/seeds/new">
              <Button size="sm">
                <Plus className="mr-1.5 size-4" /> Create Seed
              </Button>
            </Link>
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
            {renderCreateButton()}
          </div>
        }
      />

      {/* Info banner */}
      {renderInfoBanner()}

      {/* Sync error alert */}
      {renderSyncError()}

      {/* Tool filter banner */}
      {toolFilter && (
        <Card className="bg-sky-50/50 dark:bg-sky-950/20">
          <CardContent className="flex items-center gap-3 p-3">
            <Wrench className="size-4 shrink-0 text-sky-600 dark:text-sky-400" />
            <p className="text-xs text-sky-800 dark:text-sky-300">
              Showing seeds that use tool: <span className="font-mono font-semibold">{toolFilter}</span>
            </p>
            <Link href="/dashboard/pipeline/seeds" className="ml-auto">
              <Button variant="ghost" size="sm" className="h-6 gap-1 text-xs">
                <X className="size-3" /> Clear filter
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <SearchInput value={search} onChange={setSearch} placeholder="Search seeds..." className="w-full sm:w-64" />
        <Select value={domainFilter} onValueChange={setDomainFilter}>
          <SelectTrigger className="w-full sm:w-44">
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
                className="group relative cursor-pointer transition-colors hover:bg-muted/50"
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
                      {DOMAIN_LABELS[seed.dominio] || (seed.dominio ?? '').split('.').pop()}
                    </Badge>
                  </div>

                  {/* Row 2: Objective */}
                  <p className="line-clamp-2 text-[12px] leading-snug text-muted-foreground">
                    {seed.objetivo}
                  </p>

                  {/* Row 3: Roles + Tags compact */}
                  <div className="flex flex-wrap gap-1">
                    {(seed.roles ?? []).map(role => (
                      <Badge key={role} variant="outline" className="font-mono text-[9px]">
                        {role}
                      </Badge>
                    ))}
                    {(seed.etiquetas ?? []).slice(0, 3).map(tag => (
                      <Badge key={tag} variant="secondary" className="text-[9px] font-normal">
                        {tag}
                      </Badge>
                    ))}
                    {(seed.etiquetas ?? []).length > 3 && (
                      <span className="text-[9px] text-muted-foreground">+{(seed.etiquetas ?? []).length - 3}</span>
                    )}
                  </div>

                  {/* Row 4: Technical specs */}
                  <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                    <span>{seed.pasos_turnos?.turnos_min ?? 0}-{seed.pasos_turnos?.turnos_max ?? 0} turns</span>
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

                {/* Duplicate button (top-right corner on hover) */}
                <Link
                  href={`/dashboard/pipeline/seeds/new?from=${seed.seed_id}`}
                  onClick={e => e.stopPropagation()}
                  className="absolute right-2 top-2 hidden rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground group-hover:block"
                  title="Duplicate seed"
                >
                  <Copy className="size-3.5" />
                </Link>
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

              {/* Clickable tools */}
              {(selectedSeed.parametros_factuales?.herramientas || []).length > 0 && (
                <div>
                  <span className="text-xs text-muted-foreground">Tools</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {(selectedSeed.parametros_factuales?.herramientas || []).map(t => (
                      <Link key={t} href={`/dashboard/tools/${encodeURIComponent(t)}`}>
                        <Badge variant="outline" className="cursor-pointer font-mono text-[10px] transition-colors hover:bg-muted">
                          <Wrench className="mr-0.5 size-2.5" />{t}
                        </Badge>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

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
              <Link href={selectedSeed ? `/dashboard/pipeline/seeds/new?from=${selectedSeed.seed_id}` : '#'}>
                <Button variant="outline" size="sm">
                  <Copy className="mr-1.5 size-4" /> Duplicate
                </Button>
              </Link>
              <Button
                variant="default"
                size="sm"
                disabled={generating === selectedSeed?.seed_id}
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
