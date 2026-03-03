'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { AnimatePresence, motion } from 'motion/react'
import {
  AlertTriangle,
  Check,
  ChevronDown,
  CircleDot,
  Clock,
  Copy,
  ExternalLink,
  Fingerprint,
  Hash,
  Layers,
  Link2,
  Loader2,
  Network,
  RefreshCw,
  Search,
  Shield,
  ShieldCheck,
  TreePine,
  Wallet,
  Zap
} from 'lucide-react'

import type { AnchorSchedule, BlockchainStats, MerkleBatch, VerificationResponse } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { Badge } from '@/components/ui/badge'
import { BorderBeam } from '@/components/ui/border-beam'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NumberTicker } from '@/components/ui/number-ticker'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { StatusBadge } from '../status-badge'
import {
  fetchBlockchainStats,
  fetchBatches,
  fetchVerification,
  fetchAnchorSchedule,
  buildBatch,
  retryAnchor
} from '@/lib/api/blockchain'
import { isDemoMode } from '@/lib/demo'
import { DEMO_BLOCKCHAIN_STATS, DEMO_BATCHES, DEMO_ANCHOR_SCHEDULE, getDemoVerification } from '@/lib/demo/blockchain'

type AnchorFilter = 'all' | 'anchored' | 'pending' | 'failed'

function truncateHash(hash: string, chars = 10): string {
  if (hash.length <= chars * 2 + 2) return hash

  return `${hash.slice(0, chars)}...${hash.slice(-chars)}`
}

