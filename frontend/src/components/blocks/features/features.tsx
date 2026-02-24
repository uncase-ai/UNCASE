import {
  ArrowDownLeftIcon,
  ArrowUpRightIcon,
  BriefcaseBusinessIcon,
  GraduationCapIcon,
  PaintbrushIcon,
  PlusIcon,
  ThumbsUpIcon,
  UserIcon,
  UsersRoundIcon,
  ZapIcon
} from 'lucide-react'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Marquee } from '@/components/ui/marquee'
import { MotionPreset } from '@/components/ui/motion-preset'
import { Magnetic } from '@/components/ui/magnet-effect'

import { cn } from '@/lib/utils'

import StatCard from '@/components/blocks/features/stat-card'
import GoalAndTargetCard from '@/components/blocks/features/goal-and-target-card'
import SalesGrowthCard from '@/components/blocks/features/sales-growth-card'
import TargetVisibilityRippleBg from '@/components/blocks/features/target-visibility-ripple-bg'
import RegularUpdatesCard from '@/components/blocks/features/regular-updates-card'

const visitorData = [
  {
    product: 'ROUGE-L',
    percentage: 65,
    amount: 0.65,
    trend: 'up',
    heightClass: 'h-[65%]',
    color: 'bg-primary'
  },
  {
    product: 'Factual',
    percentage: 90,
    amount: 0.90,
    trend: 'up',
    heightClass: 'h-[90%]',
    color: 'bg-secondary'
  },
  {
    product: 'Privacy',
    percentage: 100,
    amount: 0.00,
    trend: 'up',
    heightClass: 'h-[100%]',
    color: 'bg-primary/60'
  }
]

