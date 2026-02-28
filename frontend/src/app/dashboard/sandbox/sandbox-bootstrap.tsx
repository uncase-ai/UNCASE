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

  useEffect(() => {
    if (didRun.current) return
    didRun.current = true

    const apiUrl = params.get('apiUrl')
    const docsUrl = params.get('docsUrl') ?? ''
    const domain = params.get('domain') ?? 'automotive.sales'
    const expiresAt = params.get('expiresAt') ?? ''
    const preloadedSeeds = Number(params.get('preloadedSeeds') ?? '0')
    const jobId = params.get('jobId') ?? ''
    const fallback = params.get('fallback') === 'true'

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
  }, [params, router])

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
