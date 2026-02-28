'use client'

import { useState } from 'react'

import {
  AlertTriangle,
  Check,
  ChevronLeft,
  ChevronRight,
  CloudOff,
  HelpCircle,
  Loader2,
  Plus,
  Trash2
} from 'lucide-react'

import type { CustomToolCreateRequest, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { registerTool as registerToolApi } from '@/lib/api/tools'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

import { JsonViewer } from './json-viewer'

// ─── Constants ───

const CATEGORIES = [
  'query',
  'action',
  'validation',
  'calculation',
  'retrieval',
  'notification',
  'integration'
] as const

const PARAM_TYPES = ['string', 'number', 'integer', 'boolean', 'array', 'object'] as const

type ParamType = (typeof PARAM_TYPES)[number]

const EXECUTION_MODES = [
  { value: 'simulated', label: 'Simulated', description: 'Returns realistic mock data based on the schema. Best for testing and development.' },
  { value: 'live', label: 'Live', description: 'Executes the actual tool logic against real services. Use in production.' },
  { value: 'mock', label: 'Mock', description: 'Returns fixed dummy data. Useful for UI prototyping.' }
] as const

const AUTH_TYPES = [
  { value: 'bearer', label: 'Bearer Token' },
  { value: 'api_key', label: 'API Key' },
  { value: 'basic', label: 'Basic Auth' }
] as const

const STEPS = [
  { number: 1, label: 'Basics' },
  { number: 2, label: 'Parameters' },
  { number: 3, label: 'Configuration' },
  { number: 4, label: 'Review' }
] as const

// ─── Types ───

interface ParameterEntry {
  id: string
  name: string
  type: ParamType
  description: string
  required: boolean
  enumValues: string
}

interface ToolCreationWizardProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  apiOnline: boolean | null
  existingToolNames: string[]
  onSuccess: () => void
}

// ─── Helpers ───

function toSnakeCase(str: string): string {
  return str
    .toLowerCase()
    .replace(/[\s-]+/g, '_')
    .replace(/[^a-z0-9_]/g, '')
}

function createEmptyParam(): ParameterEntry {
  return {
    id: crypto.randomUUID(),
    name: '',
    type: 'string',
    description: '',
    required: false,
    enumValues: ''
  }
}

function parametersToJsonSchema(params: ParameterEntry[]): Record<string, unknown> {
  const properties: Record<string, unknown> = {}
  const required: string[] = []

  for (const p of params) {
    if (!p.name.trim()) continue

    const prop: Record<string, unknown> = {
      type: p.type,
      description: p.description || undefined
    }

    if (p.type === 'string' && p.enumValues.trim()) {
      prop.enum = p.enumValues
        .split(',')
        .map(v => v.trim())
        .filter(Boolean)
    }

    properties[p.name.trim()] = prop

    if (p.required) {
      required.push(p.name.trim())
    }
  }

  return {
    type: 'object',
    properties,
    ...(required.length > 0 ? { required } : {})
  }
}

function FieldTip({ content }: { content: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <HelpCircle className="ml-1 inline-block size-3 cursor-help text-muted-foreground" />
      </TooltipTrigger>
      <TooltipContent side="right" className="max-w-[250px] text-xs">
        {content}
      </TooltipContent>
    </Tooltip>
  )
}

// ─── Step indicator ───

