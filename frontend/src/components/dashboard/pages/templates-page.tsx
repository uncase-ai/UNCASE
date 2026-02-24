'use client'

import { useCallback, useMemo, useState } from 'react'

import { Download, Eye, FileText, FlipHorizontal2, Loader2, Play } from 'lucide-react'

import type { Conversation, RenderRequest, TemplateInfo } from '@/types/api'
import { cn } from '@/lib/utils'
import { useApi } from '@/hooks/use-api'
import { downloadExport, fetchTemplates, renderTemplate } from '@/lib/api/templates'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

const SAMPLE_CONVERSATION: Conversation = {
  conversation_id: 'sample-001',
  seed_id: 'seed-demo',
  dominio: 'automotive.sales',
  idioma: 'es',
  turnos: [
    { turno: 1, rol: 'cliente', contenido: 'Busco un SUV familiar con buen consumo.', herramientas_usadas: [], metadata: {} },
    { turno: 2, rol: 'agente', contenido: 'Tenemos el Modelo X con 15km/l. Tiene 7 asientos y c\u00e1mara 360\u00b0.', herramientas_usadas: ['consultar_inventario'], metadata: {} },
    { turno: 3, rol: 'cliente', contenido: '\u00bfTienen disponibilidad en color blanco?', herramientas_usadas: [], metadata: {} },
    { turno: 4, rol: 'agente', contenido: 'S\u00ed, tenemos 3 unidades en blanco perla disponibles para entrega inmediata.', herramientas_usadas: ['verificar_disponibilidad'], metadata: {} }
  ],
  es_sintetica: false,
  created_at: new Date().toISOString(),
  metadata: {}
}

