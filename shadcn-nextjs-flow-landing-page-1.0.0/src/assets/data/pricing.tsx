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
      'All 6 industry namespaces',
      'SeedSchema v1 specification',
      'Quality evaluation metrics',
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
      'Compliance audit documentation'
    ],
    extraFeatures: ['Priority support & SLA', 'On-premise deployment', 'Custom LLM integration'],
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
      'Early access to new layers',
      'Research collaboration program',
      'Co-authorship opportunities',
      'Dedicated research support'
    ]
  }
]
