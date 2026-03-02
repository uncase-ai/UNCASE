'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import {
  ArrowDownToLine,
  ArrowRight,
  Cable,
  Check,
  ChevronDown,
  Database,
  Download,
  ExternalLink,
  Eye,
  Heart,
  Loader2,
  Lock,
  Search,
  Shield,
  Upload,
  X,
} from 'lucide-react'

import type { Conversation } from '@/types/api'
import type { PIIScanResponse } from '@/lib/api/connectors'
import { importWhatsApp, scanTextForPii } from '@/lib/api/connectors'
import { bulkCreateConversations } from '@/lib/api/conversations'
import type { HFDatasetInfoResponse, HFRowsResponse, HFSearchResult } from '@/lib/api/huggingface'
import {
  createHFRepo,
  getDatasetInfo,
  getDatasetRows,
  searchDatasets,
  uploadFileToHF,
} from '@/lib/api/huggingface'
import type { HFDatasetFormat, ParseResult } from '@/lib/api/hf-parsers'
import { parseHFRowsToConversations } from '@/lib/api/hf-parsers'
import { appendConversations, saveConversations } from './conversations-page'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

import { PageHeader } from '../page-header'

// ─── Helpers ───

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`

  return String(n)
}

const FORMAT_LABELS: Record<HFDatasetFormat, string> = {
  messages: 'Messages',
  sharegpt: 'ShareGPT',
  rlhf: 'RLHF',
  'prompt-response': 'Prompt/Response',
  unknown: 'Raw Text',
}

const HF_TOKEN_KEY = 'uncase-hf-token'

function getHFToken(): string {
  if (typeof window === 'undefined') return ''

  return localStorage.getItem(HF_TOKEN_KEY) ?? ''
}

function setHFToken(token: string) {
  localStorage.setItem(HF_TOKEN_KEY, token)
}

const STORE_KEY = 'uncase-conversations'

function loadLocalConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

// ─── Import Tab ───

type ImportStep = 'search' | 'preview' | 'done'

function ImportTab() {
  // WhatsApp state
  const [waFile, setWaFile] = useState<File | null>(null)
  const [waLoading, setWaLoading] = useState(false)
  const [waResult, setWaResult] = useState<{ total_imported: number; total_skipped: number; total_pii_anonymized: number } | null>(null)
  const [waError, setWaError] = useState('')

  // HF search state
  const [step, setStep] = useState<ImportStep>('search')
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<HFSearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState('')
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  // Selected dataset state
  const [selectedDataset, setSelectedDataset] = useState<HFSearchResult | null>(null)
  const [datasetInfo, setDatasetInfo] = useState<HFDatasetInfoResponse | null>(null)
  const [loadingInfo, setLoadingInfo] = useState(false)

  // Config/split state
  const [selectedConfig, setSelectedConfig] = useState('')
  const [selectedSplit, setSelectedSplit] = useState('')

  // Preview state
  const [rowsData, setRowsData] = useState<HFRowsResponse | null>(null)
  const [parseResult, setParseResult] = useState<ParseResult | null>(null)
  const [loadingRows, setLoadingRows] = useState(false)
  const [rowLimit, setRowLimit] = useState(20)

  // Import state
  const [importing, setImporting] = useState(false)
  const [importDone, setImportDone] = useState<{ count: number; target: string } | null>(null)
  const [hfError, setHfError] = useState('')

  // Token for gated/private datasets
  const [showTokenInput, setShowTokenInput] = useState(false)
  const [hfToken, setHfTokenLocal] = useState(getHFToken)

  // ─── WhatsApp Import ───

  const handleWaImport = useCallback(async () => {
    if (!waFile) return
    setWaLoading(true)
    setWaError('')
    const res = await importWhatsApp(waFile)

    setWaLoading(false)

    if (res.error) {
      setWaError(res.error.message)
    } else {
      setWaResult(res.data)
    }
  }, [waFile])

  // ─── HF Search ───

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
    setSearchError('')

    if (searchTimeout.current) clearTimeout(searchTimeout.current)
    if (abortRef.current) abortRef.current.abort()

    if (!query.trim()) {
      setSearchResults([])
      setSearching(false)

      return
    }

    searchTimeout.current = setTimeout(async () => {
      setSearching(true)
      const controller = new AbortController()

      abortRef.current = controller
      const res = await searchDatasets(query, 20, controller.signal)

      if (controller.signal.aborted) return
      setSearching(false)

      if (res.error) {
        if (res.error.message !== 'Request cancelled') setSearchError(res.error.message)
      } else {
        setSearchResults(res.data ?? [])
      }
    }, 400)
  }, [])

  // ─── Dataset Selection ───

  const handleSelectDataset = useCallback(async (dataset: HFSearchResult) => {
    setSelectedDataset(dataset)
    setSearchOpen(false)
    setStep('preview')
    setLoadingInfo(true)
    setHfError('')
    setDatasetInfo(null)
    setRowsData(null)
    setParseResult(null)
    setSelectedConfig('')
    setSelectedSplit('')
    setImportDone(null)

    const token = getHFToken() || undefined
    const res = await getDatasetInfo(dataset.id, token)

    setLoadingInfo(false)

    if (res.error) {
      if (res.error.status === 401) {
        setShowTokenInput(true)
        setHfError('This dataset requires authentication. Enter your HuggingFace token below.')
      } else {
        setHfError(res.error.message)
      }

      return
    }

    setDatasetInfo(res.data)

    // Auto-select first config and split
    const configs = Object.keys(res.data.dataset_info)

    if (configs.length > 0) {
      const firstConfig = configs[0]

      setSelectedConfig(firstConfig)

      const splits = Object.keys(res.data.dataset_info[firstConfig].splits)

      if (splits.length > 0) {
        setSelectedSplit(splits[0])
      }
    }
  }, [])

  // ─── Load Rows (preview) ───

  useEffect(() => {
    if (!selectedDataset || !selectedConfig || !selectedSplit) return

    let cancelled = false

    async function loadRows() {
      setLoadingRows(true)
      setHfError('')

      const token = getHFToken() || undefined
      const res = await getDatasetRows(selectedDataset!.id, selectedConfig, selectedSplit, 0, rowLimit, token)

      if (cancelled) return
      setLoadingRows(false)

      if (res.error) {
        if (res.error.status === 401) {
          setShowTokenInput(true)
          setHfError('This dataset requires authentication. Enter your HuggingFace token below.')
        } else {
          setHfError(res.error.message)
        }

        return
      }

      setRowsData(res.data)
      const parsed = parseHFRowsToConversations(res.data, selectedDataset!.id, selectedConfig)

      setParseResult(parsed)
    }

    loadRows()

    return () => { cancelled = true }
  }, [selectedDataset, selectedConfig, selectedSplit, rowLimit])

  // ─── Token retry ───

  const handleTokenSave = useCallback(() => {
    setHFToken(hfToken)
    setShowTokenInput(false)
    setHfError('')

    // Retry loading if we have a selected dataset
    if (selectedDataset) {
      handleSelectDataset(selectedDataset)
    }
  }, [hfToken, selectedDataset, handleSelectDataset])

  // ─── Import Actions ───

  const handleImportLocal = useCallback(() => {
    if (!parseResult) return
    setImporting(true)

    appendConversations(parseResult.conversations)
    setImporting(false)
    setImportDone({ count: parseResult.conversations.length, target: 'local' })
    setStep('done')
  }, [parseResult])

  const handleImportDatabase = useCallback(async () => {
    if (!parseResult) return
    setImporting(true)
    setHfError('')

    const payload = parseResult.conversations.map(c => ({
      conversation_id: c.conversation_id,
      seed_id: c.seed_id,
      dominio: c.dominio,
      idioma: c.idioma,
      turnos: c.turnos,
      es_sintetica: c.es_sintetica,
      metadata: c.metadata,
    }))

    const res = await bulkCreateConversations(payload)

    setImporting(false)

    if (res.error) {
      setHfError(res.error.message)
    } else {
      setImportDone({ count: res.data.created, target: 'database' })
      setStep('done')
    }
  }, [parseResult])

  // ─── Reset ───

  const handleReset = useCallback(() => {
    setStep('search')
    setSelectedDataset(null)
    setDatasetInfo(null)
    setRowsData(null)
    setParseResult(null)
    setImportDone(null)
    setHfError('')
    setSearchQuery('')
    setSearchResults([])
  }, [])

  // ─── Derived data ───

  const configs = datasetInfo ? Object.keys(datasetInfo.dataset_info) : []
  const splits = datasetInfo && selectedConfig
    ? Object.keys(datasetInfo.dataset_info[selectedConfig]?.splits ?? {})
    : []
  const totalRows = rowsData?.num_rows_total ?? 0

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* WhatsApp Import */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ArrowDownToLine className="h-4 w-4" />
            WhatsApp Export
          </CardTitle>
          <CardDescription>Upload a .txt file exported from WhatsApp</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="wa-file">Chat export file</Label>
            <Input
              id="wa-file"
              type="file"
              accept=".txt"
              onChange={e => setWaFile(e.target.files?.[0] ?? null)}
              className="mt-1"
            />
          </div>
          <Button onClick={handleWaImport} disabled={!waFile || waLoading} className="w-full">
            {waLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
            Import
          </Button>
          {waError && <p className="text-sm text-destructive">{waError}</p>}
          {waResult && (
            <div className="rounded-md border p-3 text-sm">
              <p>Imported: <strong>{waResult.total_imported}</strong> conversations</p>
              {waResult.total_skipped > 0 && <p>Skipped: {waResult.total_skipped}</p>}
              {waResult.total_pii_anonymized > 0 && <p>PII anonymized: {waResult.total_pii_anonymized}</p>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hugging Face Hub — Multi-step */}
      <Card className="lg:row-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Download className="h-4 w-4" />
            Hugging Face Hub
          </CardTitle>
          <CardDescription>
            Search, preview, and import public datasets directly
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Step indicator */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className={step === 'search' ? 'font-semibold text-foreground' : ''}>Search</span>
            <ArrowRight className="h-3 w-3" />
            <span className={step === 'preview' ? 'font-semibold text-foreground' : ''}>Preview</span>
            <ArrowRight className="h-3 w-3" />
            <span className={step === 'done' ? 'font-semibold text-foreground' : ''}>Import</span>
          </div>

          {/* ─── Step 1: Search ─── */}
          {step === 'search' && (
            <>
              <Popover open={searchOpen} onOpenChange={setSearchOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={searchOpen}
                    className="w-full justify-between font-normal"
                  >
                    {selectedDataset ? (
                      <span className="truncate">{selectedDataset.id}</span>
                    ) : (
                      <span className="text-muted-foreground">Search datasets...</span>
                    )}
                    <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
                  <Command shouldFilter={false}>
                    <CommandInput
                      placeholder="e.g. customer-support, medical-qa"
                      value={searchQuery}
                      onValueChange={handleSearch}
                    />
                    <CommandList>
                      {searching && (
                        <div className="flex items-center gap-2 px-4 py-3 text-sm text-muted-foreground">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Searching HuggingFace...
                        </div>
                      )}
                      {searchError && (
                        <div className="px-4 py-3 text-sm text-destructive">{searchError}</div>
                      )}
                      {!searching && searchQuery && searchResults.length === 0 && !searchError && (
                        <CommandEmpty>No datasets found</CommandEmpty>
                      )}
                      {searchResults.length > 0 && (
                        <CommandGroup>
                          {searchResults.map(ds => (
                            <CommandItem
                              key={ds.id}
                              value={ds.id}
                              onSelect={() => handleSelectDataset(ds)}
                              className="flex flex-col items-start gap-1 py-2"
                            >
                              <div className="flex w-full items-center justify-between">
                                <span className="truncate text-sm font-medium">{ds.id}</span>
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                  <span className="flex items-center gap-0.5">
                                    <Download className="h-3 w-3" />
                                    {formatNumber(ds.downloads)}
                                  </span>
                                  <span className="flex items-center gap-0.5">
                                    <Heart className="h-3 w-3" />
                                    {formatNumber(ds.likes)}
                                  </span>
                                </div>
                              </div>
                              {ds.description && (
                                <p className="line-clamp-1 text-xs text-muted-foreground">{ds.description}</p>
                              )}
                              {ds.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {ds.tags.slice(0, 3).map(tag => (
                                    <Badge key={tag} variant="outline" className="text-[10px]">
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </CommandItem>
                          ))}
                        </CommandGroup>
                      )}
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>

              {/* Token input (optional) */}
              <div className="space-y-2">
                <button
                  onClick={() => setShowTokenInput(!showTokenInput)}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  <Lock className="h-3 w-3" />
                  {showTokenInput ? 'Hide' : 'HF token (for private/gated datasets)'}
                </button>
                {showTokenInput && (
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      value={hfToken}
                      onChange={e => setHfTokenLocal(e.target.value)}
                      placeholder="hf_..."
                      className="text-xs"
                    />
                    <Button size="sm" variant="outline" onClick={handleTokenSave}>
                      Save
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}

          {/* ─── Step 2: Preview ─── */}
          {step === 'preview' && selectedDataset && (
            <>
              {/* Dataset header */}
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{selectedDataset.id}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{formatNumber(selectedDataset.downloads)} downloads</span>
                    {selectedDataset.gated && <Badge variant="outline" className="text-[10px]">Gated</Badge>}
                  </div>
                </div>
                <Button size="sm" variant="ghost" onClick={handleReset}>
                  <X className="mr-1 h-3 w-3" />
                  Change
                </Button>
              </div>

              {/* Loading info */}
              {loadingInfo && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading dataset info...
                </div>
              )}

              {/* Config / Split selectors */}
              {datasetInfo && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-xs">Config</Label>
                    <Select value={selectedConfig} onValueChange={setSelectedConfig}>
                      <SelectTrigger size="sm" className="mt-1">
                        <SelectValue placeholder="Config" />
                      </SelectTrigger>
                      <SelectContent>
                        {configs.map(c => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-xs">Split</Label>
                    <Select value={selectedSplit} onValueChange={setSelectedSplit}>
                      <SelectTrigger size="sm" className="mt-1">
                        <SelectValue placeholder="Split" />
                      </SelectTrigger>
                      <SelectContent>
                        {splits.map(s => (
                          <SelectItem key={s} value={s}>{s}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {/* Row limit */}
              {datasetInfo && (
                <div className="flex items-center justify-between">
                  <Label className="text-xs">Rows to import</Label>
                  <Select value={String(rowLimit)} onValueChange={v => setRowLimit(Number(v))}>
                    <SelectTrigger size="sm" className="w-24">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="20">20</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Loading rows */}
              {loadingRows && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading preview...
                </div>
              )}

              {/* Token input if auth required */}
              {showTokenInput && (
                <div className="rounded-md border border-yellow-500/30 bg-yellow-500/5 p-3 space-y-2">
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">Authentication required</p>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      value={hfToken}
                      onChange={e => setHfTokenLocal(e.target.value)}
                      placeholder="hf_..."
                      className="text-xs"
                    />
                    <Button size="sm" onClick={handleTokenSave}>
                      Retry
                    </Button>
                  </div>
                </div>
              )}

              {/* Preview results */}
              {parseResult && !loadingRows && (
                <div className="space-y-3">
                  {/* Stats bar */}
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary">
                      {FORMAT_LABELS[parseResult.format]}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {parseResult.conversations.length} conversations parsed
                    </span>
                    {totalRows > 0 && (
                      <span className="text-xs text-muted-foreground">
                        ({formatNumber(totalRows)} total in split)
                      </span>
                    )}
                  </div>

                  {/* Warnings */}
                  {parseResult.warnings.length > 0 && (
                    <div className="rounded-md border border-yellow-500/30 bg-yellow-500/5 p-2">
                      {parseResult.warnings.slice(0, 3).map((w, i) => (
                        <p key={i} className="text-xs text-yellow-700 dark:text-yellow-300">{w}</p>
                      ))}
                      {parseResult.warnings.length > 3 && (
                        <p className="text-xs text-muted-foreground">
                          +{parseResult.warnings.length - 3} more warnings
                        </p>
                      )}
                    </div>
                  )}

                  {/* Sample conversations */}
                  <div className="max-h-[240px] space-y-2 overflow-y-auto rounded-md border p-2">
                    {parseResult.conversations.slice(0, 5).map((conv, i) => (
                      <div key={i} className="rounded border p-2 text-xs">
                        <div className="mb-1 flex items-center justify-between">
                          <span className="font-medium">Conversation {i + 1}</span>
                          <span className="text-muted-foreground">{conv.turnos.length} turns</span>
                        </div>
                        {conv.turnos.slice(0, 3).map((turn, j) => (
                          <div key={j} className="mt-1">
                            <span className="font-medium text-muted-foreground">{turn.rol}: </span>
                            <span className="line-clamp-2">{turn.contenido}</span>
                          </div>
                        ))}
                        {conv.turnos.length > 3 && (
                          <p className="mt-1 text-muted-foreground">+{conv.turnos.length - 3} more turns</p>
                        )}
                      </div>
                    ))}
                    {parseResult.conversations.length > 5 && (
                      <p className="py-1 text-center text-xs text-muted-foreground">
                        +{parseResult.conversations.length - 5} more conversations
                      </p>
                    )}
                  </div>

                  {/* Import buttons */}
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      onClick={handleImportLocal}
                      disabled={importing || parseResult.conversations.length === 0}
                      className="w-full"
                    >
                      {importing ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Database className="mr-2 h-4 w-4" />
                      )}
                      Local Store
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleImportDatabase}
                      disabled={importing || parseResult.conversations.length === 0}
                      className="w-full"
                    >
                      {importing ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Upload className="mr-2 h-4 w-4" />
                      )}
                      Database
                    </Button>
                  </div>
                </div>
              )}

              {hfError && !showTokenInput && <p className="text-sm text-destructive">{hfError}</p>}
            </>
          )}

          {/* ─── Step 3: Done ─── */}
          {step === 'done' && importDone && (
            <div className="space-y-4">
              <div className="rounded-md border border-green-500/30 bg-green-500/5 p-4 text-center">
                <Check className="mx-auto mb-2 h-8 w-8 text-green-500" />
                <p className="text-sm font-medium">
                  {importDone.count} conversations imported
                </p>
                <p className="text-xs text-muted-foreground">
                  Saved to {importDone.target === 'local' ? 'local store' : 'database'}
                </p>
              </div>

              {importDone.target === 'local' && (
                <p className="text-center text-xs text-muted-foreground">
                  View them on the Conversations page
                </p>
              )}

              <Button onClick={handleReset} variant="outline" className="w-full">
                Import another dataset
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Webhook */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Cable className="h-4 w-4" />
            Webhook
          </CardTitle>
          <CardDescription>POST JSON conversation data to the webhook endpoint</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md bg-muted p-3">
            <code className="text-xs">POST /api/v1/connectors/webhook</code>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Send a JSON body with a &quot;conversations&quot; array. Each conversation needs a &quot;turns&quot; array
            with &quot;role&quot; and &quot;content&quot; fields.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── Upload Tab ───

function UploadTab() {
  const [token, setToken] = useState(getHFToken)
  const [repoId, setRepoId] = useState('')
  const [isPrivate, setIsPrivate] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ url: string; count: number } | null>(null)
  const [error, setError] = useState('')
  const [uploadStep, setUploadStep] = useState('')

  const handleTokenChange = useCallback((v: string) => {
    setToken(v)
    setHFToken(v)
  }, [])

  const handleUpload = useCallback(async () => {
    if (!token || !repoId) return
    setUploading(true)
    setError('')
    setResult(null)

    // Step 1: Load conversations from local store
    setUploadStep('Loading conversations...')
    const conversations = loadLocalConversations()

    if (conversations.length === 0) {
      setError('No conversations in local store. Import some conversations first.')
      setUploading(false)
      setUploadStep('')

      return
    }

    // Step 2: Convert to JSONL
    setUploadStep('Converting to JSONL...')
    const jsonl = conversations.map(c => JSON.stringify(c)).join('\n')

    // Step 3: Create repo (handles "already exists" gracefully)
    setUploadStep('Creating repository...')
    const createRes = await createHFRepo(repoId, token, isPrivate)

    if (createRes.error) {
      setError(createRes.error.message)
      setUploading(false)
      setUploadStep('')

      return
    }

    // Step 4: Upload file
    setUploadStep('Uploading conversations...')
    const uploadRes = await uploadFileToHF(repoId, token, 'conversations.jsonl', jsonl)

    setUploading(false)
    setUploadStep('')

    if (uploadRes.error) {
      setError(uploadRes.error.message)
    } else {
      setResult({ url: `https://huggingface.co/datasets/${repoId}`, count: conversations.length })
    }
  }, [token, repoId, isPrivate])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Upload className="h-4 w-4" />
          Upload to Hugging Face
        </CardTitle>
        <CardDescription>Export your local conversations as a dataset on HF Hub</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="hf-token">HuggingFace API Token</Label>
          <div className="relative mt-1">
            <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="hf-token"
              type="password"
              value={token}
              onChange={e => handleTokenChange(e.target.value)}
              placeholder="hf_..."
              className="pl-10"
            />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Stored locally in your browser</p>
        </div>

        <div>
          <Label htmlFor="hf-repo">Target Repository</Label>
          <Input
            id="hf-repo"
            value={repoId}
            onChange={e => setRepoId(e.target.value)}
            placeholder="username/my-dataset"
            className="mt-1"
          />
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="hf-private">Private Repository</Label>
          <Switch id="hf-private" checked={isPrivate} onCheckedChange={setIsPrivate} />
        </div>

        <Button onClick={handleUpload} disabled={!token || !repoId || uploading} className="w-full">
          {uploading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
          {uploadStep || 'Upload'}
        </Button>

        {error && <p className="text-sm text-destructive">{error}</p>}

        {result && (
          <div className="rounded-md border border-green-500/30 bg-green-500/5 p-3 text-sm">
            <p>
              Uploaded {result.count} conversations to{' '}
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 font-medium underline"
              >
                {repoId}
                <ExternalLink className="h-3 w-3" />
              </a>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── PII Scanner Tab ───

function PIIScannerTab() {
  const [text, setText] = useState('')
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState<PIIScanResponse | null>(null)
  const [error, setError] = useState('')

  const handleScan = useCallback(async () => {
    if (!text.trim()) return
    setScanning(true)
    setError('')
    const res = await scanTextForPii(text)

    setScanning(false)

    if (res.error) {
      setError(res.error.message)
    } else {
      setResult(res.data)
    }
  }, [text])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Shield className="h-4 w-4" />
          PII Scanner
        </CardTitle>
        <CardDescription>Scan text for personally identifiable information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="pii-text">Text to scan</Label>
          <Textarea
            id="pii-text"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Paste text here to scan for PII (emails, phones, names, SSN, etc.)"
            rows={5}
            className="mt-1"
          />
        </div>

        <Button onClick={handleScan} disabled={!text.trim() || scanning} className="w-full">
          {scanning ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
          Scan
        </Button>

        {error && <p className="text-sm text-destructive">{error}</p>}

        {result && (
          <div className="space-y-3">
            <div className="rounded-md border p-3 text-sm">
              <div className="flex items-center gap-2">
                <Badge variant={result.pii_found ? 'destructive' : 'default'}>
                  {result.pii_found ? `${result.entity_count} PII found` : 'No PII found'}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  Scanner: {result.scanner_mode}
                </span>
              </div>
            </div>

            {result.entities.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Detected entities:</p>
                {result.entities.map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <Badge variant="outline">{e.category}</Badge>
                    <span className="text-muted-foreground">
                      chars {e.start}-{e.end} ({(e.score * 100).toFixed(0)}% confidence)
                    </span>
                  </div>
                ))}
              </div>
            )}

            {result.anonymized_preview && (
              <div>
                <p className="text-sm font-medium">Anonymized preview:</p>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">
                  {result.anonymized_preview}
                </pre>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Page ───

export function ConnectorsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Connectors" description="Import, export, and scan conversation data" />

      <Tabs defaultValue="import" className="w-full">
        <TabsList>
          <TabsTrigger value="import">Import</TabsTrigger>
          <TabsTrigger value="upload">Upload to HF</TabsTrigger>
          <TabsTrigger value="pii">PII Scanner</TabsTrigger>
        </TabsList>

        <TabsContent value="import" className="mt-6">
          <ImportTab />
        </TabsContent>

        <TabsContent value="upload" className="mt-6">
          <UploadTab />
        </TabsContent>

        <TabsContent value="pii" className="mt-6">
          <PIIScannerTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
