'use client'

import { useCallback, useRef, useState, useSyncExternalStore } from 'react'

import { createDemoSandbox } from '@/lib/api/sandbox'
import { activateDemo } from '@/lib/demo'
import {
  clearSandboxSession,
  getSandboxSession,
  getSandboxTtlMs,
  isSandboxActive,
  setSandboxSession,
  subscribeSandbox
} from '@/lib/sandbox-session'
import type { SandboxSession } from '@/lib/sandbox-session'

// TTL countdown: subscribe to a 1-second tick so useSyncExternalStore
// re-reads getSandboxTtlMs() every second while the sandbox is active.
function subscribeTtl(cb: () => void): () => void {
  const unsub = subscribeSandbox(cb)
  const id = setInterval(cb, 1000)

  return () => {
    unsub()
    clearInterval(id)
  }
}

// Auto-clear expired sessions on every TTL read
function getTtlSnapshot(): number {
  const ms = getSandboxTtlMs()

  if (ms <= 0 && isSandboxActive()) {
    // Expired — clean up (will trigger subscribeSandbox listeners)
    clearSandboxSession()
  }

  return ms
}

export function useSandboxDemo() {
  const active = useSyncExternalStore(subscribeSandbox, isSandboxActive, () => false)
  const session = useSyncExternalStore(subscribeSandbox, getSandboxSession, () => null)
  const ttlMs = useSyncExternalStore(subscribeTtl, getTtlSnapshot, () => 0)

  const [booting, setBooting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const bootingRef = useRef(false)

  const start = useCallback(async (domain: string): Promise<SandboxSession | null> => {
    if (bootingRef.current) return null

    bootingRef.current = true
    setBooting(true)
    setError(null)

    try {
      const { data, error: apiError } = await createDemoSandbox(
        { domain, ttl_minutes: 30, preload_seeds: 3, language: 'es' },
        AbortSignal.timeout(120_000)
      )

      if (apiError || !data) {
        setError(apiError?.message ?? 'Failed to create demo sandbox')
        setBooting(false)
        bootingRef.current = false

        return null
      }

      // Always populate demo data in localStorage so the dashboard has content
      await activateDemo()

      const sandboxSession: SandboxSession = {
        apiUrl: data.api_url,
        docsUrl: data.docs_url,
        expiresAt: data.expires_at,
        domain: data.domain,
        preloadedSeeds: data.preloaded_seeds,
        jobId: data.job.job_id,
        createdAt: new Date().toISOString()
      }

      // Only set sandbox session (API routing) when E2B is active.
      // In fallback mode the api_url already points to the main API,
      // so we skip session setup to avoid showing a sandbox TTL banner.
      if (!data.fallback) {
        setSandboxSession(sandboxSession)
      }

      setBooting(false)
      bootingRef.current = false

      return sandboxSession
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unexpected error'

      setError(msg)
      setBooting(false)
      bootingRef.current = false

      return null
    }
  }, [])

  const stop = useCallback(() => {
    clearSandboxSession()
    setError(null)
  }, [])

  return { active, session, booting, error, ttlMs, start, stop }
}
