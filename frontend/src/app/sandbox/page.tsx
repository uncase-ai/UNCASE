import dynamic from 'next/dynamic'
import type { Metadata } from 'next'

import { Loader2 } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Connecting to Sandbox...'
}

const SandboxBootstrap = dynamic(() => import('./sandbox-bootstrap').then(m => m.SandboxBootstrap), {
  ssr: false,
  loading: () => (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <div className="flex size-16 items-center justify-center rounded-full bg-primary/10">
        <Loader2 className="size-8 animate-spin text-primary" />
      </div>
      <p className="text-sm font-medium text-muted-foreground">Loading...</p>
    </div>
  )
})

export default function SandboxPage() {
  return <SandboxBootstrap />
}
