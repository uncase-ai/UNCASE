'use client'

import { useCallback, useState } from 'react'

import Link from 'next/link'
import {
  Anchor,
  AlertTriangle,
  ChevronDown,
  Copy,
  Check,
  ExternalLink,
  Fingerprint,
  Layers,
  Link2,
  Loader2,
  RefreshCw,
  Search
} from 'lucide-react'

import type { BlockchainStats, MerkleBatch, VerificationResponse } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatsCard } from '../stats-card'
import { StatusBadge } from '../status-badge'
import {
  fetchBlockchainStats,
  fetchBatches,
  fetchVerification,
  buildBatch,
  retryAnchor
} from '@/lib/api/blockchain'

type AnchorFilter = 'all' | 'anchored' | 'pending' | 'failed'

function truncateHash(hash: string, chars = 10): string {
  if (hash.length <= chars * 2 + 2) return hash

  return `${hash.slice(0, chars)}...${hash.slice(-chars)}`
}

export function BlockchainPage() {
  const [anchorFilter, setAnchorFilter] = useState<AnchorFilter>('all')
  const [searchId, setSearchId] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [verification, setVerification] = useState<VerificationResponse | null>(null)
  const [verifyError, setVerifyError] = useState<string | null>(null)
  const [proofOpen, setProofOpen] = useState(false)
  const [copiedHash, setCopiedHash] = useState(false)
  const [building, setBuilding] = useState(false)
  const [retrying, setRetrying] = useState<string | null>(null)

  // ─── Data fetchers ───
  const statsFetcher = useCallback((signal: AbortSignal) => fetchBlockchainStats(signal), [])

  const batchFetcher = useCallback(
    (signal: AbortSignal) => {
      const params: { anchored?: boolean; limit?: number } = { limit: 50 }

      if (anchorFilter === 'anchored') params.anchored = true
      else if (anchorFilter === 'pending' || anchorFilter === 'failed') params.anchored = false

      return fetchBatches(params, signal)
    },
    [anchorFilter]
  )

  const { data: stats, loading: statsLoading, execute: refreshStats } = useApi<BlockchainStats>(statsFetcher)
  const { data: batches, loading: batchesLoading, execute: refreshBatches } = useApi<MerkleBatch[]>(batchFetcher)

  // Filter failed batches client-side (API only supports anchored=true/false)
  const filteredBatches = (batches ?? []).filter(b => {
    if (anchorFilter === 'failed') return !b.anchored && b.anchor_error
    if (anchorFilter === 'pending') return !b.anchored && !b.anchor_error

    return true
  })

  // ─── Actions ───
  const handleVerify = async () => {
    if (!searchId.trim()) return
    setVerifying(true)
    setVerifyError(null)
    setVerification(null)
    setProofOpen(false)

    const res = await fetchVerification(searchId.trim())

    if (res.data) {
      setVerification(res.data)
    } else {
      setVerifyError(res.error?.message ?? 'Verification failed')
    }

    setVerifying(false)
  }

  const handleBuild = async () => {
    setBuilding(true)
    await buildBatch()
    await refreshStats()
    await refreshBatches()
    setBuilding(false)
  }

  const handleRetry = async (batchId: string) => {
    setRetrying(batchId)
    await retryAnchor(batchId)
    await refreshStats()
    await refreshBatches()
    setRetrying(null)
  }

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedHash(true)
    setTimeout(() => setCopiedHash(false), 2000)
  }

  // ─── Network info ───
  const networkChain = (() => {
    const anchored = (batches ?? []).find(b => b.chain_id)

    if (!anchored) return null

    return {
      chainId: anchored.chain_id,
      name: anchored.chain_id === 137 ? 'Polygon Mainnet' : anchored.chain_id === 80002 ? 'Polygon Amoy (Testnet)' : `Chain ${anchored.chain_id}`,
      contractAddress: anchored.contract_address,
      explorerBase: anchored.chain_id === 137 ? 'https://polygonscan.com' : 'https://amoy.polygonscan.com'
    }
  })()

  // ─── Batch table columns ───
  const batchColumns: Column<MerkleBatch>[] = [
    {
      key: 'batch_number',
      header: '#',
      cell: row => <span className="font-mono text-xs font-medium">{row.batch_number}</span>
    },
    {
      key: 'leaf_count',
      header: 'Leaves',
      cell: row => <span className="text-xs">{row.leaf_count}</span>
    },
    {
      key: 'merkle_root',
      header: 'Merkle Root',
      cell: row => (
        <code className="text-[11px] text-muted-foreground">{truncateHash(row.merkle_root, 8)}</code>
      )
    },
    {
      key: 'anchored',
      header: 'Status',
      cell: row => {
        if (row.anchored) return <StatusBadge variant="success">Anchored</StatusBadge>
        if (row.anchor_error) return <StatusBadge variant="error">Failed</StatusBadge>

        return <StatusBadge variant="warning">Pending</StatusBadge>
      }
    },
    {
      key: 'tx_hash',
      header: 'Transaction',
      cell: row =>
        row.tx_hash ? (
          <a
            href={`${row.chain_id === 137 ? 'https://polygonscan.com' : 'https://amoy.polygonscan.com'}/tx/${row.tx_hash}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline"
          >
            {truncateHash(row.tx_hash, 6)}
            <ExternalLink className="size-3" />
          </a>
        ) : (
          <span className="text-xs text-muted-foreground">—</span>
        )
    },
    {
      key: 'created_at',
      header: 'Created',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    },
    {
      key: 'actions',
      header: '',
      cell: row =>
        !row.anchored && row.anchor_error ? (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => handleRetry(row.id)}
            disabled={retrying === row.id}
          >
            {retrying === row.id ? (
              <Loader2 className="mr-1 size-3 animate-spin" />
            ) : (
              <RefreshCw className="mr-1 size-3" />
            )}
            Retry
          </Button>
        ) : null
    }
  ]

  const isEmpty = !statsLoading && stats && stats.total_hashed === 0

  if (isEmpty) {
    return (
      <div>
        <PageHeader
          title="Blockchain Certification"
          description="On-chain quality verification via Polygon PoS"
        />
        <EmptyState
          icon={Link2}
          title="No blockchain records"
          description="Run quality evaluations to generate hashes. Batches are built automatically or manually, then anchored on Polygon."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/pipeline/evaluate">
                Go to Evaluate
              </Link>
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Blockchain Certification"
        description="On-chain quality verification via Polygon PoS"
        actions={
          <Button variant="outline" size="sm" onClick={handleBuild} disabled={building}>
            {building ? (
              <>
                <Loader2 className="mr-1.5 size-4 animate-spin" /> Building...
              </>
            ) : (
              <>
                <Layers className="mr-1.5 size-4" /> Build Batch
              </>
            )}
          </Button>
        }
      />

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Hashed"
          value={statsLoading ? null : (stats?.total_hashed ?? 0)}
          icon={Fingerprint}
          description="Evaluation reports hashed"
        />
        <StatsCard
          title="Total Batched"
          value={statsLoading ? null : (stats?.total_batched ?? 0)}
          icon={Layers}
          description={`${stats?.total_unbatched ?? 0} unbatched`}
        />
        <StatsCard
          title="Anchored On-Chain"
          value={statsLoading ? null : (stats?.total_anchored ?? 0)}
          icon={Anchor}
          description="Verified on Polygon"
        />
        <StatsCard
          title="Pending / Failed"
          value={statsLoading ? null : ((stats?.total_pending_anchor ?? 0) + (stats?.total_failed_anchor ?? 0))}
          icon={AlertTriangle}
          description={`${stats?.total_pending_anchor ?? 0} pending, ${stats?.total_failed_anchor ?? 0} failed`}
        />
      </div>

      {/* Verification Lookup */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <Search className="size-4" /> Verification Lookup
          </CardTitle>
          <CardDescription>Search by evaluation report ID to verify on-chain anchoring</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Enter evaluation report ID..."
              value={searchId}
              onChange={e => setSearchId(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') handleVerify()
              }}
              className="max-w-md font-mono text-sm"
            />
            <Button variant="outline" size="sm" onClick={handleVerify} disabled={verifying || !searchId.trim()}>
              {verifying ? <Loader2 className="size-4 animate-spin" /> : 'Verify'}
            </Button>
          </div>

          {verifyError && (
            <p className="text-sm text-destructive">{verifyError}</p>
          )}

          {verification && (
            <div className="rounded-lg border p-4 space-y-3">
              <div className="flex items-center gap-2">
                {verification.anchored ? (
                  <StatusBadge variant="success">Anchored</StatusBadge>
                ) : verification.batch_id ? (
                  <StatusBadge variant="warning">Batched</StatusBadge>
                ) : (
                  <Badge variant="secondary">Hashed</Badge>
                )}
                <span className="text-xs text-muted-foreground">
                  Hashed {new Date(verification.hashed_at).toLocaleString()}
                </span>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground w-24 shrink-0">Report Hash</span>
                  <code className="flex-1 break-all rounded bg-muted px-2 py-1 text-[11px]">
                    {verification.report_hash}
                  </code>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-7 shrink-0"
                    onClick={() => copyToClipboard(verification.report_hash)}
                  >
                    {copiedHash ? <Check className="size-3" /> : <Copy className="size-3" />}
                  </Button>
                </div>

                {verification.batch_number !== null && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">Batch</span>
                    <span className="text-xs">#{verification.batch_number}</span>
                  </div>
                )}

                {verification.tx_hash && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">Transaction</span>
                    <a
                      href={verification.explorer_url ?? '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      {truncateHash(verification.tx_hash, 8)}
                      <ExternalLink className="size-3" />
                    </a>
                  </div>
                )}

                {verification.block_number !== null && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">Block</span>
                    <span className="text-xs font-mono">{verification.block_number}</span>
                  </div>
                )}
              </div>

              {/* Merkle Proof Accordion */}
              {verification.proof && (
                <div className="border-t pt-3">
                  <button
                    onClick={() => setProofOpen(!proofOpen)}
                    className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground"
                  >
                    <ChevronDown className={`size-3 transition-transform ${proofOpen ? 'rotate-180' : ''}`} />
                    Merkle Proof ({verification.proof.siblings.length} siblings)
                  </button>
                  {proofOpen && (
                    <div className="mt-2 space-y-1.5 rounded bg-muted p-3">
                      <div className="text-[10px] text-muted-foreground">
                        <span className="font-medium">Leaf index:</span> {verification.proof.leaf_index}
                      </div>
                      <div className="text-[10px] text-muted-foreground">
                        <span className="font-medium">Leaf hash:</span>{' '}
                        <code className="break-all">{verification.proof.leaf_hash}</code>
                      </div>
                      <div className="text-[10px] text-muted-foreground">
                        <span className="font-medium">Merkle root:</span>{' '}
                        <code className="break-all">{verification.proof.merkle_root}</code>
                      </div>
                      {verification.proof.siblings.map((s, i) => (
                        <div key={i} className="flex items-center gap-2 text-[10px]">
                          <Badge variant="outline" className="text-[9px] px-1">
                            {verification.proof!.directions[i]}
                          </Badge>
                          <code className="break-all text-muted-foreground">{s}</code>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Batch Ledger */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Batch Ledger</h3>
          <Select value={anchorFilter} onValueChange={v => setAnchorFilter(v as AnchorFilter)}>
            <SelectTrigger className="w-[130px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="anchored">Anchored</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <DataTable
          columns={batchColumns}
          data={filteredBatches}
          loading={batchesLoading}
          rowKey={r => r.id}
          emptyMessage="No batches found"
        />
      </div>

      {/* Network Info */}
      {networkChain && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Network Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-24 shrink-0">Network</span>
              <Badge variant="outline">{networkChain.name}</Badge>
            </div>
            {networkChain.contractAddress && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-24 shrink-0">Contract</span>
                <a
                  href={`${networkChain.explorerBase}/address/${networkChain.contractAddress}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-mono text-primary hover:underline"
                >
                  {truncateHash(networkChain.contractAddress, 8)}
                  <ExternalLink className="size-3" />
                </a>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-24 shrink-0">Explorer</span>
              <a
                href={networkChain.explorerBase}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                {networkChain.explorerBase}
                <ExternalLink className="size-3" />
              </a>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