// ─── Trust Score Hero ───
function TrustScoreHero({ stats, loading }: { stats: BlockchainStats | null; loading: boolean }) {
  const { score, label, color } = useMemo(() => {
    if (!stats || stats.total_hashed === 0) return { score: 0, label: 'No Data', color: 'text-muted-foreground' }

    const hashRate = stats.total_hashed > 0 ? 1 : 0
    const batchRate = stats.total_hashed > 0 ? stats.total_batched / stats.total_hashed : 0
    const anchorRate = stats.total_batches > 0 ? stats.total_anchored / stats.total_batches : 0
    const failRate = stats.total_batches > 0 ? stats.total_failed_anchor / stats.total_batches : 0

    const raw = (hashRate * 20 + batchRate * 30 + anchorRate * 40 + (1 - failRate) * 10)
    const s = Math.round(Math.min(100, Math.max(0, raw)))

    if (s >= 90) return { score: s, label: 'Excellent', color: 'text-emerald-500' }
    if (s >= 70) return { score: s, label: 'Good', color: 'text-emerald-400' }
    if (s >= 50) return { score: s, label: 'Fair', color: 'text-yellow-500' }

    return { score: s, label: 'Needs Attention', color: 'text-orange-500' }
  }, [stats])

  return (
    <Card className="relative overflow-hidden">
      <BorderBeam size={120} duration={8} colorFrom="#8b5cf6" colorTo="#06b6d4" borderWidth={2} />
      <CardContent className="p-6">
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          {/* Animated shield */}
          <div className="relative flex shrink-0 items-center justify-center">
            <motion.div
              className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-500/20 via-cyan-500/20 to-emerald-500/20"
              animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              style={{ width: 96, height: 96 }}
            />
            <div className="relative flex size-24 items-center justify-center rounded-full border-2 border-violet-500/30 bg-gradient-to-br from-violet-950/80 via-slate-900/80 to-cyan-950/80">
              {loading ? (
                <Loader2 className="size-8 animate-spin text-violet-400" />
              ) : (
                <ShieldCheck className={`size-10 ${score >= 70 ? 'text-emerald-400' : score >= 50 ? 'text-yellow-400' : 'text-orange-400'}`} />
              )}
            </div>
          </div>

          <div className="flex-1 text-center sm:text-left">
            <div className="flex items-center justify-center gap-3 sm:justify-start">
              <h2 className="text-lg font-semibold">Blockchain Trust Score</h2>
              <Badge variant="outline" className={`${color} border-current/30 text-xs font-medium`}>
                {label}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Composite integrity score based on hashing coverage, batch completeness, and on-chain anchor verification across Polygon PoS.
            </p>

            <div className="mt-4 flex items-end gap-3">
              {loading ? (
                <Skeleton className="h-12 w-24" />
              ) : (
                <span className={`text-5xl font-extrabold tabular-nums tracking-tight ${color}`}>
                  <NumberTicker value={score} />
                </span>
              )}
              <span className="mb-1 text-lg text-muted-foreground">/100</span>
            </div>

            <div className="mt-3 max-w-md">
              <Progress value={loading ? 0 : score} className="h-2" />
            </div>

            <div className="mt-4 flex flex-wrap gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-violet-500" />
                Hashing: {stats ? '100%' : '—'}
              </div>
              <div className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-cyan-500" />
                Batched: {stats && stats.total_hashed > 0 ? `${Math.round(stats.total_batched / stats.total_hashed * 100)}%` : '—'}
              </div>
              <div className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-emerald-500" />
                Anchored: {stats && stats.total_batches > 0 ? `${Math.round(stats.total_anchored / stats.total_batches * 100)}%` : '—'}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Pipeline Status Steps ───
function PipelineSteps({ stats, loading }: { stats: BlockchainStats | null; loading: boolean }) {
  const steps = useMemo(() => {
    if (!stats) {
      return [
        { label: 'Evaluate', desc: 'Quality reports generated', count: 0, done: false },
        { label: 'Hash', desc: 'SHA-256 fingerprints', count: 0, done: false },
        { label: 'Batch', desc: 'Merkle trees built', count: 0, done: false },
        { label: 'Anchor', desc: 'Polygon on-chain', count: 0, done: false }
      ]
    }

    return [
      { label: 'Evaluate', desc: 'Quality reports generated', count: stats.total_hashed, done: stats.total_hashed > 0 },
      { label: 'Hash', desc: 'SHA-256 fingerprints', count: stats.total_hashed, done: stats.total_hashed > 0 },
      { label: 'Batch', desc: 'Merkle trees built', count: stats.total_batches, done: stats.total_batches > 0 },
      { label: 'Anchor', desc: 'Polygon on-chain', count: stats.total_anchored, done: stats.total_anchored > 0 }
    ]
  }, [stats])

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Network className="size-4" /> Certification Pipeline
        </CardTitle>
        <CardDescription>Each evaluation flows through four tamper-proof stages</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-start justify-between gap-2">
          {steps.map((step, i) => (
            <div key={step.label} className="flex flex-1 items-start gap-2">
              <div className="flex flex-col items-center gap-1.5">
                <motion.div
                  className={`flex size-10 items-center justify-center rounded-full border-2 transition-colors ${
                    step.done
                      ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-500'
                      : 'border-muted bg-muted/50 text-muted-foreground'
                  }`}
                  animate={step.done ? { scale: [1, 1.05, 1] } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  {loading ? (
                    <Skeleton className="size-4 rounded-full" />
                  ) : step.done ? (
                    <Check className="size-4" />
                  ) : (
                    <CircleDot className="size-4" />
                  )}
                </motion.div>
                <div className="text-center">
                  <p className="text-xs font-semibold">{step.label}</p>
                  <p className="text-[10px] text-muted-foreground">{step.desc}</p>
                  {!loading && (
                    <p className="mt-0.5 text-sm font-bold tabular-nums">
                      <NumberTicker value={step.count} />
                    </p>
                  )}
                </div>
              </div>
              {i < steps.length - 1 && (
                <div className="mt-4 flex-1">
                  <div className={`h-0.5 w-full rounded-full ${step.done ? 'bg-emerald-500/40' : 'bg-muted'}`} />
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Verification Result ───
function VerificationResult({
  verification,
  onCopy
}: {
  verification: VerificationResponse
  onCopy: (text: string) => void
}) {
  const [proofOpen, setProofOpen] = useState(false)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  const handleCopy = (text: string, field: string) => {
    onCopy(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const statusConfig = verification.anchored
    ? { icon: ShieldCheck, label: 'Verified On-Chain', variant: 'success' as const, desc: 'This evaluation is cryptographically anchored on Polygon and independently verifiable.' }
    : verification.batch_id
      ? { icon: Layers, label: 'Batched (Pending Anchor)', variant: 'warning' as const, desc: 'Included in a Merkle batch. On-chain anchoring is pending.' }
      : { icon: Hash, label: 'Hashed', variant: 'info' as const, desc: 'SHA-256 fingerprint generated. Waiting for batch inclusion.' }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Status banner */}
      <div className={`flex items-start gap-3 rounded-lg border p-4 ${
        verification.anchored
          ? 'border-emerald-500/30 bg-emerald-500/5'
          : verification.batch_id
            ? 'border-yellow-500/30 bg-yellow-500/5'
            : 'border-muted'
      }`}>
        <statusConfig.icon className={`mt-0.5 size-5 shrink-0 ${
          verification.anchored ? 'text-emerald-500' : verification.batch_id ? 'text-yellow-500' : 'text-muted-foreground'
        }`} />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold">{statusConfig.label}</span>
            <StatusBadge variant={statusConfig.variant}>{statusConfig.label}</StatusBadge>
          </div>
          <p className="mt-0.5 text-xs text-muted-foreground">{statusConfig.desc}</p>
        </div>
      </div>

      {/* Detail fields */}
      <div className="grid gap-3 rounded-lg border p-4">
        <DetailRow
          label="Report ID"
          value={verification.evaluation_report_id}
          mono
          onCopy={() => handleCopy(verification.evaluation_report_id, 'id')}
          copied={copiedField === 'id'}
        />
        <Separator />
        <DetailRow
          label="SHA-256 Hash"
          value={verification.report_hash}
          mono
          onCopy={() => handleCopy(verification.report_hash, 'hash')}
          copied={copiedField === 'hash'}
        />
        <Separator />
        <DetailRow
          label="Hashed At"
          value={new Date(verification.hashed_at).toLocaleString()}
        />

        {verification.batch_number !== null && (
          <>
            <Separator />
            <DetailRow label="Batch Number" value={`#${verification.batch_number}`} />
          </>
        )}

        {verification.tx_hash && (
          <>
            <Separator />
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium text-muted-foreground">Transaction</span>
              <div className="flex items-center gap-2">
                <a
                  href={verification.explorer_url ?? '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 rounded-md bg-violet-500/10 px-2 py-1 text-xs font-mono text-violet-600 hover:bg-violet-500/20 dark:text-violet-400"
                >
                  {truncateHash(verification.tx_hash, 10)}
                  <ExternalLink className="size-3" />
                </a>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-7"
                  onClick={() => handleCopy(verification.tx_hash!, 'tx')}
                >
                  {copiedField === 'tx' ? <Check className="size-3" /> : <Copy className="size-3" />}
                </Button>
              </div>
            </div>
          </>
        )}

        {verification.block_number !== null && (
          <>
            <Separator />
            <DetailRow label="Block Number" value={verification.block_number.toLocaleString()} mono />
          </>
        )}

        {verification.chain_id !== null && (
          <>
            <Separator />
            <DetailRow
              label="Network"
              value={verification.chain_id === 137 ? 'Polygon Mainnet' : verification.chain_id === 80002 ? 'Polygon Amoy Testnet' : `Chain ${verification.chain_id}`}
            />
          </>
        )}
      </div>

      {/* Merkle Proof Expandable */}
      {verification.proof && (
        <div className="rounded-lg border">
          <button
            onClick={() => setProofOpen(!proofOpen)}
            className="flex w-full items-center justify-between gap-2 p-4 text-left hover:bg-muted/50"
          >
            <div className="flex items-center gap-2">
              <TreePine className="size-4 text-cyan-500" />
              <span className="text-sm font-medium">Merkle Proof</span>
              <Badge variant="secondary" className="text-[10px]">
                {verification.proof.siblings.length} sibling{verification.proof.siblings.length !== 1 ? 's' : ''}
              </Badge>
            </div>
            <ChevronDown className={`size-4 text-muted-foreground transition-transform ${proofOpen ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {proofOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="border-t bg-muted/30 p-4 space-y-3">
                  <div className="grid gap-2 text-[11px]">
                    <div className="flex items-center gap-2">
                      <span className="w-20 shrink-0 font-medium text-muted-foreground">Leaf Index</span>
                      <code className="rounded bg-muted px-2 py-0.5">{verification.proof.leaf_index}</code>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="w-20 shrink-0 pt-0.5 font-medium text-muted-foreground">Leaf Hash</span>
                      <code className="break-all rounded bg-muted px-2 py-0.5 font-mono">{verification.proof.leaf_hash}</code>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="w-20 shrink-0 pt-0.5 font-medium text-muted-foreground">Root</span>
                      <code className="break-all rounded bg-muted px-2 py-0.5 font-mono">{verification.proof.merkle_root}</code>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Sibling Path
                    </p>
                    {verification.proof.siblings.map((sibling, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="flex items-center gap-2"
                      >
                        <span className="flex size-5 shrink-0 items-center justify-center rounded bg-violet-500/10 text-[9px] font-bold text-violet-500">
                          {i}
                        </span>
                        <Badge
                          variant="outline"
                          className={`shrink-0 text-[9px] ${
                            verification.proof!.directions[i] === 'left'
                              ? 'border-cyan-500/30 text-cyan-600 dark:text-cyan-400'
                              : 'border-amber-500/30 text-amber-600 dark:text-amber-400'
                          }`}
                        >
                          {verification.proof!.directions[i]}
                        </Badge>
                        <code className="flex-1 break-all text-[10px] text-muted-foreground">{sibling}</code>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  )
}

// ─── Detail Row Helper ───
function DetailRow({
  label,
  value,
  mono,
  onCopy,
  copied
}: {
  label: string
  value: string
  mono?: boolean
  onCopy?: () => void
  copied?: boolean
}) {
  return (
    <div className="flex items-center justify-between gap-2">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className={`text-xs ${mono ? 'max-w-[280px] truncate font-mono' : ''}`}>
          {value}
        </span>
        {onCopy && (
          <Button variant="ghost" size="icon" className="size-6" onClick={onCopy}>
            {copied ? <Check className="size-3 text-emerald-500" /> : <Copy className="size-3" />}
          </Button>
        )}
      </div>
    </div>
  )
}

// ─── Network Info Panel ───
function NetworkInfoPanel({ batches }: { batches: MerkleBatch[] | null }) {
  const networkChain = useMemo(() => {
    const anchored = (batches ?? []).find(b => b.chain_id)

    if (!anchored) return null

    return {
      chainId: anchored.chain_id,
      name: anchored.chain_id === 137 ? 'Polygon Mainnet' : anchored.chain_id === 80002 ? 'Polygon Amoy (Testnet)' : `Chain ${anchored.chain_id}`,
      contractAddress: anchored.contract_address,
      explorerBase: anchored.chain_id === 137 ? 'https://polygonscan.com' : 'https://amoy.polygonscan.com',
      isMainnet: anchored.chain_id === 137
    }
  }, [batches])

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Wallet className="size-4" /> Network & Contract
        </CardTitle>
      </CardHeader>
      <CardContent>
        {networkChain ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Network</span>
              <div className="flex items-center gap-2">
                <span className={`size-2 rounded-full ${networkChain.isMainnet ? 'bg-emerald-500' : 'bg-yellow-500'}`} />
                <span className="text-xs font-medium">{networkChain.name}</span>
              </div>
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Chain ID</span>
              <code className="text-xs font-mono">{networkChain.chainId}</code>
            </div>
            {networkChain.contractAddress && (
              <>
                <Separator />
                <div className="flex items-center justify-between gap-2">
                  <span className="shrink-0 text-xs text-muted-foreground">Contract</span>
                  <a
                    href={`${networkChain.explorerBase}/address/${networkChain.contractAddress}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 truncate rounded-md bg-violet-500/10 px-2 py-0.5 text-[11px] font-mono text-violet-600 hover:bg-violet-500/20 dark:text-violet-400"
                  >
                    {truncateHash(networkChain.contractAddress, 8)}
                    <ExternalLink className="size-3 shrink-0" />
                  </a>
                </div>
              </>
            )}
            <Separator />
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Explorer</span>
              <a
                href={networkChain.explorerBase}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                PolygonScan
                <ExternalLink className="size-3" />
              </a>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 py-4 text-center">
            <div className="flex size-10 items-center justify-center rounded-full bg-muted">
              <Link2 className="size-5 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground">
              No on-chain data yet. Anchor a batch to see network details.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Auto Anchor Status ───
function humanizeInterval(seconds: number): string {
  if (seconds < 120) return `Every ${seconds}s`
  if (seconds < 7200) return `Every ${Math.round(seconds / 60)} minutes`
  if (seconds < 86400) return `Every ${Math.round(seconds / 3600)} hour${Math.round(seconds / 3600) !== 1 ? 's' : ''}`

  return 'Daily'
}

function AutoAnchorStatus({ schedule, loading }: { schedule: AnchorSchedule | null; loading: boolean }) {
  const statusInfo = useMemo(() => {
    if (!schedule) return { label: 'Loading', color: 'text-muted-foreground', bg: 'bg-muted' }
    if (schedule.configured) return { label: 'Active', color: 'text-emerald-500', bg: 'bg-emerald-500/10' }
    if (schedule.enabled) return { label: 'Pending Setup', color: 'text-yellow-500', bg: 'bg-yellow-500/10' }

    return { label: 'Disabled', color: 'text-muted-foreground', bg: 'bg-muted' }
  }, [schedule])

  const steps = [
    {
      icon: Fingerprint,
      title: 'Evaluate',
      desc: 'Quality reports are automatically SHA-256 hashed after each evaluation run.'
    },
    {
      icon: Layers,
      title: 'Batch',
      desc: 'Hashes are grouped into Merkle trees on a scheduled interval.'
    },
    {
      icon: ShieldCheck,
      title: 'Anchor',
      desc: 'Merkle roots are written to Polygon, funded and managed by UNCASE.'
    }
  ]

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Zap className="size-4" /> Auto-Anchor
        </CardTitle>
        <CardDescription>UNCASE handles anchoring automatically — your evaluations are verified on-chain without any configuration</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Status row */}
        <div className="flex flex-wrap items-center gap-4">
          {loading ? (
            <Skeleton className="h-6 w-32" />
          ) : (
            <>
              <Badge variant="outline" className={`${statusInfo.color} border-current/30 text-xs font-medium`}>
                <span className={`mr-1.5 inline-block size-1.5 rounded-full ${statusInfo.bg} ${schedule?.configured ? 'animate-pulse' : ''}`} style={{ backgroundColor: schedule?.configured ? '#10b981' : undefined }} />
                {statusInfo.label}
              </Badge>
              {schedule && (
                <>
                  <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock className="size-3" />
                    {humanizeInterval(schedule.interval_seconds)}
                  </span>
                  {schedule.pending_hashes > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {schedule.pending_hashes} hash{schedule.pending_hashes !== 1 ? 'es' : ''} awaiting batch
                    </span>
                  )}
                  {schedule.failed_anchor > 0 && (
                    <span className="flex items-center gap-1 text-xs text-yellow-500">
                      <AlertTriangle className="size-3" />
                      {schedule.failed_anchor} failed — will retry automatically
                    </span>
                  )}
                </>
              )}
            </>
          )}
        </div>

        <Separator />

        {/* How it works */}
        <div className="grid gap-3 sm:grid-cols-3">
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex gap-3 rounded-lg border p-3"
            >
              <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-cyan-500/20">
                <step.icon className="size-4 text-violet-500" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="flex size-5 items-center justify-center rounded-full bg-muted text-[10px] font-bold">
                    {i + 1}
                  </span>
                  <p className="text-xs font-semibold">{step.title}</p>
                </div>
                <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Main Page ───
export function BlockchainPage() {
  const searchParams = useSearchParams()
  const [anchorFilter, setAnchorFilter] = useState<AnchorFilter>('all')
  const [searchId, setSearchId] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [verification, setVerification] = useState<VerificationResponse | null>(null)
  const [verifyError, setVerifyError] = useState<string | null>(null)
  const [building, setBuilding] = useState(false)
  const [retrying, setRetrying] = useState<string | null>(null)

  // Auto-fill from search params (linked from evaluations page)
  useEffect(() => {
    const verifyId = searchParams.get('verify')

    if (verifyId) {
      setSearchId(verifyId)
    }
  }, [searchParams])

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

  const scheduleFetcher = useCallback((signal: AbortSignal) => fetchAnchorSchedule(signal), [])

  const { data: apiStats, loading: statsLoading, execute: refreshStats } = useApi<BlockchainStats>(statsFetcher)
  const { data: apiBatches, loading: batchesLoading, execute: refreshBatches } = useApi<MerkleBatch[]>(batchFetcher)
  const { data: apiSchedule, loading: scheduleLoading } = useApi<AnchorSchedule>(scheduleFetcher)

  // Demo fallback: use demo data when API returns empty and demo mode is active
  const demo = isDemoMode()
  const stats = apiStats && apiStats.total_hashed > 0 ? apiStats : demo ? DEMO_BLOCKCHAIN_STATS : apiStats
  const batches = apiBatches && apiBatches.length > 0 ? apiBatches : demo ? DEMO_BATCHES : apiBatches
  const schedule = apiSchedule ?? (demo ? DEMO_ANCHOR_SCHEDULE : null)

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

    const res = await fetchVerification(searchId.trim())

    if (res.data && res.data.report_hash) {
      setVerification(res.data)
    } else if (demo) {
      const demoResult = getDemoVerification(searchId.trim())

      if (demoResult) {
        setVerification(demoResult)
      } else {
        setVerifyError('No demo verification found for this ID. Try: demo-conv-001, demo-conv-005, demo-conv-011, demo-conv-015, or demo-conv-019')
      }
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
  }

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
      cell: row => (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="text-xs tabular-nums">{row.leaf_count}</span>
            </TooltipTrigger>
            <TooltipContent>
              <p>{row.leaf_count} evaluation hashes in this Merkle tree (depth: {row.tree_depth})</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )
    },
    {
      key: 'merkle_root',
      header: 'Merkle Root',
      cell: row => (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <code className="cursor-help text-[11px] text-muted-foreground">{truncateHash(row.merkle_root, 8)}</code>
            </TooltipTrigger>
            <TooltipContent>
              <code className="text-[10px]">{row.merkle_root}</code>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )
    },
    {
      key: 'anchored',
      header: 'Status',
      cell: row => {
        if (row.anchored) return <StatusBadge variant="success">Anchored</StatusBadge>
        if (row.anchor_error) {
          return (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span><StatusBadge variant="error">Failed</StatusBadge></span>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">{row.anchor_error}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )
        }

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
            className="inline-flex items-center gap-1 rounded-md bg-violet-500/10 px-2 py-0.5 text-[11px] font-mono text-violet-600 hover:bg-violet-500/20 dark:text-violet-400"
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
      <div className="space-y-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20">
              <ShieldCheck className="size-5 text-violet-500" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">Blockchain Certification</h1>
              <p className="text-[15px] text-muted-foreground">Immutable quality verification via Polygon PoS</p>
            </div>
          </div>
        </div>

        <EmptyState
          icon={ShieldCheck}
          title="No blockchain records yet"
          description="Run quality evaluations to generate SHA-256 hashes. Then build Merkle batches and anchor them on Polygon for tamper-proof certification."
          action={
            <div className="flex gap-2">
              <Button asChild variant="outline">
                <Link href="/dashboard/pipeline/evaluate">
                  Go to Evaluate
                </Link>
              </Button>
            </div>
          }
        />

        <AutoAnchorStatus schedule={schedule} loading={scheduleLoading} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col items-center gap-3 text-center sm:flex-row sm:items-center sm:justify-between sm:text-left">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20">
            <ShieldCheck className="size-5 text-violet-500" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">Blockchain Certification</h1>
            <p className="text-[15px] text-muted-foreground">Immutable quality verification via Polygon PoS</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
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
        </div>
      </div>

      {/* Trust Score Hero */}
      <TrustScoreHero stats={stats} loading={statsLoading} />

      {/* Pipeline Steps */}
      <PipelineSteps stats={stats} loading={statsLoading} />

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="relative overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Total Hashed</span>
              <Fingerprint className="size-4 text-violet-500" />
            </div>
            <div className="mt-2">
              {statsLoading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">
                  <NumberTicker value={stats?.total_hashed ?? 0} />
                </div>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">SHA-256 fingerprints</p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Total Batched</span>
              <Layers className="size-4 text-cyan-500" />
            </div>
            <div className="mt-2">
              {statsLoading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">
                  <NumberTicker value={stats?.total_batched ?? 0} />
                </div>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">{stats?.total_unbatched ?? 0} unbatched</p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-emerald-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Anchored On-Chain</span>
              <ShieldCheck className="size-4 text-emerald-500" />
            </div>
            <div className="mt-2">
              {statsLoading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  <NumberTicker value={stats?.total_anchored ?? 0} />
                </div>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Verified on Polygon</p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Pending / Failed</span>
              <AlertTriangle className="size-4 text-orange-500" />
            </div>
            <div className="mt-2">
              {statsLoading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">
                  <NumberTicker value={(stats?.total_pending_anchor ?? 0) + (stats?.total_failed_anchor ?? 0)} />
                </div>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {stats?.total_pending_anchor ?? 0} pending, {stats?.total_failed_anchor ?? 0} failed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabbed Content */}
      <Tabs defaultValue="verify" className="space-y-4">
        <TabsList>
          <TabsTrigger value="verify">
            <Search className="mr-1.5 size-3.5" /> Verify
          </TabsTrigger>
          <TabsTrigger value="batches">
            <Layers className="mr-1.5 size-3.5" /> Batch Ledger
          </TabsTrigger>
          <TabsTrigger value="network">
            <Network className="mr-1.5 size-3.5" /> Network
          </TabsTrigger>
          <TabsTrigger value="guide">
            <Zap className="mr-1.5 size-3.5" /> Auto-Anchor
          </TabsTrigger>
        </TabsList>

        {/* Verify Tab */}
        <TabsContent value="verify">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Search className="size-4 text-violet-500" /> Verification Lookup
              </CardTitle>
              <CardDescription>
                Enter an evaluation report ID to verify its on-chain anchoring status, Merkle proof, and transaction details.
              </CardDescription>
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
                  className="max-w-lg font-mono text-sm"
                />
                <Button onClick={handleVerify} disabled={verifying || !searchId.trim()}>
                  {verifying ? <Loader2 className="mr-1.5 size-4 animate-spin" /> : <Search className="mr-1.5 size-4" />}
                  Verify
                </Button>
              </div>

              {verifyError && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3"
                >
                  <AlertTriangle className="size-4 text-destructive" />
                  <p className="text-sm text-destructive">{verifyError}</p>
                </motion.div>
              )}

              {verification && (
                <VerificationResult verification={verification} onCopy={copyToClipboard} />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Batches Tab */}
        <TabsContent value="batches">
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
        </TabsContent>

        {/* Network Tab */}
        <TabsContent value="network">
          <div className="grid gap-4 lg:grid-cols-2">
            <NetworkInfoPanel batches={batches} />

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Shield className="size-4" /> How It Works
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-xs text-muted-foreground">
                <div className="flex gap-3">
                  <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-violet-500/10 text-[10px] font-bold text-violet-500">1</div>
                  <p><strong className="text-foreground">Hash.</strong> Each quality evaluation report is serialized to canonical JSON and hashed with SHA-256, creating a unique 64-character fingerprint.</p>
                </div>
                <div className="flex gap-3">
                  <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-cyan-500/10 text-[10px] font-bold text-cyan-500">2</div>
                  <p><strong className="text-foreground">Batch.</strong> Multiple hashes are grouped into a binary Merkle tree. Each leaf gets a cryptographic proof linking it to the tree root.</p>
                </div>
                <div className="flex gap-3">
                  <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-[10px] font-bold text-emerald-500">3</div>
                  <p><strong className="text-foreground">Anchor.</strong> The Merkle root is submitted to a smart contract on Polygon PoS. This creates a permanent, publicly verifiable on-chain record.</p>
                </div>
                <div className="flex gap-3">
                  <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-amber-500/10 text-[10px] font-bold text-amber-500">4</div>
                  <p><strong className="text-foreground">Verify.</strong> Anyone can verify a report by recomputing its hash, walking the Merkle proof, and checking the root against the on-chain record.</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Auto-Anchor Tab */}
        <TabsContent value="guide">
          <AutoAnchorStatus schedule={schedule} loading={scheduleLoading} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
