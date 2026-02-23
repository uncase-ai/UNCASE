import type { LucideIcon } from 'lucide-react'

import {
  ShieldCheckIcon,
  GlobeIcon,
  MessageSquareIcon,
  WrenchIcon,
  LockIcon,
  SearchIcon
} from 'lucide-react'

export type Capability = {
  icon: LucideIcon
  title: string
  description: string
}

export const capabilities: Capability[] = [
  {
    icon: ShieldCheckIcon,
    title: 'Zero PII Guarantee',
    description:
      'Presidio + SpaCy PII detection. Privacy score must equal 0.00 — no exceptions.'
  },
  {
    icon: GlobeIcon,
    title: '6 Industry Domains',
    description:
      'Automotive, medical, legal, finance, industrial, education — extensible to any regulated industry.'
  },
  {
    icon: MessageSquareIcon,
    title: '10 Chat Formats',
    description:
      'ChatML, Alpaca, LLaMA, Mistral, Qwen, and more. Import and export in any format.'
  },
  {
    icon: WrenchIcon,
    title: 'Tool-Augmented Generation',
    description:
      'Seeds define tools (cotizador, simulador_credito, CRM). Synthetic conversations include tool_calls and tool_results.'
  },
  {
    icon: LockIcon,
    title: 'Differential Privacy Training',
    description:
      'DP-SGD with ε ≤8.0. Extraction attack success rate <1%. Mathematical privacy guarantees.'
  },
  {
    icon: SearchIcon,
    title: 'Full Traceability',
    description:
      'Every synthetic conversation traces back to its seed via seed_id. Audit trail from knowledge to adapter.'
  }
]
