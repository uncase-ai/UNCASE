import type { ActivityEvent } from '@/types/dashboard'

function daysAgo(n: number, hours = 10, minutes = 0): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, minutes, 0, 0)

  return d.toISOString()
}

export const DEMO_ACTIVITY: ActivityEvent[] = [
  // Day 7 — seed_created (5)
  {
    id: 'demo-act-001',
    type: 'seed_created',
    title: 'Seed created: Consulta vehículo nuevo',
    description: 'automotive.sales — demo-seed-001',
    timestamp: daysAgo(7, 9, 0),
    metadata: { seed_id: 'demo-seed-001' }
  },
  {
    id: 'demo-act-002',
    type: 'seed_created',
    title: 'Seed created: Prueba de manejo',
    description: 'automotive.sales — demo-seed-002',
    timestamp: daysAgo(7, 9, 15),
    metadata: { seed_id: 'demo-seed-002' }
  },
  {
    id: 'demo-act-003',
    type: 'seed_created',
    title: 'Seed created: Evaluación trade-in',
    description: 'automotive.sales — demo-seed-003',
    timestamp: daysAgo(7, 9, 30),
    metadata: { seed_id: 'demo-seed-003' }
  },
  {
    id: 'demo-act-004',
    type: 'seed_created',
    title: 'Seed created: Financiamiento automotriz',
    description: 'automotive.sales — demo-seed-004',
    timestamp: daysAgo(7, 10, 0),
    metadata: { seed_id: 'demo-seed-004' }
  },
  {
    id: 'demo-act-005',
    type: 'seed_created',
    title: 'Seed created: Servicio post-venta',
    description: 'automotive.sales — demo-seed-005',
    timestamp: daysAgo(7, 10, 15),
    metadata: { seed_id: 'demo-seed-005' }
  },

  // Day 6 — tool_registered
  {
    id: 'demo-act-006',
    type: 'tool_registered',
    title: 'Tool registered: inventory_lookup',
    description: 'Consulta inventario de vehículos disponibles',
    timestamp: daysAgo(6, 11, 0),
    metadata: { tool_name: 'inventory_lookup' }
  },

  // Day 5 — conversation_imported (3)
  {
    id: 'demo-act-007',
    type: 'conversation_imported',
    title: 'Conversation imported from WhatsApp',
    description: 'demo-conv-004 — automotive.sales',
    timestamp: daysAgo(5, 14, 0),
    metadata: { conversation_id: 'demo-conv-004', source: 'whatsapp' }
  },
  {
    id: 'demo-act-008',
    type: 'conversation_imported',
    title: 'Conversation imported from CRM',
    description: 'demo-conv-008 — automotive.sales',
    timestamp: daysAgo(5, 14, 30),
    metadata: { conversation_id: 'demo-conv-008', source: 'crm' }
  },
  {
    id: 'demo-act-009',
    type: 'conversation_imported',
    title: 'Conversation imported from WhatsApp',
    description: 'demo-conv-010 — automotive.sales',
    timestamp: daysAgo(5, 15, 0),
    metadata: { conversation_id: 'demo-conv-010', source: 'whatsapp' }
  },

  // Day 4 — conversation_generated (4)
  {
    id: 'demo-act-010',
    type: 'conversation_generated',
    title: 'Synthetic conversation generated',
    description: 'demo-conv-001 — from demo-seed-001',
    timestamp: daysAgo(4, 10, 0),
    metadata: { conversation_id: 'demo-conv-001', model: 'claude-3.5-sonnet' }
  },
  {
    id: 'demo-act-011',
    type: 'conversation_generated',
    title: 'Synthetic conversation generated',
    description: 'demo-conv-002 — from demo-seed-001',
    timestamp: daysAgo(4, 10, 15),
    metadata: { conversation_id: 'demo-conv-002', model: 'claude-3.5-sonnet' }
  },
  {
    id: 'demo-act-012',
    type: 'conversation_generated',
    title: 'Synthetic conversation generated',
    description: 'demo-conv-005 — from demo-seed-003',
    timestamp: daysAgo(4, 11, 0),
    metadata: { conversation_id: 'demo-conv-005', model: 'claude-3.5-sonnet' }
  },
  {
    id: 'demo-act-013',
    type: 'conversation_generated',
    title: 'Synthetic conversation generated',
    description: 'demo-conv-009 — from demo-seed-005',
    timestamp: daysAgo(4, 11, 30),
    metadata: { conversation_id: 'demo-conv-009', model: 'claude-3.5-sonnet' }
  },

  // Day 3 — evaluation_completed (3)
  {
    id: 'demo-act-014',
    type: 'evaluation_completed',
    title: 'Quality evaluation completed — batch 1',
    description: '8 passed, 4 failed (66.7% pass rate)',
    timestamp: daysAgo(3, 16, 0),
    metadata: { passed: 8, failed: 4, pass_rate: 0.667 }
  },
  {
    id: 'demo-act-015',
    type: 'evaluation_completed',
    title: 'Privacy audit completed',
    description: '1 violation detected in demo-conv-004',
    timestamp: daysAgo(3, 16, 30),
    metadata: { violations: 1 }
  },

  // Day 2 — template_rendered
  {
    id: 'demo-act-016',
    type: 'template_rendered',
    title: 'Template rendered: ShareGPT format',
    description: '7 conversations exported as sharegpt.jsonl',
    timestamp: daysAgo(2, 14, 0),
    metadata: { template: 'sharegpt', count: 7 }
  },

  // Day 1 — dataset_exported + evaluation_completed
  {
    id: 'demo-act-017',
    type: 'dataset_exported',
    title: 'Dataset exported: automotive-sales-v1-synthetic',
    description: '7 conversations, ShareGPT JSONL, 45.2 KB',
    timestamp: daysAgo(1, 10, 0),
    metadata: { export_id: 'demo-export-001' }
  },
  {
    id: 'demo-act-018',
    type: 'evaluation_completed',
    title: 'Re-evaluation completed — post-export',
    description: 'All exported conversations pass quality gates',
    timestamp: daysAgo(1, 11, 0),
    metadata: { passed: 7, failed: 0, pass_rate: 1.0 }
  }
]
