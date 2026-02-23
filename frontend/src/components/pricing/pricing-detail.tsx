'use client'

import { useState, type ReactNode } from 'react'

import { CheckIcon, MinusIcon } from 'lucide-react'

import Link from 'next/link'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

import { cn } from '@/lib/utils'
import { NumberTicker } from '@/components/ui/number-ticker'
import { PrimaryFlowButton } from '@/components/ui/flow-button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'

export type FeatureValue = boolean | string

export type PricingFeature = {
  category: string
  icon: ReactNode
  features: {
    name: string
    values: FeatureValue[]
  }[]
}

export type Plan = {
  icon: ReactNode
  title: string
  price: {
    yearly: number
    monthly: number
  }
  period: string
  buttonText: string
  isPopular?: boolean
}

export type Plans = Plan[]

const PricingDetail = ({ plans, features }: { plans: Plans; features: PricingFeature[] }) => {
  const [billingPeriod, setBillingPeriod] = useState('monthly')

  const renderFeatureValue = (value: FeatureValue) => {
    if (typeof value === 'boolean') {
      return value ? (
        <div className='bg-primary/10 flex size-6.5 items-center justify-center rounded-full'>
          <CheckIcon className='text-primary size-4.5' />
        </div>
      ) : (
        <div className='bg-muted flex size-6.5 items-center justify-center rounded-full'>
          <MinusIcon className='text-muted-foreground size-4.5' />
        </div>
      )
    }

    return <div className='text-center font-medium'>{value}</div>
  }

  return (
    <section id='pricing-details' className='pt-8 sm:pt-16 lg:pt-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        {/* Section Header */}
        <div className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'>
          <p className='text-primary text-sm font-medium uppercase'>Pricing</p>

          <h1 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Pricing Details</h1>

          <p className='text-muted-foreground mb-9 text-xl'>
            A Comprehensive Breakdown Of Our Pricing Plans to Help You Make The Best Choice!
          </p>

          {/* Billing Toggle */}
          <div className='flex justify-center'>
            <Tabs
              value={billingPeriod === 'yearly' ? 'yearly' : 'monthly'}
              onValueChange={value => setBillingPeriod(value)}
              className='bg-muted rounded-lg p-0.75'
            >
              <TabsList className='h-auto bg-transparent p-0'>
                <TabsTrigger
                  value='monthly'
                  className='data-[state=active]:bg-background data-[state=active]:text-muted dark:data-[state=active]:text-muted dark:data-[state=active]:bg-background px-3 py-1 data-[state=active]:shadow-sm dark:data-[state=active]:border-transparent'
                  aria-hidden
                >
                  <span className='text-foreground text-base'>Monthly</span>
                </TabsTrigger>
                <TabsTrigger
                  value='yearly'
                  className='data-[state=active]:bg-background data-[state=active]:text-muted dark:data-[state=active]:text-muted dark:data-[state=active]:bg-background px-3 py-1 data-[state=active]:shadow-sm dark:data-[state=active]:border-transparent'
                  aria-hidden
                >
                  <span className='text-foreground text-base'>Yearly</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>

        {/* Pricing Table */}
        <ScrollArea className='w-full whitespace-nowrap'>
          <div className='min-w-255'>
            {/* Header Row */}
            <div className='mb-13 grid grid-cols-4 gap-6'>
              {/* Discount Card */}
              <div className='flex h-full w-full flex-col justify-center gap-6 rounded-lg border border-dashed p-6'>
                <p className='text-2xl font-semibold uppercase'>Flat</p>
                <div>
                  <span className='text-destructive text-6xl font-bold'>20% </span>
                  <span className='text-xl font-medium'>OFF</span>
                </div>
                <p className='text-muted-foreground text-lg'>
                  For first 250 users,
                  <br />
                  hurry up and get in now
                </p>
              </div>

              {/* Plan Cards */}
              {plans.map((plan, index) => (
                <Card
                  key={index}
                  className={cn('bg-muted relative border-0 shadow-none', {
                    'bg-background border shadow-lg': plan.isPopular
                  })}
                >
                  <CardContent className='flex flex-col gap-6'>
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
                      {plan.isPopular && <Badge variant='destructive'>Trending</Badge>}
                    </div>

                    <p className='text-xl font-semibold'>{plan.title}</p>

                    <div className='flex items-baseline'>
                      <span className='text-5xl font-bold'>
                        $
                        <NumberTicker
                          startValue={0}
                          value={billingPeriod === 'yearly' ? plan.price.yearly : plan.price.monthly}
                        />
                      </span>
                      <span className='text-muted-foreground ml-1 text-base'>{plan.period}</span>
                    </div>

                    <PrimaryFlowButton size='lg' className='w-full *:w-full' asChild>
                      <Link href='#'>{plan.buttonText}</Link>
                    </PrimaryFlowButton>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Features Table */}
            <div className='space-y-9'>
              {features.map((section, index) => (
                <div key={index} className='space-y-6'>
                  {/* Category Header */}
                  <div className='flex items-center gap-2'>
                    <Avatar className='bg-primary/10 size-8.5 rounded-md border'>
                      <AvatarFallback className='rounded-md shadow-md [&>svg]:size-4.5'>{section.icon}</AvatarFallback>
                    </Avatar>
                    <p className='text-xl font-medium'>{section.category}</p>
                  </div>

                  {/* Feature Rows */}
                  <div className='rounded-lg border'>
                    {section.features.map((feature, featureIndex) => (
                      <div
                        key={featureIndex}
                        className={cn('grid w-full grid-cols-4 border-b', {
                          'border-b-0': featureIndex === section.features.length - 1
                        })}
                      >
                        <p className='text-muted-foreground px-3 py-5 font-medium'>{feature.name}</p>
                        {feature.values.map((value, valueIndex) => (
                          <div key={valueIndex} className='flex items-center justify-center px-3 py-4'>
                            {renderFeatureValue(value)}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom CTA Buttons */}
            <div className='mt-2.5 grid grid-cols-4 gap-4'>
              <div></div>
              {plans.map((plan, index) => (
                <div key={index} className='px-3 py-4'>
                  <PrimaryFlowButton size='lg' className='w-full *:w-full' asChild>
                    <Link href='#'>{plan.buttonText}</Link>
                  </PrimaryFlowButton>
                </div>
              ))}
            </div>
          </div>

          <ScrollBar orientation='horizontal' className='pb-0' />
        </ScrollArea>
      </div>
    </section>
  )
}

export default PricingDetail
