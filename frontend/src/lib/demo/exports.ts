interface ExportRecord {
  id: string
  name: string
  template: string
  domain: string
  conversation_count: number
  format: 'api' | 'jsonl'
  size_bytes: number
  created_at: string
  conversation_ids: string[]
}

function daysAgo(n: number, hours = 10): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

export const DEMO_EXPORTS: ExportRecord[] = [
  {
    id: 'demo-export-001',
    name: 'automotive-sales-v1-synthetic',
    template: 'sharegpt',
    domain: 'automotive.sales',
    conversation_count: 7,
    format: 'jsonl',
    size_bytes: 46285,
    created_at: daysAgo(1, 10),
    conversation_ids: [
      'demo-conv-001',
      'demo-conv-002',
      'demo-conv-003',
      'demo-conv-005',
      'demo-conv-006',
      'demo-conv-007',
      'demo-conv-009'
    ]
  },
  {
    id: 'demo-export-002',
    name: 'automotive-pilot-full',
    template: 'chatml',
    domain: 'automotive.sales',
    conversation_count: 10,
    format: 'jsonl',
    size_bytes: 72140,
    created_at: daysAgo(0, 11),
    conversation_ids: [
      'demo-conv-001',
      'demo-conv-002',
      'demo-conv-003',
      'demo-conv-004',
      'demo-conv-005',
      'demo-conv-006',
      'demo-conv-007',
      'demo-conv-008',
      'demo-conv-009',
      'demo-conv-010'
    ]
  }
]
