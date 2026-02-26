'use client'

import { useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import { Cloud, CloudOff, Code2, Loader2, Lock, Plus, Puzzle, RefreshCw, Trash2, Unlock } from 'lucide-react'

import type { CustomToolCreateRequest, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import { deleteTool as deleteToolApi, fetchTools, registerTool as registerToolApi } from '@/lib/api/tools'
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
import { Textarea } from '@/components/ui/textarea'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { SearchInput } from '../search-input'
import { StatusBadge } from '../status-badge'

// ─── Local Storage ───
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

const EXECUTION_MODE_VARIANT: Record<string, 'success' | 'warning' | 'info'> = {
  live: 'success',
  simulated: 'info',
  mock: 'warning'
}

const CATEGORIES = [
  'query',
  'action',
  'validation',
  'calculation',
  'retrieval',
  'notification',
  'integration'
] as const

// Built-in tool names — cannot be deleted
const BUILTIN_PREFIXES = [
  'buscar_inventario', 'cotizar_vehiculo', 'verificar_disponibilidad', 'solicitar_financiamiento', 'agendar_servicio',
  'consultar_historial_medico', 'buscar_medicamentos', 'agendar_cita', 'verificar_laboratorio', 'validar_seguro',
  'buscar_jurisprudencia', 'consultar_expediente', 'verificar_plazos', 'buscar_legislacion', 'calcular_honorarios',
  'consultar_portafolio', 'analizar_riesgo', 'consultar_mercado', 'verificar_cumplimiento', 'simular_inversion',
  'diagnosticar_equipo', 'consultar_inventario_partes', 'programar_mantenimiento', 'buscar_manual_tecnico', 'registrar_incidencia',
  'buscar_curriculum', 'evaluar_progreso', 'generar_ejercicio', 'buscar_recurso_educativo', 'programar_sesion'
]

export function ToolsPage() {
  const [tools, setTools] = useState<ToolDefinition[]>(() => loadTools())
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [syncing, setSyncing] = useState(false)

  // Filters
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  // Register dialog
  const [dialogOpen, setDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [registerError, setRegisterError] = useState<string | null>(null)

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDescription, setFormDescription] = useState('')
  const [formInputSchema, setFormInputSchema] = useState('{\n  "type": "object",\n  "properties": {}\n}')
  const [formOutputSchema, setFormOutputSchema] = useState('{}')
  const [formDomain, setFormDomain] = useState<string>('')
  const [formCategory, setFormCategory] = useState<string>('')
  const [formExecMode, setFormExecMode] = useState<string>('simulated')

  // Try syncing from API on mount — if it fails, fall back to localStorage data
  useEffect(() => {
    let cancelled = false

    async function syncFromApi() {
      const healthy = await checkApiHealth()

      if (cancelled) return

      setApiOnline(healthy)

      if (!healthy) return

      setSyncing(true)
      const result = await fetchTools()

      if (cancelled) return

      setSyncing(false)

      if (result.data && result.data.length > 0) {
        setTools(result.data)
        saveTools(result.data)
      }
    }

    syncFromApi()

    return () => { cancelled = true }
  }, [])

  // Listen for localStorage changes (e.g. from demo activation)
  useEffect(() => {
    function onStorage(e: StorageEvent) {
      if (e.key === STORE_KEY) {
        setTools(loadTools())
      }
    }

    window.addEventListener('storage', onStorage)

    return () => window.removeEventListener('storage', onStorage)
  }, [])

  async function handleSync() {
    setSyncing(true)
    const result = await fetchTools()

    setSyncing(false)

    if (result.data && result.data.length > 0) {
      setTools(result.data)
      saveTools(result.data)
      setApiOnline(true)
    } else {
      setApiOnline(false)
    }
  }

  // Derive unique categories from existing tools
  const availableCategories = useMemo(() => {
    const cats = new Set(tools.map(t => t.category))

    return Array.from(cats).sort()
  }, [tools])

  const filtered = useMemo(() => {
    let result = tools

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        t =>
          t.name.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q)
      )
    }

    if (domainFilter !== 'all') {
      result = result.filter(t => t.domains.includes(domainFilter))
    }

    if (categoryFilter !== 'all') {
      result = result.filter(t => t.category === categoryFilter)
    }

    return result
  }, [tools, search, domainFilter, categoryFilter])

  const builtinCount = useMemo(() => {
    return tools.filter(t => BUILTIN_PREFIXES.includes(t.name)).length
  }, [tools])

  const customCount = tools.length - builtinCount

  function isBuiltin(name: string): boolean {
    return BUILTIN_PREFIXES.includes(name)
  }

  function resetForm() {
    setFormName('')
    setFormDescription('')
    setFormInputSchema('{\n  "type": "object",\n  "properties": {}\n}')
    setFormOutputSchema('{}')
    setFormDomain('')
    setFormCategory('')
    setFormExecMode('simulated')
    setRegisterError(null)
  }

  async function handleRegister() {
    setRegisterError(null)

    if (!formName.trim()) {
      setRegisterError('Name is required')

      return
    }

    if (!formDescription.trim() || formDescription.trim().length < 10) {
      setRegisterError('Description is required (at least 10 characters)')

      return
    }

    if (!formDomain) {
      setRegisterError('Select a domain')

      return
    }

    if (!formCategory) {
      setRegisterError('Select or enter a category')

      return
    }

    let parsedInputSchema: Record<string, unknown>
    let parsedOutputSchema: Record<string, unknown>

    try {
      parsedInputSchema = JSON.parse(formInputSchema)
    } catch {
      setRegisterError('Input schema must be valid JSON')

      return
    }

    try {
      parsedOutputSchema = JSON.parse(formOutputSchema)
    } catch {
      setRegisterError('Output schema must be valid JSON')

      return
    }

    const newTool: CustomToolCreateRequest = {
      name: formName.trim(),
      description: formDescription.trim(),
      input_schema: parsedInputSchema,
      output_schema: parsedOutputSchema,
      domains: [formDomain],
      category: formCategory,
      requires_auth: false,
      execution_mode: formExecMode as 'simulated' | 'live' | 'mock',
      version: '1.0.0',
      metadata: {}
    }

    setSubmitting(true)

    // Try API first
    if (apiOnline) {
      const result = await registerToolApi(newTool)

      setSubmitting(false)

      if (result.error) {
        setRegisterError(result.error.message)

        return
      }

      setDialogOpen(false)
      resetForm()
      handleSync()

      return
    }

    // Fallback: save to localStorage only
    const toolDef: ToolDefinition = {
      name: newTool.name,
      description: newTool.description,
      input_schema: parsedInputSchema,
      output_schema: parsedOutputSchema,
      domains: newTool.domains ?? [],
      category: newTool.category ?? 'query',
      requires_auth: newTool.requires_auth ?? false,
      execution_mode: newTool.execution_mode ?? 'simulated',
      version: newTool.version ?? '1.0.0',
      metadata: newTool.metadata ?? {}
    }

    const updated = [...tools, toolDef]

    setTools(updated)
    saveTools(updated)
    setSubmitting(false)
    setDialogOpen(false)
    resetForm()
  }

  async function handleDelete(toolName: string) {
    setDeleting(true)

    // Try API first
    if (apiOnline) {
      const result = await deleteToolApi(toolName)

      setDeleting(false)
      setDeleteTarget(null)

      if (!result.error) {
        handleSync()
      }

      return
    }

    // Fallback: remove from localStorage
    const updated = tools.filter(t => t.name !== toolName)

    setTools(updated)
    saveTools(updated)
    setDeleting(false)
    setDeleteTarget(null)
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Tools"
        description={`${tools.length} tools in registry (${builtinCount} built-in, ${customCount} custom)`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSync}
              disabled={syncing}
              title={apiOnline ? 'Synced with API' : 'API offline — using local data'}
            >
              {syncing ? (
                <Loader2 className="mr-1.5 size-4 animate-spin" />
              ) : apiOnline ? (
                <Cloud className="mr-1.5 size-4 text-emerald-500" />
              ) : (
                <CloudOff className="mr-1.5 size-4 text-muted-foreground" />
              )}
              {syncing ? 'Syncing...' : 'Sync'}
            </Button>
            <Dialog open={dialogOpen} onOpenChange={open => { setDialogOpen(open); if (!open) resetForm() }}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="mr-1.5 size-4" />
                  Register Tool
                </Button>
              </DialogTrigger>
              <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle>Register Custom Tool</DialogTitle>
                  <DialogDescription>
                    Add a new tool definition.{apiOnline
                      ? ' Custom tools are persisted to the database and available across sessions.'
                      : ' Tool will be saved locally. Connect the API to persist to the database.'}
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="tool-name">Name</Label>
                    <Input
                      id="tool-name"
                      value={formName}
                      onChange={e => setFormName(e.target.value)}
                      placeholder="e.g. consultar_inventario"
                    />
                    <p className="text-[10px] text-muted-foreground">Lowercase snake_case identifier</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tool-description">Description</Label>
                    <Textarea
                      id="tool-description"
                      value={formDescription}
                      onChange={e => setFormDescription(e.target.value)}
                      placeholder="What this tool does..."
                      className="min-h-[80px]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tool-input-schema">Input Schema (JSON)</Label>
                    <Textarea
                      id="tool-input-schema"
                      value={formInputSchema}
                      onChange={e => setFormInputSchema(e.target.value)}
                      className="min-h-[100px] font-mono text-xs"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tool-output-schema">Output Schema (JSON)</Label>
                    <Textarea
                      id="tool-output-schema"
                      value={formOutputSchema}
                      onChange={e => setFormOutputSchema(e.target.value)}
                      className="min-h-[80px] font-mono text-xs"
                    />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Domain</Label>
                      <Select value={formDomain} onValueChange={setFormDomain}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select domain" />
                        </SelectTrigger>
                        <SelectContent>
                          {SUPPORTED_DOMAINS.map(d => (
                            <SelectItem key={d} value={d}>
                              {d}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Category</Label>
                      <Select value={formCategory} onValueChange={setFormCategory}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {CATEGORIES.map(c => (
                            <SelectItem key={c} value={c}>
                              {c}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Execution Mode</Label>
                    <Select value={formExecMode} onValueChange={setFormExecMode}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="simulated">Simulated</SelectItem>
                        <SelectItem value="live">Live</SelectItem>
                        <SelectItem value="mock">Mock</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {registerError && (
                    <p className="text-xs text-destructive">{registerError}</p>
                  )}
                </div>

                <DialogFooter>
                  <Button variant="outline" onClick={() => { setDialogOpen(false); resetForm() }}>
                    Cancel
                  </Button>
                  <Button onClick={handleRegister} disabled={submitting}>
                    {submitting && <Loader2 className="mr-1.5 size-4 animate-spin" />}
                    Register
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <SearchInput value={search} onChange={setSearch} placeholder="Search tools..." className="w-64" />
        <Select value={domainFilter} onValueChange={setDomainFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Domain" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Domains</SelectItem>
            {SUPPORTED_DOMAINS.map(d => (
              <SelectItem key={d} value={d}>
                {d.split('.').pop()}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {availableCategories.map(c => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{filtered.length} results</span>
      </div>

      {/* Tool cards grid */}
      {tools.length === 0 ? (
        <EmptyState
          icon={Puzzle}
          title="No tools available"
          description="Activate demo mode to load built-in tools, or connect the API to sync from the backend."
          action={
            <Button variant="outline" size="sm" onClick={handleSync}>
              <RefreshCw className="mr-1.5 size-4" />
              Try Sync
            </Button>
          }
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Puzzle}
          title="No tools match filters"
          description="Try adjusting your search or filter criteria."
          action={
            <Button variant="outline" size="sm" onClick={() => { setSearch(''); setDomainFilter('all'); setCategoryFilter('all') }}>
              Clear filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(tool => {
            const builtin = isBuiltin(tool.name)

            return (
              <Card key={tool.name} className="group relative h-full transition-colors hover:bg-muted/50">
                <Link href={`/dashboard/tools/${encodeURIComponent(tool.name)}`} className="block">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <CardTitle className="text-sm">{tool.name}</CardTitle>
                        {builtin ? (
                          <Badge variant="secondary" className="text-[9px]">built-in</Badge>
                        ) : (
                          <Badge variant="outline" className="gap-0.5 text-[9px]">
                            <Code2 className="size-2" />
                            custom
                          </Badge>
                        )}
                      </div>
                      {tool.requires_auth ? (
                        <Lock className="size-3.5 shrink-0 text-muted-foreground" />
                      ) : (
                        <Unlock className="size-3.5 shrink-0 text-muted-foreground" />
                      )}
                    </div>
                    <CardDescription className="line-clamp-2 text-xs">
                      {tool.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-1.5">
                      <StatusBadge
                        variant={EXECUTION_MODE_VARIANT[tool.execution_mode] ?? 'default'}
                        dot={false}
                      >
                        {tool.execution_mode}
                      </StatusBadge>
                      <Badge variant="outline" className="text-[10px]">
                        {tool.category}
                      </Badge>
                      {tool.domains.map(domain => (
                        <Badge key={domain} variant="secondary" className="text-[10px]">
                          {domain.split('.').pop()}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Link>

                {/* Delete button for custom tools */}
                {!builtin && (
                  <button
                    type="button"
                    onClick={e => {
                      e.preventDefault()
                      e.stopPropagation()
                      setDeleteTarget(tool.name)
                    }}
                    className="absolute right-2 top-2 hidden rounded-md p-1 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive group-hover:block"
                    title="Delete custom tool"
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                )}
              </Card>
            )
          })}
        </div>
      )}

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={open => { if (!open) setDeleteTarget(null) }}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Delete Tool</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete <code className="font-semibold">{deleteTarget}</code>? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button
              variant="destructive"
              onClick={() => deleteTarget && handleDelete(deleteTarget)}
              disabled={deleting}
            >
              {deleting && <Loader2 className="mr-1.5 size-4 animate-spin" />}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
