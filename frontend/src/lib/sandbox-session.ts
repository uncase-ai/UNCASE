import { clearSandboxApiBase, setSandboxApiBase } from '@/lib/api/client'

// ─── Types ───

export interface SandboxSession {
  apiUrl: string
  docsUrl: string
  expiresAt: string
  domain: string
  preloadedSeeds: number
  jobId: string
  createdAt: string
}

// ─── Storage Keys ───

const SESSION_KEY = 'uncase-sandbox-session'

// ─── Custom event for same-tab reactivity ───
// (sessionStorage doesn't fire 'storage' events within the same tab)

const SANDBOX_CHANGE_EVENT = 'uncase-sandbox-change'

function dispatchChange() {
  if (typeof window === 'undefined') return

  window.dispatchEvent(new CustomEvent(SANDBOX_CHANGE_EVENT))
}

export function subscribeSandbox(cb: () => void): () => void {
  if (typeof window === 'undefined') return () => {}

  window.addEventListener(SANDBOX_CHANGE_EVENT, cb)

  return () => window.removeEventListener(SANDBOX_CHANGE_EVENT, cb)
}

// ─── Session Management ───

// Cache parsed session so useSyncExternalStore always receives the same
// object reference when the underlying data hasn't changed.  Without this,
// JSON.parse creates a new object on every read, which Object.is treats as
// "changed", causing infinite re-render loops.
let _cachedRaw: string | null = null
let _cachedSession: SandboxSession | null = null

export function getSandboxSession(): SandboxSession | null {
  if (typeof window === 'undefined') return null

  try {
    const raw = sessionStorage.getItem(SESSION_KEY)

    if (raw === _cachedRaw) return _cachedSession

    _cachedRaw = raw
    _cachedSession = raw ? JSON.parse(raw) : null

    return _cachedSession
  } catch {
    return null
  }
}

export function setSandboxSession(session: SandboxSession): void {
  const raw = JSON.stringify(session)

  sessionStorage.setItem(SESSION_KEY, raw)
  _cachedRaw = raw
  _cachedSession = session
  setSandboxApiBase(session.apiUrl)
  dispatchChange()
}

export function clearSandboxSession(): void {
  sessionStorage.removeItem(SESSION_KEY)
  _cachedRaw = null
  _cachedSession = null
  clearSandboxApiBase()
  dispatchChange()
}

export function isSandboxActive(): boolean {
  const session = getSandboxSession()

  if (!session) return false

  return new Date(session.expiresAt).getTime() > Date.now()
}

export function getSandboxTtlMs(): number {
  const session = getSandboxSession()

  if (!session) return 0

  return Math.max(0, new Date(session.expiresAt).getTime() - Date.now())
}
