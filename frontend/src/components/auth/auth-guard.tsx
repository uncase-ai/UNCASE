'use client'

import type { ReactNode } from 'react'

import { useCallback, useEffect, useState } from 'react'

import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

import { useAuth } from '@/contexts/auth-context'
import { getSetupStatus } from '@/lib/api/auth'

export function AuthGuard({ children }: { children: ReactNode }) {
  const { user, isLoading, isDemo } = useAuth()
  const router = useRouter()
  const [authRequired, setAuthRequired] = useState<boolean | null>(null)

  const checkAuthRequired = useCallback(async () => {
    // If already authenticated or demo, no need to check setup
    if (user || isDemo) {
      setAuthRequired(false)

      return
    }

    const { data } = await getSetupStatus()

    if (data?.setup_complete) {
      // Users exist — auth is required
      setAuthRequired(true)
    } else {
      // No users — open mode (single-user)
      setAuthRequired(false)
    }
  }, [user, isDemo])

  useEffect(() => {
    if (!isLoading) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      checkAuthRequired()
    }
  }, [isLoading, checkAuthRequired])

  useEffect(() => {
    if (!isLoading && authRequired === true && !user && !isDemo) {
      router.replace('/login')
    }
  }, [isLoading, authRequired, user, isDemo, router])

  if (isLoading || authRequired === null) {
    return (
      <div className="flex h-dvh items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  // Auth required but not authenticated
  if (authRequired && !user && !isDemo) {
    return null
  }

  return <>{children}</>
}
