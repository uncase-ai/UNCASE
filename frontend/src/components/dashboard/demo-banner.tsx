'use client'

import { useEffect, useRef } from 'react'

import { useRouter } from 'next/navigation'
import { Cloud, FlaskConical, RotateCcw, Timer, X } from 'lucide-react'

import { activateDemo, DEMO_RUNNING_JOB_ID } from '@/lib/demo'
import { useDemoMode } from '@/hooks/use-demo-mode'
import { useSandboxDemo } from '@/hooks/use-sandbox-demo'
import { getSandboxSession } from '@/lib/sandbox-session'
import { useJobQueue } from '@/hooks/use-dashboard'
import { Button } from '@/components/ui/button'

function formatTtl(ms: number): string {
  const minutes = Math.floor(ms / 60_000)
  const seconds = Math.floor((ms % 60_000) / 1000)

  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

export function DemoBanner() {
  const { active: localActive, exit: localExit, reset } = useDemoMode()
  const { active: sandboxActive, session, ttlMs, stop: sandboxStop } = useSandboxDemo()
  const { updateJob } = useJobQueue()
  const router = useRouter()

  // When sandbox expires, transition to demo mode instead of dead state
  const prevSandboxActive = useRef(sandboxActive)

  useEffect(() => {
    if (prevSandboxActive.current && !sandboxActive && !localActive && getSandboxSession() === null) {
      activateDemo()
    }

    prevSandboxActive.current = sandboxActive
  }, [sandboxActive, localActive])

  // Live simulation: increment running job progress (local demo only)
  useEffect(() => {
    if (!localActive) return

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
  }, [localActive, updateJob])

  // Sandbox mode banner (takes priority)
  if (sandboxActive && session) {
    const handleExit = () => {
      sandboxStop()
      activateDemo()
    }

    return (
      <div className="flex items-center justify-center gap-2 border-b bg-emerald-50/50 px-3 py-2 dark:bg-emerald-950/20 sm:justify-between sm:gap-4 sm:px-4">
        <div className="flex items-center gap-2 text-sm">
          <Cloud className="size-4 shrink-0 text-emerald-600" />
          <span className="font-medium">Live Sandbox</span>
          <span className="hidden items-center gap-1 text-muted-foreground sm:inline-flex">
            — {session.domain}
          </span>
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            <Timer className="size-3" />
            {formatTtl(ttlMs)}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={handleExit} className="h-7 gap-1.5 text-xs">
            <X className="size-3.5" />
            <span className="hidden sm:inline">Exit</span>
          </Button>
        </div>
      </div>
    )
  }

  // Local demo mode banner
  if (localActive) {
    const handleExit = () => {
      localExit()
      router.push('/')
    }

    return (
      <div className="flex items-center justify-center gap-2 border-b bg-muted/50 px-3 py-2 sm:justify-between sm:gap-4 sm:px-4">
        <div className="flex items-center gap-2 text-sm">
          <FlaskConical className="size-4 shrink-0 text-muted-foreground" />
          <span className="font-medium">Demo Mode</span>
          <span className="hidden text-muted-foreground sm:inline">
            — Exploring with sample data
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={() => reset()} className="hidden h-7 gap-1.5 text-xs sm:inline-flex">
            <RotateCcw className="size-3.5" />
            Reset Data
          </Button>
          <Button variant="ghost" size="sm" onClick={handleExit} className="h-7 gap-1.5 text-xs">
            <X className="size-3.5" />
            <span className="hidden sm:inline">Exit Demo</span>
          </Button>
        </div>
      </div>
    )
  }

  return null
}
