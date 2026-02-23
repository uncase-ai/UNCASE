import type { ReactNode } from 'react'

import {
  LayersIcon,
  ShieldCheckIcon,
  BrainCircuitIcon,
  DatabaseIcon,
  FileTextIcon,
  BookOpenIcon
} from 'lucide-react'

import Header from '@/components/layout/header'
import Footer from '@/components/layout/footer'
import type { Navigation } from '@/components/layout/header-navigation'

const navigationData: Navigation[] = [
  {
    title: 'Architecture',
    contentClassName: '!w-141 grid-cols-2',
    splitItems: true,
    items: [
      {
        type: 'section',
        title: 'Core Pipeline',
        items: [
          {
            title: '5-Layer Architecture',
            href: '/#features',
            description: 'From seed engineering to LoRA-ready adapters.',
            icon: <LayersIcon className='size-4' />
          },
          {
            title: 'Privacy by Design',
            href: '/#features',
            description: 'Zero real data transits through the pipeline.',
            icon: <ShieldCheckIcon className='size-4' />
          },
          {
            title: 'Synthetic Generation',
            href: '/#features',
            description: 'High-quality conversational data from abstract seeds.',
            icon: <BrainCircuitIcon className='size-4' />
          }
        ]
      },
      {
        type: 'section',
        title: 'Integration',
        items: [
          {
            title: 'Multi-format Parser',
            href: '/#features',
            description: 'WhatsApp, JSON, CRM, transcriptions, and more.',
            icon: <DatabaseIcon className='size-4' />
          },
          {
            title: 'LoRA Pipeline',
            href: '/#features',
            description: 'Automated fine-tuning with ShareGPT, Alpaca, ChatML.',
            icon: <FileTextIcon className='size-4' />
          },
          {
            title: 'Documentation',
            href: '/#faq',
            description: 'Whitepapers, guides, and technical specs.',
            icon: <BookOpenIcon className='size-4' />
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
    title: 'Use Cases',
    href: '/#testimonials'
  },
  {
    title: 'Open Source',
    href: '/#pricing'
  },
  {
    title: 'Docs',
    href: '/docs'
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
