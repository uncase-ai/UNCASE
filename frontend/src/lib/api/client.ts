// ─── Type-safe fetch wrapper for UNCASE API ───
// Supports: retries, abort signals, file uploads, error normalization, API key auth, auto token refresh

const DEFAULT_API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const API_KEY_STORAGE_KEY = 'uncase-api-key'
const SANDBOX_BASE_KEY = 'uncase-sandbox-api-url'

function getApiBase(): string {
  if (typeof window === 'undefined') return DEFAULT_API_BASE

  return sessionStorage.getItem(SANDBOX_BASE_KEY) ?? DEFAULT_API_BASE
}

export function setSandboxApiBase(url: string): void {
  sessionStorage.setItem(SANDBOX_BASE_KEY, url)
}

export function clearSandboxApiBase(): void {
  sessionStorage.removeItem(SANDBOX_BASE_KEY)
}

export function getSandboxApiBase(): string | null {
  if (typeof window === 'undefined') return null

  return sessionStorage.getItem(SANDBOX_BASE_KEY)
}

function getStoredApiKey(): string | null {
  if (typeof window === 'undefined') return null

  return localStorage.getItem(API_KEY_STORAGE_KEY)
}

export function setStoredApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE_KEY, key)
}

export function clearStoredApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE_KEY)
}

export interface ApiError {
  status: number
  message: string
  detail?: string
  errors?: Array<{ field: string; message: string; type: string }>
}

export type ApiResponse<T> = { data: T; error: null } | { data: null; error: ApiError }

interface RequestOptions {
  signal?: AbortSignal
  headers?: Record<string, string>
  retries?: number
  retryDelay?: number
}

function normalizeError(status: number, body: unknown): ApiError {
  if (typeof body === 'object' && body !== null) {
    const obj = body as Record<string, unknown>
    const detail = typeof obj.detail === 'string' ? obj.detail : `Request failed with status ${status}`

    const errors = Array.isArray(obj.errors)
      ? (obj.errors as Array<{ field: string; message: string; type: string }>)
      : undefined

    return { status, message: detail, detail, errors }
  }

  return { status, message: `Request failed with status ${status}` }
}

function isSandboxActive(): boolean {
  if (typeof window === 'undefined') return false

  return sessionStorage.getItem(SANDBOX_BASE_KEY) !== null
}

// Safe empty response for sandbox fallback — prevents pages from breaking
// when the demo API doesn't implement a specific endpoint
function sandboxFallback<T>(): ApiResponse<T> {
  const empty = { items: [], total: 0 } as unknown as T

  return { data: empty, error: null }
}

// ─── Auto token refresh on 401 ───

let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

