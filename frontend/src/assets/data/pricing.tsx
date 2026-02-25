import { SproutIcon, FlowerIcon, Flower2Icon } from 'lucide-react'

import { type Plans } from '@/components/blocks/pricing/pricing'

export const plans: Plans = [
  {
    icon: <SproutIcon />,
    title: 'Community',
    description: 'Open source — free forever for everyone.',
    price: {
      yearly: 0,
      monthly: 0
    },
    period: ' free',
    buttonText: 'Get Started',
    features: [
      'Full 5-layer SCSF pipeline',
      '52 REST API endpoints',
      'LLM Gateway with privacy interception',
      'WhatsApp & webhook connectors',
      'All 6 industry namespaces',
      '10+ chat format exports',
      'Quality evaluation (6 metrics)',
      'E2B cloud sandboxes (BYOK)',
      'Instant demo containers',
      'Community support via GitHub'
    ]
  },
  {
    icon: <FlowerIcon />,
    title: 'Enterprise',
    description: 'For organizations in regulated industries.',
    price: {
      yearly: 0,
      monthly: 0
    },
    period: ' contact us',
    buttonText: 'Contact Sales',
    features: [
      'Everything in Community',
      'Dedicated seed engineering workshops',
      'Custom domain namespace setup',
      'Compliance audit documentation',
      'Custom connector development',
      'Opik evaluation sandboxes'
    ],
    extraFeatures: ['Priority support & SLA', 'On-premise deployment', 'Custom LLM provider integration', 'Managed sandbox infrastructure'],
    isPopular: true
  },
  {
    icon: <Flower2Icon />,
    title: 'Research',
    description: 'For academic and research institutions.',
    price: {
      yearly: 0,
      monthly: 0
    },
    period: ' free',
    buttonText: 'Apply for Access',
    features: [
      'Everything in Community',
      'Early access to new features',
      'Research collaboration program',
      'Co-authorship opportunities',
      'Dedicated research support'
    ]
  }
]
