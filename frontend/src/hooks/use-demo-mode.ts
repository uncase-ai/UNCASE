'use client'

import { useCallback, useSyncExternalStore } from 'react'

import { activateDemo, deactivateDemo, isDemoMode, resetDemoData } from '@/lib/demo'

export function useDemoMode() {
  const active = useSyncExternalStore(
    (cb) => {
      window.addEventListener('storage', cb)

      return () => window.removeEventListener('storage', cb)
    },
    () => isDemoMode(),
    () => false
  )

  const enter = useCallback(async () => {
    await activateDemo()
  }, [])

  const exit = useCallback(() => {
    deactivateDemo()
  }, [])

  const reset = useCallback(async () => {
    await resetDemoData()
  }, [])

  return { active, enter, exit, reset }
}
