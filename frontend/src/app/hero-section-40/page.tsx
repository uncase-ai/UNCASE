import {
  BrainCircuitIcon,
  GitCompareArrowsIcon,
  GitPullRequestDraftIcon,
  HeadphonesIcon,
  Trash2Icon,
  UserIcon
} from 'lucide-react'

import Header from '@/components/shadcn-studio/blocks/hero-section-40/header'
import HeroSection from '@/components/shadcn-studio/blocks/hero-section-40/hero-section-40'
import type { Navigation } from '@/components/shadcn-studio/blocks/hero-section-40/hero-navigation'

const navigationData: Navigation[] = [
  {
    title: 'Features',
    href: '#'
  },
  {
    title: 'Use cases',
    contentClassName: '!w-141 grid-cols-2',
    splitItems: true,
    items: [
      {
        type: 'section',
        title: 'Sales & Customer Operations',
        items: [
          {
            title: 'Pipeline Management',
            href: '#',
            description: 'Track movement, update statuses, and flag stalled deals.',
            icon: <GitPullRequestDraftIcon className='size-4' />
          },
          {
            title: 'Customer Onboarding',
            href: '#',
            description: 'Automate welcome emails, account setup, and key guidance.',
            icon: <UserIcon className='size-4' />
          },
          {
            title: 'Support Escalations',
            href: '#',
            description: 'Detect urgency and route issues to the right team faster.',
            icon: <HeadphonesIcon className='size-4' />
          }
        ]
      },
      {
        type: 'section',
        title: 'Internal Productivity Workflows',
        items: [
          {
            title: 'Knowledge Retrieval',
            href: '#',
            description: 'Ask AI and get instant answers from your tools/docs.',
            icon: <BrainCircuitIcon className='size-4' />
          },
          {
            title: 'Task Automation',
            href: '#',
            description: 'Convert messages into tasks and assign them automatically.',
            icon: <GitCompareArrowsIcon className='size-4' />
          },
          {
            title: 'Data Cleanup',
            href: '#',
            description: 'Auto-correct entries, remove duplicates, sync records.',
            icon: <Trash2Icon className='size-4' />
          }
        ]
      }
    ]
  },
  {
    title: 'Testimonials',
    href: '#'
  },
  {
    title: 'Pricing',
    href: '#'
  }
]

const HeroSectionPage = () => {
  return (
    <div className='flex flex-col'>
      {/* Header Section */}
      <Header navigationData={navigationData} />

      {/* Main Content */}
      <main className='flex flex-col'>
        <HeroSection />
      </main>
    </div>
  )
}

export default HeroSectionPage
