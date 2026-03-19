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
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.38,
      fidelidad_factual: 0.94,
      diversidad_lexica: 0.68,
      coherencia_dialogica: 0.82,
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.82,
      embedding_drift: 0.61
    },
    composite_score: 0.38,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 10)
  },
  {
    conversation_id: 'demo-conv-002',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.42,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.72,
      coherencia_dialogica: 0.85,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.88,
      embedding_drift: 0.66
    },
    composite_score: 0.42,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 11)
  },
  {
    conversation_id: 'demo-conv-003',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.32,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.61,
      coherencia_dialogica: 0.78,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.005,
      semantic_fidelity: 0.75,
      embedding_drift: 0.54
    },
    composite_score: 0.32,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(4, 12)
  },
  {
    conversation_id: 'demo-conv-005',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.45,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.74,
      coherencia_dialogica: 0.88,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.91,
      embedding_drift: 0.72
    },
    composite_score: 0.45,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 11)
  },
  {
    conversation_id: 'demo-conv-006',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.36,
      fidelidad_factual: 0.92,
      diversidad_lexica: 0.65,
      coherencia_dialogica: 0.79,
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.004,
      semantic_fidelity: 0.78,
      embedding_drift: 0.57
    },
    composite_score: 0.36,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 13)
  },
  {
    conversation_id: 'demo-conv-007',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.48,
      fidelidad_factual: 0.98,
      diversidad_lexica: 0.78,
      coherencia_dialogica: 0.91,
      tool_call_validity: 0.98,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.93,
      embedding_drift: 0.75
    },
    composite_score: 0.48,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(2, 16)
  },
  {
    conversation_id: 'demo-conv-009',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.39,
      fidelidad_factual: 0.93,
      diversidad_lexica: 0.67,
      coherencia_dialogica: 0.81,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.80,
      embedding_drift: 0.59
    },
    composite_score: 0.39,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(1, 16)
  },
  {
    conversation_id: 'demo-conv-010',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.34,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.63,
      coherencia_dialogica: 0.77,
      tool_call_validity: 0.92,
      privacy_score: 0.0,
      memorizacion: 0.006,
      semantic_fidelity: 0.72,
      embedding_drift: 0.51
    },
    composite_score: 0.34,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(1, 17)
  },

  // ── 4 Failing evaluations ──

  // Low lexical diversity
  {
    conversation_id: 'demo-conv-004',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.32,
      fidelidad_factual: 0.90,
      diversidad_lexica: 0.49,
      coherencia_dialogica: 0.72,
      tool_call_validity: 0.85,
      privacy_score: 0.0,
      memorizacion: 0.007,
      semantic_fidelity: 0.55,
      embedding_drift: 0.42
    },
    composite_score: 0.32,
    passed: false,
    failures: ['diversidad_lexica=0.490 (min 0.55)', 'semantic_fidelity=0.550 (min 0.60)'],
    evaluated_at: daysAgo(4, 17)
  },

  // Low factual fidelity
  {
    conversation_id: 'demo-conv-008',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.28,
      fidelidad_factual: 0.74,
      diversidad_lexica: 0.60,
      coherencia_dialogica: 0.71,
      tool_call_validity: 0.90,
      privacy_score: 0.0,
      memorizacion: 0.005,
      semantic_fidelity: 0.58,
      embedding_drift: 0.38
    },
    composite_score: 0.28,
    passed: false,
    failures: ['fidelidad_factual=0.740 (min 0.80)', 'semantic_fidelity=0.580 (min 0.60)'],
    evaluated_at: daysAgo(2, 11)
  },

  // Privacy violation
  {
    conversation_id: 'demo-conv-004-pii',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.35,
      fidelidad_factual: 0.93,
      diversidad_lexica: 0.64,
      coherencia_dialogica: 0.78,
      tool_call_validity: 1.0,
      privacy_score: 0.03,
      memorizacion: 0.004,
      semantic_fidelity: 0.76,
      embedding_drift: 0.55
    },
    composite_score: 0.0,
    passed: false,
    failures: ['privacy_score=0.03 (must be 0.0)'],
    evaluated_at: daysAgo(4, 14)
  },

  // Low dialogic coherence
  {
    conversation_id: 'demo-conv-006-v2',
    seed_id: 'featured-auto-001',
    metrics: {
      rouge_l: 0.31,
      fidelidad_factual: 0.91,
      diversidad_lexica: 0.58,
      coherencia_dialogica: 0.58,
      tool_call_validity: 0.88,
      privacy_score: 0.0,
      memorizacion: 0.008,
      semantic_fidelity: 0.62,
      embedding_drift: 0.41
    },
    composite_score: 0.31,
    passed: false,
    failures: ['coherencia_dialogica=0.580 (min 0.65)'],
    evaluated_at: daysAgo(3, 15)
  },

  // ── Medical consultation evaluations (10 passing) ──
  {
    conversation_id: 'demo-conv-011',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.41,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.76,
      coherencia_dialogica: 0.87,
      tool_call_validity: 0.97,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.90,
      embedding_drift: 0.71
    },
    composite_score: 0.41,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(10, 10)
  },
  {
    conversation_id: 'demo-conv-012',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.37,
      fidelidad_factual: 0.95,
      diversidad_lexica: 0.71,
      coherencia_dialogica: 0.83,
      tool_call_validity: 0.95,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.85,
      embedding_drift: 0.64
    },
    composite_score: 0.37,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(10, 15)
  },
  {
    conversation_id: 'demo-conv-013',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.43,
      fidelidad_factual: 0.98,
      diversidad_lexica: 0.73,
      coherencia_dialogica: 0.86,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.88,
      embedding_drift: 0.67
    },
    composite_score: 0.43,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(9, 11)
  },
  {
    conversation_id: 'demo-conv-014',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.35,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.68,
      coherencia_dialogica: 0.81,
      tool_call_validity: 0.93,
      privacy_score: 0.0,
      memorizacion: 0.004,
      semantic_fidelity: 0.82,
      embedding_drift: 0.60
    },
    composite_score: 0.35,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(8, 16)
  },
  {
    conversation_id: 'demo-conv-015',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.47,
      fidelidad_factual: 0.99,
      diversidad_lexica: 0.79,
      coherencia_dialogica: 0.92,
      tool_call_validity: 0.99,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.94,
      embedding_drift: 0.77
    },
    composite_score: 0.47,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(7, 12)
  },
  {
    conversation_id: 'demo-conv-016',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.40,
      fidelidad_factual: 0.96,
      diversidad_lexica: 0.72,
      coherencia_dialogica: 0.84,
      tool_call_validity: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.86,
      embedding_drift: 0.65
    },
    composite_score: 0.40,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(7, 17)
  },
  {
    conversation_id: 'demo-conv-017',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.44,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.77,
      coherencia_dialogica: 0.89,
      tool_call_validity: 1.0,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.91,
      embedding_drift: 0.73
    },
    composite_score: 0.44,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(6, 11)
  },
  {
    conversation_id: 'demo-conv-018',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.39,
      fidelidad_factual: 0.95,
      diversidad_lexica: 0.74,
      coherencia_dialogica: 0.84,
      tool_call_validity: 0.94,
      privacy_score: 0.0,
      memorizacion: 0.003,
      semantic_fidelity: 0.87,
      embedding_drift: 0.66
    },
    composite_score: 0.39,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(5, 12)
  },
  {
    conversation_id: 'demo-conv-019',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.49,
      fidelidad_factual: 0.99,
      diversidad_lexica: 0.80,
      coherencia_dialogica: 0.93,
      tool_call_validity: 0.98,
      privacy_score: 0.0,
      memorizacion: 0.001,
      semantic_fidelity: 0.95,
      embedding_drift: 0.78
    },
    composite_score: 0.49,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(4, 10)
  },
  {
    conversation_id: 'demo-conv-020',
    seed_id: 'featured-med-001',
    metrics: {
      rouge_l: 0.41,
      fidelidad_factual: 0.97,
      diversidad_lexica: 0.75,
      coherencia_dialogica: 0.86,
      tool_call_validity: 0.96,
      privacy_score: 0.0,
      memorizacion: 0.002,
      semantic_fidelity: 0.89,
      embedding_drift: 0.68
    },
    composite_score: 0.41,
    passed: true,
    failures: [],
    evaluated_at: daysAgo(3, 15)
  }
]
