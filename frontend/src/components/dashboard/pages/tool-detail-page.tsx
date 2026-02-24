'use client'

import { useCallback, useState } from 'react'

import Link from 'next/link'
import { ArrowLeft, Loader2, Play, Puzzle } from 'lucide-react'

import type { ToolDefinition, ToolResult } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { fetchTool, simulateTool } from '@/lib/api/tools'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

import { EmptyState } from '../empty-state'
import { JsonViewer } from '../json-viewer'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

interface ToolDetailPageProps {
  name: string
}

const EXECUTION_MODE_VARIANT: Record<string, 'success' | 'warning' | 'info'> = {
  live: 'success',
  simulated: 'info',
  mock: 'warning'
}

interface SchemaProperty {
  type?: string
  description?: string
  enum?: string[]
  default?: unknown
}

interface InputSchema {
  type?: string
  properties?: Record<string, SchemaProperty>
  required?: string[]
}

function buildInitialArgs(schema: InputSchema): Record<string, unknown> {
  const args: Record<string, unknown> = {}
  const properties = schema.properties ?? {}

  for (const [key, prop] of Object.entries(properties)) {
    if (prop.default !== undefined) {
      args[key] = prop.default
    } else if (prop.type === 'boolean') {
      args[key] = false
    } else if (prop.type === 'number' || prop.type === 'integer') {
      args[key] = 0
    } else if (prop.enum && prop.enum.length > 0) {
      args[key] = prop.enum[0]
    } else if (prop.type === 'string') {
      args[key] = ''
    } else {
      args[key] = ''
    }
  }

  return args
}

