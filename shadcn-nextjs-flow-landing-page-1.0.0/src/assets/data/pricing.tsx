import { Flower2Icon, FlowerIcon, SproutIcon } from 'lucide-react'

import { type Plans } from '@/components/blocks/pricing/pricing'

export const plans: Plans = [
  {
    icon: <SproutIcon />,
    title: 'Essential Plan',
    description: 'Perfect for solo founders and small teams',
    price: {
      yearly: 24,
      monthly: 29
    },
    period: '/month',
    buttonText: 'Basic Access',
    features: [
      '1 user seat',
      'Real-time product analytics',
      'Up to 1K tracked users',
      'Basic revenue insights',
      'Email support'
    ]
  },
  {
    icon: <FlowerIcon />,
    title: 'Advanced Plan',
    description: 'Build for small businesses.',
    price: {
      yearly: 39,
      monthly: 49
    },
    period: '/month',
    buttonText: 'Premium Access',
    features: [
      'Up to 10 user seats',
      'Advanced sales & engagement reports',
      'Up to 10K tracked users',
      'Smart growth insights'
    ],
    extraFeatures: ['API & integrations', 'Team collaboration tools', 'Secure data infrastructure'],
    isPopular: true
  },
  {
    icon: <Flower2Icon />,
    title: 'Pro Plan',
    description: 'Designed for growing teams and business.',
    price: {
      yearly: 80,
      monthly: 99
    },
    period: '/month',
    buttonText: 'Elite Access',
    features: [
      'Up to 25 user seats',
      'Advanced automation workflows',
      'Up to 50K tracked users',
      'Predictive growth insights',
      'Priority email & chat support'
    ]
  }
]
