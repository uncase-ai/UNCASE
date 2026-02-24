import { ChartLineIcon, Flower2Icon, FlowerIcon, RocketIcon, SproutIcon, UsersRoundIcon } from 'lucide-react'

import { type Plans, type PricingFeature } from '@/components/pricing/pricing-detail'

export const plans: Plans = [
  {
    icon: <SproutIcon />,
    title: 'Essential Plan',
    price: {
      yearly: 24,
      monthly: 29
    },
    period: '/month',
    buttonText: 'Basic Access',
    isPopular: false
  },
  {
    icon: <FlowerIcon />,
    title: 'Advanced Plan',
    price: {
      yearly: 39,
      monthly: 49
    },
    period: '/month',
    buttonText: 'Premium Access',
    isPopular: true
  },
  {
    icon: <Flower2Icon />,
    title: 'Pro Plan',
    price: {
      yearly: 80,
      monthly: 99
    },
    period: '/month',
    buttonText: 'Elite Access',
    isPopular: false
  }
]

export const pricingFeatures: PricingFeature[] = [
  {
    category: 'Core Analytics',
    icon: <ChartLineIcon />,
    features: [
      {
        name: 'Real-time dashboard',
        values: [true, true, true]
      },
      {
        name: 'Key metrics',
        values: [true, true, true]
      },
      {
        name: 'Custom date range & filters',
        values: [true, true, true]
      },
      {
        name: 'Product performance insights',
        values: [true, true, true]
      },
      {
        name: 'Growth trends',
        values: [false, true, true]
      },
      {
        name: 'Goal & target tracking',
        values: ['Basic', 'Advanced', 'Advanced']
      },
      {
        name: 'Data export (CSV / PDF)',
        values: ['CSV', 'CSV + PDF', 'CSV + PDF']
      }
    ]
  },
  {
    category: 'Growth Insights',
    icon: <RocketIcon />,
    features: [
      {
        name: 'User engagement insights',
        values: ['Basic', 'Advanced', 'Advanced']
      },
      {
        name: 'Conversion funnels',
        values: [false, true, true]
      },
      {
        name: 'Audience segmentation',
        values: [false, 'Limited', 'Unlimited']
      },
      {
        name: 'Performance comparisons',
        values: [false, false, true]
      },
      {
        name: 'Retention & cohort analysis',
        values: [false, true, true]
      }
    ]
  },
  {
    category: 'Team & Support',
    icon: <UsersRoundIcon />,
    features: [
      {
        name: 'Team members',
        values: ['1', 'Up to 3', '10+']
      },
      {
        name: 'Integrations & API',
        values: ['Limited', 'Standard', 'Unlimited']
      },
      {
        name: 'Support level',
        values: ['Email', 'Priority', 'Dedicated']
      }
    ]
  }
]
