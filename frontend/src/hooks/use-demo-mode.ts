'use client'

import { useCallback, useSyncExternalStore } from 'react'

import { activateDemo, deactivateDemo, isDemoMode, resetDemoData } from '@/lib/demo'

const noop = () => {}
const DEMO_MODE_KEY = 'uncase-demo-mode'

function subscribeStorage(cb: () => void) {
  if (typeof window === 'undefined') return noop

  // Only react to the demo-mode key — not every localStorage write.
  // Without this filter, every demo-data key dispatch (seeds, conversations,
  // evaluations, etc.) triggers an unnecessary snapshot check.
  const handler = (e: StorageEvent) => {
    if (e.key === null || e.key === DEMO_MODE_KEY) cb()
  }

  window.addEventListener('storage', handler)

  return () => window.removeEventListener('storage', handler)
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
