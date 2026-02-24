'use client'

import { useEffect, useState } from 'react'

import {
  ArrowUpRightIcon,
  BookOpenIcon,
  BrainCircuitIcon,
  CpuIcon,
  GaugeIcon,
  PlayIcon,
  ScaleIcon,
  SparklesIcon
} from 'lucide-react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { activateDemo } from '@/lib/demo'

import { Badge } from '@/components/ui/badge'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BorderBeam } from '@/components/ui/border-beam'
import { PrimaryFlowButton, SecondaryFlowButton } from '@/components/ui/flow-button'
import { NumberTicker } from '@/components/ui/number-ticker'

import ComplianceProblem from '@/components/shadcn-studio/blocks/hero-section-40/compliance-problem'
import SeedEngineering from '@/components/shadcn-studio/blocks/hero-section-40/seed-engineering'
import SyntheticGeneration from '@/components/shadcn-studio/blocks/hero-section-40/synthetic-generation'
import QualityEvaluation from '@/components/shadcn-studio/blocks/hero-section-40/quality-evaluation'
import LoraTraining from '@/components/shadcn-studio/blocks/hero-section-40/lora-training'

const tabs = [
  {
    name: 'The Problem',
    value: 'compliance-problem',
    icon: ScaleIcon,
    content: <ComplianceProblem />
  },
  {
    name: 'Seed Engineering',
    value: 'seed-engineering',
    icon: BrainCircuitIcon,
    content: <SeedEngineering />
  },
  {
    name: 'Synthesis',
    value: 'synthetic-generation',
    icon: SparklesIcon,
    content: <SyntheticGeneration />
  },
  {
    name: 'Quality Gates',
    value: 'quality-evaluation',
    icon: GaugeIcon,
    content: <QualityEvaluation />
  },
  {
    name: 'LoRA Training',
    value: 'lora-training',
    icon: CpuIcon,
    content: <LoraTraining />
  }
]

const stats = [
  { value: 0, suffix: '%', label: 'PII in final data', decimalPlaces: 0 },
  { value: 6, suffix: '+', label: 'Industry domains', decimalPlaces: 0 },
  { value: 99.5, suffix: '%', label: 'Size reduction vs base model', decimalPlaces: 1 },
  { value: 10, suffix: '+', label: 'Chat formats', decimalPlaces: 0 }
]

