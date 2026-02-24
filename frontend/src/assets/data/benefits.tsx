import { ShieldCheckIcon, BrainCircuitIcon, LayersIcon, ZapIcon, NetworkIcon, PlugIcon } from 'lucide-react'

import { type Features } from '@/components/blocks/benefits/benefits'

export const benefits: Features = [
  {
    icon: <ShieldCheckIcon />,
    title: 'Privacy by Design, Not by Patch',
    description:
      'No real patient, client, or user data ever transits through the pipeline. Seeds capture reasoning patterns and domain structure — never conversations. Every LLM call passes through a Privacy Interceptor that scans for PII in real-time. Compliant with GDPR, HIPAA, LFPDPPP, AI Act, and CCPA from day one.',
    image: '/images/logo/whitepaper-privacy.png'
  },
  {
    icon: <BrainCircuitIcon />,
    title: 'Expert Knowledge, Infinitely Scaled',
    description:
      'Transform decades of specialized expertise into abstract seed structures that train AI models. Your best professionals become seed engineers — their knowledge generates thousands of high-quality synthetic conversations without exposing privileged information.',
    image: '/images/logo/whitepaper-foundations.png'
  },
  {
    icon: <NetworkIcon />,
    title: 'Any LLM Provider, One Gateway',
    description:
      'Route synthetic generation through Claude, GPT, Gemini, Qwen, LLaMA, or any LiteLLM-compatible provider. The built-in Provider Registry stores encrypted API keys, and the Gateway proxies every request with automatic privacy interception — audit, warn, or block.',
    image: '/images/logo/whitepaper-architecture.png'
  },
  {
    icon: <PlugIcon />,
    title: 'Connect Any Data Source',
    description:
      'Ingest conversations from WhatsApp exports, webhooks, CRM systems, transcriptions, and more. The Connector Hub normalizes everything into UNCASE format — ready for seed engineering and synthetic generation at scale.',
    image: '/images/logo/whitepaper-cover.png'
  },
  {
    icon: <LayersIcon />,
    title: 'Modular 5-Layer Pipeline',
    description:
      'Each layer delivers value independently. Start with seed engineering, add parsing, quality evaluation, synthetic generation, and LoRA training incrementally. 47 API endpoints cover the full lifecycle — no big-bang deployment needed.',
    image: '/images/logo/whitepaper-architecture.png'
  },
  {
    icon: <ZapIcon />,
    title: 'Radical Cost Efficiency',
    description:
      'LoRA adapters of 50-150 MB instead of 28 GB base models. Training in 2-8 hours on a single A100. Infrastructure cost: $15-$45 USD per specialized adapter. Fine-tuning is no longer a luxury — it is accessible to any organization.',
    image: '/images/logo/whitepaper-foundations.png'
  }
]
