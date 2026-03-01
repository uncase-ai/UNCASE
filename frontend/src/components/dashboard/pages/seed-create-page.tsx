'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Check,
  ExternalLink,
  HelpCircle,
  Info,
  Layers,
  Loader2,
  Plus,
  Trash2,
  Wrench,
  X
} from 'lucide-react'

import type { ScenarioTemplate, SeedSchema, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { fetchScenarioPack } from '@/lib/api/scenarios'
import { createEmptySeed, createSeedApi, validateSeed } from '@/lib/api/seeds'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

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

const DOMAIN_LABELS: Record<string, string> = {
  'automotive.sales': 'Automotive',
  'medical.consultation': 'Medical',
  'legal.advisory': 'Legal',
  'finance.advisory': 'Finance',
  'industrial.support': 'Industrial',
  'education.tutoring': 'Education'
}

const STEP_LABELS = [
  'Basic Info',
  'Roles',
  'Turn Structure',
  'Context & Tools',
  'Privacy',
  'Review'
]

function loadProjectTools(): ToolDefinition[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem('uncase-tools')

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem('uncase-seeds')

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveSeeds(seeds: SeedSchema[]) {
  localStorage.setItem('uncase-seeds', JSON.stringify(seeds))
}

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

export function SeedCreatePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const fromId = searchParams.get('from')

  const [step, setStep] = useState(1)
  const [draft, setDraft] = useState<Partial<SeedSchema>>(() => createEmptySeed())
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [creating, setCreating] = useState(false)
  const [syncError, setSyncError] = useState<string | null>(null)

  // API connectivity
  const [apiAvailable, setApiAvailable] = useState(false)

  // Scenarios
  const [domainScenarios, setDomainScenarios] = useState<ScenarioTemplate[]>([])
  const [scenariosLoading, setScenariosLoading] = useState(false)

  // Tag input
  const [tagInput, setTagInput] = useState('')

  // Source seed banner
  const [sourceSeed, setSourceSeed] = useState<SeedSchema | null>(null)

  // Load source seed when duplicating
  useEffect(() => {
    if (!fromId) return

    const seeds = loadSeeds()
    const source = seeds.find(s => s.seed_id === fromId)

    if (source) {
      setSourceSeed(source)
      setDraft({
        ...source,
        seed_id: '', // will be assigned on create
        created_at: '',
        updated_at: ''
      })
    }
  }, [fromId])

  // Check API health
  useEffect(() => {
    let cancelled = false

    async function init() {
      const healthy = await checkApiHealth()

      if (!cancelled) setApiAvailable(healthy)
    }

    init()

    return () => { cancelled = true }
  }, [])

  // Load scenarios when entering step 4
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

  useEffect(() => {
    if (step === 4 && draft.dominio && apiAvailable) {
      loadDomainScenarios(draft.dominio)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step])

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

  // ─── Tags ───
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

  // ─── Validation ───
  function handleValidate() {
    const errors = validateSeed(draft)

    setValidationErrors(errors)

    return errors.length === 0
  }

  // ─── Create ───
  async function handleCreate() {
    if (!handleValidate()) return

    setCreating(true)
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
        newSeed.seed_id = data.id
      } else if (error) {
        setSyncError(`Failed to save to server: ${error.message}`)
      }
    }

    const existing = loadSeeds()
    const updated = [newSeed, ...existing]

    saveSeeds(updated)
    setCreating(false)
    router.push('/dashboard/pipeline/seeds')
  }

  // ─── Computed ───
  const allTools = useMemo(() => loadProjectTools(), [])

  // ─── Render ───
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard/pipeline/seeds">
          <Button variant="ghost" size="icon" className="size-8">
            <ArrowLeft className="size-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Create Seed</h1>
          <p className="text-sm text-muted-foreground">
            Step {step} of {TOTAL_STEPS} — {STEP_LABELS[step - 1]}
          </p>
        </div>
      </div>

      {/* Source seed banner */}
      {sourceSeed && (
        <Card className="bg-sky-50/50 dark:bg-sky-950/20">
          <CardContent className="flex items-center gap-3 p-3">
            <Info className="size-4 shrink-0 text-sky-600 dark:text-sky-400" />
            <p className="text-xs text-sky-800 dark:text-sky-300">
              Creating from: <span className="font-semibold">{DOMAIN_LABELS[sourceSeed.dominio] || sourceSeed.dominio}</span>
              {' — '}{sourceSeed.objetivo.slice(0, 80)}{sourceSeed.objetivo.length > 80 ? '...' : ''}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Step indicator */}
      <div className="flex items-center gap-1">
        {STEP_LABELS.map((label, i) => {
          const stepNum = i + 1
          const isActive = stepNum === step
          const isDone = stepNum < step

          return (
            <div key={label} className="flex flex-1 items-center gap-1">
              <button
                onClick={() => setStep(stepNum)}
                className={cn(
                  'flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                  isActive && 'bg-primary text-primary-foreground',
                  isDone && 'bg-muted text-foreground',
                  !isActive && !isDone && 'text-muted-foreground hover:bg-muted/50'
                )}
              >
                <span className={cn(
                  'flex size-5 items-center justify-center rounded-full text-[10px] font-bold',
                  isActive && 'bg-primary-foreground/20',
                  isDone && 'bg-primary/10 text-primary',
                  !isActive && !isDone && 'bg-muted'
                )}>
                  {isDone ? <Check className="size-3" /> : stepNum}
                </span>
                <span className="hidden sm:inline">{label}</span>
              </button>
              {i < STEP_LABELS.length - 1 && (
                <div className={cn('h-px flex-1', isDone ? 'bg-primary/30' : 'bg-border')} />
              )}
            </div>
          )
        })}
      </div>

      {/* Sync error */}
      {syncError && (
        <Card className="bg-muted/40">
          <CardContent className="flex items-center gap-3 p-3">
            <AlertTriangle className="size-4 shrink-0 text-muted-foreground" />
            <p className="text-xs text-muted-foreground">{syncError}</p>
            <Button variant="ghost" size="sm" className="ml-auto h-6 text-xs" onClick={() => setSyncError(null)}>
              Dismiss
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step content */}
      <Card>
        <CardContent className="p-6">
          {renderStep()}
        </CardContent>
      </Card>

      {/* Footer navigation */}
      <div className="sticky bottom-0 flex items-center justify-between rounded-lg border bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <Button
          variant="outline"
          size="sm"
          disabled={step === 1}
          onClick={() => setStep(s => s - 1)}
        >
          <ArrowLeft className="mr-1.5 size-4" /> Back
        </Button>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{step}/{TOTAL_STEPS}</span>
          {step < TOTAL_STEPS ? (
            <Button size="sm" onClick={() => setStep(s => s + 1)}>
              Next <ArrowRight className="ml-1.5 size-4" />
            </Button>
          ) : (
            <Button size="sm" onClick={handleCreate} disabled={creating || validationErrors.length > 0}>
              {creating ? (
                <><Loader2 className="mr-1.5 size-4 animate-spin" /> Creating...</>
              ) : (
                'Create Seed'
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  )

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

            {/* Assistant Name + Brand Greeting side by side on full page */}
            <div className="grid gap-4 sm:grid-cols-2">
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
              <div className="space-y-2">
                <Label className="flex items-center gap-1">
                  Brand Greeting
                  <FieldTooltip text="A mandatory opening line or greeting template the assistant must use. Include your brand name or slogan so it appears naturally in generated conversations." />
                </Label>
                <Input
                  value={draft.parametros_factuales?.saludo_marca || ''}
                  onChange={e => updateParametros({ saludo_marca: e.target.value })}
                  placeholder={draft.idioma === 'es'
                    ? 'Ej: Bienvenido a AutoMax, soy Sofia...'
                    : "e.g. Welcome to AutoMax! I'm Sofia..."}
                />
              </div>
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

            {/* Tools — 2-column grid on full page */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                Tools
                <FieldTooltip text="Select tools the assistant can invoke during the conversation. Only selected tools will be available to the generator." />
              </Label>
              {allTools.length > 0 ? (
                <div className={cn('gap-4', domainTools.length > 0 && otherTools.length > 0 ? 'grid sm:grid-cols-2' : 'space-y-2')}>
                  {domainTools.length > 0 && (
                    <div className="space-y-1.5">
                      {selectedDomain && (
                        <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                          {DOMAIN_LABELS[selectedDomain] || selectedDomain} tools
                        </p>
                      )}
                      <div className="max-h-56 space-y-1 overflow-y-auto rounded-md border p-2">
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
                                <Link
                                  href={`/dashboard/tools/${encodeURIComponent(tool.name)}`}
                                  className="font-mono text-xs font-medium hover:underline"
                                  onClick={e => e.stopPropagation()}
                                >
                                  {tool.name}
                                  <ExternalLink className="ml-0.5 inline size-2.5 text-muted-foreground" />
                                </Link>
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
                      <div className="max-h-56 space-y-1 overflow-y-auto rounded-md border p-2">
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
                                <Link
                                  href={`/dashboard/tools/${encodeURIComponent(tool.name)}`}
                                  className="font-mono text-xs font-medium hover:underline"
                                  onClick={e => e.stopPropagation()}
                                >
                                  {tool.name}
                                  <ExternalLink className="ml-0.5 inline size-2.5 text-muted-foreground" />
                                </Link>
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
                    <p className="text-[10px] text-muted-foreground sm:col-span-2">{selectedTools.size} tool{selectedTools.size > 1 ? 's' : ''} selected</p>
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
                                <Badge variant="outline" className="bg-orange-500/10 text-[9px] text-orange-600">edge</Badge>
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
}
