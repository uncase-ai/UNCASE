import type { LucideIcon } from 'lucide-react'

import {
  ShieldCheckIcon,
  GlobeIcon,
  RadioIcon,
  WrenchIcon,
  LockIcon,
  SearchIcon,
  NetworkIcon,
  MessageSquareIcon,
  ServerIcon,
  CloudIcon,
  PlayCircleIcon,
  BarChart3Icon,
  PuzzleIcon,
  BookOpenIcon,
  ClipboardListIcon,
  DollarSignIcon,
  ActivityIcon
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
      'Dual-strategy detection with Presidio NER + regex patterns. Privacy Interceptor scans all inbound and outbound LLM traffic in real-time. Privacy score must equal 0.00 — no exceptions.'
  },
  {
    icon: NetworkIcon,
    title: 'Universal LLM Gateway',
    description:
      'Route requests to any LLM provider through a single API. Privacy interception on every call — audit, warn, or block mode. Provider-aware generation with encrypted API keys at rest.'
  },
  {
    icon: RadioIcon,
    title: 'Connector Hub',
    description:
      'Ingest conversations from WhatsApp exports, webhooks, CRMs, and custom sources. BaseConnector abstraction makes adding new data origins straightforward.'
  },
  {
    icon: GlobeIcon,
    title: '6 Regulated Industries',
    description:
      'Automotive, medical, legal, finance, industrial, education — each with domain-specific seed templates, quality thresholds, and compliance rules. Extensible to any regulated vertical.'
  },
  {
    icon: WrenchIcon,
    title: 'Tool-Augmented Generation',
    description:
      'Seeds define callable tools (cotizador, simulador_credito, CRM lookups). Synthetic conversations include realistic tool_calls and tool_results.'
  },
  {
    icon: LockIcon,
    title: 'Differential Privacy Training',
    description:
      'DP-SGD with epsilon ≤ 8.0. Extraction attack success rate < 1%. Mathematical privacy guarantees throughout the entire fine-tuning pipeline.'
  },
  {
    icon: SearchIcon,
    title: 'Full Traceability',
    description:
      'Every synthetic conversation traces back to its seed via seed_id. Complete audit trail from expert knowledge to trained adapter — required for regulatory compliance.'
  },
  {
    icon: MessageSquareIcon,
    title: '10+ Chat Formats',
    description:
      'Import and export in ChatML, Alpaca, ShareGPT, LLaMA, Mistral, Qwen, OpenAI, and more. Multi-format parser with auto-detection for seamless integration.'
  },
  {
    icon: ServerIcon,
    title: '75+ REST API Endpoints',
    description:
      'Complete API coverage: seeds, generation, evaluation, providers, connectors, gateway, templates, tools, imports, sandboxes, knowledge, usage, audit, costs, webhooks, organizations, and health monitoring. Versioned at /api/v1/.'
  },
  {
    icon: CloudIcon,
    title: 'E2B Cloud Sandboxes',
    description:
      'Parallel generation in isolated MicroVMs — one sandbox per seed, ~2s boot time. Fan out 20 concurrent sandboxes for massive throughput. Automatic fallback to local generation when E2B is not configured.'
  },
  {
    icon: PlayCircleIcon,
    title: 'Instant Demo Containers',
    description:
      'Spin up a fully configured UNCASE instance for any industry vertical in seconds. Pre-loaded seeds, running API, Swagger docs — auto-destroys after 5-60 minutes. Zero installation required.'
  },
  {
    icon: BarChart3Icon,
    title: 'Opik Evaluation Sandboxes',
    description:
      'Ephemeral LLM-as-judge evaluation machines with Opik. Hallucination detection, coherence GEval, answer relevance — all inside an isolated sandbox. Results are exported before auto-destruction.'
  },
  {
    icon: PuzzleIcon,
    title: 'Plugin Marketplace',
    description:
      '6 official plugins and 30 domain-specific tools across all industries. Extensible plugin registry with install/uninstall lifecycle. Each domain gets 5 specialized tools (cotizador, simulador, CRM, etc.).'
  },
  {
    icon: BookOpenIcon,
    title: 'Knowledge Base',
    description:
      'Upload domain documents (facts, procedures, terminology, reference) with automatic server-side chunking. Full-text search across chunks. Persistent PostgreSQL storage with organization-level isolation.'
  },
  {
    icon: ClipboardListIcon,
    title: 'Audit Logging & Compliance',
    description:
      'Immutable audit trail for every API action — seeds created, evaluations run, models trained. Data retention policies with configurable TTLs. Full compliance traceability from seed to adapter.'
  },
  {
    icon: DollarSignIcon,
    title: 'LLM Cost Tracking',
    description:
      'Per-organization and per-job cost breakdowns across all LLM providers. Provider-aware pricing estimates. Daily cost timelines and usage metering with event-level granularity.'
  },
  {
    icon: ActivityIcon,
    title: 'Observability Stack',
    description:
      'Prometheus metrics export + pre-built Grafana dashboards. Request rate, latency percentiles, error rates, and top endpoints — all out of the box with Docker Compose observability profile.'
  }
]
