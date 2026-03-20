'use client'

import { useCallback, useMemo, useRef, useState } from 'react'

import Link from 'next/link'
import {
  AlertCircle,
  ArrowDownToLine,
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  Copy,
  Eye,
  FileText,
  FileUp,
  Globe,
  Info,
  Loader2,
  Lock,
  Plug,
  RefreshCw,
  Save,
  ScanSearch,
  Server,
  Settings2,
  Shield,
  Sparkles,
  User,
  Users,
  Wrench,
  X,
  Zap
} from 'lucide-react'

import type { ImportResult, ToolDefinition } from '@/types/api'
import { cn } from '@/lib/utils'
import { detectFormat, importCsv, importJsonl, parseJsonlLocally } from '@/lib/api/imports'
import { scanConversationsForTools, generateToolsFromScan, deduplicateTools } from '@/lib/tool-scanner'
import type { ToolScanResult, ScannedTool } from '@/lib/tool-scanner'
import { generateMCPServer, validateToolForMCP } from '@/lib/mcp-generator'
import type { MCPDeploymentPreview } from '@/lib/mcp-generator'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

import { appendConversations } from './conversations-page'

// ─── Constants ───

type UploadState = 'idle' | 'dragover' | 'uploading' | 'done' | 'error'
type ImportStep = 'upload' | 'review' | 'scan' | 'tools' | 'mcp' | 'save'

const STEPS: { id: ImportStep; label: string; icon: typeof ArrowDownToLine }[] = [
  { id: 'upload', label: 'Upload', icon: ArrowDownToLine },
  { id: 'review', label: 'Review', icon: Eye },
  { id: 'scan', label: 'Tool Scan', icon: ScanSearch },
  { id: 'tools', label: 'Tools', icon: Wrench },
  { id: 'mcp', label: 'MCP Server', icon: Server },
  { id: 'save', label: 'Save', icon: Save },
]

const STATE_STYLES: Record<UploadState, string> = {
  idle: 'border-muted-foreground/25 bg-muted/20 hover:border-muted-foreground/40 hover:bg-muted/30',
  dragover: 'border-foreground/30 bg-muted/40 scale-[1.01]',
  uploading: 'border-muted-foreground/25 bg-muted/20 animate-pulse',
  done: 'border-foreground/30 bg-muted/30',
  error: 'border-destructive/30 bg-muted/20',
}

const VISIBILITY_OPTIONS = [
  { value: 'private', label: 'Private', icon: Lock, desc: 'Only you can use this tool' },
  { value: 'organization', label: 'Organization', icon: Users, desc: 'Shared with your org' },
  { value: 'public', label: 'Public', icon: Globe, desc: 'Listed in marketplace' },
] as const

const CATEGORY_COLORS: Record<string, string> = {
  query: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  action: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  validation: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  calculation: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  retrieval: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300',
  notification: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
  integration: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
}

// ─── Helper: role icon ───

function RoleIcon({ role }: { role: string }) {
  const isUser = ['user', 'usuario', 'cliente', 'paciente', 'alumno', 'operador'].includes(role.toLowerCase())

  return isUser
    ? <User className="size-3 text-muted-foreground" />
    : <Bot className="size-3 text-muted-foreground" />
}

// ─── Main Component ───

