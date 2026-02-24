'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Check,
  Cloud,
  CloudOff,
  HelpCircle,
  Info,
  Plus,
  RefreshCw,
  Sprout,
  Trash2,
  X
} from 'lucide-react'

import type { SeedSchema } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { createEmptySeed, createSeedApi, deleteSeedApi, fetchSeeds, validateSeed } from '@/lib/api/seeds'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
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

// ─── Domain Colors — neutral palette ───
const DOMAIN_COLORS: Record<string, string> = {
  'automotive.sales': '',
  'medical.consultation': '',
  'legal.advisory': '',
  'finance.advisory': '',
  'industrial.support': '',
  'education.tutoring': ''
}

const TONES = ['profesional', 'informal', 'tecnico', 'empatico'] as const
const LANGUAGES = ['es', 'en'] as const
const ANONYMIZATION_METHODS = ['presidio', 'regex', 'spacy', 'manual', 'none'] as const
const TOTAL_STEPS = 6

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
        await loadFromApi()
      }
    }

    init()

    return () => { cancelled = true }
  }, [loadFromApi])

  // ─── Filtering ───
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

    return result
  }, [seeds, search, domainFilter])

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

    const newSeed: SeedSchema = {
      ...(draft as SeedSchema),
      seed_id: crypto.randomUUID().replace(/-/g, ''),
      created_at: now,
      updated_at: now
    }

    // Try backend first
    if (apiAvailable) {
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
        metricas_calidad: newSeed.metricas_calidad
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
        <CardContent className="flex items-start gap-3 p-4">
          <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
          <div className="space-y-1 text-xs text-muted-foreground">
            <p className="font-medium text-foreground">What are Seeds?</p>
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
      case 1:
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
              <Input
                value={draft.objetivo || ''}
                onChange={e => updateDraft({ objetivo: e.target.value })}
                placeholder="What should this conversation achieve?"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label className="flex items-center gap-1">
                  Language
                  <FieldTooltip text="The primary language for generated conversations. ISO 639-1 code." />
                </Label>
                <Select value={draft.idioma || 'es'} onValueChange={v => updateDraft({ idioma: v })}>
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
                <Select value={draft.tono || 'profesional'} onValueChange={v => updateDraft({ tono: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TONES.map(t => (
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

      case 4:
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Step 4: Factual Parameters</h3>
              <p className="text-xs text-muted-foreground">
                Domain-specific context, constraints, and available tools. This ensures generated conversations stay factually accurate.
              </p>
            </div>
            <div className="space-y-2">
              <Label>Context</Label>
              <Textarea
                value={draft.parametros_factuales?.contexto || ''}
                onChange={e => updateParametros({ contexto: e.target.value })}
                placeholder="Describe the factual context for the conversation..."
                className="min-h-[80px]"
              />
            </div>
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
            <div className="space-y-2">
              <Label>Tools</Label>
              {(draft.parametros_factuales?.herramientas || []).map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Input
                    value={item}
                    onChange={e => updateParamListItem('herramientas', i, e.target.value)}
                    placeholder={`Tool ${i + 1}`}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0"
                    onClick={() => removeFromParamList('herramientas', i)}
                  >
                    <X className="size-3.5" />
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => addToParamList('herramientas')}>
                <Plus className="mr-1.5 size-4" /> Add Tool
              </Button>
            </div>
          </div>
        )

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
          {filtered.map(seed => (
            <Card
              key={seed.seed_id}
              className="cursor-pointer transition-colors hover:bg-muted/50"
              onClick={() => { setSelectedSeed(seed); setDetailOpen(true) }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm font-medium">
                    {seed.seed_id.slice(0, 16)}...
                  </CardTitle>
                  <Badge
                    variant="secondary"
                    className={cn('shrink-0 text-[10px]', DOMAIN_COLORS[seed.dominio])}
                  >
                    {seed.dominio.split('.').pop()}
                  </Badge>
                </div>
                <CardDescription className="line-clamp-2 text-xs">
                  {seed.objetivo.length > 80 ? seed.objetivo.slice(0, 80) + '...' : seed.objetivo}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {/* Roles */}
                <div className="flex flex-wrap gap-1">
                  {seed.roles.map(role => (
                    <Badge key={role} variant="outline" className="text-[10px]">
                      {role}
                    </Badge>
                  ))}
                </div>

                {/* Tags */}
                {seed.etiquetas.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {seed.etiquetas.slice(0, 4).map(tag => (
                      <Badge key={tag} variant="secondary" className="text-[9px] font-normal">
                        {tag}
                      </Badge>
                    ))}
                    {seed.etiquetas.length > 4 && (
                      <span className="text-[9px] text-muted-foreground">+{seed.etiquetas.length - 4}</span>
                    )}
                  </div>
                )}

                {/* Footer info */}
                <div className="flex items-center justify-between pt-1 text-[10px] text-muted-foreground">
                  <span>
                    {seed.pasos_turnos.turnos_min}-{seed.pasos_turnos.turnos_max} turns
                  </span>
                  <Badge variant="secondary" className="text-[9px]">{seed.idioma}</Badge>
                  <span>{new Date(seed.created_at).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>
          ))}
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

          <DialogFooter>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => selectedSeed && handleDelete(selectedSeed.seed_id)}
            >
              <Trash2 className="mr-1.5 size-4" /> Delete Seed
            </Button>
            <Button variant="outline" size="sm" onClick={() => setDetailOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
