'use client'

import { useCallback, useMemo, useState } from 'react'

import {
  Download,
  FileDown,
  Loader2,
  PackageOpen,
  Server,
  ShieldCheck,
  Trash2
} from 'lucide-react'

import type { Conversation, QualityReport, RenderRequest, SeedSchema, TemplateInfo } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'

import { useApi } from '@/hooks/use-api'
import { downloadExport, fetchTemplates } from '@/lib/api/templates'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { DatasetCertification } from '../dataset-certification'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

// ─── Local Storage Keys ───
const CONVERSATIONS_KEY = 'uncase-conversations'
const EXPORTS_KEY = 'uncase-exports'
const EVALUATIONS_KEY = 'uncase-evaluations'
const SEEDS_KEY = 'uncase-seeds'

// ─── Types ───
interface ExportRecord {
  id: string
  name: string
  template: string
  domain: string
  conversation_count: number
  format: 'api' | 'jsonl'
  size_bytes: number
  created_at: string
  conversation_ids: string[]
}

// ─── Storage helpers ───
function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadExports(): ExportRecord[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(EXPORTS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveExports(exports: ExportRecord[]) {
  localStorage.setItem(EXPORTS_KEY, JSON.stringify(exports))
}

function loadEvaluations(): QualityReport[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(EVALUATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(SEEDS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

// ─── Helpers ───
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

function triggerDownload(content: string, filename: string) {
  const blob = new Blob([content], { type: 'application/jsonl' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')

  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')

  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export function ExportPage() {
  const [conversations] = useState<Conversation[]>(() => loadConversations())
  const [evaluations] = useState<QualityReport[]>(() => loadEvaluations())
  const [seeds] = useState<SeedSchema[]>(() => loadSeeds())
  const [exports, setExports] = useState<ExportRecord[]>(() => loadExports())
  const [certOpen, setCertOpen] = useState(false)

  // Template loading
  const { data: templates, loading: templatesLoading } = useApi<TemplateInfo[]>(
    useCallback((signal: AbortSignal) => fetchTemplates(signal), [])
  )

  // Export builder state
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [syntheticOnly, setSyntheticOnly] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [toolCallMode, setToolCallMode] = useState<'none' | 'inline'>('none')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [exportName, setExportName] = useState('')
  const [exporting, setExporting] = useState(false)

  // ─── Filtered conversations ───
  const filteredConversations = useMemo(() => {
    let result = conversations

    if (domainFilter !== 'all') {
      result = result.filter(c => c.dominio === domainFilter)
    }

    if (syntheticOnly) {
      result = result.filter(c => c.es_sintetica)
    }

    return result
  }, [conversations, domainFilter, syntheticOnly])

  // ─── Estimated size ───
  const estimatedSize = useMemo(() => {
    const jsonl = filteredConversations
      .map(c => JSON.stringify(c))
      .join('\n')

    return new Blob([jsonl]).size
  }, [filteredConversations])

  // ─── Domain stats ───
  const domainCounts = useMemo(() => {
    const counts: Record<string, number> = {}

    for (const c of conversations) {
      counts[c.dominio] = (counts[c.dominio] || 0) + 1
    }

    return counts
  }, [conversations])

  // ─── Quality certificate ───
  const qualityCertificate = useMemo(() => {
    if (filteredConversations.length === 0 || evaluations.length === 0) return null

    const relevantEvals = evaluations.filter(e =>
      filteredConversations.some(c => c.conversation_id === e.conversation_id)
    )

    if (relevantEvals.length === 0) return null

    const avgComposite = relevantEvals.reduce((sum, e) => sum + e.composite_score, 0) / relevantEvals.length
    const avgRouge = relevantEvals.reduce((sum, e) => sum + e.metrics.rouge_l, 0) / relevantEvals.length
    const avgFidelity = relevantEvals.reduce((sum, e) => sum + e.metrics.fidelidad_factual, 0) / relevantEvals.length
    const avgTTR = relevantEvals.reduce((sum, e) => sum + e.metrics.diversidad_lexica, 0) / relevantEvals.length
    const avgCoherence = relevantEvals.reduce((sum, e) => sum + e.metrics.coherencia_dialogica, 0) / relevantEvals.length
    const passRate = Math.round((relevantEvals.filter(e => e.passed).length / relevantEvals.length) * 100)
    const evaluated = relevantEvals.length
    const total = filteredConversations.length

    return {
      avgComposite,
      avgRouge,
      avgFidelity,
      avgTTR,
      avgCoherence,
      passRate,
      evaluated,
      total
    }
  }, [filteredConversations, evaluations])

  // ─── Export via API ───
  async function handleExportApi() {
    if (filteredConversations.length === 0 || !selectedTemplate) return

    setExporting(true)

    const req: RenderRequest = {
      conversations: filteredConversations,
      template_name: selectedTemplate,
      tool_call_mode: toolCallMode,
      ...(systemPrompt.trim() ? { system_prompt: systemPrompt.trim() } : {})
    }

    const blob = await downloadExport(req)

    if (blob) {
      const filename = `${exportName || 'uncase-export'}-${selectedTemplate}.txt`

      triggerBlobDownload(blob, filename)

      const record: ExportRecord = {
        id: crypto.randomUUID(),
        name: exportName || 'Untitled Export',
        template: selectedTemplate,
        domain: domainFilter,
        conversation_count: filteredConversations.length,
        format: 'api',
        size_bytes: blob.size,
        created_at: new Date().toISOString(),
        conversation_ids: filteredConversations.map(c => c.conversation_id)
      }

      const updated = [record, ...exports]

      setExports(updated)
      saveExports(updated)
    }

    setExporting(false)
  }

  // ─── Export as JSONL ───
  function handleExportJsonl() {
    if (filteredConversations.length === 0) return

    const jsonl = filteredConversations
      .map(c => JSON.stringify(c))
      .join('\n')

    const filename = `${exportName || 'uncase-export'}.jsonl`

    triggerDownload(jsonl, filename)

    const sizeBytes = new Blob([jsonl]).size

    const record: ExportRecord = {
      id: crypto.randomUUID(),
      name: exportName || 'Untitled Export',
      template: 'raw-jsonl',
      domain: domainFilter,
      conversation_count: filteredConversations.length,
      format: 'jsonl',
      size_bytes: sizeBytes,
      created_at: new Date().toISOString(),
      conversation_ids: filteredConversations.map(c => c.conversation_id)
    }

    const updated = [record, ...exports]

    setExports(updated)
    saveExports(updated)
  }

  // ─── Re-download from history ───
  function handleRedownload(record: ExportRecord) {
    const allConversations = loadConversations()
    const idSet = new Set(record.conversation_ids)
    const selected = allConversations.filter(c => idSet.has(c.conversation_id))

    if (selected.length === 0) return

    const jsonl = selected.map(c => JSON.stringify(c)).join('\n')
    const filename = `${record.name}.jsonl`

    triggerDownload(jsonl, filename)
  }

  // ─── Delete export record ───
  function handleDeleteExport(id: string) {
    const updated = exports.filter(e => e.id !== id)

    setExports(updated)
    saveExports(updated)
  }

  // ─── Table columns ───
  const exportColumns: Column<ExportRecord>[] = [
    {
      key: 'name',
      header: 'Name',
      cell: row => <span className="text-xs font-medium">{row.name}</span>
    },
    {
      key: 'template',
      header: 'Template',
      cell: row => <Badge variant="secondary" className="text-[10px]">{row.template}</Badge>
    },
    {
      key: 'domain',
      header: 'Domain',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {row.domain === 'all' ? 'All' : row.domain.split('.').pop()}
        </span>
      )
    },
    {
      key: 'count',
      header: 'Conversations',
      cell: row => <span className="text-xs">{row.conversation_count}</span>
    },
    {
      key: 'format',
      header: 'Format',
      cell: row => (
        <StatusBadge variant={row.format === 'api' ? 'info' : 'default'} dot={false}>
          {row.format.toUpperCase()}
        </StatusBadge>
      )
    },
    {
      key: 'size',
      header: 'Size',
      cell: row => <span className="text-xs text-muted-foreground">{formatBytes(row.size_bytes)}</span>
    },
    {
      key: 'date',
      header: 'Date',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    },
    {
      key: 'actions',
      header: '',
      cell: row => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="size-7"
            onClick={e => { e.stopPropagation(); handleRedownload(row) }}
          >
            <Download className="size-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="size-7"
            onClick={e => { e.stopPropagation(); handleDeleteExport(row.id) }}
          >
            <Trash2 className="size-3.5 text-destructive" />
          </Button>
        </div>
      ),
      className: 'w-20'
    }
  ]

  // ─── Empty state ───
  if (conversations.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Export Center"
          description="Export conversation datasets for fine-tuning"
        />
        <EmptyState
          icon={PackageOpen}
          title="No conversations to export"
          description="Import or generate conversations first, then come back to export datasets."
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Export Center"
        description={`${conversations.length} conversations available for export`}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Export Builder */}
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Export Builder</CardTitle>
              <CardDescription className="text-xs">
                Configure and export your conversation dataset.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Export name */}
              <div className="space-y-2">
                <Label className="text-xs">Export Name</Label>
                <Input
                  value={exportName}
                  onChange={e => setExportName(e.target.value)}
                  placeholder="my-training-dataset"
                />
              </div>

              {/* Filters row */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-xs">Domain Filter</Label>
                  <Select value={domainFilter} onValueChange={setDomainFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All domains" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Domains</SelectItem>
                      {SUPPORTED_DOMAINS.map(d => (
                        <SelectItem key={d} value={d}>
                          {d.split('.').pop()} ({domainCounts[d] || 0})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-xs">Template</Label>
                  <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                    <SelectTrigger>
                      <SelectValue placeholder={templatesLoading ? 'Loading...' : 'Select template'} />
                    </SelectTrigger>
                    <SelectContent>
                      {templates?.map(t => (
                        <SelectItem key={t.name} value={t.name}>
                          {t.display_name}
                        </SelectItem>
                      )) ?? []}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Options row */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-xs">Tool Call Mode</Label>
                  <Select
                    value={toolCallMode}
                    onValueChange={v => setToolCallMode(v as 'none' | 'inline')}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      <SelectItem value="inline">Inline</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center justify-between rounded-md border px-3 py-2">
                  <div>
                    <Label className="text-xs">Synthetic Only</Label>
                    <p className="text-[10px] text-muted-foreground">Only include synthetic data</p>
                  </div>
                  <Switch
                    checked={syntheticOnly}
                    onCheckedChange={setSyntheticOnly}
                  />
                </div>
              </div>

              {/* System prompt */}
              <div className="space-y-2">
                <Label className="text-xs">System Prompt (optional)</Label>
                <Textarea
                  value={systemPrompt}
                  onChange={e => setSystemPrompt(e.target.value)}
                  placeholder="Optional system prompt to prepend to each conversation..."
                  className="min-h-[80px]"
                />
              </div>

              {/* Preview */}
              <div className="rounded-md border bg-muted/50 p-3">
                <p className="text-xs font-medium">Export Preview</p>
                <div className="mt-1 grid grid-cols-3 gap-2 text-[11px] text-muted-foreground">
                  <div>
                    Conversations: <strong className="text-foreground">{filteredConversations.length}</strong>
                  </div>
                  <div>
                    Estimated size: <strong className="text-foreground">{formatBytes(estimatedSize)}</strong>
                  </div>
                  <div>
                    Template: <strong className="text-foreground">{selectedTemplate || 'none'}</strong>
                  </div>
                </div>
              </div>

              {/* Export buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={handleExportApi}
                  disabled={exporting || filteredConversations.length === 0 || !selectedTemplate}
                >
                  {exporting ? (
                    <Loader2 className="mr-1.5 size-4 animate-spin" />
                  ) : (
                    <Server className="mr-1.5 size-4" />
                  )}
                  Export via API
                </Button>
                <Button
                  variant="outline"
                  onClick={handleExportJsonl}
                  disabled={filteredConversations.length === 0}
                >
                  <FileDown className="mr-1.5 size-4" />
                  Export as JSONL
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setCertOpen(true)}
                  disabled={filteredConversations.length === 0}
                >
                  <ShieldCheck className="mr-1.5 size-4" />
                  Download Certification
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quality Certificate */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="size-4 text-muted-foreground" />
                <CardTitle className="text-sm font-medium">Quality Certificate</CardTitle>
              </div>
              <CardDescription className="text-xs">
                Average quality scores for the selected conversations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {qualityCertificate ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Evaluated</span>
                    <span className="text-xs font-medium">
                      {qualityCertificate.evaluated} / {qualityCertificate.total}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Pass Rate</span>
                    <StatusBadge variant={qualityCertificate.passRate >= 80 ? 'success' : qualityCertificate.passRate >= 50 ? 'warning' : 'error'}>
                      {qualityCertificate.passRate}%
                    </StatusBadge>
                  </div>
                  <div className="space-y-2 border-t pt-2">
                    {[
                      { label: 'Composite', value: qualityCertificate.avgComposite },
                      { label: 'ROUGE-L', value: qualityCertificate.avgRouge },
                      { label: 'Fidelity', value: qualityCertificate.avgFidelity },
                      { label: 'TTR', value: qualityCertificate.avgTTR },
                      { label: 'Coherence', value: qualityCertificate.avgCoherence }
                    ].map(metric => (
                      <div key={metric.label} className="flex items-center justify-between">
                        <span className="text-[11px] text-muted-foreground">{metric.label}</span>
                        <span className="text-[11px] font-mono font-medium">
                          {metric.value.toFixed(3)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">
                  No evaluations available for the selected conversations. Run evaluations first to see quality metrics.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Quick stats */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Dataset Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(domainCounts).map(([domain, count]) => (
                <div key={domain} className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[10px]">
                    {domain.split('.').pop()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{count} conversations</span>
                </div>
              ))}
              <div className="border-t pt-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Synthetic</span>
                  <span className="text-xs font-medium">
                    {conversations.filter(c => c.es_sintetica).length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Real</span>
                  <span className="text-xs font-medium">
                    {conversations.filter(c => !c.es_sintetica).length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Export History */}
      {exports.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Export History</h3>
          <DataTable
            columns={exportColumns}
            data={exports}
            rowKey={r => r.id}
            emptyMessage="No exports yet"
          />
        </div>
      )}

      {/* Certification dialog */}
      <DatasetCertification
        open={certOpen}
        onOpenChange={setCertOpen}
        conversations={filteredConversations}
        evaluations={evaluations}
        seeds={seeds}
        exportName={exportName}
        domain={domainFilter}
        template={selectedTemplate}
      />
    </div>
  )
}
