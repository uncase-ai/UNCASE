import type { QualityReport } from '@/types/api'

function daysAgo(n: number, hours = 12): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

export const DEMO_EVALUATIONS: QualityReport[] = [
  // ── 8 Passing automotive evaluations ──
  {
    conversation_id: 'demo-conv-001',
    seed_id: 'demo-seed-001',
    metrics: {
      rouge_l: 0.78,
      fidelidad_factual: 0.94,
      diversidad_lexica: 0.68,
      coherencia_dialogica: 0.91,
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.82,
      embedding_drift: 0.71
    },
    composite_score: 0.68,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.88,
      embedding_drift: 0.76
    },
    composite_score: 0.72,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.005,
      semantic_fidelity: 0.75,
      embedding_drift: 0.64
    },
    composite_score: 0.61,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.91,
      embedding_drift: 0.82
    },
    composite_score: 0.74,
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
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.004,
      semantic_fidelity: 0.78,
      embedding_drift: 0.67
    },
    composite_score: 0.65,
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
      tool_call_validity: 0.98,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.93,
      embedding_drift: 0.85
    },
    composite_score: 0.78,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.80,
      embedding_drift: 0.69
    },
    composite_score: 0.67,
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
      tool_call_validity: 0.92,
      privacy_score: 0.0,
      memorizacion: 0.006,
      semantic_fidelity: 0.72,
      embedding_drift: 0.61
    },
    composite_score: 0.61,
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
      tool_call_validity: 0.85,
      privacy_score: 0.0,
      memorizacion: 0.007,
      semantic_fidelity: 0.55,
      embedding_drift: 0.42
    },
    composite_score: 0,
    passed: false,
    failures: ['ROUGE-L below threshold (0.48 < 0.65)', 'Semantic fidelity below threshold (0.55 < 0.60)'],
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
      tool_call_validity: 0.90,
      privacy_score: 0.0,
      memorizacion: 0.005,
      semantic_fidelity: 0.58,
      embedding_drift: 0.45
    },
    composite_score: 0,
    passed: false,
    failures: ['ROUGE-L below threshold (0.55 < 0.65)', 'Semantic fidelity below threshold (0.58 < 0.60)'],
    evaluated_at: daysAgo(2, 11)
  },

  // Privacy violation
  {
    conversation_id: 'demo-conv-004-pii',
    seed_id: 'demo-seed-002',
    metrics: {
      rouge_l: 0.71,
      fidelidad_factual: 0.93,
      diversidad_lexica: 0.64,
      coherencia_dialogica: 0.89,
      tool_call_validity: 1.0,
      privacy_score: 0.03,
      memorizacion: 0.004,
      semantic_fidelity: 0.76,
      embedding_drift: 0.65
    },
    composite_score: 0.0,
    passed: false,
    failures: ['Privacy score violation (0.03 > 0.00) — PII detected in turn 3'],
    evaluated_at: daysAgo(4, 14)
  },

  // Low coherence
  {
    conversation_id: 'demo-conv-006-v2',
    seed_id: 'demo-seed-003',
    metrics: {
      rouge_l: 0.69,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.58,
      coherencia_dialogica: 0.72,
      tool_call_validity: 0.88,
      privacy_score: 0.0,
      memorizacion: 0.008,
      semantic_fidelity: 0.62,
      embedding_drift: 0.48
    },
    composite_score: 0,
    passed: false,
    failures: ['Dialogic coherence below threshold (0.72 < 0.80)'],
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
      tool_call_validity: 0.97,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.90,
      embedding_drift: 0.81
    },
    composite_score: 0.76,
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
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.85,
      embedding_drift: 0.74
    },
    composite_score: 0.71,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.88,
      embedding_drift: 0.77
    },
    composite_score: 0.73,
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
      tool_call_validity: 0.93,
      privacy_score: 0.0,
      memorizacion: 0.004,
      semantic_fidelity: 0.82,
      embedding_drift: 0.70
    },
    composite_score: 0.68,
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
      tool_call_validity: 0.99,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.94,
      embedding_drift: 0.87
    },
    composite_score: 0.79,
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
      tool_call_validity: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.86,
      embedding_drift: 0.75
    },
    composite_score: 0.72,
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
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.91,
      embedding_drift: 0.83
    },
    composite_score: 0.77,
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
      tool_call_validity: 0.94,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.87,
      embedding_drift: 0.76
    },
    composite_score: 0.74,
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
      tool_call_validity: 0.98,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.95,
      embedding_drift: 0.88
    },
    composite_score: 0.80,
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
      tool_call_validity: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.89,
      embedding_drift: 0.78
    },
    composite_score: 0.75,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 15)
  }
]
