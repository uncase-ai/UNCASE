'use client'

import { useEffect, useRef, useState } from 'react'

import { useRouter, useSearchParams } from 'next/navigation'
import { Cloud, Loader2 } from 'lucide-react'

import { activateDemo } from '@/lib/demo'
import { setSandboxSession } from '@/lib/sandbox-session'

type BootstrapState = 'loading' | 'ready' | 'error'

export function SandboxBootstrap() {
  const router = useRouter()
  const params = useSearchParams()
  const [state, setState] = useState<BootstrapState>('loading')
  const [status, setStatus] = useState('Connecting to sandbox...')
  const didRun = useRef(false)

  // Capture params in a ref so the effect has no reactive dependencies
  // that could cause re-render loops after Suspense resolution.
  const paramsRef = useRef(params)
  paramsRef.current = params

  useEffect(() => {
    if (didRun.current) return
    didRun.current = true

    const sp = paramsRef.current
    const apiUrl = sp.get('apiUrl')
    const docsUrl = sp.get('docsUrl') ?? ''
    const domain = sp.get('domain') ?? 'automotive.sales'
    const expiresAt = sp.get('expiresAt') ?? ''
    const preloadedSeeds = Number(sp.get('preloadedSeeds') ?? '0')
    const jobId = sp.get('jobId') ?? ''
    const fallback = sp.get('fallback') === 'true'

    async function bootstrap() {
      try {
        // Step 1: Populate all localStorage keys with demo data
        setStatus('Loading dashboard data...')
        await activateDemo()

        if (!fallback && apiUrl) {
          // Step 2: Set up sandbox session → routes API calls to E2B sandbox
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

          // Step 3: Fetch seeds from sandbox and overwrite demo seeds
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

        // Step 4: Redirect to dashboard
        setStatus('Launching dashboard...')
        setState('ready')
        router.replace('/dashboard')
      } catch {
        setState('error')
        setStatus('Something went wrong. Redirecting...')

        // Fallback: just go to dashboard with demo data
        setTimeout(() => router.replace('/dashboard'), 1500)
      }
    }

    bootstrap()
  // eslint-disable-next-line react-hooks/exhaustive-deps
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
