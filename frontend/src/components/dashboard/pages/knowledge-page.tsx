'use client'

import { useCallback, useMemo, useRef, useState } from 'react'

import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  Cloud,
  CloudOff,
  FileText,
  HardDrive,
  List,
  Loader2,
  Search,
  Tag,
  Trash2,
  Upload,
  X
} from 'lucide-react'

import type { KnowledgeChunk, KnowledgeDocument, KnowledgeType } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { checkApiHealth } from '@/lib/api/client'
import type {
  KnowledgeDocumentResponse,
  KnowledgeDocumentSummary,
  KnowledgeListResponse,
  KnowledgeSearchResponse
} from '@/lib/api/knowledge'
import {
  deleteKnowledgeDocument,
  fetchKnowledgeDocuments,
  searchKnowledgeChunks,
  uploadKnowledgeDocument
} from '@/lib/api/knowledge'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

// ─── Local storage (fallback when API is offline) ───

const STORE_KEY = 'uncase-knowledge'

function loadLocalDocuments(): KnowledgeDocument[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveLocalDocuments(docs: KnowledgeDocument[]) {
  localStorage.setItem(STORE_KEY, JSON.stringify(docs))
}

// ─── Text chunking (client-side fallback) ───

function chunkText(text: string, chunkSize = 800, overlap = 100): string[] {
  const paragraphs = text.split(/\n{2,}/)
  const chunks: string[] = []
  let current = ''

  for (const para of paragraphs) {
    const trimmed = para.trim()

    if (!trimmed) continue

    if (current.length + trimmed.length > chunkSize && current.length > 0) {
      chunks.push(current.trim())

      const words = current.split(/\s+/)
      const overlapWords = Math.ceil(overlap / 5)

      current = words.slice(-overlapWords).join(' ') + '\n\n' + trimmed
    } else {
      current += (current ? '\n\n' : '') + trimmed
    }
  }

  if (current.trim()) {
    chunks.push(current.trim())
  }

  if (chunks.length === 0 && text.trim().length > 0) {
    const sentences = text.split(/(?<=[.!?])\s+/)
    let buf = ''

    for (const s of sentences) {
      if (buf.length + s.length > chunkSize && buf.length > 0) {
        chunks.push(buf.trim())
        buf = s
      } else {
        buf += (buf ? ' ' : '') + s
      }
    }

    if (buf.trim()) {
      chunks.push(buf.trim())
    }
  }

  return chunks
}

// ─── Type labels ───

const TYPE_LABELS: Record<KnowledgeType, string> = {
  facts: 'Facts',
  procedures: 'Procedures',
  terminology: 'Terminology',
  reference: 'Reference'
}

const TYPE_DESCRIPTIONS: Record<KnowledgeType, string> = {
  facts: 'Product catalogs, specifications, pricing, features',
  procedures: 'SOPs, workflows, compliance steps, protocols',
  terminology: 'Domain glossary, abbreviations, jargon definitions',
  reference: 'Regulations, policies, manuals, general context'
}

// ─── Helpers ───

function apiDocToLocal(doc: KnowledgeDocumentSummary | KnowledgeDocumentResponse): KnowledgeDocument {
  const chunks: KnowledgeChunk[] = 'chunks' in doc && doc.chunks
    ? doc.chunks.map(c => ({
        id: c.id,
        document_id: c.document_id,
        content: c.content,
        type: c.type as KnowledgeType,
        domain: c.domain,
        tags: c.tags,
        source: c.source,
        order: c.order
      }))
    : []

  return {
    id: doc.id,
    filename: doc.filename,
    domain: doc.domain,
    type: doc.type as KnowledgeType,
    chunk_count: doc.chunk_count,
    chunks,
    uploaded_at: doc.created_at,
    metadata: (doc.metadata as Record<string, unknown>) ?? {}
  }
}

// ─── Component ───

export function KnowledgePage() {
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Storage mode
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)
  const [storageMode, setStorageMode] = useState<'api' | 'local'>('local')

  // Documents (unified state for both modes)
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(() => loadLocalDocuments())
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null)

  // Upload dialog state
  const [showUpload, setShowUpload] = useState(false)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadDomain, setUploadDomain] = useState<string>(SUPPORTED_DOMAINS[0])
  const [uploadType, setUploadType] = useState<KnowledgeType>('reference')
  const [uploadTags, setUploadTags] = useState('')
  const [processing, setProcessing] = useState(false)

  // Search results from API
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResponse | null>(null)

  // Check API availability and load documents
  const initFetcher = useCallback(async (signal: AbortSignal) => {
    const isHealthy = await checkApiHealth()

    setApiAvailable(isHealthy)

    if (isHealthy) {
      setStorageMode('api')
      const res = await fetchKnowledgeDocuments({ page_size: 100 }, { signal })

      if (res.data) {
        const apiDocs = res.data.items.map(apiDocToLocal)

        setDocuments(apiDocs)

        // Sync to localStorage as cache
        saveLocalDocuments(apiDocs)

        return { data: res.data, error: null }
      }

      return res
    }

    // Fallback: load from localStorage
    setStorageMode('local')
    const localDocs = loadLocalDocuments()

    setDocuments(localDocs)

    return {
      data: { items: [], total: localDocs.length, page: 1, page_size: 100 } as KnowledgeListResponse,
      error: null
    }
  }, [])

  useApi<KnowledgeListResponse>(initFetcher)

  // Stats
  const totalChunks = useMemo(() => documents.reduce((s, d) => s + d.chunks.length, 0), [documents])

  const filteredDocuments = useMemo(() => {
    let result = documents

    if (typeFilter !== 'all') {
      result = result.filter(d => d.type === typeFilter)
    }

    if (domainFilter !== 'all') {
      result = result.filter(d => d.domain === domainFilter)
    }

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        d =>
          d.filename.toLowerCase().includes(q) ||
          d.chunks.some(c => c.content.toLowerCase().includes(q) || c.tags.some(t => t.toLowerCase().includes(q)))
      )
    }

    return result
  }, [documents, search, typeFilter, domainFilter])

  // Filtered chunks for search highlighting (local mode)
  const matchingChunks = useMemo(() => {
    if (!search || storageMode === 'api') return null

    const q = search.toLowerCase()
    const matches: (KnowledgeChunk & { docFilename: string })[] = []

    for (const doc of filteredDocuments) {
      for (const chunk of doc.chunks) {
        if (chunk.content.toLowerCase().includes(q) || chunk.tags.some(t => t.toLowerCase().includes(q))) {
          matches.push({ ...chunk, docFilename: doc.filename })
        }
      }
    }

    return matches.slice(0, 20)
  }, [filteredDocuments, search, storageMode])

  // API search with debounce
  const handleSearch = useCallback(
    async (query: string) => {
      setSearch(query)

      if (storageMode === 'api' && query.trim().length >= 2) {
        const res = await searchKnowledgeChunks(query, {
          domain: domainFilter !== 'all' ? domainFilter : undefined,
          type: typeFilter !== 'all' ? typeFilter : undefined
        })

        if (res.data) {
          setSearchResults(res.data)
        }
      } else {
        setSearchResults(null)
      }
    },
    [storageMode, domainFilter, typeFilter]
  )

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]

    if (file) {
      setUploadFile(file)
    }
  }, [])

  const handleUpload = useCallback(async () => {
    if (!uploadFile) return
    setProcessing(true)

    try {
      const text = await uploadFile.text()

      const tags = uploadTags
        .split(',')
        .map(t => t.trim())
        .filter(Boolean)

      if (storageMode === 'api') {
        // Upload via API — server does chunking
        const res = await uploadKnowledgeDocument({
          filename: uploadFile.name,
          content: text,
          domain: uploadDomain,
          type: uploadType,
          tags
        })

        if (res.data) {
          const newDoc = apiDocToLocal(res.data)
          const updated = [...documents, newDoc]

          setDocuments(updated)
          saveLocalDocuments(updated)
        }
      } else {
        // Client-side chunking (offline fallback)
        const rawChunks = chunkText(text)
        const docId = `kb-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

        const chunks: KnowledgeChunk[] = rawChunks.map((content, i) => ({
          id: `${docId}-${i}`,
          document_id: docId,
          content,
          type: uploadType,
          domain: uploadDomain,
          tags,
          source: uploadFile.name,
          order: i
        }))

        const doc: KnowledgeDocument = {
          id: docId,
          filename: uploadFile.name,
          domain: uploadDomain,
          type: uploadType,
          chunk_count: chunks.length,
          chunks,
          uploaded_at: new Date().toISOString(),
          metadata: { size_bytes: uploadFile.size, tags }
        }

        const updated = [...documents, doc]

        setDocuments(updated)
        saveLocalDocuments(updated)
      }

      // Reset upload state
      setShowUpload(false)
      setUploadFile(null)
      setUploadTags('')

      if (fileInputRef.current) fileInputRef.current.value = ''
    } finally {
      setProcessing(false)
    }
  }, [uploadFile, uploadDomain, uploadType, uploadTags, documents, storageMode])

  const handleDelete = useCallback(
    async (docId: string) => {
      if (storageMode === 'api') {
        await deleteKnowledgeDocument(docId)
      }

      const updated = documents.filter(d => d.id !== docId)

      setDocuments(updated)
      saveLocalDocuments(updated)

      if (expandedDoc === docId) setExpandedDoc(null)
    },
    [documents, expandedDoc, storageMode]
  )

  // ─── Storage mode badge ───
  function StorageBadge() {
    if (apiAvailable === null) return null

    return (
      <Badge variant="outline" className="gap-1.5 text-[10px]">
        {storageMode === 'api' ? (
          <>
            <Cloud className="size-2.5" /> Synced to API
          </>
        ) : (
          <>
            <HardDrive className="size-2.5" /> Local storage
          </>
        )}
      </Badge>
    )
  }

  // ─── Upload dialog ───
  function renderUploadDialog() {
    return (
      <Dialog open={showUpload} onOpenChange={setShowUpload}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>File *</Label>
              <Input
                ref={fileInputRef}
                type="file"
                accept=".txt,.md,.csv,.tsv,.log"
                onChange={handleFileSelect}
              />
              <p className="text-[11px] text-muted-foreground">
                Supported: .txt, .md, .csv, .tsv, .log (plain text files).
                {storageMode === 'api' && ' Server-side chunking with configurable parameters.'}
              </p>
            </div>

            <div className="space-y-1">
              <Label>Domain *</Label>
              <Select value={uploadDomain} onValueChange={setUploadDomain}>
                <SelectTrigger>
                  <SelectValue />
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

            <div className="space-y-1">
              <Label>Knowledge Type *</Label>
              <Select value={uploadType} onValueChange={v => setUploadType(v as KnowledgeType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(Object.entries(TYPE_LABELS) as [KnowledgeType, string][]).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-[11px] text-muted-foreground">{TYPE_DESCRIPTIONS[uploadType]}</p>
            </div>

            <div className="space-y-1">
              <Label>Tags</Label>
              <Input
                placeholder="e.g. pricing, SUV, 2024 (comma-separated)"
                value={uploadTags}
                onChange={e => setUploadTags(e.target.value)}
              />
            </div>

            <Button onClick={handleUpload} disabled={!uploadFile || processing}>
              {processing ? (
                <>
                  <Loader2 className="mr-1.5 size-4 animate-spin" /> Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-1.5 size-4" /> Upload & Chunk
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  // ─── Empty state ───
  if (documents.length === 0 && !showUpload) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Knowledge Base"
          description="Upload domain literature to ground synthetic generation in real facts"
          actions={
            <div className="flex items-center gap-2">
              <StorageBadge />
              <Button size="sm" onClick={() => setShowUpload(true)}>
                <Upload className="mr-1.5 size-3.5" />
                Upload Document
              </Button>
            </div>
          }
        />

        <EmptyState
          icon={BookOpen}
          title="No knowledge documents yet"
          description="Upload manuals, procedures, product catalogs, or domain reference material. The system will extract and chunk the content for use during seed creation and synthetic generation."
          action={
            <Button variant="outline" onClick={() => setShowUpload(true)}>
              <Upload className="mr-1.5 size-4" /> Upload your first document
            </Button>
          }
        />

        {/* Offline notice */}
        {storageMode === 'local' && apiAvailable === false && (
          <Card className="border-amber-500/30 bg-amber-500/5">
            <CardContent className="flex items-center gap-3 py-4">
              <CloudOff className="size-4 shrink-0 text-amber-500" />
              <div>
                <p className="text-xs font-medium text-amber-700 dark:text-amber-400">API unavailable</p>
                <p className="text-[11px] text-muted-foreground">
                  Documents are stored locally. They will sync to the backend when the API becomes available.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Type reference */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Types</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(Object.entries(TYPE_LABELS) as [KnowledgeType, string][]).map(([key, label]) => (
              <div key={key} className="flex items-start gap-3">
                <Badge variant="outline" className="mt-0.5 shrink-0 text-[10px] font-normal">
                  {label}
                </Badge>
                <span className="text-xs text-muted-foreground">{TYPE_DESCRIPTIONS[key]}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {renderUploadDialog()}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Knowledge Base"
        description={`${documents.length} documents, ${totalChunks} chunks`}
        actions={
          <div className="flex items-center gap-2">
            <StorageBadge />
            <Button size="sm" onClick={() => setShowUpload(true)}>
              <Upload className="mr-1.5 size-3.5" />
              Upload Document
            </Button>
          </div>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative w-64">
          <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search content, tags..."
            value={search}
            onChange={e => handleSearch(e.target.value)}
            className="pl-8"
          />
          {search && (
            <button
              className="absolute right-2 top-1/2 -translate-y-1/2"
              onClick={() => {
                setSearch('')
                setSearchResults(null)
              }}
            >
              <X className="size-3.5 text-muted-foreground" />
            </button>
          )}
        </div>

        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {(Object.entries(TYPE_LABELS) as [KnowledgeType, string][]).map(([key, label]) => (
              <SelectItem key={key} value={key}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

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

        <span className="ml-auto text-xs text-muted-foreground">
          {filteredDocuments.length} documents
        </span>
      </div>

      {/* API search results */}
      {searchResults && searchResults.results.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Matching Chunks ({searchResults.total})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {searchResults.results.map(result => (
              <div key={result.chunk_id} className="rounded border bg-muted/30 px-3 py-2">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-[10px] font-medium text-muted-foreground">{result.filename}</span>
                  <Badge variant="outline" className="text-[9px]">
                    {TYPE_LABELS[result.type as KnowledgeType] ?? result.type}
                  </Badge>
                  {result.tags.map(t => (
                    <span key={t} className="text-[9px] text-muted-foreground">
                      #{t}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground line-clamp-3">{result.content}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Local search results (fallback) */}
      {matchingChunks && matchingChunks.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Matching Chunks ({matchingChunks.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {matchingChunks.map(chunk => (
              <div key={chunk.id} className="rounded border bg-muted/30 px-3 py-2">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-[10px] font-medium text-muted-foreground">{chunk.docFilename}</span>
                  <Badge variant="outline" className="text-[9px]">
                    {TYPE_LABELS[chunk.type]}
                  </Badge>
                  {chunk.tags.map(t => (
                    <span key={t} className="text-[9px] text-muted-foreground">
                      #{t}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground line-clamp-3">{chunk.content}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Documents list */}
      <div className="space-y-2">
        {filteredDocuments.map(doc => {
          const isExpanded = expandedDoc === doc.id

          return (
            <Collapsible
              key={doc.id}
              open={isExpanded}
              onOpenChange={() => setExpandedDoc(isExpanded ? null : doc.id)}
            >
              <div className="rounded-lg border transition-colors hover:bg-muted/30">
                <CollapsibleTrigger asChild>
                  <button className="flex w-full items-center gap-3 px-4 py-3 text-left">
                    {isExpanded ? (
                      <ChevronDown className="size-3.5 shrink-0 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="size-3.5 shrink-0 text-muted-foreground" />
                    )}
                    <FileText className="size-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="truncate text-sm font-medium">{doc.filename}</span>
                        <Badge variant="outline" className="shrink-0 text-[10px] font-normal">
                          {TYPE_LABELS[doc.type]}
                        </Badge>
                        <Badge variant="secondary" className="shrink-0 text-[10px]">
                          {doc.domain.split('.').pop()}
                        </Badge>
                      </div>
                      <div className="mt-0.5 flex items-center gap-3 text-[11px] text-muted-foreground">
                        <span>{doc.chunk_count} chunks</span>
                        <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                        {(doc.metadata.tags as string[])?.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Tag className="size-2.5" />
                            {(doc.metadata.tags as string[]).join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-7 shrink-0"
                      onClick={e => {
                        e.stopPropagation()
                        handleDelete(doc.id)
                      }}
                    >
                      <Trash2 className="size-3 text-muted-foreground" />
                    </Button>
                  </button>
                </CollapsibleTrigger>

                <CollapsibleContent>
                  <Separator />
                  <div className="space-y-2 px-4 py-3">
                    {doc.chunks.length > 0 ? (
                      doc.chunks.map((chunk, ci) => (
                        <div key={chunk.id} className="rounded border bg-muted/20 px-3 py-2">
                          <div className="mb-1 flex items-center gap-2 text-[10px] text-muted-foreground">
                            <span className="font-medium">Chunk {ci + 1}</span>
                            <span>{chunk.content.length} chars</span>
                          </div>
                          <p className="text-xs text-muted-foreground whitespace-pre-wrap line-clamp-5">
                            {chunk.content}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="py-2 text-center text-xs text-muted-foreground">
                        Expand to load chunks from the API.
                      </p>
                    )}
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>
          )
        })}
      </div>

      {filteredDocuments.length === 0 && documents.length > 0 && (
        <EmptyState
          icon={Search}
          title="No matching documents"
          description="Try adjusting your search or filters."
        />
      )}

      {/* Integration note */}
      <Card className="border-dashed">
        <CardContent className="flex items-center gap-3 py-4">
          <List className="size-4 shrink-0 text-muted-foreground" />
          <div>
            <p className="text-xs font-medium">How knowledge is used</p>
            <p className="text-[11px] text-muted-foreground">
              Knowledge chunks are injected as factual context during synthetic generation, enriching seeds with domain-specific
              facts, procedures, and terminology. This makes generated conversations deeply specialized to your industry.
            </p>
          </div>
        </CardContent>
      </Card>

      {renderUploadDialog()}
    </div>
  )
}
