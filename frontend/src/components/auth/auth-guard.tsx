'use client'

import type { ReactNode } from 'react'

import { useEffect } from 'react'

import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

import { useAuth } from '@/contexts/auth-context'

export function AuthGuard({ children }: { children: ReactNode }) {
  const { user, isLoading, isDemo } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user && !isDemo) {
      router.replace('/login')
    }
  }, [isLoading, user, isDemo, router])

  if (isLoading) {
    return (
      <div className="flex h-dvh items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!user && !isDemo) {
    return null
  }

  return <>{children}</>
}
