'use client'

import { useEffect, useRef, useState } from 'react'

import { Cloud, Loader2 } from 'lucide-react'

import { activateDemo } from '@/lib/demo'
import { setSandboxSession } from '@/lib/sandbox-session'

type BootstrapState = 'loading' | 'ready' | 'error'

export function SandboxBootstrap() {
  const [state, setState] = useState<BootstrapState>('loading')
  const [status, setStatus] = useState('Connecting to sandbox...')
  const didRun = useRef(false)

  useEffect(() => {
    if (didRun.current) return
    didRun.current = true

    // Read params directly from the URL — avoids useSearchParams() which
    // requires Suspense and can cause re-render loops in Next.js 16.
    const sp = new URLSearchParams(window.location.search)
    const apiUrl = sp.get('apiUrl')
    const docsUrl = sp.get('docsUrl') ?? ''
    const domain = sp.get('domain') ?? 'automotive.sales'
    const expiresAt = sp.get('expiresAt') ?? ''
    const preloadedSeeds = Number(sp.get('preloadedSeeds') ?? '0')
    const jobId = sp.get('jobId') ?? ''
    const fallback = sp.get('fallback') === 'true'

    async function bootstrap() {
      try {
        setStatus('Loading dashboard data...')
        await activateDemo()

        if (!fallback && apiUrl) {
          setStatus('Connecting to live sandbox...')
          setSandboxSession({
            apiUrl,
            docsUrl,
            expiresAt,
            domain,
            preloadedSeeds,
            jobId,
            createdAt: new Date().toISOString()
          })

          setStatus('Loading domain seeds...')

          try {
            const res = await fetch(`${apiUrl}/api/v1/seeds`, {
              signal: AbortSignal.timeout(10_000)
            })

            if (res.ok) {
              const data = await res.json()
              const seeds = data.seeds ?? data.items ?? []

              if (seeds.length > 0) {
                localStorage.setItem('uncase-seeds', JSON.stringify(seeds))
                window.dispatchEvent(new StorageEvent('storage', { key: 'uncase-seeds' }))
              }
            }
          } catch {
            // Sandbox seeds unavailable — demo seeds will be used
          }
        }

        setStatus('Launching dashboard...')
        setState('ready')
        window.location.replace('/dashboard')
      } catch {
        setState('error')
        setStatus('Something went wrong. Redirecting...')
        setTimeout(() => { window.location.replace('/dashboard') }, 1500)
      }
    }

    bootstrap()
  }, [])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <div className="flex size-16 items-center justify-center rounded-full bg-primary/10">
        {state === 'loading' ? (
          <Loader2 className="size-8 animate-spin text-primary" />
        ) : (
          <Cloud className="size-8 text-primary" />
        )}
      </div>
      <p className="text-sm font-medium text-muted-foreground">{status}</p>
    </div>
  )
}
