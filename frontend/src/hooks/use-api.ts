'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import type { ApiError, ApiResponse } from '@/lib/api/client'

interface UseApiState<T> {
  data: T | null
  error: ApiError | null
  loading: boolean
}

interface UseApiOptions {
  immediate?: boolean
  retryOnError?: boolean
}

export function useApi<T>(
  fetcher: (signal: AbortSignal) => Promise<ApiResponse<T>>,
  options: UseApiOptions = {}
) {
  const { immediate = true, retryOnError = false } = options
  const [state, setState] = useState<UseApiState<T>>({ data: null, error: null, loading: immediate })
  const abortRef = useRef<AbortController | null>(null)
  const mountedRef = useRef(true)

  const execute = useCallback(async () => {
    // Cancel any in-flight request
    abortRef.current?.abort()
    const controller = new AbortController()

    abortRef.current = controller

    setState(prev => ({ ...prev, loading: true, error: null }))

    const result = await fetcher(controller.signal)

    if (!mountedRef.current) return result

    if (result.error) {
      setState({ data: null, error: result.error, loading: false })
    } else {
      setState({ data: result.data, error: null, loading: false })
    }

    return result
  }, [fetcher])

  const retry = useCallback(() => {
    return execute()
  }, [execute])

  useEffect(() => {
    mountedRef.current = true

    if (immediate) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      execute()
    }

    return () => {
      mountedRef.current = false
      abortRef.current?.abort()
    }
  }, [execute, immediate])

  // Auto-retry on error with exponential backoff
  useEffect(() => {
    if (!retryOnError || !state.error || state.error.status === 0) return

    const timer = setTimeout(() => {
      if (mountedRef.current) execute()
    }, 5000)

    return () => clearTimeout(timer)
  }, [retryOnError, state.error, execute])

  return { ...state, execute, retry, mutate: (data: T) => setState(prev => ({ ...prev, data })) }
}

// Polling hook for job status, health checks, etc.
export function usePolling<T>(
  fetcher: (signal: AbortSignal) => Promise<ApiResponse<T>>,
  intervalMs: number,
  enabled = true
) {
  const api = useApi(fetcher, { immediate: enabled })

  useEffect(() => {
    if (!enabled) return

    const id = setInterval(() => {
      api.execute()
    }, intervalMs)

    return () => clearInterval(id)
  }, [enabled, intervalMs]) // eslint-disable-line react-hooks/exhaustive-deps

  return api
}