export function ImportPage() {
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Step navigation
  const [step, setStep] = useState<ImportStep>('upload')

  // Upload state
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [detectedFormat, setDetectedFormat] = useState<'csv' | 'jsonl' | 'unknown' | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  // Scan state
  const [scanning, setScanning] = useState(false)
  const [scanResults, setScanResults] = useState<ToolScanResult[]>([])
  const [scanProgress, setScanProgress] = useState(0)

  // Tool generation state
  const [generatedTools, setGeneratedTools] = useState<ScannedTool[]>([])
  const [selectedTools, setSelectedTools] = useState<Set<string>>(new Set())
  const [toolVisibility, setToolVisibility] = useState<Record<string, string>>({})
  const [expandedTool, setExpandedTool] = useState<string | null>(null)

  // MCP state
  const [mcpPreview, setMcpPreview] = useState<MCPDeploymentPreview | null>(null)
  const [mcpServerName, setMcpServerName] = useState('')
  const [mcpRateLimit, setMcpRateLimit] = useState(60)
  const [codeCopied, setCodeCopied] = useState(false)

  // Save state
  const [savedConversations, setSavedConversations] = useState(false)
  const [savedTools, setSavedTools] = useState(false)

  // ─── Derived ───

  const stepIdx = STEPS.findIndex(s => s.id === step)

  const scanSummary = useMemo(() => {
    if (scanResults.length === 0) return null
    const withTools = scanResults.filter(r => r.requires_tools)
    const allToolNames = new Set(scanResults.flatMap(r => r.identified_tools.map(t => t.name)))
    const allDomains = new Set(result?.conversations.map(c => c.dominio) ?? [])

    return {
      scanned: scanResults.length,
      withTools: withTools.length,
      uniqueTools: allToolNames.size,
      avgConfidence: scanResults.reduce((s, r) => s + r.confidence, 0) / scanResults.length,
      domains: [...allDomains],
    }
  }, [scanResults, result])

  const selectedToolsList = useMemo(
    () => generatedTools.filter(t => selectedTools.has(t.name)),
    [generatedTools, selectedTools]
  )

  // ─── Reset ───

  function resetAll() {
    setStep('upload')
    setUploadState('idle')
    setSelectedFile(null)
    setDetectedFormat(null)
    setResult(null)
    setUploadError(null)
    setScanning(false)
    setScanResults([])
    setScanProgress(0)
    setGeneratedTools([])
    setSelectedTools(new Set())
    setToolVisibility({})
    setExpandedTool(null)
    setMcpPreview(null)
    setMcpServerName('')
    setMcpRateLimit(60)
    setCodeCopied(false)
    setSavedConversations(false)
    setSavedTools(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // ─── Upload handlers ───

  function handleFileSelect(file: File) {
    const format = detectFormat(file.name)

    setSelectedFile(file)
    setDetectedFormat(format)
    setUploadError(null)
    setResult(null)

    if (format === 'unknown') {
      setUploadState('error')
      setUploadError('Unsupported file format. Please use .csv, .jsonl, or .ndjson files.')

      return
    }

    handleUpload(file, format)
  }

  async function handleUpload(file: File, format: 'csv' | 'jsonl') {
    setUploadState('uploading')
    setUploadError(null)

    const apiResult = format === 'csv' ? await importCsv(file) : await importJsonl(file)

    if (apiResult.data) {
      setResult(apiResult.data)
      setUploadState('done')
      setStep('review')

      return
    }

    if (format === 'jsonl') {
      try {
        const localResult = await parseJsonlLocally(file)

        if (localResult.conversations.length > 0 || localResult.errors.length > 0) {
          setResult(localResult)
          setUploadState('done')
          setStep('review')

          return
        }
      } catch {
        // Fall through to error
      }
    }

    setUploadState('error')
    setUploadError(apiResult.error?.message ?? 'Import failed')
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (uploadState !== 'uploading') setUploadState('dragover')
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (!['uploading', 'done', 'error'].includes(uploadState)) setUploadState('idle')
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files[0])
  }

  // ─── Tool scan ───

  const runToolScan = useCallback(async () => {
    if (!result || result.conversations.length === 0) return

    setScanning(true)
    setScanProgress(0)
    setScanResults([])

    // Simulate progressive scanning
    const convs = result.conversations
    const batchSize = Math.max(1, Math.ceil(convs.length / 5))
    const allResults: ToolScanResult[] = []

    for (let i = 0; i < convs.length; i += batchSize) {
      const batch = convs.slice(i, i + batchSize)
      const batchResults = await scanConversationsForTools(batch)

      allResults.push(...batchResults)
      setScanProgress(Math.round(((i + batch.length) / convs.length) * 100))

      // Small delay for UX
      await new Promise(r => setTimeout(r, 200))
    }

    setScanResults(allResults)
    setScanProgress(100)

    // Auto-generate tools from scan
    const tools = generateToolsFromScan(allResults)
    const unique = deduplicateTools(tools)

    setGeneratedTools(unique)
    setSelectedTools(new Set(unique.map(t => t.name)))

    // Default visibility
    const vis: Record<string, string> = {}

    for (const t of unique) vis[t.name] = t.visibility
    setToolVisibility(vis)

    setScanning(false)
    setStep('tools')
  }, [result])

  // ─── MCP generation ───

  function generateMCP() {
    if (selectedToolsList.length === 0) return

    const toolDefs: ToolDefinition[] = selectedToolsList.map(t => ({
      name: t.name,
      description: t.description,
      input_schema: t.input_schema as Record<string, unknown>,
      output_schema: t.output_schema as Record<string, unknown>,
      domains: t.domains,
      category: t.category,
      requires_auth: t.auth_type !== 'none',
      execution_mode: t.execution_mode,
      version: t.version,
      metadata: {
        method: t.method,
        endpoint_url: t.endpoint_url,
        auth_type: t.auth_type,
        fallback_strategy: t.fallback_strategy,
        error_handling: t.error_handling,
        rate_limit: t.rate_limit,
        mcp_compatible: t.mcp_compatible,
        visibility: toolVisibility[t.name] ?? 'private',
      },
    }))

    const name = mcpServerName.trim() || `uncase-${result?.conversations[0]?.dominio?.split('.')[0] ?? 'tools'}`

    const preview = generateMCPServer({
      serverName: name,
      description: `MCP server for ${toolDefs.length} tools from imported conversations`,
      tools: toolDefs,
      rateLimitPerMinute: mcpRateLimit,
      corsOrigins: ['*'],
    })

    setMcpPreview(preview)
    setStep('mcp')
  }

  // ─── Save ───

  function handleSaveConversations() {
    if (!result || result.conversations.length === 0) return
    appendConversations(result.conversations)
    setSavedConversations(true)
  }

  function handleSaveTools() {
    if (selectedToolsList.length === 0) return

    const toolDefs: ToolDefinition[] = selectedToolsList.map(t => ({
      name: t.name,
      description: t.description,
      input_schema: t.input_schema as Record<string, unknown>,
      output_schema: t.output_schema as Record<string, unknown>,
      domains: t.domains,
      category: t.category,
      requires_auth: t.auth_type !== 'none',
      execution_mode: t.execution_mode,
      version: t.version,
      metadata: {
        method: t.method,
        endpoint_url: t.endpoint_url,
        auth_type: t.auth_type,
        fallback_strategy: t.fallback_strategy,
        error_handling: t.error_handling,
        rate_limit: t.rate_limit,
        mcp_compatible: t.mcp_compatible,
        visibility: toolVisibility[t.name] ?? 'private',
        source: 'import_scan',
        imported_at: new Date().toISOString(),
      },
    }))

    try {
      const existing: ToolDefinition[] = JSON.parse(localStorage.getItem('uncase-tools') || '[]')
      const existingNames = new Set(existing.map(t => t.name))
      const newTools = toolDefs.filter(t => !existingNames.has(t.name))

      localStorage.setItem('uncase-tools', JSON.stringify([...existing, ...newTools]))
      window.dispatchEvent(new StorageEvent('storage', { key: 'uncase-tools' }))
      setSavedTools(true)
    } catch {
      // storage full
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text)
    setCodeCopied(true)
    setTimeout(() => setCodeCopied(false), 2000)
  }

  // ─── Render: Step indicator ───

  function renderStepIndicator() {
    return (
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {STEPS.map((s, i) => {
          const StepIcon = s.icon
          const isActive = s.id === step
          const isComplete = i < stepIdx
          const isClickable = isComplete || (s.id === 'review' && result)

          return (
            <div key={s.id} className="flex items-center">
              {i > 0 && (
                <div className={cn('mx-1 h-px w-4 sm:w-8', isComplete ? 'bg-foreground/40' : 'bg-muted-foreground/20')} />
              )}
              <button
                className={cn(
                  'flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
                  isActive && 'bg-foreground text-background',
                  isComplete && !isActive && 'bg-muted text-foreground',
                  !isActive && !isComplete && 'text-muted-foreground',
                  isClickable && !isActive && 'cursor-pointer hover:bg-muted'
                )}
                onClick={() => isClickable && setStep(s.id)}
                disabled={!isClickable && !isActive}
              >
                {isComplete && !isActive ? (
                  <CheckCircle2 className="size-3" />
                ) : (
                  <StepIcon className="size-3" />
                )}
                <span className="hidden sm:inline">{s.label}</span>
              </button>
            </div>
          )
        })}
      </div>
    )
  }

  // ─── Render: Upload step ───

  function renderUploadStep() {
    return (
      <div className="space-y-4">
        <Card className="bg-muted/40">
          <CardContent className="flex items-start gap-3 p-4">
            <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
            <div className="space-y-1 text-xs text-muted-foreground">
              <p className="text-base font-semibold text-foreground">Import &amp; Tool Discovery Pipeline</p>
              <p>
                Upload conversation data, then our scanner analyzes it to identify tool usage patterns and automatically
                generates robust, MCP-compatible tool definitions ready for the pipeline. Supports OpenAI, ShareGPT,
                and UNCASE native formats.
              </p>
            </div>
          </CardContent>
        </Card>

        <div
          className={cn(
            'relative flex min-h-[240px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-all',
            STATE_STYLES[uploadState]
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploadState === 'uploading' ? (
            <Loader2 className="mb-4 size-10 animate-spin text-muted-foreground" />
          ) : uploadState === 'error' ? (
            <AlertCircle className="mb-4 size-10 text-destructive" />
          ) : uploadState === 'dragover' ? (
            <FileUp className="mb-4 size-10 text-foreground" />
          ) : (
            <ArrowDownToLine className="mb-4 size-10 text-muted-foreground" />
          )}

          {uploadState === 'uploading' && (
            <p className="text-sm text-muted-foreground">Processing file...</p>
          )}
          {uploadState === 'error' && uploadError && (
            <>
              <p className="mb-2 text-sm text-destructive">{uploadError}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={e => { e.stopPropagation(); if (selectedFile && detectedFormat && detectedFormat !== 'unknown') handleUpload(selectedFile, detectedFormat) }}>
                  <RefreshCw className="mr-1.5 size-3" /> Retry
                </Button>
              </div>
            </>
          )}
          {!uploadError && uploadState !== 'uploading' && (
            <>
              <p className="mb-1 text-sm font-medium">
                {uploadState === 'dragover' ? 'Drop your file here' : 'Drag and drop your file here'}
              </p>
              <p className="mb-4 text-xs text-muted-foreground">
                Supports .csv, .jsonl, and .ndjson — OpenAI, ShareGPT, or UNCASE format
              </p>
              <Button variant="outline" size="sm" onClick={e => { e.stopPropagation(); fileInputRef.current?.click() }}>
                Browse files
              </Button>
            </>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.jsonl,.ndjson"
            className="hidden"
            onChange={e => { if (e.target.files?.[0]) handleFileSelect(e.target.files[0]) }}
          />
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { label: 'CSV', desc: 'conversation_id, role, content columns', ext: '.csv' },
            { label: 'JSONL', desc: '{"messages": [...]} per line', ext: '.jsonl' },
            { label: 'NDJSON', desc: 'Native UNCASE conversation objects', ext: '.ndjson' },
          ].map(f => (
            <Card key={f.label} className="bg-muted/30">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <FileText className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs font-medium">{f.label}</p>
                    <p className="text-xs text-muted-foreground">{f.desc}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  // ─── Render: Review step ───

  function renderReviewStep() {
    if (!result) return null

    const convs = result.conversations
    const domains = [...new Set(convs.map(c => c.dominio))]
    const toolsUsed = new Set(convs.flatMap(c => c.turnos.flatMap(t => t.herramientas_usadas)))
    const avgTurns = convs.length > 0 ? Math.round(convs.reduce((s, c) => s + c.turnos.length, 0) / convs.length) : 0

    return (
      <div className="space-y-4">
        {/* File info */}
        {selectedFile && (
          <div className="flex items-center gap-3">
            <FileText className="size-4 text-muted-foreground" />
            <span className="text-sm font-medium">{selectedFile.name}</span>
            <Badge variant="secondary" className="text-xs uppercase">{detectedFormat}</Badge>
            <Badge variant="outline" className="text-xs">{(selectedFile.size / 1024).toFixed(1)} KB</Badge>
          </div>
        )}

        {/* Stats grid */}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{result.conversations_imported}</p>
              <p className="text-xs text-muted-foreground">Conversations imported</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{avgTurns}</p>
              <p className="text-xs text-muted-foreground">Avg turns per conversation</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{domains.length}</p>
              <p className="text-xs text-muted-foreground">Domains detected</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{toolsUsed.size}</p>
              <p className="text-xs text-muted-foreground">Explicit tool references</p>
            </CardContent>
          </Card>
        </div>

        {result.conversations_failed > 0 && (
          <Card className="border-destructive/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-destructive">
                {result.conversations_failed} Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-20">Line</TableHead>
                    <TableHead>Error</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.errors.slice(0, 10).map((err, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-mono text-xs">{err.line}</TableCell>
                      <TableCell className="text-xs text-destructive">{err.error}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {result.errors.length > 10 && (
                <p className="mt-2 text-xs text-muted-foreground">+{result.errors.length - 10} more errors</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Conversation preview */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Conversation Preview</CardTitle>
            <CardDescription className="text-xs">
              Showing first {Math.min(5, convs.length)} of {convs.length} conversations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {convs.slice(0, 5).map(conv => (
              <div key={conv.conversation_id} className="rounded-lg border p-3">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-muted-foreground">{conv.conversation_id.slice(0, 12)}...</span>
                  <Badge variant="secondary" className="text-xs">{conv.dominio}</Badge>
                  <Badge variant="outline" className="text-xs">{conv.turnos.length} turns</Badge>
                  <Badge variant="outline" className="text-xs uppercase">{conv.idioma}</Badge>
                  {conv.turnos.some(t => t.herramientas_usadas.length > 0) && (
                    <Badge variant="outline" className="gap-1 text-xs">
                      <Wrench className="size-2.5" /> Tools
                    </Badge>
                  )}
                </div>
                <div className="space-y-1">
                  {conv.turnos.slice(0, 3).map(turn => (
                    <div key={turn.turno} className="flex items-start gap-2 text-xs">
                      <RoleIcon role={turn.rol} />
                      <span className="shrink-0 font-medium text-muted-foreground">{turn.rol}:</span>
                      <span className="line-clamp-1 text-muted-foreground">
                        {turn.contenido.slice(0, 100)}{turn.contenido.length > 100 ? '...' : ''}
                      </span>
                    </div>
                  ))}
                  {conv.turnos.length > 3 && (
                    <p className="pl-5 text-xs text-muted-foreground">+{conv.turnos.length - 3} more turns</p>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Domain breakdown */}
        {domains.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {domains.map(d => {
              const count = convs.filter(c => c.dominio === d).length

              return (
                <Badge key={d} variant="outline" className="gap-1 text-xs">
                  {d} <span className="font-bold">{count}</span>
                </Badge>
              )
            })}
          </div>
        )}

        {/* Next action */}
        <div className="flex items-center gap-3">
          <Button onClick={() => { setStep('scan'); runToolScan() }}>
            <ScanSearch className="mr-1.5 size-4" />
            Scan for Tools
          </Button>
          <Button variant="outline" onClick={() => setStep('save')}>
            Skip to Save
          </Button>
        </div>
      </div>
    )
  }

  // ─── Render: Scan step ───

  function renderScanStep() {
    return (
      <div className="space-y-4">
        {scanning ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center gap-4 p-8">
              <Loader2 className="size-8 animate-spin text-muted-foreground" />
              <div className="w-full max-w-xs space-y-2">
                <Progress value={scanProgress} className="h-2" />
                <p className="text-center text-xs text-muted-foreground">
                  Scanning conversations for tool usage patterns... {scanProgress}%
                </p>
              </div>
            </CardContent>
          </Card>
        ) : scanSummary ? (
          <>
            <Card className="bg-muted/40">
              <CardContent className="p-4">
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold">{scanSummary.scanned}</p>
                    <p className="text-xs text-muted-foreground">Conversations scanned</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{scanSummary.withTools}</p>
                    <p className="text-xs text-muted-foreground">Require tools</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{scanSummary.uniqueTools}</p>
                    <p className="text-xs text-muted-foreground">Unique tools identified</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{(scanSummary.avgConfidence * 100).toFixed(0)}%</p>
                    <p className="text-xs text-muted-foreground">Avg confidence</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Per-conversation results */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Scan Results</CardTitle>
              </CardHeader>
              <CardContent className="max-h-[300px] overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Conversation</TableHead>
                      <TableHead>Tools</TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>Reasoning</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scanResults.map(r => (
                      <TableRow key={r.conversation_id}>
                        <TableCell className="font-mono text-xs">{r.conversation_id.slice(0, 10)}...</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {r.identified_tools.map(t => (
                              <Badge key={t.name} variant="outline" className="text-xs">{t.name}</Badge>
                            ))}
                            {r.identified_tools.length === 0 && (
                              <span className="text-xs text-muted-foreground">None</span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={r.confidence > 0.7 ? 'default' : 'secondary'} className="text-xs">
                            {(r.confidence * 100).toFixed(0)}%
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate text-xs text-muted-foreground">
                          {r.reasoning}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Button onClick={() => setStep('tools')}>
              <Wrench className="mr-1.5 size-4" />
              Review Generated Tools ({generatedTools.length})
            </Button>
          </>
        ) : (
          <EmptyState
            icon={ScanSearch}
            title="Ready to scan"
            description="Click below to analyze imported conversations for tool usage patterns."
            action={
              <Button onClick={runToolScan}>
                <Sparkles className="mr-1.5 size-4" /> Start Tool Scan
              </Button>
            }
          />
        )}
      </div>
    )
  }

  // ─── Render: Tools step ───

  function renderToolsStep() {
    if (generatedTools.length === 0) {
      return (
        <EmptyState
          icon={Wrench}
          title="No tools identified"
          description="The scan didn't identify any tool patterns. You can still save conversations."
          action={<Button variant="outline" onClick={() => setStep('save')}>Continue to Save</Button>}
        />
      )
    }

    return (
      <div className="space-y-4">
        {/* Header actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <p className="text-sm font-medium">{generatedTools.length} tools generated</p>
            <Badge variant="secondary" className="text-xs">{selectedTools.size} selected</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="text-xs"
              onClick={() => setSelectedTools(new Set(generatedTools.map(t => t.name)))}
            >
              Select All
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-xs"
              onClick={() => setSelectedTools(new Set())}
            >
              Clear
            </Button>
          </div>
        </div>

        {/* Tool cards */}
        <div className="space-y-2">
          {generatedTools.map(tool => {
            const isSelected = selectedTools.has(tool.name)
            const isExpanded = expandedTool === tool.name
            const validation = validateToolForMCP(tool as unknown as ToolDefinition)
            const vis = toolVisibility[tool.name] ?? 'private'
            const paramCount = Object.keys(tool.input_schema.properties).length

            return (
              <Card
                key={tool.name}
                className={cn('transition-colors', isSelected && 'border-foreground/20 bg-muted/30')}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={checked => {
                        const next = new Set(selectedTools)

                        if (checked) next.add(tool.name)
                        else next.delete(tool.name)
                        setSelectedTools(next)
                      }}
                      className="mt-1"
                    />

                    <div className="min-w-0 flex-1">
                      {/* Row 1: Name + badges */}
                      <div className="mb-1.5 flex flex-wrap items-center gap-2">
                        <span className="font-mono text-sm font-semibold">{tool.name}</span>
                        <Badge className={cn('text-xs', CATEGORY_COLORS[tool.category] ?? '')}>
                          {tool.category}
                        </Badge>
                        <Badge variant="outline" className="gap-1 text-xs">
                          {tool.method}
                        </Badge>
                        {tool.auth_type !== 'none' && (
                          <Badge variant="outline" className="gap-1 text-xs">
                            <Lock className="size-2" /> {tool.auth_type}
                          </Badge>
                        )}
                        {tool.mcp_compatible && (
                          <Badge variant="outline" className="gap-1 text-xs">
                            <Plug className="size-2" /> MCP
                          </Badge>
                        )}
                        {!validation.valid && (
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger>
                                <AlertCircle className="size-3 text-amber-500" />
                              </TooltipTrigger>
                              <TooltipContent className="max-w-xs text-xs">
                                {validation.issues.join('; ')}
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        )}
                      </div>

                      {/* Row 2: Description */}
                      <p className="mb-2 text-xs text-muted-foreground">{tool.description}</p>

                      {/* Row 3: Domains + params */}
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        {tool.domains.map(d => (
                          <Badge key={d} variant="secondary" className="text-xs">{d}</Badge>
                        ))}
                        <span className="text-xs text-muted-foreground">{paramCount} params</span>
                        <span className="text-xs text-muted-foreground">v{tool.version}</span>
                      </div>

                      {/* Row 4: Visibility selector */}
                      {isSelected && (
                        <div className="mb-2 flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">Visibility:</Label>
                          <div className="flex gap-1">
                            {VISIBILITY_OPTIONS.map(v => {
                              const VIcon = v.icon

                              return (
                                <TooltipProvider key={v.value}>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <button
                                        className={cn(
                                          'flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors',
                                          vis === v.value
                                            ? 'bg-foreground text-background'
                                            : 'bg-muted text-muted-foreground hover:text-foreground'
                                        )}
                                        onClick={() => setToolVisibility(prev => ({ ...prev, [tool.name]: v.value }))}
                                      >
                                        <VIcon className="size-2.5" />
                                        {v.label}
                                      </button>
                                    </TooltipTrigger>
                                    <TooltipContent className="text-xs">{v.desc}</TooltipContent>
                                  </Tooltip>
                                </TooltipProvider>
                              )
                            })}
                          </div>
                        </div>
                      )}

                      {/* Expand/collapse */}
                      <button
                        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                        onClick={() => setExpandedTool(isExpanded ? null : tool.name)}
                      >
                        {isExpanded ? <ChevronDown className="size-3" /> : <ChevronRight className="size-3" />}
                        {isExpanded ? 'Hide' : 'Show'} details
                      </button>

                      {/* Expanded details */}
                      {isExpanded && (
                        <div className="mt-3 space-y-3 border-t pt-3">
                          <div className="grid gap-3 sm:grid-cols-2">
                            <div>
                              <p className="mb-1 text-xs font-medium">Endpoint</p>
                              <code className="block rounded bg-muted px-2 py-1 text-xs">{tool.endpoint_url}</code>
                            </div>
                            <div>
                              <p className="mb-1 text-xs font-medium">Fallback Strategy</p>
                              <p className="text-xs text-muted-foreground">{tool.fallback_strategy}</p>
                            </div>
                          </div>

                          <div>
                            <p className="mb-1 text-xs font-medium">Error Handling</p>
                            <p className="text-xs text-muted-foreground">{tool.error_handling}</p>
                          </div>

                          <Tabs defaultValue="input" className="w-full">
                            <TabsList className="h-7">
                              <TabsTrigger value="input" className="text-xs">Input Schema</TabsTrigger>
                              <TabsTrigger value="output" className="text-xs">Output Schema</TabsTrigger>
                            </TabsList>
                            <TabsContent value="input">
                              <pre className="max-h-[200px] overflow-auto rounded-md bg-muted p-2 text-xs">
                                {JSON.stringify(tool.input_schema, null, 2)}
                              </pre>
                            </TabsContent>
                            <TabsContent value="output">
                              <pre className="max-h-[200px] overflow-auto rounded-md bg-muted p-2 text-xs">
                                {JSON.stringify(tool.output_schema, null, 2)}
                              </pre>
                            </TabsContent>
                          </Tabs>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {selectedToolsList.length > 0 && (
            <Button onClick={generateMCP}>
              <Server className="mr-1.5 size-4" />
              Generate MCP Server ({selectedToolsList.length} tools)
            </Button>
          )}
          <Button variant="outline" onClick={() => setStep('save')}>
            Skip to Save
          </Button>
        </div>
      </div>
    )
  }

  // ─── Render: MCP step ───

  function renderMCPStep() {
    if (!mcpPreview) {
      return (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">MCP Server Configuration</CardTitle>
              <CardDescription className="text-xs">
                Generate a deployable MCP server from your selected tools
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-xs">Server Name</Label>
                  <Input
                    value={mcpServerName}
                    onChange={e => setMcpServerName(e.target.value)}
                    placeholder="my-tool-server"
                    className="text-sm"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Rate Limit (req/min)</Label>
                  <Input
                    type="number"
                    value={mcpRateLimit}
                    onChange={e => setMcpRateLimit(Number(e.target.value))}
                    min={1}
                    max={1000}
                    className="text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Shield className="size-3" />
                <span>{selectedToolsList.length} tools will be included</span>
              </div>

              <Button onClick={generateMCP}>
                <Zap className="mr-1.5 size-4" />
                Generate MCP Server
              </Button>
            </CardContent>
          </Card>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        {/* Summary */}
        <Card className="bg-muted/40">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Server className="size-8 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-semibold">{mcpPreview.serverName}</p>
                <p className="text-xs text-muted-foreground">
                  {mcpPreview.toolCount} tools | Rate limit: {mcpRateLimit} req/min
                </p>
              </div>
              <Badge variant="outline">Generated</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Security notes */}
        {mcpPreview.securityNotes.length > 0 && (
          <Card className="border-amber-200 dark:border-amber-800">
            <CardContent className="p-3">
              <p className="mb-1 text-xs font-medium text-amber-700 dark:text-amber-300">Security Notes</p>
              {mcpPreview.securityNotes.map((note, i) => (
                <p key={i} className="text-xs text-amber-600 dark:text-amber-400">• {note}</p>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Tabs: Code / Connection / Config */}
        <Tabs defaultValue="code" className="w-full">
          <TabsList>
            <TabsTrigger value="code" className="gap-1 text-xs">
              <Code2 className="size-3" /> Generated Code
            </TabsTrigger>
            <TabsTrigger value="connection" className="gap-1 text-xs">
              <Plug className="size-3" /> Connection
            </TabsTrigger>
            <TabsTrigger value="config" className="gap-1 text-xs">
              <Settings2 className="size-3" /> MCP Config
            </TabsTrigger>
          </TabsList>

          <TabsContent value="code" className="space-y-2">
            <div className="flex items-center justify-end">
              <Button
                variant="ghost"
                size="sm"
                className="gap-1 text-xs"
                onClick={() => copyToClipboard(mcpPreview.generatedCode)}
              >
                <Copy className="size-3" />
                {codeCopied ? 'Copied!' : 'Copy'}
              </Button>
            </div>
            <pre className="max-h-[400px] overflow-auto rounded-lg border bg-muted/50 p-4 text-xs leading-relaxed">
              {mcpPreview.generatedCode}
            </pre>
          </TabsContent>

          <TabsContent value="connection" className="space-y-3">
            <Card>
              <CardContent className="space-y-3 p-4">
                <div>
                  <p className="mb-1 text-xs font-medium">curl Example</p>
                  <pre className="rounded bg-muted p-2 text-xs">{mcpPreview.connectionInfo.curlExample}</pre>
                </div>
                <div>
                  <p className="mb-1 text-xs font-medium">Deploy Command</p>
                  <pre className="rounded bg-muted p-2 text-xs">{mcpPreview.connectionInfo.deployCommand}</pre>
                </div>
                {mcpPreview.connectionInfo.envVars.length > 0 && (
                  <div>
                    <p className="mb-1 text-xs font-medium">Required Environment Variables</p>
                    {mcpPreview.connectionInfo.envVars.map(v => (
                      <code key={v} className="mr-2 rounded bg-muted px-1.5 py-0.5 text-xs">{v}</code>
                    ))}
                  </div>
                )}
                <div>
                  <p className="mb-1 text-xs font-medium">Tool Endpoints</p>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="text-xs">Tool</TableHead>
                        <TableHead className="text-xs">Method</TableHead>
                        <TableHead className="text-xs">URL</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mcpPreview.connectionInfo.toolEndpoints.map(ep => (
                        <TableRow key={ep.name}>
                          <TableCell className="font-mono text-xs">{ep.name}</TableCell>
                          <TableCell className="text-xs">{ep.method}</TableCell>
                          <TableCell className="max-w-[200px] truncate text-xs">{ep.url}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="config">
            <pre className="max-h-[300px] overflow-auto rounded-lg border bg-muted/50 p-4 text-xs">
              {JSON.stringify(mcpPreview.connectionInfo.mcpConfig ?? {}, null, 2)}
            </pre>
          </TabsContent>
        </Tabs>

        <Button onClick={() => setStep('save')}>
          <ArrowRight className="mr-1.5 size-4" />
          Continue to Save
        </Button>
      </div>
    )
  }

  // ─── Render: Save step ───

  function renderSaveStep() {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Save Import Results</CardTitle>
            <CardDescription className="text-xs">
              Save your imported conversations and generated tools to the local store
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Conversations */}
            {result && result.conversations.length > 0 && (
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <FileText className="size-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{result.conversations.length} Conversations</p>
                    <p className="text-xs text-muted-foreground">
                      {[...new Set(result.conversations.map(c => c.dominio))].join(', ')}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleSaveConversations}
                  disabled={savedConversations}
                  variant={savedConversations ? 'outline' : 'default'}
                  size="sm"
                >
                  {savedConversations ? (
                    <><CheckCircle2 className="mr-1.5 size-4" /> Saved</>
                  ) : (
                    <><Save className="mr-1.5 size-4" /> Save Conversations</>
                  )}
                </Button>
              </div>
            )}

            {/* Tools */}
            {selectedToolsList.length > 0 && (
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <Wrench className="size-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{selectedToolsList.length} Tools</p>
                    <p className="text-xs text-muted-foreground">
                      {selectedToolsList.map(t => t.name).slice(0, 3).join(', ')}
                      {selectedToolsList.length > 3 && ` +${selectedToolsList.length - 3} more`}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleSaveTools}
                  disabled={savedTools}
                  variant={savedTools ? 'outline' : 'default'}
                  size="sm"
                >
                  {savedTools ? (
                    <><CheckCircle2 className="mr-1.5 size-4" /> Saved</>
                  ) : (
                    <><Save className="mr-1.5 size-4" /> Save Tools</>
                  )}
                </Button>
              </div>
            )}

            {/* MCP Server */}
            {mcpPreview && (
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <Server className="size-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{mcpPreview.serverName}</p>
                    <p className="text-xs text-muted-foreground">{mcpPreview.toolCount} tools, MCP server code generated</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(mcpPreview.generatedCode)}
                >
                  <Copy className="mr-1.5 size-4" />
                  {codeCopied ? 'Copied!' : 'Copy Code'}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation links */}
        {(savedConversations || savedTools) && (
          <div className="flex flex-wrap items-center gap-3">
            {savedConversations && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/conversations">View Conversations</Link>
              </Button>
            )}
            {savedTools && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/tools">View Tools</Link>
              </Button>
            )}
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/pipeline">Back to Pipeline</Link>
            </Button>
          </div>
        )}

        {/* Start new import */}
        <Button variant="ghost" size="sm" onClick={resetAll}>
          <RefreshCw className="mr-1.5 size-4" /> Start New Import
        </Button>
      </div>
    )
  }

  // ─── Main render ───

  return (
    <div className="space-y-4">
      <PageHeader
        title="Import & Tool Discovery"
        description="Upload conversations, scan for tool patterns, and generate MCP-compatible tools"
        actions={
          step !== 'upload' ? (
            <Button variant="outline" size="sm" onClick={resetAll}>
              <X className="mr-1.5 size-4" /> New Import
            </Button>
          ) : undefined
        }
      />

      {renderStepIndicator()}

      {step === 'upload' && renderUploadStep()}
      {step === 'review' && renderReviewStep()}
      {step === 'scan' && renderScanStep()}
      {step === 'tools' && renderToolsStep()}
      {step === 'mcp' && renderMCPStep()}
      {step === 'save' && renderSaveStep()}
    </div>
  )
}
