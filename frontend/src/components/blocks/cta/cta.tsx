'use client'

import Link from 'next/link'
import { ArrowUpRightIcon, BookOpenIcon, SendIcon } from 'lucide-react'

import { cn } from '@/lib/utils'

import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { NumberTicker } from '@/components/ui/number-ticker'

import { PrimaryFlowButton, SecondaryFlowButton } from '@/components/ui/flow-button'
import { MotionPreset } from '@/components/ui/motion-preset'

import LogoVector from '@/assets/svg/logo-vector'
import DottedSheet from '@/assets/svg/dotted-sheet'

const stats = [
  { value: 0, suffix: '%', description: 'Zero PII tolerance', decimalPlaces: 0 },
  { value: 15, suffix: '-$45', description: 'USD per adapter', decimalPlaces: 0 },
  { value: 99.5, suffix: '%', description: 'vs 28GB base model', decimalPlaces: 1 },
  { value: 6, suffix: '+', description: 'Supported domains', decimalPlaces: 0 }
] as const

const CTASection = () => {
  return (
    <section id='cta' className='relative z-1 pt-16 pb-16 sm:pt-32 sm:pb-16 lg:pt-48 lg:pb-24'>
      <div className='bg-background mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        <Card className='dark:bg-muted bg-primary relative overflow-hidden rounded-3xl border-none pt-20 pb-32 text-center shadow-2xl max-sm:pt-10 max-sm:pb-15'>
          <CardContent className='px-6'>
            <MotionPreset
              fade
              blur
              slide={{ direction: 'down', offset: 50 }}
              delay={0.3}
              transition={{ duration: 0.5 }}
              className='flex flex-col items-center justify-center gap-4'
            >
              <h2 className='dark:text-foreground text-2xl font-semibold text-white md:text-3xl lg:text-4xl'>
                Build the Future of Privacy-First AI
              </h2>

              <p className='dark:text-muted-foreground w-full text-xl text-white/80 lg:max-w-2xl'>
                Join the UNCASE community. Contribute to the framework, extend domain namespaces, or deploy your own
                specialized LoRA adapters.
              </p>

              {/* Stats row */}
              <div className='mt-4 flex flex-wrap items-center justify-center gap-6 sm:gap-8 lg:gap-12'>
                {stats.map((stat, index) => (
                  <div
                    key={index}
                    className={cn(
                      'flex flex-col items-center gap-1',
                      index !== 0 && 'lg:border-l lg:border-white/20 lg:pl-12 dark:lg:border-muted-foreground/20'
                    )}
                  >
                    <span className='dark:text-foreground text-3xl font-bold text-white md:text-4xl'>
                      <NumberTicker value={stat.value} decimalPlaces={stat.decimalPlaces} />
                      {stat.suffix}
                    </span>
                    <span className='dark:text-muted-foreground text-sm text-white/80'>{stat.description}</span>
                  </div>
                ))}
              </div>

              {/* Dual CTA buttons */}
              <div className='mt-6 flex flex-wrap items-center justify-center gap-4'>
                <PrimaryFlowButton size='lg' asChild>
                  <Link href='https://github.com/marianomoralesr/UNCASE' target='_blank' rel='noopener noreferrer'>
                    View on GitHub
                    <ArrowUpRightIcon className='ml-2 size-4' />
                  </Link>
                </PrimaryFlowButton>
                <SecondaryFlowButton size='lg' asChild>
                  <Link href='#'>
                    Read the Whitepaper
                    <BookOpenIcon className='ml-2 size-4' />
                  </Link>
                </SecondaryFlowButton>
              </div>
            </MotionPreset>
            <MotionPreset
              className='absolute bottom-0 left-0 text-[#F4F4F5]/10'
              fade
              slide
              transition={{ duration: 0.5 }}
            >
              <LogoVector className='max-lg:hidden' />
            </MotionPreset>

            <MotionPreset
              className='absolute right-0 bottom-0 text-[#F4F4F5]/10'
              fade
              slide={{ direction: 'right' }}
              transition={{ duration: 0.5 }}
            >
              <LogoVector className='rotate-y-180 max-lg:hidden' />
            </MotionPreset>
          </CardContent>
        </Card>

        <MotionPreset fade blur zoom={{ initialScale: 0.95 }} delay={0.6} transition={{ duration: 0.4 }}>
          <form onSubmit={e => e.preventDefault()}>
            <div className='border-primary dark:border-primary/70 bg-background relative mx-auto -mt-9.25 flex size-fit w-full max-w-lg gap-2.5 rounded-xl border-2 p-2'>
              <Input
                type='email'
                name='cta-email'
                placeholder='Your email for updates'
                className='h-10 border-none shadow-none focus-visible:ring-transparent dark:bg-transparent'
                required
              />
              <PrimaryFlowButton size='lg' className='hidden shrink-0 sm:inline-flex'>
                Stay updated
              </PrimaryFlowButton>
              <PrimaryFlowButton size='icon-lg' className='hidden shrink-0 max-sm:inline-flex' type='submit'>
                <SendIcon />
              </PrimaryFlowButton>
            </div>
          </form>
        </MotionPreset>
      </div>

      <DottedSheet className='pointer-events-none absolute inset-x-0 -z-1 mx-auto w-full max-w-7xl px-4 max-sm:-top-1/2 sm:bottom-1/4 sm:px-6 lg:px-8' />
    </section>
  )
}

export default CTASection
