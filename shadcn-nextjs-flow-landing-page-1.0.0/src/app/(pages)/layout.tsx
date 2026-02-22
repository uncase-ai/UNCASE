import type { ReactNode } from 'react'

import {
  LayoutDashboardIcon,
  TelescopeIcon,
  ChartScatterIcon,
  ChartPieIcon,
  GitPullRequestIcon,
  UsersIcon
} from 'lucide-react'

import Header from '@/components/layout/header'
import Footer from '@/components/layout/footer'
import type { Navigation } from '@/components/layout/header-navigation'

const navigationData: Navigation[] = [
  {
    title: 'Features',
    contentClassName: '!w-141 grid-cols-2',
    splitItems: true,
    items: [
      {
        type: 'section',
        title: 'Analytics & Insights',
        items: [
          {
            title: 'Unified Dashboard',
            href: '/#features',
            description: 'Get every key business metric in one place.',
            icon: <LayoutDashboardIcon className='size-4' />
          },
          {
            title: 'Competitor Tracking',
            href: '#',
            description: 'Benchmark performance and market trends.',
            icon: <TelescopeIcon className='size-4' />
          },
          {
            title: 'Sales Analytics',
            href: '#',
            description: 'Track revenue growth, conversions & profitability.',
            icon: <ChartScatterIcon className='size-4' />
          }
        ]
      },
      {
        type: 'section',
        title: 'Productivity & Optimization',
        items: [
          {
            title: 'Report & Export',
            href: '#',
            description: 'Share insights quickly with automated reporting.',
            icon: <ChartPieIcon className='size-4' />
          },
          {
            title: 'Workflow Scheduling',
            href: '#',
            description: 'Plan content & operational tasks seamlessly.',
            icon: <GitPullRequestIcon className='size-4' />
          },
          {
            title: 'User Management',
            href: '#',
            description: 'Manage roles and access with complete control.',
            icon: <UsersIcon className='size-4' />
          }
        ]
      }
    ]
  },
  {
    title: 'Benefits',
    href: '/#benefits'
  },
  {
    title: 'Testimonials',
    href: '/#testimonials'
  },
  {
    title: 'Pricing',
    href: '/pricing'
  },
  {
    title: 'Blog',
    href: '/blog'
  }
]

const PagesLayout = ({ children }: Readonly<{ children: ReactNode }>) => {
  return (
    <div className='flex flex-col bg-[repeating-linear-gradient(45deg,color-mix(in_oklab,var(--border)40%,transparent)0,color-mix(in_oklab,var(--border)40%,transparent)1px,transparent_0,transparent_50%)] bg-size-[12px_12px] bg-fixed'>
      <div className='mx-auto h-full w-full max-w-336 px-4 sm:px-6 lg:px-8'>
        <div className='bg-background h-full w-full max-w-7xl border-x'>
          {/* Header Section */}
          <Header navigationData={navigationData} />

          {/* Main Content */}
          <main className='flex flex-1 flex-col *:scroll-mt-16'>{children}</main>

          {/* Footer Section */}
          <Footer />
        </div>
      </div>
    </div>
  )
}

export default PagesLayout