async function attemptTokenRefresh(): Promise<boolean> {
  if (isRefreshing && refreshPromise) return refreshPromise

  isRefreshing = true
  refreshPromise = (async () => {
    try {
      const refreshToken = localStorage.getItem('uncase-refresh-token')

      if (!refreshToken) return false

      const res = await fetch(`${getApiBase()}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!res.ok) return false

      const data = await res.json()

      localStorage.setItem('uncase-access-token', data.access_token)
      localStorage.setItem('uncase-refresh-token', data.refresh_token)

      return true
    } catch {
      return false
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { signal, headers = {}, retries = 0, retryDelay = 1000 } = options
  const url = `${getApiBase()}${path}`
  const sandbox = isSandboxActive()

  // Inject API key if stored
  const apiKey = getStoredApiKey()

  if (apiKey && !headers['X-API-Key']) {
    headers['X-API-Key'] = apiKey
  }

  // Inject Bearer token if stored (user auth takes priority over API key)
  if (typeof window !== 'undefined') {
    const accessToken = localStorage.getItem('uncase-access-token')

    if (accessToken && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }
  }

  let refreshAttempted = false

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        method,
        signal,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        ...(body !== undefined ? { body: JSON.stringify(body) } : {})
      })

      if (res.status === 204) {
        return { data: null as unknown as T, error: null }
      }

      const contentType = res.headers.get('content-type') ?? ''

      if (!res.ok) {
        // In sandbox mode, return safe empty data for 404/405 instead of error
        if (sandbox && (res.status === 404 || res.status === 405)) {
          return sandboxFallback<T>()
        }

        // Auto-refresh on 401 (expired token) — retry once
        if (res.status === 401 && !refreshAttempted && !path.includes('/auth/') && typeof window !== 'undefined') {
          refreshAttempted = true
          const refreshed = await attemptTokenRefresh()

          if (refreshed) {
            // Retry the original request with new token
            const newToken = localStorage.getItem('uncase-access-token')

            if (newToken) headers['Authorization'] = `Bearer ${newToken}`
            continue
          }

          // Refresh failed — clear tokens and redirect to login
          localStorage.removeItem('uncase-access-token')
          localStorage.removeItem('uncase-refresh-token')
          window.location.href = '/login'

          return { data: null, error: { status: 401, message: 'Session expired' } }
        }

        const errorBody = contentType.includes('json') ? await res.json() : await res.text()
        const error = normalizeError(res.status, errorBody)

        if (attempt < retries && res.status >= 500) {
          await new Promise(r => setTimeout(r, retryDelay * (attempt + 1)))
          continue
        }

        return { data: null, error }
      }

      if (contentType.includes('json')) {
        const data = await res.json()

        return { data: data as T, error: null }
      }

      // For text/plain responses (e.g., template export)
      const text = await res.text()

      return { data: text as unknown as T, error: null }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return { data: null, error: { status: 0, message: 'Request cancelled' } }
      }

      // In sandbox mode, return safe empty data on network errors
      if (sandbox) {
        return sandboxFallback<T>()
      }

      if (attempt < retries) {
        await new Promise(r => setTimeout(r, retryDelay * (attempt + 1)))
        continue
      }

      const message = err instanceof Error ? err.message : 'Network error'

      return { data: null, error: { status: 0, message } }
    }
  }

  return { data: null, error: { status: 0, message: 'Max retries exceeded' } }
}

export function apiGet<T>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
  return request<T>('GET', path, undefined, options)
}

export function apiPost<T>(path: string, body?: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
  return request<T>('POST', path, body, options)
}

export function apiPut<T>(path: string, body?: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
  return request<T>('PUT', path, body, options)
}

export function apiDelete<T = void>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
  return request<T>('DELETE', path, undefined, options)
}

export function apiPatch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
  return request<T>('PATCH', path, body, options)
}

export async function apiUpload<T>(
  path: string,
  file: File,
  params?: Record<string, string>,
  options?: RequestOptions
): Promise<ApiResponse<T>> {
  const url = new URL(`${getApiBase()}${path}`)

  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }

  const formData = new FormData()

  formData.append('file', file)

  // Inject API key for uploads
  const uploadHeaders: Record<string, string> = { ...(options?.headers ?? {}) }
  const storedKey = getStoredApiKey()

  if (storedKey && !uploadHeaders['X-API-Key']) {
    uploadHeaders['X-API-Key'] = storedKey
  }

  try {
    const res = await fetch(url.toString(), {
      method: 'POST',
      body: formData,
      signal: options?.signal,
      headers: uploadHeaders
    })

    if (!res.ok) {
      const contentType = res.headers.get('content-type') ?? ''
      const errorBody = contentType.includes('json') ? await res.json() : await res.text()

      return { data: null, error: normalizeError(res.status, errorBody) }
    }

    const data = await res.json()

    return { data: data as T, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Upload cancelled' } }
    }

    const message = err instanceof Error ? err.message : 'Upload failed'

    return { data: null, error: { status: 0, message } }
  }
}

// ─── Connectivity check ───
export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${getApiBase()}/health`, { signal: AbortSignal.timeout(3000) })

    return res.ok
  } catch {
    return false
  }
}

export async function checkApiHealthDetailed(): Promise<{ ok: boolean; llmConfigured: boolean }> {
  try {
    const res = await fetch(`${getApiBase()}/health`, { signal: AbortSignal.timeout(3000) })

    if (!res.ok) return { ok: false, llmConfigured: false }

    const data = await res.json()

    return { ok: true, llmConfigured: data.llm_configured ?? false }
  } catch {
    return { ok: false, llmConfigured: false }
  }
}

const API_BASE = DEFAULT_API_BASE

export { API_BASE, getApiBase }
