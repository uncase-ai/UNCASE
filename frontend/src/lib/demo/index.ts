import { DEMO_SEEDS } from './seeds'
import { DEMO_CONVERSATIONS } from './conversations'
import { DEMO_EVALUATIONS } from './evaluations'
import { DEMO_PIPELINE_JOBS, DEMO_RUNNING_JOB_ID } from './pipeline-jobs'
import { DEMO_ACTIVITY } from './activity'
import { DEMO_EXPORTS } from './exports'

const DEMO_MODE_KEY = 'uncase-demo-mode'

const STORAGE_KEYS = [
  'uncase-seeds',
  'uncase-conversations',
  'uncase-evaluations',
  'uncase-pipeline-jobs',
  'uncase-activity',
  'uncase-exports'
] as const

function dispatchStorageEvent(key: string) {
  window.dispatchEvent(new StorageEvent('storage', { key }))
}

export function populateDemoData(): void {
  const entries: [string, unknown][] = [
    ['uncase-seeds', DEMO_SEEDS],
    ['uncase-conversations', DEMO_CONVERSATIONS],
    ['uncase-evaluations', DEMO_EVALUATIONS],
    ['uncase-pipeline-jobs', DEMO_PIPELINE_JOBS],
    ['uncase-activity', DEMO_ACTIVITY],
    ['uncase-exports', DEMO_EXPORTS]
  ]

  for (const [key, data] of entries) {
    localStorage.setItem(key, JSON.stringify(data))
  }

  // Dispatch after all writes so listeners react
  for (const [key] of entries) {
    dispatchStorageEvent(key)
  }
}

export function activateDemo(): void {
  localStorage.setItem(DEMO_MODE_KEY, 'true')
  dispatchStorageEvent(DEMO_MODE_KEY)
  populateDemoData()
}

export function deactivateDemo(): void {
  localStorage.removeItem(DEMO_MODE_KEY)

  for (const key of STORAGE_KEYS) {
    localStorage.removeItem(key)
  }

  dispatchStorageEvent(DEMO_MODE_KEY)

  for (const key of STORAGE_KEYS) {
    dispatchStorageEvent(key)
  }
}

export function resetDemoData(): void {
  populateDemoData()
}

export function isDemoMode(): boolean {
  if (typeof window === 'undefined') return false

  return localStorage.getItem(DEMO_MODE_KEY) === 'true'
}

export { DEMO_RUNNING_JOB_ID }
