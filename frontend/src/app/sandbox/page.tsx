import { Suspense } from 'react'
import type { Metadata } from 'next'

import { Loader2 } from 'lucide-react'

import { SandboxBootstrap } from './sandbox-bootstrap'

export const metadata: Metadata = {
  title: 'Connecting to Sandbox...'
}

function SandboxFallback() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <div className="flex size-16 items-center justify-center rounded-full bg-primary/10">
        <Loader2 className="size-8 animate-spin text-primary" />
      </div>
      <p className="text-sm font-medium text-muted-foreground">Loading...</p>
    </div>
  )
}

export default function SandboxPage() {
  return (
    <Suspense fallback={<SandboxFallback />}>
      <SandboxBootstrap />
    </Suspense>
  )
}
