'use client'

import { useEffect, useState } from 'react'

import Link from 'next/link'
import {
  ArrowDownToLine,
  ArrowRight,
  CheckCircle2,
  FlaskConical,
  Library,
  Loader2,
  Lock,
  PackageOpen,
  Plus,
  Rocket,
  Sprout
} from 'lucide-react'

import type { JobResponse } from '@/types/api'
import { fetchJobs, getJobStatusColor } from '@/lib/api/jobs'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

import { PageHeader } from '../page-header'

// ─── Stage readiness from localStorage ───

function getLocalCount(key: string): number {
  if (typeof window === 'undefined') return 0

  try {
    const raw = localStorage.getItem(key)

    return raw ? JSON.parse(raw).length : 0
  } catch {
    return 0
  }
}

function getEvalPassCount(): number {
  if (typeof window === 'undefined') return 0

  try {
    const raw = localStorage.getItem('uncase-evaluations')

    if (!raw) return 0
    const evals = JSON.parse(raw) as { passed?: boolean }[]

    return evals.filter(e => e.passed).length
  } catch {
    return 0
  }
}

interface StageConfig {
  id: string
  label: string
  description: string
  icon: typeof Sprout
  href: string
  details: string[]
  isReady: () => boolean
  lockedReason?: string
  getCount: () => number
  countLabel: string
  cta: string
  ctaHref: string
}

const STAGES: StageConfig[] = [
  {
    id: 'seed',
    label: 'Seed Engineering',
    description: 'Define conversation structure, domain, roles, and quality constraints.',
    icon: Sprout,
    href: '/dashboard/pipeline/seeds',
    details: [
      'Define domain (automotive, medical, legal...)',
      'Set roles and turn structure',
      'Configure factual parameters'
    ],
    isReady: () => true,
    getCount: () => getLocalCount('uncase-seeds'),
    countLabel: 'seeds',
    cta: 'Create Seed',
    ctaHref: '/dashboard/pipeline/seeds/new'
  },
  {
    id: 'knowledge',
    label: 'Knowledge Base',
    description: 'Upload domain literature, manuals, and procedures to ground generation in real facts.',
    icon: Library,
    href: '/dashboard/knowledge',
    details: [
      'Product catalogs, SOPs, glossaries',
      'Auto-chunking with overlap',
      'Feeds into seed enrichment and generation'
    ],
    isReady: () => true,
    getCount: () => 0,
    countLabel: 'documents',
    cta: 'Upload Documents',
    ctaHref: '/dashboard/knowledge'
  },
  {
    id: 'import',
    label: 'Data Import',
    description: 'Upload raw conversational data in CSV or JSONL format for seed extraction.',
    icon: ArrowDownToLine,
    href: '/dashboard/pipeline/import',
    details: [
      'Drag-and-drop CSV/JSONL files',
      'Auto-detect format',
      'PII removal at ingestion'
    ],
    isReady: () => true,
    getCount: () => 0,
    countLabel: 'imports',
    cta: 'Import Data',
    ctaHref: '/dashboard/pipeline/import'
  },
  {
    id: 'generate',
    label: 'Synthetic Generation',
    description: 'Generate synthetic conversations from validated seeds using LLM providers.',
    icon: Rocket,
    href: '/dashboard/pipeline/generate',
    details: [
      'Multi-provider LLM support',
      'Knowledge-grounded generation',
      'Auto re-evaluation after generation'
    ],
    isReady: () => getLocalCount('uncase-seeds') > 0,
    lockedReason: 'Create seeds first',
    getCount: () => getLocalCount('uncase-conversations'),
    countLabel: 'conversations',
    cta: 'Generate',
    ctaHref: '/dashboard/pipeline/generate'
  },
  {
    id: 'evaluate',
    label: 'Quality Evaluation',
    description: 'Run 9 quality metrics: ROUGE-L, fidelity, diversity, coherence, tool validity, privacy gate, memorization, and optional LLM-as-Judge scoring.',
    icon: FlaskConical,
    href: '/dashboard/pipeline/evaluate',
    details: [
      '5 core + 2 gate + 2 optional metrics',
      'Fidelity >= 0.80, Coherence >= 0.65, ROUGE-L >= 0.20',
      'Zero PII tolerance + memorization < 1%'
    ],
    isReady: () => getLocalCount('uncase-conversations') > 0,
    lockedReason: 'Generate or import conversations first',
    getCount: () => getEvalPassCount(),
    countLabel: 'passed',
    cta: 'Evaluate',
    ctaHref: '/dashboard/pipeline/evaluate'
  },
  {
    id: 'export',
    label: 'Dataset Export',
    description: 'Bundle certified conversations into training-ready datasets.',
    icon: PackageOpen,
    href: '/dashboard/pipeline/export',
    details: [
      '10 chat template formats',
      'Export as JSONL for fine-tuning',
      'Blockchain-anchored quality certificate'
    ],
    isReady: () => getLocalCount('uncase-conversations') > 0,
    lockedReason: 'Generate or import conversations first',
    getCount: () => getLocalCount('uncase-exports'),
    countLabel: 'exports',
    cta: 'Export',
    ctaHref: '/dashboard/pipeline/export'
  }
]

