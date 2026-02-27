// ─── Type-safe fetch wrapper for UNCASE API ───
// Supports: retries, abort signals, file uploads, error normalization, API key auth

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
}

export type ApiResponse<T> = { data: T; error: null } | { data: null; error: ApiError }

interface RequestOptions {
  signal?: AbortSignal
  headers?: Record<string, string>
  retries?: number
  retryDelay?: number
}

function normalizeError(status: number, body: unknown): ApiError {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = (body as { detail: string }).detail

    return { status, message: detail, detail }
  }

  return { status, message: `Request failed with status ${status}` }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { signal, headers = {}, retries = 0, retryDelay = 1000 } = options
  const url = `${getApiBase()}${path}`

  // Inject API key if stored
  const apiKey = getStoredApiKey()

  if (apiKey && !headers['X-API-Key']) {
    headers['X-API-Key'] = apiKey
  }

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

const API_BASE = DEFAULT_API_BASE

export { API_BASE, getApiBase }
