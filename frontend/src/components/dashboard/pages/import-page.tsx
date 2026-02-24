'use client'

import { useRef, useState } from 'react'

import Link from 'next/link'
import {
  AlertCircle,
  ArrowDownToLine,
  CheckCircle2,
  FileUp,
  Loader2,
  RefreshCw,
  Save,
  X
} from 'lucide-react'

import type { ImportResult } from '@/types/api'
import { cn } from '@/lib/utils'
import { detectFormat, importCsv, importJsonl, parseJsonlLocally } from '@/lib/api/imports'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

import { appendConversations } from './conversations-page'

type UploadState = 'idle' | 'dragover' | 'uploading' | 'done' | 'error'

const STATE_STYLES: Record<UploadState, string> = {
  idle: 'border-muted-foreground/25 bg-muted/20 hover:border-muted-foreground/40 hover:bg-muted/30',
  dragover: 'border-foreground/30 bg-muted/40 scale-[1.01]',
  uploading: 'border-muted-foreground/25 bg-muted/20 animate-pulse',
  done: 'border-foreground/30 bg-muted/30',
  error: 'border-destructive/30 bg-muted/20'
}

const STATE_ICONS: Record<UploadState, typeof ArrowDownToLine> = {
  idle: ArrowDownToLine,
  dragover: FileUp,
  uploading: Loader2,
  done: CheckCircle2,
  error: AlertCircle
}