export function PipelinePage() {
  const readiness = STAGES.map(s => s.isReady())
  const counts = STAGES.map(s => s.getCount())
  const [recentJobs, setRecentJobs] = useState<JobResponse[]>([])
  const [error, setError] = useState<string | null>(null)

  // Fetch recent pipeline/generation jobs from backend
  useEffect(() => {
    let cancelled = false

    fetchJobs({ page: 1, page_size: 5 })
      .then(res => {
        if (!cancelled && res.data) {
          setRecentJobs(Array.isArray(res.data) ? res.data : (res.data as { items: JobResponse[] }).items ?? [])
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load pipeline jobs')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  // Determine the recommended next step
  const seedCount = counts[0]
  const convCount = counts[3]
  const evalCount = counts[4]
  const exportCount = counts[5]

  let nextStepIdx = 0

  if (seedCount > 0 && convCount === 0) nextStepIdx = 3 // generate
  else if (convCount > 0 && evalCount === 0) nextStepIdx = 4 // evaluate
  else if (evalCount > 0 && exportCount === 0) nextStepIdx = 5 // export
  else if (exportCount > 0) nextStepIdx = -1 // all done
  else nextStepIdx = 0 // create seeds

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pipeline"
        description="End-to-end workflow for producing certified synthetic training data"
      />

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
          <p className="text-destructive text-sm">{error}</p>
        </div>
      )}

      {/* Recommended next step */}
      {nextStepIdx >= 0 && (
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="flex items-center gap-3 p-4">
            <ArrowRight className="size-4 shrink-0 text-primary" />
            <div className="flex-1">
              <p className="text-xs font-medium">Recommended next step</p>
              <p className="text-[11px] text-muted-foreground">
                {nextStepIdx === 0 && 'Create your first seed to define the conversation structure for your domain.'}
                {nextStepIdx === 3 && `You have ${seedCount} seed${seedCount !== 1 ? 's' : ''} ready. Generate synthetic conversations from them.`}
                {nextStepIdx === 4 && `You have ${convCount} conversation${convCount !== 1 ? 's' : ''} to evaluate. Run quality checks to certify them.`}
                {nextStepIdx === 5 && `${evalCount} conversation${evalCount !== 1 ? 's' : ''} passed quality checks. Export your certified dataset.`}
              </p>
            </div>
            <Link href={STAGES[nextStepIdx].ctaHref}>
              <Button size="sm" className="gap-1.5">
                {nextStepIdx === 0 && <Plus className="size-3" />}
                {STAGES[nextStepIdx].cta}
                <ArrowRight className="size-3" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {nextStepIdx === -1 && (
        <Card className="bg-green-50/50 border-green-200 dark:bg-green-950/20 dark:border-green-800">
          <CardContent className="flex items-center gap-3 p-4">
            <CheckCircle2 className="size-4 shrink-0 text-green-600 dark:text-green-400" />
            <div className="flex-1">
              <p className="text-xs font-medium text-green-800 dark:text-green-300">Pipeline complete</p>
              <p className="text-[11px] text-green-700/80 dark:text-green-400/70">
                You have certified datasets ready for fine-tuning. Create more seeds or iterate to improve quality.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pipeline stages */}
      <div className="relative">
        {STAGES.map((stage, i) => {
          const ready = readiness[i]
          const count = counts[i]
          const isNext = i === nextStepIdx
          const StageIcon = stage.icon

          const stageContent = (
            <div
              className={cn(
                'group relative flex items-start gap-3 rounded-lg border px-3 py-3 transition-colors sm:gap-4 sm:px-5 sm:py-4',
                isNext && ready && 'border-primary/40 bg-primary/5',
                ready && !isNext && 'bg-background hover:bg-muted/50',
                !ready && 'cursor-default border-dashed bg-muted/20 opacity-60'
              )}
            >
              {/* Step number */}
              <div className="flex flex-col items-center gap-0">
                <div
                  className={cn(
                    'flex size-9 shrink-0 items-center justify-center rounded-full border text-sm font-medium',
                    count > 0 && ready
                      ? 'border-green-300 bg-green-50 text-green-700 dark:border-green-700 dark:bg-green-950 dark:text-green-400'
                      : ready
                        ? 'border-foreground/20 bg-background text-foreground'
                        : 'border-muted-foreground/20 text-muted-foreground'
                  )}
                >
                  {count > 0 && ready ? (
                    <CheckCircle2 className="size-4" />
                  ) : (
                    <StageIcon className="size-4" />
                  )}
                </div>
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={cn('text-[10px] font-normal', !ready && 'text-muted-foreground')}>
                    Stage {i + 1}
                  </Badge>
                  <span className={cn('text-sm font-medium', !ready && 'text-muted-foreground')}>
                    {stage.label}
                  </span>
                  {!ready && (
                    <Lock className="size-3 text-muted-foreground" />
                  )}
                  {count > 0 && ready && (
                    <Badge variant="secondary" className="text-[10px]">
                      {count} {stage.countLabel}
                    </Badge>
                  )}
                </div>
                <p className={cn('mt-0.5 text-xs', ready ? 'text-muted-foreground' : 'text-muted-foreground/60')}>
                  {stage.description}
                </p>
                <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                  {stage.details.map(d => (
                    <li key={d} className={cn('text-[11px]', ready ? 'text-muted-foreground' : 'text-muted-foreground/50')}>
                      {d}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action */}
              <div className="shrink-0 self-center">
                {ready ? (
                  <Button variant={isNext ? 'default' : 'outline'} size="sm" className="gap-1.5">
                    {isNext ? stage.cta : 'Open'}
                    <ArrowRight className="size-3" />
                  </Button>
                ) : (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="outline" size="sm" className="gap-1.5" disabled>
                        Locked
                        <Lock className="size-3" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>{stage.lockedReason}</TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>
          )

          return (
            <div key={stage.id}>
              {/* Connector */}
              {i > 0 && (
                <div className="flex justify-start pl-[1.55rem]">
                  <div className={cn(
                    'h-5 w-px',
                    readiness[i] ? 'bg-foreground/15' : 'bg-muted-foreground/10'
                  )} />
                </div>
              )}

              {ready ? (
                <Link href={stage.href} className="block">
                  {stageContent}
                </Link>
              ) : (
                stageContent
              )}
            </div>
          )
        })}
      </div>

      {/* Recent Jobs */}
      {recentJobs.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Recent Pipeline Jobs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentJobs.map(job => (
              <div key={job.id} className="flex items-center gap-3 rounded-md border px-3 py-2">
                {(job.status === 'running' || job.status === 'pending') && (
                  <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />
                )}
                {job.status === 'completed' && (
                  <CheckCircle2 className="size-4 shrink-0 text-green-500" />
                )}
                {(job.status === 'failed' || job.status === 'cancelled') && (
                  <div className="size-4 shrink-0 rounded-full bg-destructive/20" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-medium">
                    {job.job_type} <span className="text-muted-foreground">#{job.id.slice(0, 8)}</span>
                  </p>
                  {job.current_stage && (
                    <p className="text-[11px] text-muted-foreground">{job.current_stage}</p>
                  )}
                </div>
                <Badge variant="outline" className={cn('text-[10px]', getJobStatusColor(job.status))}>
                  {job.status}
                </Badge>
                {typeof job.progress === 'number' && job.progress > 0 && job.progress < 1 && (
                  <Progress value={Math.round(job.progress * 100)} className="h-1.5 w-16" />
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Flywheel note */}
      <div className="flex items-center gap-3 rounded-lg border border-dashed px-5 py-3.5">
        <CheckCircle2 className="size-4 shrink-0 text-muted-foreground" />
        <div>
          <p className="text-xs font-medium">Flywheel Loop</p>
          <p className="text-[11px] text-muted-foreground">
            After export, deploy your LoRA adapter to production. Collect feedback and feed it back as new seeds.
          </p>
        </div>
      </div>
    </div>
  )
}
