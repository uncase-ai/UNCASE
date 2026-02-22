import { ShieldCheckIcon, BrainCircuitIcon, LayersIcon, ZapIcon } from 'lucide-react'

import { type Features } from '@/components/blocks/benefits/benefits'

export const benefits: Features = [
  {
    icon: <ShieldCheckIcon />,
    title: 'Privacy by Design',
    description:
      'No real patient, client, or user data ever transits through the pipeline. Seeds capture reasoning patterns and domain structure — not conversations. Compliant with GDPR, HIPAA, LFPDPPP, and AI Act from day one.',
    image: '/images/benefits/image-01.webp'
  },
  {
    icon: <BrainCircuitIcon />,
    title: 'Expert Knowledge, Preserved',
    description:
      'Transform decades of specialized expertise into abstract seed structures that train AI models. Your best professionals become seed engineers — their knowledge scales without exposing privileged information.',
    image: '/images/benefits/image-02.webp'
  },
  {
    icon: <LayersIcon />,
    title: 'Modular 5-Layer Pipeline',
    description:
      'Each layer delivers value independently. Start with seed engineering, add parsing, quality evaluation, synthetic generation, and LoRA training incrementally. No big-bang deployment needed.',
    image: '/images/benefits/image-03.webp'
  },
  {
    icon: <ZapIcon />,
    title: 'Radical Cost Efficiency',
    description:
      'LoRA adapters of 50–150 MB instead of 28 GB base models. Training in 2–8 hours on a single A100. Infrastructure cost: $15–$45 USD per specialized adapter. Fine-tuning is no longer a luxury.',
    image: '/images/benefits/image-04.webp'
  }
]
