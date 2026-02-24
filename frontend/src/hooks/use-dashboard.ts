'use client'

import { useCallback, useSyncExternalStore } from 'react'

import type { PipelineJob } from '@/types/dashboard'

const SIDEBAR_KEY = 'uncase-sidebar-collapsed'
const JOBS_KEY = 'uncase-pipeline-jobs'

const EMPTY_JOBS: PipelineJob[] = []
const noop = () => {}

function readSidebarState(): boolean {
  if (typeof window === 'undefined') return false

  return localStorage.getItem(SIDEBAR_KEY) === 'true'
}

function subscribeStorage(cb: () => void) {
  if (typeof window === 'undefined') return noop

  window.addEventListener('storage', cb)

  return () => window.removeEventListener('storage', cb)
}

export function useSidebar() {
  const collapsed = useSyncExternalStore(subscribeStorage, readSidebarState, () => false)

  const toggle = useCallback(() => {
    if (typeof window === 'undefined') return

    const next = !readSidebarState()

    localStorage.setItem(SIDEBAR_KEY, String(next))
    window.dispatchEvent(new StorageEvent('storage', { key: SIDEBAR_KEY }))
  }, [])

  const setCollapsed = useCallback((value: boolean) => {
    if (typeof window === 'undefined') return

    localStorage.setItem(SIDEBAR_KEY, String(value))
    window.dispatchEvent(new StorageEvent('storage', { key: SIDEBAR_KEY }))
  }, [])

  return { collapsed, toggle, setCollapsed }
}

// Cache the last raw JSON string and parsed result so useSyncExternalStore
// gets a stable reference when the underlying data hasn't changed.
let _cachedJobsRaw: string | null = null
let _cachedJobs: PipelineJob[] = EMPTY_JOBS

function readJobs(): PipelineJob[] {
  if (typeof window === 'undefined') return EMPTY_JOBS

  try {
    const raw = localStorage.getItem(JOBS_KEY)

    if (raw === _cachedJobsRaw) return _cachedJobs

    _cachedJobsRaw = raw
    _cachedJobs = raw ? JSON.parse(raw) : EMPTY_JOBS

    return _cachedJobs
  } catch {
    return EMPTY_JOBS
  }
}

function dispatchJobsUpdate() {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new StorageEvent('storage', { key: JOBS_KEY }))
  }
}

export function useJobQueue() {
  const jobs = useSyncExternalStore(subscribeStorage, readJobs, () => EMPTY_JOBS)

  const persist = useCallback((nextJobs: PipelineJob[]) => {
    localStorage.setItem(JOBS_KEY, JSON.stringify(nextJobs))
    dispatchJobsUpdate()
  }, [])

  const addJob = useCallback(
    (job: Omit<PipelineJob, 'id' | 'created_at' | 'status' | 'progress'>) => {
      const current = readJobs()

      const newJob: PipelineJob = {
        ...job,
        id: crypto.randomUUID(),
        status: 'queued',
        progress: 0,
        created_at: new Date().toISOString()
      }

      persist([newJob, ...current])

      return newJob.id
    },
    [persist]
  )

  const updateJob = useCallback(
    (id: string, updates: Partial<PipelineJob>) => {
      const current = readJobs()

      persist(current.map(j => (j.id === id ? { ...j, ...updates } : j)))
    },
    [persist]
  )

  const removeJob = useCallback(
    (id: string) => {
      const current = readJobs()

      persist(current.filter(j => j.id !== id))
    },
    [persist]
  )

  const clearCompleted = useCallback(() => {
    const current = readJobs()

    persist(current.filter(j => j.status === 'queued' || j.status === 'running'))
  }, [persist])

  const activeJobs = jobs.filter(j => j.status === 'running' || j.status === 'queued')
  const completedJobs = jobs.filter(j => j.status === 'completed' || j.status === 'failed')

  return { jobs, activeJobs, completedJobs, addJob, updateJob, removeJob, clearCompleted }
}
