'use client'

import { useCallback, useMemo, useState } from 'react'

import Link from 'next/link'
import { Loader2, Lock, Plus, Puzzle, Unlock } from 'lucide-react'

import type { ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { cn } from '@/lib/utils'
import { useApi } from '@/hooks/use-api'
import { fetchTools, registerTool } from '@/lib/api/tools'
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

const DOMAIN_COLORS: Record<string, string> = {
  'automotive.sales': 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  'medical.consultation': 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  'legal.advisory': 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
  'finance.advisory': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300',
  'industrial.support': 'bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300',
  'education.tutoring': 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-300'
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

export function ToolsPage() {
  const { data: tools, loading, error, execute: refetchTools } = useApi<ToolDefinition[]>(
    useCallback((signal: AbortSignal) => fetchTools(undefined, signal), [])
  )

  // Filters
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  // Register dialog
  const [dialogOpen, setDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [registerError, setRegisterError] = useState<string | null>(null)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDescription, setFormDescription] = useState('')
  const [formInputSchema, setFormInputSchema] = useState('{\n  "type": "object",\n  "properties": {}\n}')
  const [formDomain, setFormDomain] = useState<string>('')
  const [formCategory, setFormCategory] = useState<string>('')

  // Derive unique categories from existing tools
  const availableCategories = useMemo(() => {
    if (!tools) return []
    const cats = new Set(tools.map(t => t.category))

    return Array.from(cats).sort()
  }, [tools])

  const filtered = useMemo(() => {
    if (!tools) return []
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

  function resetForm() {
    setFormName('')
    setFormDescription('')
    setFormInputSchema('{\n  "type": "object",\n  "properties": {}\n}')
    setFormDomain('')
    setFormCategory('')
    setRegisterError(null)
  }

  async function handleRegister() {
    setRegisterError(null)

    if (!formName.trim()) {
      setRegisterError('Name is required')

      return
    }

    if (!formDescription.trim()) {
      setRegisterError('Description is required')

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

    let parsedSchema: Record<string, unknown>

    try {
      parsedSchema = JSON.parse(formInputSchema)
    } catch {
      setRegisterError('Input schema must be valid JSON')

      return
    }

    const newTool: ToolDefinition = {
      name: formName.trim(),
      description: formDescription.trim(),
      input_schema: parsedSchema,
      domains: [formDomain],
      category: formCategory,
      requires_auth: false,
      execution_mode: 'simulated',
      version: '1.0.0',
      metadata: {}
    }

    setSubmitting(true)
    const result = await registerTool(newTool)

    setSubmitting(false)

    if (result.error) {
      setRegisterError(result.error.message)

      return
    }

    setDialogOpen(false)
    resetForm()
    refetchTools()
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Tools" description="Tool registry for conversation simulations" />
        <div className="flex items-center justify-center py-16">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader title="Tools" description="Tool registry for conversation simulations" />
        <EmptyState
          icon={Puzzle}
          title="Failed to load tools"
          description={error.message}
          action={<Button variant="outline" onClick={() => refetchTools()}>Retry</Button>}
        />
      </div>
    )
  }

  if (!tools || tools.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Tools"
          description="Tool registry for conversation simulations"
          actions={<RegisterToolButton />}
        />
        <EmptyState
          icon={Puzzle}
          title="No tools registered"
          description="Register your first tool to enable tool call simulation in conversations."
          action={<RegisterToolButton />}
        />
        <RegisterToolDialog />
      </div>
    )
  }

  function RegisterToolButton() {
    return (
      <Dialog open={dialogOpen} onOpenChange={open => { setDialogOpen(open); if (!open) resetForm() }}>
        <DialogTrigger asChild>
          <Button size="sm">
            <Plus className="mr-1.5 size-4" />
            Register Tool
          </Button>
        </DialogTrigger>
      </Dialog>
    )
  }

  function RegisterToolDialog() {
    return (
      <Dialog open={dialogOpen} onOpenChange={open => { setDialogOpen(open); if (!open) resetForm() }}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Register Tool</DialogTitle>
            <DialogDescription>
              Add a new tool definition to the registry for use in conversation simulations.
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
              <Label htmlFor="tool-schema">Input Schema (JSON)</Label>
              <Textarea
                id="tool-schema"
                value={formInputSchema}
                onChange={e => setFormInputSchema(e.target.value)}
                className="min-h-[120px] font-mono text-xs"
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
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Tools"
        description={`${tools.length} tools in registry`}
        actions={<RegisterToolButton />}
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
      {filtered.length === 0 ? (
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
          {filtered.map(tool => (
            <Link key={tool.name} href={`/dashboard/tools/${encodeURIComponent(tool.name)}`}>
              <Card className="h-full cursor-pointer transition-all hover:shadow-sm hover:ring-1 hover:ring-border">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-sm">{tool.name}</CardTitle>
                    {tool.requires_auth ? (
                      <Lock className="size-3.5 shrink-0 text-amber-500" />
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
                    {/* Execution mode */}
                    <StatusBadge
                      variant={EXECUTION_MODE_VARIANT[tool.execution_mode] ?? 'default'}
                      dot={false}
                    >
                      {tool.execution_mode}
                    </StatusBadge>

                    {/* Category */}
                    <Badge variant="outline" className="text-[10px]">
                      {tool.category}
                    </Badge>

                    {/* Domains */}
                    {tool.domains.map(domain => (
                      <Badge
                        key={domain}
                        variant="secondary"
                        className={cn('text-[10px]', DOMAIN_COLORS[domain])}
                      >
                        {domain.split('.').pop()}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Register dialog (always rendered so it can open) */}
      <RegisterToolDialog />
    </div>
  )
}
