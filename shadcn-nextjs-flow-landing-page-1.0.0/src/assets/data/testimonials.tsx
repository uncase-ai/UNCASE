import type { TestimonialItem } from '@/components/blocks/testimonials/testimonial-card'

export const testimonials: TestimonialItem[] = [
  {
    name: 'Emily Watson',
    username: '@emilywatson',
    avatar: '/images/avatar/avatar-7.webp',
    rating: 4.5,
    content: (
      <>
        Finally, a dashboard that shows{' '}
        <span className='bg-primary/5 text-primary'>everything that matters-users, orders, and revenue</span> all in one
        clean view. It helps us make informed decisions much faster.
      </>
    )
  },
  {
    name: 'Alex Rivera',
    username: '@alexrivera',
    avatar: '/images/avatar/avatar-8.webp',
    rating: 5,
    content: (
      <>
        The interface is incredibly intuitive and the tools are very practical. We&apos;ve{' '}
        <span className='bg-primary/5 text-primary'>cut our deal cycle time almost in half</span> since making the
        switch. Adoption across the team was effortless.
      </>
    )
  },
  {
    name: 'Marcus Johnson',
    username: '@marcusjohnson',
    avatar: '/images/avatar/avatar-9.webp',
    rating: 4.5,
    content: (
      <>
        The seamless integrations streamlined my daily workflow significantly. I can manage emails, track clients, and
        schedule follow-ups <span className='bg-primary/5 text-primary'>without ever leaving the platform</span>.
      </>
    )
  },
  {
    name: 'Sarah Chen',
    username: '@sarahchen',
    avatar: '/images/avatar/avatar-10.webp',
    rating: 5,
    content: (
      <>
        From onboarding to daily usage, everything feels well thought out. The components are{' '}
        <span className='bg-primary/5 text-primary'>polished, consistent, and production-ready</span>. Shipping new
        features is noticeably faster.
      </>
    )
  },
  {
    name: 'Ncdai',
    username: '@ncdai',
    avatar: '/images/avatar/avatar-2.webp',
    rating: 4,
    content: (
      <>
        Clean design and sensible defaults make a huge difference. The{' '}
        <span className='bg-primary/5 text-primary'>documentation is clear and easy to follow</span>, which saved me
        hours during setup.
      </>
    )
  },
  {
    name: 'Lisa Thompson',
    username: '@lisathompson',
    avatar: '/images/avatar/avatar-1.webp',
    rating: 5,
    content: (
      <>
        I&apos;ve used many UI kits, but this one strikes the perfect balance. The{' '}
        <span className='bg-primary/5 text-primary'>customization options are incredibly flexible</span> without
        sacrificing design quality.
      </>
    )
  }
]
