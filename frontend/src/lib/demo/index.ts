const DEMO_MODE_KEY = 'uncase-demo-mode'

const STORAGE_KEYS = [
  'uncase-seeds',
  'uncase-conversations',
  'uncase-evaluations',
  'uncase-pipeline-jobs',
  'uncase-activity',
  'uncase-exports',
  'uncase-tools'
] as const

export const DEMO_RUNNING_JOB_ID = 'demo-job-003'

function dispatchStorageEvent(key: string) {
  if (typeof window === 'undefined') return

  window.dispatchEvent(new StorageEvent('storage', { key }))
}

async function loadDemoData() {
  const [{ DEMO_SEEDS }, { DEMO_CONVERSATIONS }, { DEMO_EVALUATIONS }, { DEMO_PIPELINE_JOBS }, { DEMO_ACTIVITY }, { DEMO_EXPORTS }, { DEMO_TOOLS }] =
    await Promise.all([
      import('./seeds'),
      import('./conversations'),
      import('./evaluations'),
      import('./pipeline-jobs'),
      import('./activity'),
      import('./exports'),
      import('./tools')
    ])

  return [
    ['uncase-seeds', DEMO_SEEDS],
    ['uncase-conversations', DEMO_CONVERSATIONS],
    ['uncase-evaluations', DEMO_EVALUATIONS],
    ['uncase-pipeline-jobs', DEMO_PIPELINE_JOBS],
    ['uncase-activity', DEMO_ACTIVITY],
    ['uncase-exports', DEMO_EXPORTS],
    ['uncase-tools', DEMO_TOOLS]
  ] as [string, unknown][]
}

function writeAndDispatch(entries: [string, unknown][]) {
  for (const [key, data] of entries) {
    localStorage.setItem(key, JSON.stringify(data))
  }

  for (const [key] of entries) {
    dispatchStorageEvent(key)
  }
}

export async function populateDemoData(): Promise<void> {
  const entries = await loadDemoData()

  writeAndDispatch(entries)
}

export async function activateDemo(): Promise<void> {
  localStorage.setItem(DEMO_MODE_KEY, 'true')
  dispatchStorageEvent(DEMO_MODE_KEY)
  await populateDemoData()
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

export async function resetDemoData(): Promise<void> {
  await populateDemoData()
}

export function isDemoMode(): boolean {
  if (typeof window === 'undefined') return false

  return localStorage.getItem(DEMO_MODE_KEY) === 'true'
}
