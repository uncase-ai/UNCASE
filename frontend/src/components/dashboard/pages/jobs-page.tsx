'use client'

import { useCallback, useState } from 'react'

import {
  AlertCircle,
  Ban,
  CheckCircle2,
  Clock,
  Loader2,
  Play,
  RefreshCw
} from 'lucide-react'

import type { JobResponse } from '@/types/api'
import { cn } from '@/lib/utils'
import { useApi } from '@/hooks/use-api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { cancelJob, fetchJobs, getJobStatusBadge } from '@/lib/api/jobs'

type StatusFilter = 'all' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

const STATUS_ICONS: Record<string, typeof Clock> = {
  pending: Clock,
  running: Play,
  completed: CheckCircle2,
  failed: AlertCircle,
  cancelled: Ban
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)

  if (hours < 24) return `${hours}h ago`

  const days = Math.floor(hours / 24)

  return `${days}d ago`
}

export function JobsPage() {
  const [filter, setFilter] = useState<StatusFilter>('all')
  const [refreshKey, setRefreshKey] = useState(0)

  const fetcher = useCallback(
    (signal: AbortSignal) => {
      void refreshKey // trigger refetch on refresh
      const params: Record<string, string> = { page_size: '50' }

      if (filter !== 'all') params.status = filter

      return fetchJobs(params, signal)
    },
    [filter, refreshKey]
  )

  const { data: jobs, loading, error } = useApi<JobResponse[]>(fetcher)

  const handleRefresh = () => setRefreshKey(k => k + 1)

  const handleCancel = async (jobId: string) => {
    const res = await cancelJob(jobId)

    if (!res.error) {
      handleRefresh()
    }
  }

  const statusCounts = jobs
    ? {
        pending: jobs.filter(j => j.status === 'pending').length,
        running: jobs.filter(j => j.status === 'running').length,
        completed: jobs.filter(j => j.status === 'completed').length,
        failed: jobs.filter(j => j.status === 'failed').length
      }
    : { pending: 0, running: 0, completed: 0, failed: 0 }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Job Queue"
        description="Monitor background jobs: pipeline runs, generation, evaluation, and training tasks."
        actions={
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className={cn('mr-2 size-4', loading && 'animate-spin')} />
            Refresh
          </Button>
        }
      />

      {/* Status summary cards */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {(Object.entries(statusCounts) as [string, number][]).map(([status, count]) => {
          const Icon = STATUS_ICONS[status] ?? Clock

          return (
            <Card
              key={status}
              className={cn('cursor-pointer transition-colors hover:bg-accent/50', filter === status && 'ring-2 ring-primary')}
              onClick={() => setFilter(filter === status ? 'all' : (status as StatusFilter))}
            >
              <CardContent className="flex items-center gap-3 p-4">
                <Icon className="size-5 text-muted-foreground" />
                <div>
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-xs capitalize text-muted-foreground">{status}</p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-2">
        {(['all', 'pending', 'running', 'completed', 'failed', 'cancelled'] as const).map(s => (
          <Button key={s} variant={filter === s ? 'default' : 'ghost'} size="sm" onClick={() => setFilter(s)}>
            {s === 'all' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}
          </Button>
        ))}
      </div>

      {/* Job list */}
      {loading && !jobs ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            <AlertCircle className="mx-auto mb-2 size-8" />
            <p>Failed to load jobs: {error.message}</p>
          </CardContent>
        </Card>
      ) : !jobs?.length ? (
        <EmptyState
          icon={Clock}
          title="No jobs yet"
          description="Submit a pipeline run or batch operation to see jobs here."
        />
      ) : (
        <div className="space-y-3">
          {jobs.map(job => (
            <Card key={job.id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-sm font-mono">{job.id.slice(0, 12)}</CardTitle>
                  <Badge variant={getJobStatusBadge(job.status)}>{job.status}</Badge>
                  <Badge variant="outline">{job.job_type}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{timeAgo(job.created_at)}</span>
                  {!['completed', 'failed', 'cancelled'].includes(job.status) && (
                    <Button variant="ghost" size="sm" onClick={() => handleCancel(job.id)}>
                      <Ban className="mr-1 size-3" />
                      Cancel
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {job.status === 'running' && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{job.current_stage ?? 'Processing...'}</span>
                        <span>{Math.round(job.progress * 100)}%</span>
                      </div>
                      <Progress value={job.progress * 100} />
                    </div>
                  )}
                  {job.status_message && (
                    <p className="text-xs text-muted-foreground">{job.status_message}</p>
                  )}
                  {job.error_message && (
                    <p className="text-xs text-destructive">{job.error_message}</p>
                  )}
                  {job.result && (
                    <div className="flex gap-4 text-xs text-muted-foreground">
                      {job.result.conversations_generated !== undefined && (
                        <span>Generated: {String(job.result.conversations_generated)}</span>
                      )}
                      {job.result.conversations_passed !== undefined && (
                        <span>Passed: {String(job.result.conversations_passed)}</span>
                      )}
                      {job.result.pass_rate !== undefined && (
                        <span>Pass rate: {(Number(job.result.pass_rate) * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
