'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  AlertTriangle,
  ArrowUpDown,
  BarChart3,
  Check,
  Cloud,
  CloudOff,
  Copy,
  Info,
  Play,
  Plus,
  RefreshCw,
  Sparkles,
  Sprout,
  Star,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, QualityReport, SeedSchema, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { fetchSeeds } from '@/lib/api/seeds'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { EmptyState } from '../empty-state'
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

  const router = useRouter()

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

  const [seedStats] = useState(() => computeSeedStats())

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
                onClick={() => router.push(`/dashboard/pipeline/seeds/${seed.seed_id}`)}
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

    </div>
  )
}
