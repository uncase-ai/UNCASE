'use client'

import { useEffect } from 'react'

import { useRouter } from 'next/navigation'
import { FlaskConical, RotateCcw, X } from 'lucide-react'

import { DEMO_RUNNING_JOB_ID } from '@/lib/demo'
import { useDemoMode } from '@/hooks/use-demo-mode'
import { useJobQueue } from '@/hooks/use-dashboard'
import { Button } from '@/components/ui/button'

export function DemoBanner() {
  const { active, exit, reset } = useDemoMode()
  const { updateJob } = useJobQueue()
  const router = useRouter()

  // Live simulation: increment running job progress
  useEffect(() => {
    if (!active) return

    const interval = setInterval(() => {
      try {
        const stored = localStorage.getItem('uncase-pipeline-jobs')

        if (!stored) return

        const jobs = JSON.parse(stored) as { id: string; status: string; progress: number }[]
        const runningJob = jobs.find((j) => j.id === DEMO_RUNNING_JOB_ID)

        if (!runningJob || runningJob.status !== 'running' || runningJob.progress >= 99) return

        const increment = Math.random() < 0.5 ? 1 : 2
        const next = Math.min(runningJob.progress + increment, 99)

        updateJob(DEMO_RUNNING_JOB_ID, { progress: next })
      } catch {
        // ignore parse errors
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [active, updateJob])

  if (!active) return null

  const handleExit = () => {
    exit()
    router.push('/')
  }

  return (
    <div className="flex items-center justify-between gap-4 border-b bg-muted/50 px-4 py-2">
      <div className="flex items-center gap-2 text-sm">
        <FlaskConical className="size-4 shrink-0 text-muted-foreground" />
        <span className="font-medium">Demo Mode</span>
        <span className="hidden text-muted-foreground sm:inline">
          — Exploring with sample automotive sales data
        </span>
      </div>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" onClick={() => reset()} className="h-7 gap-1.5 text-xs">
          <RotateCcw className="size-3.5" />
          <span className="hidden sm:inline">Reset Data</span>
        </Button>
        <Button variant="ghost" size="sm" onClick={handleExit} className="h-7 gap-1.5 text-xs">
          <X className="size-3.5" />
          <span className="hidden sm:inline">Exit Demo</span>
        </Button>
      </div>
    </div>
  )
}
