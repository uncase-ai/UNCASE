'use client'

import { useEffect, useMemo, useState } from 'react'

import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  ChevronDown,
  Cloud,
  CloudOff,
  Filter,
  Layers,
  Loader2,
  RefreshCw,
  Sparkles,
  Target,
  Wrench,
  X,
  Zap
} from 'lucide-react'

import type { ScenarioPackDetail, ScenarioPackSummary, ScenarioTemplate, SkillLevel } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { fetchScenarioPack, fetchScenarioPacks } from '@/lib/api/scenarios'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger
} from '@/components/ui/collapsible'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { SearchInput } from '../search-input'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'

// ─── Domain display names ───
const DOMAIN_LABELS: Record<string, { label: string; icon: string }> = {
  'automotive.sales': { label: 'Automotive Sales', icon: '🚗' },
  'medical.consultation': { label: 'Medical Consultation', icon: '🏥' },
  'finance.advisory': { label: 'Finance Advisory', icon: '💰' },
  'legal.advisory': { label: 'Legal Advisory', icon: '⚖️' },
  'industrial.support': { label: 'Industrial Support', icon: '🏭' },
  'education.tutoring': { label: 'Education Tutoring', icon: '📚' }
}

const SKILL_COLORS: Record<SkillLevel, string> = {
  basic: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  intermediate: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
  advanced: 'bg-rose-500/10 text-rose-700 dark:text-rose-400'
}

