import type { QualityReport } from '@/types/api'

function daysAgo(n: number, hours = 12): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

export const DEMO_EVALUATIONS: QualityReport[] = [
  // ── 8 Passing evaluations ──
  {
    conversation_id: 'demo-conv-001',
    seed_id: 'demo-seed-001',
    metrics: {
      rouge_l: 0.78,
      fidelidad_factual: 0.94,
      diversidad_lexica: 0.68,
      coherencia_dialogica: 0.91,
      privacy_score: 0.0,
      memorizacion: 0.003
    },
    composite_score: 0.78,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 10)
  },
  {
    conversation_id: 'demo-conv-002',
    seed_id: 'demo-seed-001',
    metrics: {
      rouge_l: 0.82,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.72,
      coherencia_dialogica: 0.93,
      privacy_score: 0.0,
      memorizacion: 0.002
    },
    composite_score: 0.82,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 11)
  },
  {
    conversation_id: 'demo-conv-003',
    seed_id: 'demo-seed-002',
    metrics: {
      rouge_l: 0.72,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.61,
      coherencia_dialogica: 0.88,
      privacy_score: 0.0,
      memorizacion: 0.005
    },
    composite_score: 0.72,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(4, 12)
  },
  {
    conversation_id: 'demo-conv-005',
    seed_id: 'demo-seed-003',
    metrics: {
      rouge_l: 0.85,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.74,
      coherencia_dialogica: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.001
    },
    composite_score: 0.85,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 11)
  },
  {
    conversation_id: 'demo-conv-006',
    seed_id: 'demo-seed-003',
    metrics: {
      rouge_l: 0.76,
      fidelidad_factual: 0.92,
      diversidad_lexica: 0.65,
      coherencia_dialogica: 0.89,
      privacy_score: 0.0,
      memorizacion: 0.004
    },
    composite_score: 0.76,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 13)
  },
  {
    conversation_id: 'demo-conv-007',
    seed_id: 'demo-seed-004',
    metrics: {
      rouge_l: 0.91,
      fidelidad_factual: 0.98,
      diversidad_lexica: 0.78,
      coherencia_dialogica: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.001
    },
    composite_score: 0.91,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(2, 16)
  },
  {
    conversation_id: 'demo-conv-009',
    seed_id: 'demo-seed-005',
    metrics: {
      rouge_l: 0.79,
      fidelidad_factual: 0.93,
      diversidad_lexica: 0.67,
      coherencia_dialogica: 0.90,
      privacy_score: 0.0,
      memorizacion: 0.003
    },
    composite_score: 0.79,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(1, 16)
  },
  {
    conversation_id: 'demo-conv-010',
    seed_id: 'demo-seed-005',
    metrics: {
      rouge_l: 0.74,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.63,
      coherencia_dialogica: 0.87,
      privacy_score: 0.0,
      memorizacion: 0.006
    },
    composite_score: 0.74,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(1, 17)
  },

  // ── 4 Failing evaluations ──

  // Low ROUGE-L (structural coherence)
  {
    conversation_id: 'demo-conv-004',
    seed_id: 'demo-seed-002',
    metrics: {
      rouge_l: 0.48,
      fidelidad_factual: 0.90,
      diversidad_lexica: 0.59,
      coherencia_dialogica: 0.86,
      privacy_score: 0.0,
      memorizacion: 0.007
    },
    composite_score: 0.48,
    passed: false,
    failures: ['ROUGE-L below threshold (0.48 < 0.65)'],
    evaluated_at: daysAgo(4, 17)
  },
  {
    conversation_id: 'demo-conv-008',
    seed_id: 'demo-seed-004',
    metrics: {
      rouge_l: 0.55,
      fidelidad_factual: 0.92,
      diversidad_lexica: 0.60,
      coherencia_dialogica: 0.88,
      privacy_score: 0.0,
      memorizacion: 0.005
    },
    composite_score: 0.55,
    passed: false,
    failures: ['ROUGE-L below threshold (0.55 < 0.65)'],
    evaluated_at: daysAgo(2, 11)
  },

  // Privacy violation
  {
    conversation_id: 'demo-conv-004',
    seed_id: 'demo-seed-002',
    metrics: {
      rouge_l: 0.71,
      fidelidad_factual: 0.93,
      diversidad_lexica: 0.64,
      coherencia_dialogica: 0.89,
      privacy_score: 0.03,
      memorizacion: 0.004
    },
    composite_score: 0.0,
    passed: false,
    failures: ['Privacy score violation (0.03 > 0.00) — PII detected in turn 3'],
    evaluated_at: daysAgo(4, 14)
  },

  // Low coherence
  {
    conversation_id: 'demo-conv-006',
    seed_id: 'demo-seed-003',
    metrics: {
      rouge_l: 0.69,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.58,
      coherencia_dialogica: 0.72,
      privacy_score: 0.0,
      memorizacion: 0.008
    },
    composite_score: 0.58,
    passed: false,
    failures: ['Dialogic coherence below threshold (0.72 < 0.85)'],
    evaluated_at: daysAgo(3, 15)
  },

  // ── Medical consultation evaluations (10 passing) ──
  {
    conversation_id: 'demo-conv-011',
    seed_id: 'demo-seed-006',
    metrics: {
      rouge_l: 0.88,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.76,
      coherencia_dialogica: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.002
    },
    composite_score: 0.88,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(10, 10)
  },
  {
    conversation_id: 'demo-conv-012',
    seed_id: 'demo-seed-006',
    metrics: {
      rouge_l: 0.83,
      fidelidad_factual: 0.95,
      diversidad_lexica: 0.71,
      coherencia_dialogica: 0.92,
      privacy_score: 0.0,
      memorizacion: 0.003
    },
    composite_score: 0.83,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(10, 15)
  },
  {
    conversation_id: 'demo-conv-013',
    seed_id: 'demo-seed-007',
    metrics: {
      rouge_l: 0.86,
      fidelidad_factual: 0.98,
      diversidad_lexica: 0.73,
      coherencia_dialogica: 0.94,
      privacy_score: 0.0,
      memorizacion: 0.002
    },
    composite_score: 0.86,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(9, 11)
  },
  {
    conversation_id: 'demo-conv-014',
    seed_id: 'demo-seed-007',
    metrics: {
      rouge_l: 0.80,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.68,
      coherencia_dialogica: 0.91,
      privacy_score: 0.0,
      memorizacion: 0.004
    },
    composite_score: 0.80,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(8, 16)
  },
  {
    conversation_id: 'demo-conv-015',
    seed_id: 'demo-seed-008',
    metrics: {
      rouge_l: 0.91,
      fidelidad_factual: 0.99,
      diversidad_lexica: 0.79,
      coherencia_dialogica: 0.97,
      privacy_score: 0.0,
      memorizacion: 0.001
    },
    composite_score: 0.91,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(7, 12)
  },
  {
    conversation_id: 'demo-conv-016',
    seed_id: 'demo-seed-008',
    metrics: {
      rouge_l: 0.84,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.72,
      coherencia_dialogica: 0.93,
      privacy_score: 0.0,
      memorizacion: 0.003
    },
    composite_score: 0.84,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(7, 17)
  },
  {
    conversation_id: 'demo-conv-017',
    seed_id: 'demo-seed-009',
    metrics: {
      rouge_l: 0.89,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.77,
      coherencia_dialogica: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.002
    },
    composite_score: 0.89,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(6, 11)
  },
  {
    conversation_id: 'demo-conv-018',
    seed_id: 'demo-seed-009',
    metrics: {
      rouge_l: 0.85,
      fidelidad_factual: 0.95,
      diversidad_lexica: 0.74,
      coherencia_dialogica: 0.93,
      privacy_score: 0.0,
      memorizacion: 0.003
    },
    composite_score: 0.85,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 12)
  },
  {
    conversation_id: 'demo-conv-019',
    seed_id: 'demo-seed-010',
    metrics: {
      rouge_l: 0.92,
      fidelidad_factual: 0.99,
      diversidad_lexica: 0.80,
      coherencia_dialogica: 0.97,
      privacy_score: 0.0,
      memorizacion: 0.001
    },
    composite_score: 0.92,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(4, 10)
  },
  {
    conversation_id: 'demo-conv-020',
    seed_id: 'demo-seed-010',
    metrics: {
      rouge_l: 0.87,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.75,
      coherencia_dialogica: 0.94,
      privacy_score: 0.0,
      memorizacion: 0.002
    },
    composite_score: 0.87,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 15)
  }
]
