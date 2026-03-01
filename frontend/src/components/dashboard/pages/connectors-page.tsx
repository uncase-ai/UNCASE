'use client'

import { useCallback, useRef, useState } from 'react'

import {
  ArrowDownToLine,
  Cable,
  Download,
  Heart,
  Loader2,
  Lock,
  Search,
  Shield,
  Upload,
} from 'lucide-react'

import type {
  ConnectorImportResponse,
  HFDatasetInfo,
  HFUploadResult,
  PIIScanResponse,
} from '@/lib/api/connectors'
import {
  importHFDataset,
  importWhatsApp,
  scanTextForPii,
  searchHFDatasets,
  uploadToHF,
} from '@/lib/api/connectors'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

import { PageHeader } from '../page-header'

// ─── Helpers ───

function formatBytes(bytes: number | null): string {
  if (bytes === null || bytes === 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes

  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }

  return `${size.toFixed(1)} ${units[i]}`
}

const HF_TOKEN_KEY = 'uncase-hf-token'

function getHFToken(): string {
  if (typeof window === 'undefined') return ''

  return localStorage.getItem(HF_TOKEN_KEY) ?? ''
}

function setHFToken(token: string) {
  localStorage.setItem(HF_TOKEN_KEY, token)
}

// ─── Import Tab ───

function ImportTab() {
  const [waFile, setWaFile] = useState<File | null>(null)
  const [waLoading, setWaLoading] = useState(false)
  const [waResult, setWaResult] = useState<ConnectorImportResponse | null>(null)
  const [waError, setWaError] = useState('')

  const [hfQuery, setHfQuery] = useState('')
  const [hfResults, setHfResults] = useState<HFDatasetInfo[]>([])
  const [hfSearching, setHfSearching] = useState(false)
  const [hfImporting, setHfImporting] = useState<string | null>(null)
  const [hfImportResult, setHfImportResult] = useState<ConnectorImportResponse | null>(null)
  const [hfError, setHfError] = useState('')
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

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

  const handleHfSearch = useCallback((q: string) => {
    setHfQuery(q)
    setHfError('')
    if (searchTimeout.current) clearTimeout(searchTimeout.current)

    if (!q.trim()) {
      setHfResults([])

      return
    }

    searchTimeout.current = setTimeout(async () => {
      setHfSearching(true)
      const res = await searchHFDatasets(q, 20)

      setHfSearching(false)

      if (res.error) {
        setHfError(res.error.message)
      } else {
        setHfResults(res.data ?? [])
      }
    }, 500)
  }, [])

  const handleHfImport = useCallback(async (repoId: string) => {
    setHfImporting(repoId)
    setHfError('')
    const token = getHFToken() || undefined
    const res = await importHFDataset(repoId, 'train', token)

    setHfImporting(null)

    if (res.error) {
      setHfError(res.error.message)
    } else {
      setHfImportResult(res.data)
    }
  }, [])

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

      {/* Hugging Face Search + Import */}
      <Card className="lg:row-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Download className="h-4 w-4" />
            Hugging Face Hub
          </CardTitle>
          <CardDescription>Search and import public or private datasets</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search datasets (e.g. customer-support, chat)"
              value={hfQuery}
              onChange={e => handleHfSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          {hfSearching && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Searching...
            </div>
          )}

          {hfError && <p className="text-sm text-destructive">{hfError}</p>}

          {hfResults.length > 0 && (
            <div className="max-h-[400px] space-y-2 overflow-y-auto">
              {hfResults.map(ds => (
                <div
                  key={ds.repo_id}
                  className="flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-muted/50"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{ds.repo_id}</p>
                    {ds.description && (
                      <p className="truncate text-xs text-muted-foreground">{ds.description}</p>
                    )}
                    <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Download className="h-3 w-3" /> {ds.downloads.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" /> {ds.likes}
                      </span>
                      {ds.size_bytes && <span>{formatBytes(ds.size_bytes)}</span>}
                    </div>
                    {ds.tags.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {ds.tags.slice(0, 5).map(tag => (
                          <Badge key={tag} variant="outline" className="text-[10px]">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleHfImport(ds.repo_id)}
                    disabled={hfImporting === ds.repo_id}
                    className="ml-3 shrink-0"
                  >
                    {hfImporting === ds.repo_id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Import'
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}

          {hfImportResult && (
            <div className="rounded-md border border-green-500/30 bg-green-500/5 p-3 text-sm">
              <p>Imported: <strong>{hfImportResult.total_imported}</strong> conversations</p>
              {hfImportResult.total_skipped > 0 && <p>Skipped: {hfImportResult.total_skipped}</p>}
              {hfImportResult.errors.length > 0 && (
                <p className="text-destructive">Errors: {hfImportResult.errors.length}</p>
              )}
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
  const [result, setResult] = useState<HFUploadResult | null>(null)
  const [error, setError] = useState('')

  const handleTokenChange = useCallback((v: string) => {
    setToken(v)
    setHFToken(v)
  }, [])

  const handleUpload = useCallback(async () => {
    if (!token || !repoId) return
    setUploading(true)
    setError('')

    const res = await uploadToHF({
      conversation_ids: ['all'],
      repo_id: repoId,
      token,
      private: isPrivate,
    })

    setUploading(false)

    if (res.error) {
      setError(res.error.message)
    } else if (res.data) {
      setResult(res.data)
    }
  }, [token, repoId, isPrivate])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Upload className="h-4 w-4" />
          Upload to Hugging Face
        </CardTitle>
        <CardDescription>Export your conversations as a public or private dataset</CardDescription>
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
          Upload
        </Button>

        {error && <p className="text-sm text-destructive">{error}</p>}

        {result && (
          <div className="rounded-md border border-green-500/30 bg-green-500/5 p-3 text-sm">
            <p>
              Uploaded to{' '}
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium underline"
              >
                {result.repo_id}
              </a>
            </p>
            <p className="text-xs text-muted-foreground">{result.files_uploaded} file(s) uploaded</p>
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
