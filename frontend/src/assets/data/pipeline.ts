import type { LucideIcon } from 'lucide-react'

import { SproutIcon, FileSearchIcon, ShieldCheckIcon, BrainCircuitIcon, CpuIcon } from 'lucide-react'

export type PipelineStep = {
  step: number
  icon: LucideIcon
  title: string
  description: string
}

export const pipelineSteps: PipelineStep[] = [
  {
    step: 1,
    icon: SproutIcon,
    title: 'Seed Engine',
    description:
      'Real conversations → PII stripping (Presidio + SpaCy) → SeedSchema v1 capturing reasoning patterns and domain rules.'
  },
  {
    step: 2,
    icon: FileSearchIcon,
    title: 'Parser & Validator',
    description:
      'Multi-format import (CSV, JSONL — auto-detects OpenAI/ShareGPT/UNCASE) → validated Conversation objects with traceability.'
  },
  {
    step: 3,
    icon: ShieldCheckIcon,
    title: 'Quality Evaluator',
    description:
      '6 hard-gated metrics: ROUGE-L ≥0.65, Factual ≥0.90, TTR ≥0.55, Coherence ≥0.85, Privacy =0.00, Memorization <0.01.'
  },
  {
    step: 4,
    icon: BrainCircuitIcon,
    title: 'Synthetic Generator',
    description:
      'LiteLLM-powered generation with simulated tool execution — conversations include tool_calls and tool_results.'
  },
  {
    step: 5,
    icon: CpuIcon,
    title: 'LoRA Pipeline',
    description: 'LoRA/QLoRA training with DP-SGD (ε ≤8.0) → 50-150MB adapter, $15-45 USD cost.'
  }
]

export type DataFlowStep = {
  title: string
  content: Record<string, string | number | boolean>
}

export const dataFlowSteps: DataFlowStep[] = [
  {
    title: 'Expert Knowledge In',
    content: {
      dominio: 'automotive.sales',
      objetivo: 'financiamiento_vehicular',
      roles: 'asesor, cliente',
      herramientas: 'cotizador, simulador_credito, CRM',
      turnos_min: 6,
      turnos_max: 24
    }
  },
  {
    title: 'Privacy Enforced',
    content: {
      pii_eliminado: true,
      metodo: 'Presidio + SpaCy',
      datos_reales: false,
      privacy_score: 0.0
    }
  },
  {
    title: 'Quality Certified',
    content: {
      'ROUGE-L': 0.72,
      factual_fidelity: 0.94,
      lexical_diversity: 0.61,
      dialogic_coherence: 0.89
    }
  },
  {
    title: 'Synthetic Output',
    content: {
      es_sintetica: true,
      seed_id: 'seed_financiamiento_001',
      tool_calls: 3,
      tool_results: 3,
      turnos: 14
    }
  },
  {
    title: 'Trained Adapter',
    content: {
      size: '50-150MB',
      chat_formats: 10,
      'dp_sgd_epsilon': 8.0,
      extraction_rate: '<1%'
    }
  }
]
