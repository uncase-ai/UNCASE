import { ChartPieIcon, BotMessageSquareIcon, LayersIcon, ChartSplineIcon } from 'lucide-react'

import { type Features } from '@/components/blocks/benefits/benefits'

export const benefits: Features = [
  {
    icon: <ChartPieIcon />,
    title: 'Unified Sales Overview',
    description:
      'Monitor leads, purchases, and orders in real-time to stay updated on every key business metric. This ensures you have the latest insights to make informed decisions.',
    image: '/images/benefits/image-01.webp'
  },
  {
    icon: <BotMessageSquareIcon />,
    title: 'Automated Follow-Ups',
    description:
      'Let smart reminders handle repetitive tasks, allowing you to concentrate on closing more deals rather than managing them. This way, you can maximise your productivity and achieve better results.',
    image: '/images/benefits/image-02.webp'
  },
  {
    icon: <LayersIcon />,
    title: 'Clean & Simple Workflow',
    description:
      'Move deals effortlessly through stages with our intuitive pipeline system designed for clarity and control. This system ensures that you always have a clear view of your progress.',
    image: '/images/benefits/image-03.webp'
  },
  {
    icon: <ChartSplineIcon />,
    title: 'Instant Performance Insights',
    description:
      'Get accurate reports and analytics that help you understand growth patterns and make confident decisions. These insights empower you to strategies effectively for future success.',
    image: '/images/benefits/image-04.webp'
  }
]
