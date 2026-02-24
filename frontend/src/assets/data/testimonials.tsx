import type { TestimonialItem } from '@/components/blocks/testimonials/testimonial-card'

export const testimonials: TestimonialItem[] = [
  {
    name: 'Automotive Dealership',
    username: '@automotive.sales',
    avatar: '/images/avatar/avatar-7.webp',
    rating: 5,
    content: (
      <>
        6 sales points, 150 salespeople, thousands of WhatsApp conversations.{' '}
        <span className='bg-primary/5 text-primary'>80 seeds generated 40,000 synthetic conversations</span> — new
        salespeople onboard with a specialized AI assistant in 12 weeks.
      </>
    )
  },
  {
    name: 'Primary Care Network',
    username: '@medical.consultation',
    avatar: '/images/avatar/avatar-8.webp',
    rating: 5,
    content: (
      <>
        45 rural clinics with chronic physician shortage. Experienced doctors became seed engineers —{' '}
        <span className='bg-primary/5 text-primary'>synthetic triage protocols specific to local disease patterns</span>{' '}
        expanded nursing capacity without replacing physicians.
      </>
    )
  },
  {
    name: 'Corporate Law Firm',
    username: '@legal.advisory',
    avatar: '/images/avatar/avatar-9.webp',
    rating: 4.5,
    content: (
      <>
        20 years of privileged attorney-client conversations. Seeds capture{' '}
        <span className='bg-primary/5 text-primary'>analytical patterns without conversation details</span> — the model
        learns domain rigor while attorney-client privilege remains intact.
      </>
    )
  },
  {
    name: 'Wealth Management',
    username: '@finance.advisory',
    avatar: '/images/avatar/avatar-10.webp',
    rating: 5,
    content: (
      <>
        15 portfolio advisors, high-net-worth clients. Seeds abstract rebalancing and{' '}
        <span className='bg-primary/5 text-primary'>risk communication patterns during market volatility</span> —
        consistent, specialized client communication at scale.
      </>
    )
  },
  {
    name: 'Manufacturing Plant',
    username: '@industrial.support',
    avatar: '/images/avatar/avatar-2.webp',
    rating: 4.5,
    content: (
      <>
        Decades of fault diagnosis expertise from senior technicians.{' '}
        <span className='bg-primary/5 text-primary'>Predictive maintenance patterns encoded as seeds</span> — new
        engineers diagnose issues faster with AI-assisted troubleshooting.
      </>
    )
  },
  {
    name: 'E-learning Platform',
    username: '@education.tutoring',
    avatar: '/images/avatar/avatar-1.webp',
    rating: 5,
    content: (
      <>
        Adaptive evaluation patterns from master teachers.{' '}
        <span className='bg-primary/5 text-primary'>Synthetic tutoring sessions personalized to learning gaps</span> —
        AI tutors that understand pedagogical strategies, not just content.
      </>
    )
  }
]