export function ImportPage() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [detectedFormat, setDetectedFormat] = useState<'csv' | 'jsonl' | 'unknown' | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  function resetState() {
    setUploadState('idle')
    setSelectedFile(null)
    setDetectedFormat(null)
    setResult(null)
    setUploadError(null)
    setSaved(false)

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  function handleFileSelect(file: File) {
    const format = detectFormat(file.name)

    setSelectedFile(file)
    setDetectedFormat(format)
    setUploadError(null)
    setResult(null)
    setSaved(false)

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

    // Try the API first
    const apiResult = format === 'csv' ? await importCsv(file) : await importJsonl(file)

    if (apiResult.data) {
      setResult(apiResult.data)
      setUploadState('done')

      return
    }

    // Fallback: parse JSONL locally when the API is unreachable
    if (format === 'jsonl') {
      try {
        const localResult = await parseJsonlLocally(file)

        if (localResult.conversations.length > 0 || localResult.errors.length > 0) {
          setResult(localResult)
          setUploadState('done')

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

    if (uploadState !== 'uploading') {
      setUploadState('dragover')
    }
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()

    if (uploadState !== 'uploading' && uploadState !== 'done' && uploadState !== 'error') {
      setUploadState('idle')
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()

    const files = e.dataTransfer.files

    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files

    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  function handleSaveToLocalStore() {
    if (!result || result.conversations.length === 0) return
    appendConversations(result.conversations)
    setSaved(true)
  }

  function handleRetry() {
    if (selectedFile && detectedFormat && detectedFormat !== 'unknown') {
      handleUpload(selectedFile, detectedFormat)
    } else {
      resetState()
    }
  }

  const StateIcon = STATE_ICONS[uploadState]

  // Empty / initial state
  if (!selectedFile && !result) {
    return (
      <div className="space-y-6">
        <PageHeader title="Import Data" description="Upload conversation data from CSV or JSONL files" />

        {/* Drop zone */}
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
          <StateIcon
            className={cn(
              'mb-4 size-10 text-muted-foreground',
              uploadState === 'dragover' && 'text-foreground'
            )}
          />
          <p className="mb-1 text-sm font-medium">
            {uploadState === 'dragover' ? 'Drop your file here' : 'Drag and drop your file here'}
          </p>
          <p className="mb-4 text-xs text-muted-foreground">
            Supports .csv, .jsonl, and .ndjson files
          </p>
          <Button variant="outline" size="sm" onClick={e => { e.stopPropagation(); fileInputRef.current?.click() }}>
            Browse files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.jsonl,.ndjson"
            className="hidden"
            onChange={handleInputChange}
          />
        </div>

        <EmptyState
          icon={ArrowDownToLine}
          title="No data imported yet"
          description="Upload a CSV or JSONL file containing conversation data to get started."
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Import Data"
        description="Upload conversation data from CSV or JSONL files"
        actions={
          <Button variant="outline" size="sm" onClick={resetState}>
            <X className="mr-1.5 size-4" />
            New Import
          </Button>
        }
      />

      {/* Drop zone with file info */}
      <div
        className={cn(
          'relative flex min-h-[160px] flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 text-center transition-all',
          STATE_STYLES[uploadState]
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <StateIcon
          className={cn(
            'mb-3 size-8',
            uploadState === 'uploading' && 'animate-spin text-muted-foreground',
            uploadState === 'done' && 'text-foreground',
            uploadState === 'error' && 'text-destructive',
            uploadState === 'dragover' && 'text-foreground',
            uploadState === 'idle' && 'text-muted-foreground'
          )}
        />

        {selectedFile && (
          <div className="mb-2 flex items-center gap-2">
            <span className="text-sm font-medium">{selectedFile.name}</span>
            {detectedFormat && detectedFormat !== 'unknown' && (
              <Badge variant="secondary" className="text-[10px] uppercase">
                {detectedFormat}
              </Badge>
            )}
          </div>
        )}

        {uploadState === 'uploading' && (
          <p className="text-xs text-muted-foreground">Processing file...</p>
        )}
        {uploadState === 'done' && (
          <p className="text-xs text-muted-foreground">Import complete</p>
        )}
        {uploadState === 'error' && uploadError && (
          <p className="text-xs text-destructive">{uploadError}</p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.jsonl,.ndjson"
          className="hidden"
          onChange={handleInputChange}
        />
      </div>

      {/* Error with retry */}
      {uploadState === 'error' && (
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={handleRetry}>
            <RefreshCw className="mr-1.5 size-4" />
            Retry
          </Button>
          <Button variant="ghost" size="sm" onClick={resetState}>
            Choose another file
          </Button>
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Summary counts */}
          <div className="grid gap-3 sm:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground">Imported</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-3xl font-bold">
                  {result.conversations_imported}
                </span>
                <span className="ml-1.5 text-sm text-muted-foreground">conversations</span>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground">Failed</CardTitle>
              </CardHeader>
              <CardContent>
                <span
                  className="text-3xl font-bold"
                >
                  {result.conversations_failed}
                </span>
                <span className="ml-1.5 text-sm text-muted-foreground">conversations</span>
              </CardContent>
            </Card>
          </div>

          {/* Error table */}
          {result.errors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Import Errors</CardTitle>
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
                    {result.errors.map((err, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-mono text-xs">{err.line}</TableCell>
                        <TableCell className="text-xs text-destructive">
                          {err.error}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Parsed conversations */}
          {result.conversations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">
                  Parsed Conversations ({result.conversations.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Accordion type="multiple" className="w-full">
                  {result.conversations.map(conv => (
                    <AccordionItem key={conv.conversation_id} value={conv.conversation_id}>
                      <AccordionTrigger className="py-3 text-sm">
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-xs">
                            {conv.conversation_id.slice(0, 16)}...
                          </span>
                          <Badge variant="secondary" className="text-[10px]">
                            {conv.dominio}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {conv.turnos.length} turns
                          </span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-2 pl-1">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-muted-foreground">ID: </span>
                              <span className="font-mono">{conv.conversation_id}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Seed: </span>
                              <span className="font-mono">{conv.seed_id}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Domain: </span>
                              <span>{conv.dominio}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Turns: </span>
                              <span>{conv.turnos.length}</span>
                            </div>
                          </div>
                          {conv.turnos.slice(0, 3).map(turn => (
                            <div key={turn.turno} className="rounded border bg-muted/30 px-3 py-2 text-xs">
                              <span className="font-medium">{turn.rol}:</span>{' '}
                              <span className="text-muted-foreground">
                                {turn.contenido.length > 120
                                  ? turn.contenido.slice(0, 120) + '...'
                                  : turn.contenido}
                              </span>
                            </div>
                          ))}
                          {conv.turnos.length > 3 && (
                            <p className="text-[10px] text-muted-foreground">
                              +{conv.turnos.length - 3} more turns
                            </p>
                          )}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-3">
            {result.conversations.length > 0 && (
              <Button
                onClick={handleSaveToLocalStore}
                disabled={saved}
                variant={saved ? 'outline' : 'default'}
              >
                {saved ? (
                  <CheckCircle2 className="mr-1.5 size-4" />
                ) : (
                  <Save className="mr-1.5 size-4" />
                )}
                {saved ? 'Saved to Local Store' : 'Save to Local Store'}
              </Button>
            )}

            {saved && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/conversations">
                  View in Conversations
                </Link>
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  )
}
