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

export function getSandboxSession(): SandboxSession | null {
  if (typeof window === 'undefined') return null

  try {
    const raw = sessionStorage.getItem(SESSION_KEY)

    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setSandboxSession(session: SandboxSession): void {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session))
  setSandboxApiBase(session.apiUrl)
  dispatchChange()
}

export function clearSandboxSession(): void {
  sessionStorage.removeItem(SESSION_KEY)
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
