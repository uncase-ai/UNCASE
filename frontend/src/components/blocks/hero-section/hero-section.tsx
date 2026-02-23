'use client'

import { useRef, useState, useEffect } from 'react'

import { ArrowUpRightIcon, CircleCheckIcon, LoaderIcon } from 'lucide-react'
import { useScroll } from 'motion/react'

import Link from 'next/link'

import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { BackgroundRippleEffect } from '@/components/ui/background-ripple-effect'
import { MotionPreset } from '@/components/ui/motion-preset'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

import TextFlip from '@/components/blocks/hero-section/text-flip'

import { cn } from '@/lib/utils'

import FlowLogo from '@/assets/svg/flow-logo'

const HeroSection = () => {
  const [scrollProgress, setScrollProgress] = useState(0)

  const containerRef = useRef<HTMLDivElement>(null)

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start']
  })

  useEffect(() => {
    return scrollYProgress.on('change', latest => {
      setScrollProgress(latest * 100)
    })
  }, [scrollYProgress])

  return (
    <section id='home' className='relative px-4 py-8 max-sm:pb-42 sm:px-6 sm:py-16 lg:px-8 lg:py-24'>
      <BackgroundRippleEffect />
      <div className='pointer-events-none absolute inset-x-0 top-0 z-5 h-128 bg-[radial-gradient(transparent_20%,var(--background)_90%)]' />
      <div className='space-y-12 sm:space-y-16 lg:space-y-24'>
        <div className='flex flex-col items-center gap-4'>
          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            className='z-10'
          >
            <Badge variant='outline' className='bg-background text-sm font-normal'>
              Open Source Framework — Privacy-First Synthetic Data
            </Badge>
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.2}
            component='h1'
            className='z-10 text-center text-3xl font-semibold md:text-4xl lg:text-5xl lg:leading-[1.29167]'
          >
            Fine-tune AI for <TextFlip />
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.4}
            component='p'
            className='text-muted-foreground z-10 max-w-156 text-center text-xl'
          >
            Generate high-quality synthetic conversational data for LoRA fine-tuning — without exposing a single real
            data point. Privacy by design, domain-agnostic, open source.
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.6}
            className='z-10'
          >
            <PrimaryFlowButton size='lg' asChild>
              <Link href='https://github.com/marianomoralesr/UNCASE'>
                View on GitHub
                <ArrowUpRightIcon />
              </Link>
            </PrimaryFlowButton>
          </MotionPreset>
        </div>

        <MotionPreset
          ref={containerRef}
          fade
          slide={{ direction: 'down' }}
          transition={{ duration: 0.5 }}
          inView={false}
          delay={0.8}
          className='relative z-10 mb-0 flex min-h-full flex-col items-center justify-start'
        >
          <div className='bg-background aspect-512/494 w-full max-w-5xl overflow-hidden rounded-xl border p-[1.318%]'>
            <div className='flex h-full w-full overflow-hidden rounded-lg border'>
              {/* Dashboard Sidebar */}
              {scrollProgress >= 10 ? (
                <div className='w-1/5'>
                  <img src='/images/hero-section/sidebar.webp' alt='Dashboard sidebar' className='dark:hidden' />
                  <img
                    src='/images/hero-section/sidebar-dark.webp'
                    alt='Dashboard sidebar'
                    className='hidden dark:inline-block'
                  />
                </div>
              ) : (
                <div className='bg-sidebar flex w-1/5 flex-col gap-[3%] border-r p-[1.215%]'>
                  <div className='flex h-[2.8%] shrink-0 items-center space-x-[2.32%]'>
                    <Skeleton className='bg-foreground/6 aspect-square h-[92.35%] rounded-full' />
                    <div className='flex h-full flex-1 flex-col justify-between'>
                      <Skeleton className='bg-foreground/6 h-[53.85%] w-2/5' />
                      <Skeleton className='bg-foreground/6 h-[33%] w-3/5' />
                    </div>
                  </div>
                  <div className='flex h-[1.508%] items-center space-x-[2.32%]'>
                    <Skeleton className='bg-foreground/6 aspect-square h-full' />
                    <Skeleton className='bg-foreground/6 h-[85.8%] w-[32%]' />
                    <Skeleton className='bg-foreground/6 ml-auto aspect-square h-full' />
                  </div>
                  <div className='h-[26.697%] space-y-[9.275%]'>
                    <Skeleton className='bg-foreground/6 h-[3.23%] w-[30%]' />
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-3/5' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[48%]' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[61%]' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[63%]' />
                      <Skeleton className='bg-foreground/6 ml-auto aspect-square h-full' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[59%]' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[58%]' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[57%]' />
                    </div>
                    <div className='flex h-[5.65%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[30%]' />
                    </div>
                  </div>
                  <div className='h-[17.009%] space-y-[9.275%]'>
                    <Skeleton className='bg-foreground/6 h-[5.07%] w-1/2' />
                    <div className='flex h-[8.87%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-3/5' />
                    </div>
                    <div className='flex h-[8.87%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[72%]' />
                    </div>
                    <div className='flex h-[8.87%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[42%]' />
                    </div>
                    <div className='flex h-[8.87%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[65%]' />
                    </div>
                    <div className='flex h-[8.87%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] w-[52%]' />
                    </div>
                  </div>
                </div>
              )}

              <div className='flex w-4/5 flex-col'>
                {/* Dashboard Header */}
                {scrollProgress >= 10 ? (
                  <div>
                    <img src='/images/hero-section/header.webp' alt='Header' className='dark:hidden' />
                    <img
                      src='/images/hero-section/header-dark.webp'
                      alt='Header'
                      className='hidden dark:inline-block'
                    />
                  </div>
                ) : (
                  <div className='flex h-[3.736%] shrink-0 items-center justify-between space-x-4 border-b px-[2%]'>
                    <div className='flex h-[39.8%] w-[17.5%] items-center space-x-[2.32%]'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 h-[71.5%] flex-1' />
                    </div>
                    <div className='flex h-1/2 w-[6%] justify-between'>
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                      <Skeleton className='bg-foreground/6 aspect-square h-full' />
                    </div>
                  </div>
                )}

                {/* Dashboard Widgets */}
                <div className='grid grid-cols-3 gap-[1.266%] p-[1.266%]'>
                  {/* Widget Card 1 */}
                  {scrollProgress >= 10 ? (
                    <MotionPreset
                      zoom={{ initialScale: 0.95 }}
                      transition={{ duration: 0.5 }}
                      inView={false}
                      className={cn('rounded-lg transition-all ease-out', {
                        'shadow-xl': scrollProgress >= 10 && scrollProgress < 37
                      })}
                    >
                      <img src='/images/hero-section/stats-01.webp' alt='Stats 01' className='dark:hidden' />
                      <img
                        src='/images/hero-section/stats-01-dark.webp'
                        alt='Stats 01'
                        className='hidden dark:inline-block'
                      />
                    </MotionPreset>
                  ) : (
                    <Skeleton className='bg-foreground/6 aspect-250/107' />
                  )}

                  {/* Widget Card 2 */}
                  {scrollProgress >= 10 ? (
                    <MotionPreset
                      zoom={{ initialScale: 0.95 }}
                      transition={{ duration: 0.5 }}
                      inView={false}
                      className={cn('rounded-lg transition-all ease-out', {
                        'shadow-xl': scrollProgress >= 10 && scrollProgress < 37
                      })}
                    >
                      <img src='/images/hero-section/stats-02.webp' alt='Stats 02' className='dark:hidden' />
                      <img
                        src='/images/hero-section/stats-02-dark.webp'
                        alt='Stats 02'
                        className='hidden dark:inline-block'
                      />
                    </MotionPreset>
                  ) : (
                    <Skeleton className='bg-foreground/6 aspect-250/107' />
                  )}

                  {/* Widget Card 3 */}
                  {scrollProgress >= 10 ? (
                    <MotionPreset
                      zoom={{ initialScale: 0.95 }}
                      transition={{ duration: 0.5 }}
                      inView={false}
                      className={cn('rounded-lg transition-all ease-out', {
                        'shadow-xl': scrollProgress >= 10 && scrollProgress < 37
                      })}
                    >
                      <img src='/images/hero-section/stats-03.webp' alt='Stats 03' className='dark:hidden' />
                      <img
                        src='/images/hero-section/stats-03-dark.webp'
                        alt='Stats 03'
                        className='hidden dark:inline-block'
                      />
                    </MotionPreset>
                  ) : (
                    <Skeleton className='bg-foreground/6 aspect-250/107' />
                  )}
                </div>

                {/* Dashboard Content */}
                <div className='grid grid-cols-3 gap-[1.266%] p-[1.266%] pt-0'>
                  <div className='flex flex-col justify-between'>
                    {scrollProgress >= 37 ? (
                      <MotionPreset
                        zoom={{ initialScale: 0.95 }}
                        transition={{ duration: 0.5 }}
                        inView={false}
                        className={cn('rounded-lg transition-all ease-out', {
                          'shadow-xl': scrollProgress >= 37 && scrollProgress < 47
                        })}
                      >
                        <img src='/images/hero-section/product-card.webp' alt='Product Card' className='dark:hidden' />
                        <img
                          src='/images/hero-section/product-card-dark.webp'
                          alt='Product Card'
                          className='hidden dark:inline-block'
                        />
                      </MotionPreset>
                    ) : (
                      <Skeleton className='bg-foreground/6 aspect-250/181' />
                    )}
                    {scrollProgress >= 37 ? (
                      <MotionPreset
                        zoom={{ initialScale: 0.95 }}
                        transition={{ duration: 0.5 }}
                        inView={false}
                        className={cn('rounded-lg transition-all ease-out', {
                          'shadow-xl': scrollProgress >= 37 && scrollProgress < 47
                        })}
                      >
                        <img src='/images/hero-section/earning-card.webp' alt='Earning Card' className='dark:hidden' />
                        <img
                          src='/images/hero-section/earning-card-dark.webp'
                          alt='Earning Card'
                          className='hidden dark:inline-block'
                        />
                      </MotionPreset>
                    ) : (
                      <Skeleton className='bg-foreground/6 aspect-125/121' />
                    )}
                  </div>
                  {scrollProgress >= 37 ? (
                    <MotionPreset
                      zoom={{ initialScale: 0.95 }}
                      transition={{ duration: 0.5 }}
                      inView={false}
                      className={cn('col-span-2 rounded-lg transition-all ease-out', {
                        'shadow-xl': scrollProgress >= 37 && scrollProgress < 47
                      })}
                    >
                      <img src='/images/hero-section/sales-card.webp' alt='Sales Card' className='dark:hidden' />
                      <img
                        src='/images/hero-section/sales-card-dark.webp'
                        alt='Sales Card'
                        className='hidden dark:inline-block'
                      />
                    </MotionPreset>
                  ) : (
                    <Skeleton className='bg-foreground/6 col-span-2 aspect-170/143' />
                  )}
                </div>

                {/* Dashboard Table */}
                <div className='p-[1.266%] pt-0'>
                  {scrollProgress >= 47 ? (
                    <MotionPreset
                      zoom={{ initialScale: 0.95 }}
                      transition={{ duration: 0.5 }}
                      inView={false}
                      className={cn('rounded-lg transition-all ease-out', {
                        'shadow-xl': scrollProgress >= 47 && scrollProgress < 70
                      })}
                    >
                      <img src='/images/hero-section/table.webp' alt='Table' className='dark:hidden' />
                      <img
                        src='/images/hero-section/table-dark.webp'
                        alt='Table'
                        className='hidden dark:inline-block'
                      />
                    </MotionPreset>
                  ) : (
                    <Skeleton className='bg-foreground/6 col-span-2 aspect-385/156' />
                  )}
                </div>

                {/* Dashboard Footer */}
                {scrollProgress >= 47 ? (
                  <div>
                    <img src='/images/hero-section/footer.webp' alt='Dashboard Footer' className='dark:hidden' />
                    <img
                      src='/images/hero-section/footer-dark.webp'
                      alt='Dashboard Footer Dark'
                      className='hidden dark:inline-block'
                    />
                  </div>
                ) : (
                  <div className='px-[1.266%]'>
                    <Skeleton className='bg-foreground/6 col-span-2 aspect-790/29' />
                  </div>
                )}
              </div>
            </div>
          </div>
        </MotionPreset>

        <MotionPreset
          fade
          slide={{ direction: 'down' }}
          transition={{ duration: 0.5 }}
          inView={false}
          delay={0.8}
          className='sticky bottom-10 z-15 flex justify-center transition-all duration-500 ease-in-out'
        >
          <div className='bg-primary text-primary-foreground mt-2 flex items-center gap-10 rounded-xl px-3.5 py-2 shadow-lg'>
            <div className='flex items-center gap-2 font-medium'>
              <FlowLogo className='size-8 rounded-full shadow-[0_20px_25px_-8px_var(--primary-foreground),0_8px_10px_-6px_var(--primary-foreground)]' />
              {scrollProgress < 20 && <span>Layer 0: Seed Engine ready</span>}
              {scrollProgress >= 20 && scrollProgress < 30 && <span>Layer 1: Parsing conversations</span>}
              {scrollProgress >= 30 && scrollProgress < 40 && <span>Layer 2: Quality validated</span>}
              {scrollProgress >= 40 && scrollProgress < 50 && <span>Layer 3: Generating synthetic data</span>}
              {scrollProgress >= 50 && <span>Layer 4: LoRA adapter trained</span>}
            </div>
            {scrollProgress >= 50 ? (
              <CircleCheckIcon className='size-4.5' />
            ) : (
              <LoaderIcon className='size-4.5 animate-spin' />
            )}
          </div>
        </MotionPreset>
      </div>
    </section>
  )
}

export default HeroSection