const HeroSection40 = () => {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState(tabs[0]?.value || 'compliance-problem')

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTab(currentTab => {
        const currentIndex = tabs.findIndex(tab => tab.value === currentTab)
        const nextIndex = (currentIndex + 1) % tabs.length

        return tabs[nextIndex].value
      })
    }, 8000)

    return () => clearInterval(interval)
  }, [activeTab])

  return (
    <section id='home' className='relative flex flex-col overflow-hidden'>
      <div className='border-b px-4 sm:px-6 lg:px-8'>
        <div className='mx-auto flex max-w-7xl flex-col gap-6 border-x px-4 py-8 sm:px-6 sm:py-16 lg:px-8 lg:py-24'>
          <div className='flex flex-col items-center gap-4 text-center'>
            <Badge variant='outline' className='bg-muted relative gap-2.5 px-1.5 py-1'>
              <span className='bg-primary text-primary-foreground flex h-5.5 items-center rounded-full px-2 py-0.5'>
                Open Source
              </span>
              <span className='text-muted-foreground text-sm font-normal text-wrap'>
                Privacy-First Synthetic Data Framework
              </span>
              <BorderBeam colorFrom='var(--primary)' colorTo='var(--primary)' size={35} />
            </Badge>

            <h1 className='text-2xl font-semibold sm:text-3xl lg:text-5xl lg:leading-[1.29167]'>
              Fine-tune AI for regulated industries
              <br />
              without exposing a single real data point
            </h1>

            <p className='text-muted-foreground max-w-3xl text-xl'>
              UNCASE transforms expert knowledge into privacy-safe synthetic conversational data for LoRA fine-tuning.
              Zero PII. Full traceability. Domain-agnostic. Open source.
            </p>

            <div className='flex flex-wrap items-center justify-center gap-4 sm:gap-6 lg:gap-8'>
              <PrimaryFlowButton size='lg' asChild>
                <Link href='https://github.com/marianomoralesr/UNCASE'>
                  <ArrowUpRightIcon />
                  View on GitHub
                </Link>
              </PrimaryFlowButton>
              <SecondaryFlowButton size='lg' asChild>
                <Link href='/docs'>
                  <BookOpenIcon />
                  Read the Whitepaper
                </Link>
              </SecondaryFlowButton>
              <SecondaryFlowButton
                size='lg'
                onClick={async () => {
                  await activateDemo()
                  router.push('/dashboard')
                }}
              >
                <PlayIcon />
                Try Demo
              </SecondaryFlowButton>
            </div>
          </div>

          <div className='flex w-full items-center justify-center gap-6 max-sm:flex-col sm:gap-8'>
            {stats.map((stat, index) => (
              <div key={stat.label} className='flex items-center gap-6 sm:gap-8'>
                <div className='flex flex-col items-center'>
                  <span className='text-2xl font-semibold'>
                    <NumberTicker value={stat.value} decimalPlaces={stat.decimalPlaces} />
                    {stat.suffix}
                  </span>
                  <span className='text-muted-foreground text-sm'>{stat.label}</span>
                </div>
                {index < stats.length - 1 && (
                  <Separator orientation='vertical' className='data-[orientation=vertical]:h-8 max-sm:hidden' />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} data-horizontal className='w-full gap-0'>
        <div className='border-b px-4 sm:px-6 lg:px-8'>
          <div className='mx-auto max-w-7xl border-x'>
            <ScrollArea className='-m-px *:overflow-hidden!'>
              <TabsList className='h-fit w-full -space-x-px rounded-none bg-transparent p-0 group-data-[orientation=horizontal]/tabs:h-fit'>
                {tabs.map(({ icon: Icon, name, value }) => (
                  <TabsTrigger
                    key={value}
                    value={value}
                    className='border-border text-foreground focus-visible:outline-primary/20 data-[state=active]:border-primary/60! data-[state=active]:bg-muted! h-15 flex-1 cursor-pointer rounded-none px-4 py-2.5 text-base focus-visible:ring-0 focus-visible:outline-[3px] focus-visible:-outline-offset-4 data-[state=active]:z-1'
                  >
                    <Icon />
                    {name}
                  </TabsTrigger>
                ))}
              </TabsList>
              <ScrollBar orientation='horizontal' className='z-2' />
            </ScrollArea>
          </div>
        </div>

        <div className='px-4 sm:px-6 lg:px-8'>
          <div className='relative mx-auto h-151 max-w-7xl border-x'>
            {/* Background Dots */}
            <div className='pointer-events-none absolute inset-0 -z-2 bg-[radial-gradient(color-mix(in_oklab,var(--primary)10%,transparent)_2px,transparent_2px)] bg-size-[20px_20px] bg-fixed' />

            {/* Background Gradient Overlay */}
            <div className='bg-background pointer-events-none absolute inset-0 -z-1 flex items-center justify-center mask-[radial-gradient(ellipse_at_center,transparent_20%,black)]' />

            <ScrollArea className='h-full *:data-[slot=scroll-area-viewport]:h-full [&>[data-slot=scroll-area-viewport]>div]:h-full'>
              {tabs.map(tab => (
                <TabsContent
                  key={tab.value}
                  value={tab.value}
                  className='flex h-full items-center justify-center p-4 sm:p-6 lg:p-8'
                >
                  {tab.content}
                </TabsContent>
              ))}

              <ScrollBar orientation='horizontal' />
            </ScrollArea>
          </div>
        </div>
      </Tabs>
    </section>
  )
}

export default HeroSection40