export function TemplatesPage() {
  const { data: templates, loading, error } = useApi<TemplateInfo[]>(
    useCallback((signal: AbortSignal) => fetchTemplates(signal), [])
  )

  // Selection state — single or compare mode
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([])
  const [compareMode, setCompareMode] = useState(false)
  const [toolCallMode, setToolCallMode] = useState<'none' | 'inline'>('none')

  // Conversation JSON input
  const [conversationJson, setConversationJson] = useState('')
  const [jsonError, setJsonError] = useState<string | null>(null)

  // Render state — supports two panels for compare mode
  const [renderedOutput, setRenderedOutput] = useState<string[]>([])
  const [renderedOutputB, setRenderedOutputB] = useState<string[]>([])
  const [rendering, setRendering] = useState(false)
  const [renderingB, setRenderingB] = useState(false)

  const maxSelections = compareMode ? 2 : 1

  function handleSelectTemplate(name: string) {
    setSelectedTemplates(prev => {
      if (prev.includes(name)) {
        return prev.filter(n => n !== name)
      }

      if (prev.length >= maxSelections) {
        // Replace last selection
        return [...prev.slice(0, maxSelections - 1), name]
      }

      return [...prev, name]
    })

    // Clear previous renders when selection changes
    setRenderedOutput([])
    setRenderedOutputB([])
  }

  function handleToggleCompare() {
    const next = !compareMode

    setCompareMode(next)

    if (!next && selectedTemplates.length > 1) {
      setSelectedTemplates(prev => [prev[0]])
    }

    setRenderedOutput([])
    setRenderedOutputB([])
  }

  function parseConversation(): Conversation | null {
    setJsonError(null)

    if (!conversationJson.trim()) {
      setJsonError('Paste a conversation JSON to render')

      return null
    }

    try {
      const parsed = JSON.parse(conversationJson) as Conversation

      if (!parsed.turnos || !Array.isArray(parsed.turnos)) {
        setJsonError('Invalid conversation: missing "turnos" array')

        return null
      }

      return parsed
    } catch {
      setJsonError('Invalid JSON — check syntax and try again')

      return null
    }
  }

  async function handleRender() {
    const conversation = parseConversation()

    if (!conversation) return

    if (selectedTemplates.length === 0) {
      setJsonError('Select at least one template')

      return
    }

    const reqA: RenderRequest = {
      conversations: [conversation],
      template_name: selectedTemplates[0],
      tool_call_mode: toolCallMode
    }

    setRendering(true)
    setRenderedOutput([])

    const resultA = await renderTemplate(reqA)

    if (resultA.data) {
      setRenderedOutput(resultA.data.rendered)
    } else {
      setJsonError(resultA.error?.message ?? 'Render failed')
    }

    setRendering(false)

    // Compare mode — render second template
    if (compareMode && selectedTemplates.length === 2) {
      const reqB: RenderRequest = {
        conversations: [conversation],
        template_name: selectedTemplates[1],
        tool_call_mode: toolCallMode
      }

      setRenderingB(true)
      setRenderedOutputB([])

      const resultB = await renderTemplate(reqB)

      if (resultB.data) {
        setRenderedOutputB(resultB.data.rendered)
      }

      setRenderingB(false)
    }
  }

  async function handleExport() {
    const conversation = parseConversation()

    if (!conversation || selectedTemplates.length === 0) return

    const req: RenderRequest = {
      conversations: [conversation],
      template_name: selectedTemplates[0],
      tool_call_mode: toolCallMode
    }

    const blob = await downloadExport(req)

    if (!blob) {
      setJsonError('Export failed — check the API connection')

      return
    }

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')

    a.href = url
    a.download = `${selectedTemplates[0]}-export.txt`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  function handleLoadSample() {
    setConversationJson(JSON.stringify(SAMPLE_CONVERSATION, null, 2))
    setJsonError(null)
  }

  const selectedDisplay = useMemo(() => {
    if (!templates) return []

    return selectedTemplates.map(name => templates.find(t => t.name === name)).filter(Boolean) as TemplateInfo[]
  }, [templates, selectedTemplates])

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Templates" description="Chat template browser and renderer" />
        <div className="flex items-center justify-center py-16">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader title="Templates" description="Chat template browser and renderer" />
        <EmptyState
          icon={FileText}
          title="Failed to load templates"
          description={error.message}
          action={<Button variant="outline" onClick={() => window.location.reload()}>Retry</Button>}
        />
      </div>
    )
  }

  if (!templates || templates.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Templates" description="Chat template browser and renderer" />
        <EmptyState
          icon={FileText}
          title="No templates available"
          description="The API returned no templates. Ensure the backend is running and templates are configured."
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Templates"
        description={`${templates.length} chat templates available`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant={compareMode ? 'default' : 'outline'}
              size="sm"
              onClick={handleToggleCompare}
            >
              <FlipHorizontal2 className="mr-1.5 size-4" />
              Compare
            </Button>
          </div>
        }
      />

      {/* Template grid */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {templates.map(template => {
          const isSelected = selectedTemplates.includes(template.name)
          const selectionIndex = selectedTemplates.indexOf(template.name)

          return (
            <Card
              key={template.name}
              className={cn(
                'cursor-pointer transition-all hover:shadow-sm',
                isSelected && 'ring-2 ring-primary ring-offset-2 ring-offset-background'
              )}
              onClick={() => handleSelectTemplate(template.name)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm">{template.display_name}</CardTitle>
                  {isSelected && compareMode && (
                    <Badge variant="default" className="shrink-0 text-[10px]">
                      {selectionIndex === 0 ? 'A' : 'B'}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {template.supports_tool_calls && (
                    <StatusBadge variant="success" dot={false}>
                      Tool Calls
                    </StatusBadge>
                  )}
                  {template.special_tokens.map(token => (
                    <Badge
                      key={token}
                      variant="secondary"
                      className="font-mono text-[10px]"
                    >
                      {token}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Render Preview Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Render Preview</h2>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">Tool call mode:</span>
            <ToggleGroup
              type="single"
              variant="outline"
              size="sm"
              value={toolCallMode}
              onValueChange={v => { if (v) setToolCallMode(v as 'none' | 'inline') }}
            >
              <ToggleGroupItem value="none">None</ToggleGroupItem>
              <ToggleGroupItem value="inline">Inline</ToggleGroupItem>
            </ToggleGroup>
          </div>
        </div>

        {/* JSON input */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Conversation JSON</label>
            <Button variant="ghost" size="sm" onClick={handleLoadSample}>
              Load sample
            </Button>
          </div>
          <Textarea
            value={conversationJson}
            onChange={e => {
              setConversationJson(e.target.value)
              setJsonError(null)
            }}
            placeholder='Paste a conversation JSON object here...'
            className="min-h-[200px] font-mono text-xs"
          />
          {jsonError && (
            <p className="text-xs text-destructive">{jsonError}</p>
          )}
        </div>

        {/* Selected templates summary */}
        {selectedDisplay.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Eye className="size-4" />
            <span>
              Rendering with:{' '}
              {selectedDisplay.map((t, i) => (
                <span key={t.name}>
                  {i > 0 && ' vs '}
                  <strong className="text-foreground">{t.display_name}</strong>
                </span>
              ))}
            </span>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleRender}
            disabled={rendering || renderingB || selectedTemplates.length === 0}
          >
            {rendering || renderingB ? (
              <Loader2 className="mr-1.5 size-4 animate-spin" />
            ) : (
              <Play className="mr-1.5 size-4" />
            )}
            Render
          </Button>
          <Button
            variant="outline"
            onClick={handleExport}
            disabled={selectedTemplates.length === 0 || !conversationJson.trim()}
          >
            <Download className="mr-1.5 size-4" />
            Export
          </Button>
        </div>

        {/* Render output panels */}
        {compareMode && selectedTemplates.length === 2 ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-2">
              <h3 className="text-sm font-medium">
                A: {selectedDisplay[0]?.display_name ?? selectedTemplates[0]}
              </h3>
              <pre className="max-h-[400px] overflow-auto rounded-lg border bg-muted/50 p-4 text-xs">
                {rendering ? 'Rendering...' : renderedOutput.length > 0 ? renderedOutput.join('\n---\n') : 'Click "Render" to see output'}
              </pre>
            </div>
            <div className="space-y-2">
              <h3 className="text-sm font-medium">
                B: {selectedDisplay[1]?.display_name ?? selectedTemplates[1]}
              </h3>
              <pre className="max-h-[400px] overflow-auto rounded-lg border bg-muted/50 p-4 text-xs">
                {renderingB ? 'Rendering...' : renderedOutputB.length > 0 ? renderedOutputB.join('\n---\n') : 'Click "Render" to see output'}
              </pre>
            </div>
          </div>
        ) : (
          renderedOutput.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium">Output</h3>
              <pre className="max-h-[400px] overflow-auto rounded-lg border bg-muted/50 p-4 text-xs">
                {renderedOutput.join('\n---\n')}
              </pre>
            </div>
          )
        )}
      </div>
    </div>
  )
}