export function ScenariosPage() {
  const [packs, setPacks] = useState<ScenarioPackSummary[]>([])
  const [selectedPack, setSelectedPack] = useState<ScenarioPackDetail | null>(null)
  const [selectedScenario, setSelectedScenario] = useState<ScenarioTemplate | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingPack, setLoadingPack] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)

  // Filters
  const [search, setSearch] = useState('')
  const [skillFilter, setSkillFilter] = useState<string>('all')
  const [edgeCaseFilter, setEdgeCaseFilter] = useState<string>('all')

  // Check API and load packs
  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError(null)

      try {
        const health = await checkApiHealth()

        if (cancelled) return
        setApiOnline(health.ok)

        if (!health.ok) {
          setError('API is offline. Scenario packs require a running backend.')
          setLoading(false)

          return
        }

        const res = await fetchScenarioPacks()

        if (cancelled) return

        if (res.data) {
          setPacks(res.data.packs)
        } else {
          setError(res.error ?? 'Failed to load scenario packs')
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [])

  // Load full pack when selected
  const handleSelectDomain = async (domain: string) => {
    setLoadingPack(true)
    setSelectedPack(null)
    setSearch('')
    setSkillFilter('all')
    setEdgeCaseFilter('all')

    try {
      const res = await fetchScenarioPack(domain)

      if (res.data) {
        setSelectedPack(res.data)
      } else {
        setError(res.error ?? 'Failed to load pack details')
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load pack')
    } finally {
      setLoadingPack(false)
    }
  }

  // Filter scenarios
  const filteredScenarios = useMemo(() => {
    if (!selectedPack) return []

    let result = [...selectedPack.scenarios]

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        s =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.intent.toLowerCase().includes(q) ||
          s.tags.some(t => t.toLowerCase().includes(q))
      )
    }

    if (skillFilter !== 'all') {
      result = result.filter(s => s.skill_level === skillFilter)
    }

    if (edgeCaseFilter !== 'all') {
      result = result.filter(s => (edgeCaseFilter === 'edge' ? s.edge_case : !s.edge_case))
    }

    return result
  }, [selectedPack, search, skillFilter, edgeCaseFilter])

  // Summary stats
  const totalScenarios = packs.reduce((sum, p) => sum + p.scenario_count, 0)
  const totalEdgeCases = packs.reduce((sum, p) => sum + p.edge_case_count, 0)

  // Loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Scenario Packs" description="Loading scenario packs..." />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  // Error / offline
  if (packs.length === 0 && !selectedPack) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Scenario Packs"
          description="Curated conversation archetypes for synthetic data generation"
          actions={
            <StatusBadge variant={apiOnline ? 'success' : 'error'} className="text-[10px]">
              {apiOnline ? <Cloud className="mr-1 size-3" /> : <CloudOff className="mr-1 size-3" />}
              {apiOnline ? 'API' : 'Offline'}
            </StatusBadge>
          }
        />
        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}
        <EmptyState
          icon={Layers}
          title="No scenario packs available"
          description="Scenario packs are loaded from the backend API. Make sure the API is running and has the scenario packs registered."
          action={
            <Button variant="outline" onClick={() => window.location.reload()}>
              <RefreshCw className="mr-1.5 size-4" /> Retry
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Scenario Packs"
        description={`${packs.length} domain packs with ${totalScenarios} scenario templates across ${SUPPORTED_DOMAINS.length} industries`}
        actions={
          <StatusBadge variant={apiOnline ? 'success' : 'error'} className="text-[10px]">
            {apiOnline ? <Cloud className="mr-1 size-3" /> : <CloudOff className="mr-1 size-3" />}
            {apiOnline ? 'API' : 'Offline'}
          </StatusBadge>
        }
      />

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Summary stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard title="Domain Packs" value={packs.length} icon={Layers} description="Industry verticals" />
        <StatsCard
          title="Total Scenarios"
          value={totalScenarios}
          icon={BookOpen}
          description="Conversation archetypes"
        />
        <StatsCard title="Edge Cases" value={totalEdgeCases} icon={AlertTriangle} description="Stress-test scenarios" />
        <StatsCard
          title="Avg per Pack"
          value={packs.length > 0 ? Math.round(totalScenarios / packs.length) : 0}
          icon={Target}
          description="Scenarios per domain"
        />
      </div>

      {/* Pack grid */}
      <div>
        <h3 className="mb-3 text-sm font-semibold">Select a Domain Pack</h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {packs.map(pack => {
            const info = DOMAIN_LABELS[pack.domain] ?? { label: pack.domain, icon: '📋' }
            const isSelected = selectedPack?.domain === pack.domain

            return (
              <Card
                key={pack.id}
                className={cn(
                  'cursor-pointer transition-all hover:shadow-md',
                  isSelected && 'ring-2 ring-primary'
                )}
                onClick={() => handleSelectDomain(pack.domain)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{info.icon}</span>
                      <CardTitle className="text-sm">{info.label}</CardTitle>
                    </div>
                    <Badge variant="secondary" className="text-[10px]">
                      v{pack.version}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">{pack.description}</CardDescription>
                </CardHeader>
                <CardContent className="pb-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        <BookOpen className="size-3" />
                        {pack.scenario_count} scenarios
                      </span>
                      <span className="flex items-center gap-1">
                        <AlertTriangle className="size-3" />
                        {pack.edge_case_count} edge cases
                      </span>
                    </div>
                    <ArrowRight className="size-3.5" />
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {pack.skill_levels.map(level => (
                      <Badge
                        key={level}
                        variant="outline"
                        className={cn('text-[10px]', SKILL_COLORS[level as SkillLevel])}
                      >
                        {level}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Selected pack detail */}
      {loadingPack && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="size-5 animate-spin text-muted-foreground" />
          <span className="ml-2 text-sm text-muted-foreground">Loading pack...</span>
        </div>
      )}

      {selectedPack && !loadingPack && (
        <div className="space-y-3">
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <Filter className="size-4 text-muted-foreground" />
            <SearchInput
              value={search}
              onValueChange={setSearch}
              placeholder="Search scenarios..."
              className="w-52"
            />
            <Select value={skillFilter} onValueChange={setSkillFilter}>
              <SelectTrigger className="w-36">
                <SelectValue placeholder="Skill level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All levels</SelectItem>
                <SelectItem value="basic">Basic</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
            <Select value={edgeCaseFilter} onValueChange={setEdgeCaseFilter}>
              <SelectTrigger className="w-36">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All types</SelectItem>
                <SelectItem value="happy">Happy path</SelectItem>
                <SelectItem value="edge">Edge cases</SelectItem>
              </SelectContent>
            </Select>
            {(search || skillFilter !== 'all' || edgeCaseFilter !== 'all') && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch('')
                  setSkillFilter('all')
                  setEdgeCaseFilter('all')
                }}
              >
                <X className="mr-1 size-3" /> Clear
              </Button>
            )}
            <span className="ml-auto text-xs text-muted-foreground">
              {filteredScenarios.length} of {selectedPack.scenario_count} scenarios
            </span>
          </div>

          {/* Scenario cards */}
          <div className="grid gap-2">
            {filteredScenarios.map(scenario => (
              <ScenarioCard
                key={scenario.name}
                scenario={scenario}
                onSelect={() => setSelectedScenario(scenario)}
              />
            ))}
            {filteredScenarios.length === 0 && (
              <div className="rounded-lg border border-dashed py-8 text-center text-sm text-muted-foreground">
                No scenarios match your filters
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scenario detail dialog */}
      <ScenarioDetailDialog
        scenario={selectedScenario}
        onClose={() => setSelectedScenario(null)}
      />
    </div>
  )
}

// ─── Scenario Card ───

function ScenarioCard({
  scenario,
  onSelect
}: {
  scenario: ScenarioTemplate
  onSelect: () => void
}) {
  const weightPercent = Math.min(Math.round((scenario.weight / 10) * 100), 100)

  return (
    <Card className="cursor-pointer transition-all hover:shadow-sm" onClick={onSelect}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-medium">{formatName(scenario.name)}</h4>
              <Badge
                variant="outline"
                className={cn('text-[10px]', SKILL_COLORS[scenario.skill_level])}
              >
                {scenario.skill_level}
              </Badge>
              {scenario.edge_case && (
                <Badge variant="outline" className="text-[10px] bg-orange-500/10 text-orange-700 dark:text-orange-400">
                  <AlertTriangle className="mr-0.5 size-2.5" /> edge case
                </Badge>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{scenario.description}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {scenario.expected_tool_sequence.length > 0 && (
                <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                  <Wrench className="size-3" />
                  {scenario.expected_tool_sequence.length} tool{scenario.expected_tool_sequence.length > 1 ? 's' : ''}
                </span>
              )}
              <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                <Zap className="size-3" />
                {scenario.flow_steps.length} steps
              </span>
              <div className="flex flex-wrap gap-1">
                {scenario.tags.slice(0, 3).map(tag => (
                  <Badge key={tag} variant="secondary" className="text-[10px] px-1.5">
                    {tag}
                  </Badge>
                ))}
                {scenario.tags.length > 3 && (
                  <Badge variant="secondary" className="text-[10px] px-1.5">
                    +{scenario.tags.length - 3}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 text-right">
            <span className="text-[10px] text-muted-foreground">Weight</span>
            <div className="flex items-center gap-1.5">
              <Progress value={weightPercent} className="h-1.5 w-12" />
              <span className="text-xs font-mono font-medium">{scenario.weight}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Scenario Detail Dialog ───

function ScenarioDetailDialog({
  scenario,
  onClose
}: {
  scenario: ScenarioTemplate | null
  onClose: () => void
}) {
  if (!scenario) return null

  return (
    <Dialog open={!!scenario} onOpenChange={open => !open && onClose()}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <DialogTitle className="text-base">{formatName(scenario.name)}</DialogTitle>
            <Badge
              variant="outline"
              className={cn('text-[10px]', SKILL_COLORS[scenario.skill_level])}
            >
              {scenario.skill_level}
            </Badge>
            {scenario.edge_case && (
              <Badge variant="outline" className="text-[10px] bg-orange-500/10 text-orange-700 dark:text-orange-400">
                edge case
              </Badge>
            )}
          </div>
          <DialogDescription className="text-xs">{scenario.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Intent */}
          <div>
            <h5 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Intent</h5>
            <p className="text-sm">{scenario.intent}</p>
          </div>

          {/* Flow Steps */}
          <div>
            <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Conversation Flow ({scenario.flow_steps.length} steps)
            </h5>
            <ol className="space-y-1.5">
              {scenario.flow_steps.map((step, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-medium">
                    {i + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Tool Sequence */}
          {scenario.expected_tool_sequence.length > 0 && (
            <div>
              <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Expected Tool Sequence
              </h5>
              <div className="flex flex-wrap items-center gap-1.5">
                {scenario.expected_tool_sequence.map((tool, i) => (
                  <span key={i} className="flex items-center gap-1">
                    <Badge variant="outline" className="font-mono text-[11px]">
                      <Wrench className="mr-1 size-3" />
                      {tool}
                    </Badge>
                    {i < scenario.expected_tool_sequence.length - 1 && (
                      <ArrowRight className="size-3 text-muted-foreground" />
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-3 rounded-lg bg-muted/50 p-3">
            <div>
              <span className="text-[10px] font-medium text-muted-foreground">Domain</span>
              <p className="text-xs font-medium">{scenario.domain}</p>
            </div>
            <div>
              <span className="text-[10px] font-medium text-muted-foreground">Weight</span>
              <p className="text-xs font-medium">{scenario.weight}</p>
            </div>
            <div>
              <span className="text-[10px] font-medium text-muted-foreground">Skill Level</span>
              <p className="text-xs font-medium capitalize">{scenario.skill_level}</p>
            </div>
            <div>
              <span className="text-[10px] font-medium text-muted-foreground">Edge Case</span>
              <p className="text-xs font-medium">{scenario.edge_case ? 'Yes' : 'No'}</p>
            </div>
          </div>

          {/* Tags */}
          <div>
            <h5 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Tags</h5>
            <div className="flex flex-wrap gap-1">
              {scenario.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="text-[10px]">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── Helpers ───

function formatName(name: string): string {
  return name
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}