function PropertyField({
  propKey,
  prop,
  value,
  required,
  onChange
}: {
  propKey: string
  prop: SchemaProperty
  value: unknown
  required: boolean
  onChange: (key: string, value: unknown) => void
}) {
  const label = prop.description || propKey
  const labelId = `field-${propKey}`

  // Boolean -> Switch
  if (prop.type === 'boolean') {
    return (
      <div className="flex items-center justify-between gap-4">
        <Label htmlFor={labelId} className="text-sm">
          {label}
          {required && <span className="ml-0.5 text-destructive">*</span>}
        </Label>
        <Switch
          id={labelId}
          checked={value === true}
          onCheckedChange={checked => onChange(propKey, checked)}
        />
      </div>
    )
  }

  // Enum -> Select
  if (prop.enum && prop.enum.length > 0) {
    return (
      <div className="space-y-2">
        <Label htmlFor={labelId}>
          {label}
          {required && <span className="ml-0.5 text-destructive">*</span>}
        </Label>
        <Select value={String(value ?? '')} onValueChange={v => onChange(propKey, v)}>
          <SelectTrigger id={labelId} className="w-full">
            <SelectValue placeholder={`Select ${propKey}`} />
          </SelectTrigger>
          <SelectContent>
            {prop.enum.map(opt => (
              <SelectItem key={opt} value={opt}>
                {opt}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    )
  }

  // Number / integer -> Input type=number
  if (prop.type === 'number' || prop.type === 'integer') {
    return (
      <div className="space-y-2">
        <Label htmlFor={labelId}>
          {label}
          {required && <span className="ml-0.5 text-destructive">*</span>}
        </Label>
        <Input
          id={labelId}
          type="number"
          value={value === undefined || value === null ? '' : String(value)}
          onChange={e => {
            const num = prop.type === 'integer' ? parseInt(e.target.value, 10) : parseFloat(e.target.value)

            onChange(propKey, isNaN(num) ? 0 : num)
          }}
          placeholder={`Enter ${propKey}`}
        />
      </div>
    )
  }

  // String -> Input
  if (prop.type === 'string') {
    return (
      <div className="space-y-2">
        <Label htmlFor={labelId}>
          {label}
          {required && <span className="ml-0.5 text-destructive">*</span>}
        </Label>
        <Input
          id={labelId}
          value={String(value ?? '')}
          onChange={e => onChange(propKey, e.target.value)}
          placeholder={`Enter ${propKey}`}
        />
      </div>
    )
  }

  // Fallback: Textarea for JSON
  return (
    <div className="space-y-2">
      <Label htmlFor={labelId}>
        {label}
        {required && <span className="ml-0.5 text-destructive">*</span>}
      </Label>
      <Textarea
        id={labelId}
        value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
        onChange={e => {
          try {
            onChange(propKey, JSON.parse(e.target.value))
          } catch {
            onChange(propKey, e.target.value)
          }
        }}
        placeholder={`Enter ${propKey} as JSON`}
        className="min-h-[80px] font-mono text-xs"
      />
    </div>
  )
}

export function ToolDetailPage({ name }: ToolDetailPageProps) {
  const { data: tool, loading, error, retry } = useApi<ToolDefinition>(
    useCallback((signal: AbortSignal) => fetchTool(name, signal), [name])
  )

  const [args, setArgs] = useState<Record<string, unknown>>({})
  const [argsInitialized, setArgsInitialized] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [simulationResult, setSimulationResult] = useState<ToolResult | null>(null)
  const [simulationError, setSimulationError] = useState<string | null>(null)

  // Initialize args from schema once tool loads
  if (tool && !argsInitialized) {
    const schema = tool.input_schema as InputSchema

    setArgs(buildInitialArgs(schema))
    setArgsInitialized(true)
  }

  function handleArgChange(key: string, value: unknown) {
    setArgs(prev => ({ ...prev, [key]: value }))
  }

  async function handleSimulate() {
    if (!tool) return
    setSimulating(true)
    setSimulationError(null)
    setSimulationResult(null)

    const result = await simulateTool(tool.name, args)

    if (result.error) {
      setSimulationError(result.error.message)
    } else if (result.data) {
      setSimulationResult(result.data)
    }

    setSimulating(false)
  }

  // Loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Tool Details"
          actions={
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/tools">
                <ArrowLeft className="mr-1.5 size-4" />
                Back
              </Link>
            </Button>
          }
        />
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-8 w-48" />
          <div className="grid gap-4 lg:grid-cols-2">
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Tool Details"
          actions={
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/tools">
                <ArrowLeft className="mr-1.5 size-4" />
                Back
              </Link>
            </Button>
          }
        />
        <EmptyState
          icon={Puzzle}
          title="Failed to load tool"
          description={error.message}
          action={<Button variant="outline" onClick={retry}>Retry</Button>}
        />
      </div>
    )
  }

  if (!tool) return null

  const schema = tool.input_schema as InputSchema
  const properties = schema.properties ?? {}
  const requiredFields = new Set(schema.required ?? [])
  const hasProperties = Object.keys(properties).length > 0

  return (
    <div className="space-y-6">
      <PageHeader
        title={tool.name}
        description={tool.description}
        actions={
          <Button variant="outline" size="sm" asChild>
            <Link href="/dashboard/tools">
              <ArrowLeft className="mr-1.5 size-4" />
              Back to Tools
            </Link>
          </Button>
        }
      />

      {/* Tool Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Tool Information</CardTitle>
          <CardDescription>{tool.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-2">
            {/* Domains */}
            {tool.domains.map(domain => (
              <Badge key={domain} variant="secondary">
                {domain}
              </Badge>
            ))}

            {/* Category */}
            <Badge variant="outline">{tool.category}</Badge>

            {/* Auth */}
            <Badge variant={tool.requires_auth ? 'destructive' : 'outline'}>
              {tool.requires_auth ? 'Auth Required' : 'No Auth'}
            </Badge>

            {/* Execution Mode */}
            <StatusBadge variant={EXECUTION_MODE_VARIANT[tool.execution_mode] ?? 'default'}>
              {tool.execution_mode}
            </StatusBadge>

            {/* Version */}
            <Badge variant="outline" className="font-mono text-[10px]">
              v{tool.version}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Schema Viewers */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Input Schema</CardTitle>
          </CardHeader>
          <CardContent>
            <JsonViewer data={tool.input_schema} maxHeight="300px" />
          </CardContent>
        </Card>

        {tool.output_schema && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Output Schema</CardTitle>
            </CardHeader>
            <CardContent>
              <JsonViewer data={tool.output_schema} maxHeight="300px" />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Simulation Playground */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Simulation Playground</CardTitle>
          <CardDescription>
            Test this tool by providing input arguments and running a simulation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Dynamic form from input_schema.properties */}
          {hasProperties ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {Object.entries(properties).map(([key, prop]) => (
                <PropertyField
                  key={key}
                  propKey={key}
                  prop={prop}
                  value={args[key]}
                  required={requiredFields.has(key)}
                  onChange={handleArgChange}
                />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              This tool has no input parameters defined.
            </p>
          )}

          {/* Simulate button */}
          <div className="flex items-center gap-3">
            <Button onClick={handleSimulate} disabled={simulating}>
              {simulating ? (
                <Loader2 className="mr-1.5 size-4 animate-spin" />
              ) : (
                <Play className="mr-1.5 size-4" />
              )}
              {simulating ? 'Simulating...' : 'Simulate'}
            </Button>
            {simulationError && (
              <p className="text-sm text-destructive">{simulationError}</p>
            )}
          </div>

          {/* Simulation Result */}
          {simulationResult && (
            <Card className="border-dashed">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <CardTitle className="text-sm">Simulation Result</CardTitle>
                  <StatusBadge
                    variant={
                      simulationResult.status === 'success'
                        ? 'success'
                        : simulationResult.status === 'error'
                          ? 'error'
                          : 'warning'
                    }
                  >
                    {simulationResult.status}
                  </StatusBadge>
                  {simulationResult.duration_ms !== undefined && (
                    <span className="text-xs text-muted-foreground">
                      {simulationResult.duration_ms}ms
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <JsonViewer data={simulationResult.result} maxHeight="300px" />
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
