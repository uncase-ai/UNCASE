import type { PipelineJob } from '@/types/dashboard'

function daysAgo(n: number, hours = 10): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

export const DEMO_PIPELINE_JOBS: PipelineJob[] = [
  {
    id: 'demo-job-001',
    stage: 'seed',
    status: 'completed',
    progress: 100,
    label: 'Seed creation — automotive.sales (5 seeds)',
    created_at: daysAgo(6, 8),
    started_at: daysAgo(6, 8),
    completed_at: daysAgo(6, 8),
    metadata: { seed_count: 5, domain: 'automotive.sales' }
  },
  {
    id: 'demo-job-002',
    stage: 'import',
    status: 'completed',
    progress: 100,
    label: 'Import conversations — WhatsApp + CRM (3 files)',
    created_at: daysAgo(4, 9),
    started_at: daysAgo(4, 9),
    completed_at: daysAgo(4, 9),
    metadata: { source: 'multi', files: 3, conversations_imported: 3 }
  },
  {
    id: 'demo-job-003',
    stage: 'evaluate',
    status: 'running',
    progress: 65,
    label: 'Quality evaluation — batch 2 (6 conversations)',
    created_at: daysAgo(0, 9),
    started_at: daysAgo(0, 9),
    metadata: { batch: 2, total_conversations: 6 }
  },
  {
    id: 'demo-job-004',
    stage: 'generate',
    status: 'queued',
    progress: 0,
    label: 'Synthetic generation — automotive.sales (10 target)',
    created_at: daysAgo(0, 9),
    metadata: { target_count: 10, domain: 'automotive.sales' }
  }
]

export const DEMO_RUNNING_JOB_ID = 'demo-job-003'
