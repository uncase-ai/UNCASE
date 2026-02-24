'use client'

import { useCallback, useSyncExternalStore } from 'react'

import { activateDemo, deactivateDemo, isDemoMode, resetDemoData } from '@/lib/demo'

const noop = () => {}

function subscribeStorage(cb: () => void) {
  if (typeof window === 'undefined') return noop

  window.addEventListener('storage', cb)

  return () => window.removeEventListener('storage', cb)
}

export function useDemoMode() {
  const active = useSyncExternalStore(subscribeStorage, isDemoMode, () => false)

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
