'use client'

import { useState, type ReactNode } from 'react'

import { CheckIcon, CircleIcon } from 'lucide-react'

import Link from 'next/link'

import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

import { cn } from '@/lib/utils'
import { NumberTicker } from '@/components/ui/number-ticker'
import { MotionPreset } from '@/components/ui/motion-preset'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

// import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'

export type Plans = {
  icon: ReactNode
  title: string
  description: string
  price: {
    yearly: number
    monthly: number
  }
  period: string
  buttonText: string
  features: string[]
  extraFeatures?: string[]
  isPopular?: boolean
}[]

const Pricing = ({ plans }: { plans: Plans }) => {
  const [billingPeriod] = useState('monthly')

  return (
    <section id='pricing' className='relative overflow-hidden py-8 sm:py-16 lg:py-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        {/* Section Header */}
        <MotionPreset
          className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
        >
          <p className='text-primary text-sm font-medium uppercase'>Open Source</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Free and Open Source</h2>

          <p className='text-muted-foreground text-base sm:text-xl'>
            UNCASE is open source at its core. Enterprise and research programs offer additional support.
          </p>

          <div className='mx-auto mb-9 w-fit rounded-lg border border-dashed px-2 py-0.5'>
            <p className='text-muted-foreground'>
              The core framework is <span className='text-primary font-semibold'>100% free</span> — forever
            </p>
          </div>
        </MotionPreset>

        <div className='grid grid-cols-1 gap-6 *:h-fit sm:grid-cols-2 lg:grid-cols-3'>
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={cn('w-full p-2 pb-4 shadow-none', {
                'bg-muted sm:max-lg:order-1 sm:max-lg:col-span-full': plan.isPopular
              })}
            >
              <CardContent
                className={cn('bg-muted flex flex-col gap-6 rounded-lg p-6', {
                  'bg-background relative overflow-hidden shadow-lg': plan.isPopular
                })}
              >
                <div className={cn({ 'flex items-start justify-between': plan.isPopular })}>
                  <Avatar className='size-12 rounded-md shadow-md'>
                    <AvatarFallback
                      className={cn('rounded-md shadow-md', {
                        [plan.isPopular ? 'bg-muted text-foreground' : 'bg-card text-foreground']: true
                      })}
                    >
                      {plan.icon}
                    </AvatarFallback>
                  </Avatar>
                  {plan.isPopular && (
                    <Badge variant='destructive' className='z-10'>
                      Trending
                    </Badge>
                  )}
                </div>
                <div className='flex-1 space-y-2.5'>
                  <h3 className='text-2xl font-semibold'>{plan.title}</h3>
                  <p>{plan.description}</p>
                </div>
                <p className='text-primary text-5xl font-bold'>
                  $
                  <NumberTicker
                    startValue={0}
                    value={billingPeriod === 'yearly' ? plan.price.yearly : plan.price.monthly}
                  />
                  <span className='text-muted-foreground ml-0.75 text-lg font-normal'>{plan.period}</span>
                </p>

                <PrimaryFlowButton size='lg' className='w-full *:w-full [&>a]:after:-inset-50' asChild>
                  <Link href='#'>{plan.buttonText}</Link>
                </PrimaryFlowButton>
              </CardContent>
              <div className='space-y-4'>
                <ul className='space-y-1.5 px-4'>
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className='flex items-center gap-2 py-1'>
                      <CheckIcon className='text-primary size-3.5 shrink-0' />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.extraFeatures && plan.extraFeatures.length > 0 && (
                  <>
                    <Separator className='-mx-2 w-auto!' />
                    <ul className='space-y-1.5 px-4'>
                      {plan.extraFeatures.map((feature, featureIndex) => (
                        <li key={featureIndex} className='flex items-center gap-2 py-1'>
                          <CircleIcon className='fill-primary text-primary size-2.5 shrink-0' />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Pricing