const Features = () => {
  return (
    <section id='features' className='py-8 sm:py-16 lg:py-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
          className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'
        >
          <p className='text-primary text-sm font-medium uppercase'>Architecture</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>5-Layer Pipeline. Zero Real Data. Full Control.</h2>

          <p className='text-muted-foreground text-xl'>
            From expert knowledge to production-ready LoRA adapters — each layer operates independently,
            every step is auditable, and no real data ever touches the pipeline.
          </p>
        </MotionPreset>

        <div className='grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3'>
          {/* Column 1 */}
          <div className='flex flex-col gap-6'>
            {/* Product Reach Card */}
            <MotionPreset fade slide={{ direction: 'down', offset: 35 }} transition={{ duration: 0.5 }}>
              <Card className='gap-26.5 shadow-none'>
                <div className='flex flex-col items-center gap-8 px-4.5'>
                  <MotionPreset
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={0.15}
                    transition={{ duration: 0.5 }}
                  >
                    <StatCard
                      avatarIcon={<UsersRoundIcon className='size-4' />}
                      title='Quality Score'
                      statNumber='0.92'
                      percentage={12}
                    />
                  </MotionPreset>

                  <MotionPreset
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={0.3}
                    transition={{ duration: 0.5 }}
                    className='relative flex w-full rounded-xl border px-4 py-6'
                  >
                    {visitorData.map((item, index) => (
                      <div
                        key={index}
                        className={cn(
                          'flex grow flex-col gap-2.5 border-dashed px-3 py-2',
                          index < visitorData.length - 1 && 'border-r'
                        )}
                      >
                        <span className='text-muted-foreground text-sm'>{item.product}</span>

                        <div className='text-2xl font-medium'>{item.percentage}%</div>
                        <div className='flex min-h-25 flex-1 items-end'>
                          <div className={cn('bg-primary grow rounded-xl', item.heightClass, item.color)}></div>
                        </div>
                        <div className='flex items-center justify-between gap-2'>
                          <span className='text-muted-foreground text-sm'>{item.amount}</span>
                          {item.trend === 'up' ? (
                            <ArrowUpRightIcon className='size-4' />
                          ) : (
                            <ArrowDownLeftIcon className='size-4' />
                          )}
                        </div>
                      </div>
                    ))}
                    <Magnetic
                      range={130}
                      strength={0.25}
                      className='absolute -bottom-14 left-1/2 w-71.5 -translate-x-1/2'
                    >
                      <MotionPreset
                        fade
                        zoom
                        delay={0.75}
                        transition={{ duration: 0.5 }}
                        className='bg-card flex items-center gap-2 rounded-xl border p-4 shadow-lg'
                      >
                        <Avatar className='size-9.5 rounded-full shadow-md'>
                          <AvatarFallback className='bg-primary/10 text-primary shrink-0 rounded-sm'>
                            <ThumbsUpIcon className='size-4.5' />
                          </AvatarFallback>
                        </Avatar>
                        <p className='text-muted-foreground text-xs'>
                          Quality metrics improved by <span className='text-card-foreground'>32%</span> with seed
                          optimization — zero PII detected across 40K synthetic conversations
                        </p>
                      </MotionPreset>
                    </Magnetic>
                  </MotionPreset>
                </div>

                <CardContent className='flex flex-col gap-4'>
                  <MotionPreset
                    component='h3'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={0.45}
                    transition={{ duration: 0.5 }}
                    className='text-2xl font-semibold'
                  >
                    Layer 0 — Seed Engine
                  </MotionPreset>
                  <MotionPreset
                    component='p'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={0.6}
                    transition={{ duration: 0.5 }}
                    className='text-muted-foreground'
                  >
                    Convert expert conversations into abstract seed structures — capturing reasoning patterns without
                    any sensitive data.
                  </MotionPreset>
                </CardContent>
              </Card>
            </MotionPreset>

            {/* Targeted Visibility Card */}
            <MotionPreset
              fade
              slide={{ direction: 'down', offset: 35 }}
              delay={0.9}
              transition={{ duration: 0.5 }}
              className='h-full'
            >
              <Card className='h-full justify-between gap-0 pt-0 shadow-none'>
                <MotionPreset
                  fade
                  slide={{ direction: 'down', offset: 35 }}
                  delay={1.05}
                  transition={{ duration: 0.5 }}
                  className='relative mx-auto flex h-fit w-fit justify-center'
                >
                  <TargetVisibilityRippleBg className='text-border pointer-events-none size-45 select-none' />

                  <div className='absolute top-1/2 -translate-y-1/2'>
                    <Avatar className='size-16 rounded-full border shadow-lg'>
                      <AvatarFallback className='bg-background text-primary shrink-0 rounded-sm'>
                        <UserIcon className='size-8 stroke-1' />
                      </AvatarFallback>
                    </Avatar>
                    <Badge className='absolute top-0 right-0 size-5 rounded-full px-1'>
                      <PlusIcon className='size-2.5' />
                    </Badge>
                  </div>

                  <MotionPreset
                    fade
                    className='absolute top-8 -left-10 -rotate-5'
                    motionProps={{
                      animate: {
                        y: [0, -10, 0],
                        opacity: 1
                      },
                      transition: {
                        y: {
                          duration: 2,
                          repeat: Infinity,
                          ease: 'easeOut'
                        },
                        opacity: {
                          duration: 0.5,
                          delay: 1.2
                        }
                      }
                    }}
                  >
                    <Badge className='bg-background text-foreground border-border gap-2.5 px-3 py-1.5 transition-shadow duration-200 hover:shadow-sm'>
                      <ZapIcon className='size-3.5' />
                      Healthcare
                    </Badge>
                  </MotionPreset>

                  <MotionPreset
                    fade
                    className='absolute bottom-10 -left-15 rotate-5'
                    motionProps={{
                      animate: {
                        y: [0, -9, 0],
                        opacity: 1
                      },
                      transition: {
                        y: {
                          duration: 1.9,
                          repeat: Infinity,
                          ease: 'easeOut'
                        },
                        opacity: {
                          duration: 0.5,
                          delay: 1.35
                        }
                      }
                    }}
                  >
                    <Badge className='bg-background text-foreground border-border gap-2.5 px-3 py-1.5 transition-shadow duration-200 hover:shadow-sm'>
                      <PaintbrushIcon className='size-3.5' />
                      Finance
                    </Badge>
                  </MotionPreset>

                  <MotionPreset
                    fade
                    className='absolute top-8 -right-15 -rotate-10 sm:-right-17'
                    motionProps={{
                      animate: {
                        y: [0, -10, 0],
                        opacity: 1
                      },
                      transition: {
                        y: {
                          duration: 2.1,
                          repeat: Infinity,
                          ease: 'easeOut'
                        },
                        opacity: {
                          duration: 0.5,
                          delay: 1.5
                        }
                      }
                    }}
                  >
                    <Badge className='bg-background text-foreground border-border gap-2.5 px-3 py-1.5 transition-shadow duration-200 hover:shadow-sm'>
                      <BriefcaseBusinessIcon className='size-3.5' />
                      Legal
                    </Badge>
                  </MotionPreset>

                  <MotionPreset
                    fade
                    className='absolute -right-10 bottom-10 rotate-10'
                    motionProps={{
                      animate: {
                        y: [0, -8, 0],
                        opacity: 1
                      },
                      transition: {
                        y: {
                          duration: 1.8,
                          repeat: Infinity,
                          ease: 'easeOut'
                        },
                        opacity: {
                          duration: 0.5,
                          delay: 1.65
                        }
                      }
                    }}
                  >
                    <Badge className='bg-background text-foreground border-border gap-2.5 px-3 py-1.5 transition-shadow duration-200 hover:shadow-sm'>
                      <GraduationCapIcon className='size-3.5' />
                      Education
                    </Badge>
                  </MotionPreset>
                </MotionPreset>

                <CardContent className='flex flex-col gap-4'>
                  <MotionPreset
                    component='h3'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={1.8}
                    inView={false}
                    transition={{ duration: 0.5 }}
                    className='text-2xl font-semibold'
                  >
                    Domain-Agnostic Design
                  </MotionPreset>

                  <MotionPreset
                    component='p'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={1.95}
                    inView={false}
                    transition={{ duration: 0.5 }}
                    className='text-muted-foreground'
                  >
                    The same core pipeline works across healthcare, finance, legal, education, and manufacturing — one framework, any industry.
                  </MotionPreset>
                </CardContent>
              </Card>
            </MotionPreset>
          </div>

          {/* Column 2 */}
          <div className='flex h-full flex-col gap-6'>
            {/* Goals & Targets Card */}
            <MotionPreset fade slide={{ direction: 'down', offset: 35 }} transition={{ duration: 0.5 }}>
              <GoalAndTargetCard />
            </MotionPreset>

            {/* Sales & Growth Card */}
            <MotionPreset
              fade
              slide={{ direction: 'down', offset: 35 }}
              delay={0.6}
              transition={{ duration: 0.5 }}
              className='grow'
            >
              <SalesGrowthCard />
            </MotionPreset>
          </div>

          {/* Column 3 */}
          <div className='flex flex-col gap-6 md:max-xl:col-span-2'>
            {/* Regular Updates Card */}
            <MotionPreset fade slide={{ direction: 'down', offset: 35 }} transition={{ duration: 0.5 }}>
              <RegularUpdatesCard />
            </MotionPreset>

            {/* Customer Payments Card */}
            <MotionPreset
              fade
              slide={{ direction: 'down', offset: 35 }}
              delay={0.6}
              transition={{ duration: 0.5 }}
              className='flex-1'
            >
              <Card className='h-full justify-between shadow-none'>
                <MotionPreset
                  fade
                  slide={{ direction: 'down', offset: 35 }}
                  delay={0.75}
                  transition={{ duration: 0.5 }}
                  className='flex flex-col gap-1'
                >
                  <Marquee pauseOnHover reverse duration={30} gap={0.5} className='px-2 py-1.5'>
                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 shrink-0'>
                        Certified
                      </Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_fin_001</span>
                        <span className='text-muted-foreground text-xs font-light'>09:15</span>
                      </div>
                    </div>

                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge className='bg-primary/10 text-primary shrink-0'>Generated</Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_tri_012</span>
                        <span className='text-muted-foreground text-xs font-light'>11:45</span>
                      </div>
                    </div>

                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge variant='outline' className='shrink-0'>Validated</Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_due_007</span>
                        <span className='text-muted-foreground text-xs font-light'>14:30</span>
                      </div>
                    </div>
                  </Marquee>

                  <Marquee pauseOnHover duration={30} gap={0.5} className='px-2 py-1.5'>
                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 shrink-0'>
                        Certified
                      </Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_edu_003</span>
                        <span className='text-muted-foreground text-xs font-light'>19:15</span>
                      </div>
                    </div>

                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge className='bg-primary/10 text-primary shrink-0'>Generated</Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_mfg_018</span>
                        <span className='text-muted-foreground text-xs font-light'>18:30</span>
                      </div>
                    </div>

                    <div className='flex w-58 items-center gap-3 rounded-xl border py-1.5 pr-3 pl-2 hover:shadow-md'>
                      <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 shrink-0'>
                        Certified
                      </Badge>
                      <div className='flex flex-1 flex-col items-start gap-0.5'>
                        <span className='text-sm'>seed_adv_009</span>
                        <span className='text-muted-foreground text-xs font-light'>09:15</span>
                      </div>
                    </div>
                  </Marquee>
                </MotionPreset>

                <CardContent className='flex flex-col gap-4'>
                  <MotionPreset
                    component='h3'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={0.9}
                    inView={false}
                    transition={{ duration: 0.5 }}
                    className='text-2xl font-semibold'
                  >
                    Regulatory Compliance
                  </MotionPreset>

                  <MotionPreset
                    component='p'
                    fade
                    slide={{ direction: 'down', offset: 35 }}
                    delay={1.05}
                    inView={false}
                    transition={{ duration: 0.5 }}
                    className='text-muted-foreground'
                  >
                    GDPR, HIPAA, LFPDPPP, AI Act, CCPA — UNCASE is designed to comply with all major privacy
                    regulations simultaneously.
                  </MotionPreset>
                </CardContent>
              </Card>
            </MotionPreset>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Features