function StepIndicator({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center gap-1.5">
      {STEPS.map((step, idx) => {
        const isDone = step.number < currentStep
        const isActive = step.number === currentStep

        return (
          <div key={step.number} className="flex items-center gap-1.5">
            <div
              className={cn(
                'flex size-6 items-center justify-center rounded-full text-[11px] font-medium transition-colors',
                isActive && 'bg-primary text-primary-foreground ring-2 ring-primary/30',
                isDone && 'bg-primary/15 text-primary',
                !isActive && !isDone && 'bg-muted text-muted-foreground'
              )}
            >
              {isDone ? <Check className="size-3" /> : step.number}
            </div>
            <span
              className={cn(
                'text-xs',
                isActive && 'font-medium text-foreground',
                !isActive && 'text-muted-foreground'
              )}
            >
              {step.label}
            </span>
            {idx < STEPS.length - 1 && (
              <div
                className={cn(
                  'h-px w-6 transition-colors',
                  isDone ? 'bg-primary/50' : 'bg-border'
                )}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Step 1: Basics ───

function StepBasics({
  name,
  description,
  domains,
  category,
  onNameChange,
  onDescriptionChange,
  onDomainsChange,
  onCategoryChange
}: {
  name: string
  description: string
  domains: string[]
  category: string
  onNameChange: (v: string) => void
  onDescriptionChange: (v: string) => void
  onDomainsChange: (v: string[]) => void
  onCategoryChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="wiz-name" className="text-xs">
          Name <span className="text-destructive">*</span>
          <FieldTip content="Unique snake_case identifier. Spaces and dashes are auto-converted." />
        </Label>
        <Input
          id="wiz-name"
          placeholder="e.g. check_inventory"
          value={name}
          onChange={e => onNameChange(toSnakeCase(e.target.value))}
          className="font-mono text-sm"
        />
        {name && (
          <p className="text-[10px] text-muted-foreground">
            Identifier: <code className="rounded bg-muted px-1">{name}</code>
          </p>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="wiz-desc" className="text-xs">
          Description <span className="text-destructive">*</span>
          <FieldTip content="The LLM reads this to decide when to call the tool. Be specific about what the tool does, its inputs, and expected outputs." />
        </Label>
        <Textarea
          id="wiz-desc"
          placeholder="What this tool does and when the LLM should use it..."
          value={description}
          onChange={e => onDescriptionChange(e.target.value)}
          className="min-h-[80px] resize-none text-sm"
        />
        <p className={cn('text-[10px]', description.length < 10 ? 'text-muted-foreground' : 'text-emerald-600')}>
          {description.length} / 10 min characters
        </p>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label className="text-xs">
          Domain(s) <span className="text-destructive">*</span>
          <FieldTip content="Select one or more industry domains where this tool applies." />
        </Label>
        <div className="grid grid-cols-2 gap-2">
          {SUPPORTED_DOMAINS.map(d => {
            const checked = domains.includes(d)
            const domainLabel = d.split('.').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' / ')

            return (
              <label
                key={d}
                className={cn(
                  'flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-xs transition-colors',
                  checked ? 'border-primary/40 bg-primary/5' : 'border-border hover:bg-muted/50'
                )}
              >
                <Checkbox
                  checked={checked}
                  onCheckedChange={on => {
                    if (on) {
                      onDomainsChange([...domains, d])
                    } else {
                      onDomainsChange(domains.filter(x => x !== d))
                    }
                  }}
                />
                <span>{domainLabel}</span>
              </label>
            )
          })}
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label className="text-xs">
          Category <span className="text-destructive">*</span>
        </Label>
        <Select value={category} onValueChange={onCategoryChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map(c => (
              <SelectItem key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}

// ─── Step 2: Parameters ───

function ParameterRow({
  param,
  onChange,
  onRemove
}: {
  param: ParameterEntry
  onChange: (patch: Partial<ParameterEntry>) => void
  onRemove: () => void
}) {
  return (
    <div className="flex flex-col gap-2 rounded-md border p-3">
      <div className="grid grid-cols-[1fr_120px_24px] items-start gap-2">
        <div className="flex flex-col gap-1">
          <Input
            placeholder="parameter_name"
            value={param.name}
            onChange={e => onChange({ name: toSnakeCase(e.target.value) })}
            className="h-8 font-mono text-xs"
          />
        </div>
        <Select value={param.type} onValueChange={v => onChange({ type: v as ParamType })}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PARAM_TYPES.map(t => (
              <SelectItem key={t} value={t} className="text-xs">
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant="ghost"
          size="icon"
          className="size-8 text-muted-foreground hover:text-destructive"
          onClick={onRemove}
        >
          <Trash2 className="size-3.5" />
        </Button>
      </div>

      <Input
        placeholder="Description of this parameter..."
        value={param.description}
        onChange={e => onChange({ description: e.target.value })}
        className="h-8 text-xs"
      />

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-1.5 text-xs">
          <Checkbox
            checked={param.required}
            onCheckedChange={on => onChange({ required: !!on })}
          />
          Required
        </label>

        {param.type === 'string' && (
          <div className="flex flex-1 items-center gap-1.5">
            <span className="shrink-0 text-[10px] text-muted-foreground">Enum:</span>
            <Input
              placeholder="value1, value2, value3"
              value={param.enumValues}
              onChange={e => onChange({ enumValues: e.target.value })}
              className="h-7 flex-1 text-[11px]"
            />
          </div>
        )}
      </div>
    </div>
  )
}

function StepParameters({
  inputParams,
  outputParams,
  onInputChange,
  onOutputChange
}: {
  inputParams: ParameterEntry[]
  outputParams: ParameterEntry[]
  onInputChange: (params: ParameterEntry[]) => void
  onOutputChange: (params: ParameterEntry[]) => void
}) {
  const [showOutput, setShowOutput] = useState(false)

  function updateParam(list: ParameterEntry[], id: string, patch: Partial<ParameterEntry>): ParameterEntry[] {
    return list.map(p => (p.id === id ? { ...p, ...patch } : p))
  }

  function removeParam(list: ParameterEntry[], id: string): ParameterEntry[] {
    return list.filter(p => p.id !== id)
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Input Parameters */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <Label className="text-xs">
            Input Parameters
            <FieldTip content="Define the parameters the LLM will provide when calling this tool. These become the JSON Schema input_schema." />
          </Label>
          <Button
            variant="outline"
            size="sm"
            className="h-7 gap-1 text-xs"
            onClick={() => onInputChange([...inputParams, createEmptyParam()])}
          >
            <Plus className="size-3" />
            Add Parameter
          </Button>
        </div>

        {inputParams.length === 0 ? (
          <div className="flex items-center justify-center rounded-md border border-dashed py-6">
            <p className="text-xs text-muted-foreground">No input parameters defined. Click &quot;Add Parameter&quot; to start.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {inputParams.map(p => (
              <ParameterRow
                key={p.id}
                param={p}
                onChange={patch => onInputChange(updateParam(inputParams, p.id, patch))}
                onRemove={() => onInputChange(removeParam(inputParams, p.id))}
              />
            ))}
          </div>
        )}
      </div>

      <Separator />

      {/* Output Parameters (collapsible) */}
      <div className="flex flex-col gap-2">
        <button
          type="button"
          className="flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
          onClick={() => setShowOutput(!showOutput)}
        >
          {showOutput ? <ChevronLeft className="size-3 rotate-[-90deg]" /> : <ChevronRight className="size-3" />}
          Output Parameters
          <Badge variant="secondary" className="text-[9px]">optional</Badge>
        </button>

        {showOutput && (
          <div className="flex flex-col gap-2">
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                className="h-7 gap-1 text-xs"
                onClick={() => onOutputChange([...outputParams, createEmptyParam()])}
              >
                <Plus className="size-3" />
                Add Output
              </Button>
            </div>

            {outputParams.length === 0 ? (
              <div className="flex items-center justify-center rounded-md border border-dashed py-4">
                <p className="text-xs text-muted-foreground">No output parameters defined.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {outputParams.map(p => (
                  <ParameterRow
                    key={p.id}
                    param={p}
                    onChange={patch => onOutputChange(updateParam(outputParams, p.id, patch))}
                    onRemove={() => onOutputChange(removeParam(outputParams, p.id))}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Step 3: Configuration ───

function StepConfiguration({
  executionMode,
  requiresAuth,
  authType,
  version,
  onExecModeChange,
  onRequiresAuthChange,
  onAuthTypeChange,
  onVersionChange
}: {
  executionMode: string
  requiresAuth: boolean
  authType: string
  version: string
  onExecModeChange: (v: string) => void
  onRequiresAuthChange: (v: boolean) => void
  onAuthTypeChange: (v: string) => void
  onVersionChange: (v: string) => void
}) {
  const activeMode = EXECUTION_MODES.find(m => m.value === executionMode)

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <Label className="text-xs">
          Execution Mode
          <FieldTip content="Controls how the tool responds when invoked during conversations." />
        </Label>
        <Select value={executionMode} onValueChange={onExecModeChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {EXECUTION_MODES.map(m => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {activeMode && (
          <p className="text-[11px] text-muted-foreground">{activeMode.description}</p>
        )}
      </div>

      <Separator />

      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-0.5">
            <Label className="text-xs">Requires Authentication</Label>
            <p className="text-[10px] text-muted-foreground">
              Enable if the tool needs credentials to execute
            </p>
          </div>
          <Switch
            checked={requiresAuth}
            onCheckedChange={onRequiresAuthChange}
          />
        </div>

        {requiresAuth && (
          <div className="flex flex-col gap-1.5 pl-1">
            <Label className="text-xs">Auth Type</Label>
            <Select value={authType} onValueChange={onAuthTypeChange}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AUTH_TYPES.map(a => (
                  <SelectItem key={a.value} value={a.value}>
                    {a.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      <Separator />

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="wiz-version" className="text-xs">Version</Label>
        <Input
          id="wiz-version"
          value={version}
          onChange={e => onVersionChange(e.target.value)}
          className="w-32 font-mono text-sm"
        />
      </div>
    </div>
  )
}

// ─── Step 4: Review ───

function ReviewField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b py-2 last:border-0">
      <span className="w-28 shrink-0 text-xs text-muted-foreground">{label}</span>
      <span className="text-right text-xs font-medium">{children}</span>
    </div>
  )
}

function StepReview({
  name,
  description,
  domains,
  category,
  executionMode,
  requiresAuth,
  authType,
  version,
  inputParams,
  outputParams,
  apiOnline
}: {
  name: string
  description: string
  domains: string[]
  category: string
  executionMode: string
  requiresAuth: boolean
  authType: string
  version: string
  inputParams: ParameterEntry[]
  outputParams: ParameterEntry[]
  apiOnline: boolean | null
}) {
  const inputSchema = parametersToJsonSchema(inputParams)
  const outputSchema = outputParams.length > 0 ? parametersToJsonSchema(outputParams) : {}

  return (
    <div className="flex flex-col gap-4">
      {!apiOnline && (
        <div className="flex items-center gap-2 rounded-md border border-amber-500/30 bg-amber-500/5 px-3 py-2">
          <CloudOff className="size-4 shrink-0 text-amber-600" />
          <p className="text-xs text-amber-700 dark:text-amber-400">
            API is offline. Tool will be saved locally and synced when the API reconnects.
          </p>
        </div>
      )}

      {/* Summary card */}
      <div className="rounded-md border p-3">
        <ReviewField label="Name">
          <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]">{name}</code>
        </ReviewField>
        <ReviewField label="Description">
          <span className="max-w-[200px] break-words text-right">{description}</span>
        </ReviewField>
        <ReviewField label="Domain(s)">
          <div className="flex flex-wrap justify-end gap-1">
            {domains.map(d => (
              <Badge key={d} variant="secondary" className="text-[10px]">
                {d.split('.').pop()}
              </Badge>
            ))}
          </div>
        </ReviewField>
        <ReviewField label="Category">
          <Badge variant="outline" className="text-[10px]">{category}</Badge>
        </ReviewField>
        <ReviewField label="Execution Mode">
          <Badge
            variant={executionMode === 'live' ? 'default' : 'secondary'}
            className="text-[10px]"
          >
            {executionMode}
          </Badge>
        </ReviewField>
        <ReviewField label="Auth">
          {requiresAuth ? (
            <Badge variant="outline" className="text-[10px]">{authType}</Badge>
          ) : (
            <span className="text-muted-foreground">None</span>
          )}
        </ReviewField>
        <ReviewField label="Version">
          <code className="font-mono text-[11px]">{version}</code>
        </ReviewField>
        <ReviewField label="Input Params">
          {inputParams.filter(p => p.name.trim()).length} defined
        </ReviewField>
        {outputParams.length > 0 && (
          <ReviewField label="Output Params">
            {outputParams.filter(p => p.name.trim()).length} defined
          </ReviewField>
        )}
      </div>

      {/* JSON Schema Preview */}
      <div className="flex flex-col gap-1.5">
        <Label className="text-xs">Schema Preview</Label>
        <Tabs defaultValue="input">
          <TabsList className="h-8">
            <TabsTrigger value="input" className="text-xs">Input Schema</TabsTrigger>
            <TabsTrigger value="output" className="text-xs">Output Schema</TabsTrigger>
          </TabsList>
          <TabsContent value="input" className="mt-2">
            <JsonViewer data={inputSchema} maxHeight="200px" />
          </TabsContent>
          <TabsContent value="output" className="mt-2">
            <JsonViewer data={outputSchema} maxHeight="200px" />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// ─── Local storage helpers (same keys as tools-page) ───

const STORE_KEY = 'uncase-tools'

function loadTools(): ToolDefinition[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveTools(tools: ToolDefinition[]) {
  localStorage.setItem(STORE_KEY, JSON.stringify(tools))
}

// ─── Main Wizard ───

export function ToolCreationWizard({
  open,
  onOpenChange,
  apiOnline,
  existingToolNames,
  onSuccess
}: ToolCreationWizardProps) {
  // Step state
  const [step, setStep] = useState(1)

  // Step 1: Basics
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [domains, setDomains] = useState<string[]>([])
  const [category, setCategory] = useState('')

  // Step 2: Parameters
  const [inputParams, setInputParams] = useState<ParameterEntry[]>([])
  const [outputParams, setOutputParams] = useState<ParameterEntry[]>([])

  // Step 3: Configuration
  const [executionMode, setExecutionMode] = useState('simulated')
  const [requiresAuth, setRequiresAuth] = useState(false)
  const [authType, setAuthType] = useState('bearer')
  const [version, setVersion] = useState('1.0.0')

  // Submission
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function reset() {
    setStep(1)
    setName('')
    setDescription('')
    setDomains([])
    setCategory('')
    setInputParams([])
    setOutputParams([])
    setExecutionMode('simulated')
    setRequiresAuth(false)
    setAuthType('bearer')
    setVersion('1.0.0')
    setSubmitting(false)
    setError(null)
  }

  function handleClose() {
    onOpenChange(false)
    setTimeout(reset, 200)
  }

  // ─── Validation ───

  function validateStep(s: number): string | null {
    if (s === 1) {
      if (!name.trim()) return 'Name is required'
      if (existingToolNames.includes(name.trim())) return `A tool named "${name}" already exists`
      if (description.trim().length < 10) return 'Description must be at least 10 characters'
      if (domains.length === 0) return 'Select at least one domain'
      if (!category) return 'Select a category'
    }

    // Step 2 & 3 have no required fields (params are optional, config has defaults)
    return null
  }

  function handleNext() {
    const err = validateStep(step)

    if (err) {
      setError(err)

      return
    }

    setError(null)
    setStep(s => Math.min(s + 1, 4))
  }

  function handlePrev() {
    setError(null)
    setStep(s => Math.max(s - 1, 1))
  }

  // ─── Submission ───

  async function handleRegister() {
    setError(null)

    const inputSchema = parametersToJsonSchema(inputParams)
    const outputSchema = outputParams.length > 0 ? parametersToJsonSchema(outputParams) : undefined

    const request: CustomToolCreateRequest = {
      name: name.trim(),
      description: description.trim(),
      input_schema: inputSchema,
      output_schema: outputSchema,
      domains,
      category,
      requires_auth: requiresAuth,
      execution_mode: executionMode as 'simulated' | 'live' | 'mock',
      version,
      metadata: requiresAuth ? { auth_type: authType } : {}
    }

    setSubmitting(true)

    if (apiOnline) {
      const result = await registerToolApi(request)

      setSubmitting(false)

      if (result.error) {
        setError(result.error.message)

        return
      }

      handleClose()
      onSuccess()

      return
    }

    // Fallback: localStorage
    const toolDef: ToolDefinition = {
      name: request.name,
      description: request.description,
      input_schema: inputSchema,
      output_schema: outputSchema ?? {},
      domains,
      category,
      requires_auth: requiresAuth,
      execution_mode: executionMode as 'simulated' | 'live' | 'mock',
      version,
      metadata: request.metadata ?? {}
    }

    const existing = loadTools()

    saveTools([...existing, toolDef])
    setSubmitting(false)
    handleClose()
    onSuccess()
  }

  // ─── Render ───

  const isFirst = step === 1
  const isLast = step === 4

  return (
    <Dialog open={open} onOpenChange={open => { if (!open) handleClose() }}>
      <DialogContent className="flex max-h-[90vh] max-w-lg flex-col gap-0 overflow-hidden p-0">
        {/* Header */}
        <DialogHeader className="shrink-0 px-5 pb-3 pt-5">
          <DialogTitle className="text-base">Register Custom Tool</DialogTitle>
          <DialogDescription className="text-xs">
            {apiOnline
              ? 'Build a tool definition step by step. It will be saved to the database.'
              : 'Build a tool definition step by step. It will be saved locally until the API reconnects.'}
          </DialogDescription>
        </DialogHeader>

        {/* Step indicator */}
        <div className="shrink-0 px-5 pb-3">
          <StepIndicator currentStep={step} />
        </div>

        <Separator className="shrink-0" />

        {/* Step content — scrollable */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {step === 1 && (
            <StepBasics
              name={name}
              description={description}
              domains={domains}
              category={category}
              onNameChange={setName}
              onDescriptionChange={setDescription}
              onDomainsChange={setDomains}
              onCategoryChange={setCategory}
            />
          )}
          {step === 2 && (
            <StepParameters
              inputParams={inputParams}
              outputParams={outputParams}
              onInputChange={setInputParams}
              onOutputChange={setOutputParams}
            />
          )}
          {step === 3 && (
            <StepConfiguration
              executionMode={executionMode}
              requiresAuth={requiresAuth}
              authType={authType}
              version={version}
              onExecModeChange={setExecutionMode}
              onRequiresAuthChange={setRequiresAuth}
              onAuthTypeChange={setAuthType}
              onVersionChange={setVersion}
            />
          )}
          {step === 4 && (
            <StepReview
              name={name}
              description={description}
              domains={domains}
              category={category}
              executionMode={executionMode}
              requiresAuth={requiresAuth}
              authType={authType}
              version={version}
              inputParams={inputParams}
              outputParams={outputParams}
              apiOnline={apiOnline}
            />
          )}

          {error && (
            <div className="mt-3 flex items-center gap-1.5 text-xs text-destructive">
              <AlertTriangle className="size-3.5 shrink-0" />
              {error}
            </div>
          )}
        </div>

        <Separator className="shrink-0" />

        {/* Footer */}
        <DialogFooter className="flex shrink-0 items-center justify-between px-5 py-3">
          <span className="text-xs text-muted-foreground">
            {step} / {STEPS.length}
          </span>

          <div className="flex items-center gap-2">
            {isFirst ? (
              <Button variant="outline" size="sm" className="h-8 text-xs" onClick={handleClose}>
                Cancel
              </Button>
            ) : (
              <Button
                variant="outline"
                size="sm"
                className="h-8 gap-1 text-xs"
                onClick={handlePrev}
                disabled={submitting}
              >
                <ChevronLeft className="size-3" />
                Back
              </Button>
            )}

            {!isLast && (
              <Button size="sm" className="h-8 gap-1 text-xs" onClick={handleNext}>
                Next
                <ChevronRight className="size-3" />
              </Button>
            )}

            {isLast && (
              <Button
                size="sm"
                className="h-8 text-xs"
                onClick={handleRegister}
                disabled={submitting}
              >
                {submitting && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
                Register Tool
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
