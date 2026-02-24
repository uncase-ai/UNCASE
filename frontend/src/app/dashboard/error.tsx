'use client'

import { useEffect } from 'react'

import { AlertTriangle, RefreshCw } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export default function DashboardError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error('[UNCASE Dashboard Error]', error)
  }, [error])

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardContent className="flex flex-col items-center gap-4 pt-6 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-destructive/10">
            <AlertTriangle className="size-6 text-destructive" />
          </div>
          <div className="space-y-1">
            <h2 className="text-lg font-semibold">Something went wrong</h2>
            <p className="text-sm text-muted-foreground">
              The dashboard encountered an unexpected error. This is usually temporary.
            </p>
          </div>
          {error.message && (
            <code className="max-w-full truncate rounded bg-muted px-3 py-1.5 text-xs">{error.message}</code>
          )}
          <div className="flex gap-2">
            <Button onClick={reset} variant="outline" size="sm" className="gap-1.5">
              <RefreshCw className="size-3.5" />
              Try Again
            </Button>
            <Button onClick={() => (window.location.href = '/dashboard')} size="sm">
              Back to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
