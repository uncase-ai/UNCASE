'use client'

import { useCallback, useSyncExternalStore } from 'react'

export function useIsMobile(breakpoint = 767) {
  const subscribe = useCallback(
    (onStoreChange: () => void) => {
      const mq = window.matchMedia(`(max-width: ${breakpoint}px)`)

      mq.addEventListener('change', onStoreChange)

      return () => mq.removeEventListener('change', onStoreChange)
    },
    [breakpoint]
  )

  const getSnapshot = useCallback(() => window.matchMedia(`(max-width: ${breakpoint}px)`).matches, [breakpoint])

  const getServerSnapshot = useCallback(() => false, [])

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}
