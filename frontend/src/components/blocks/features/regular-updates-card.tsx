'use client'

import { useEffect, useState } from 'react'

import { TrendingDownIcon, TrendingUpIcon, TriangleAlertIcon, UserPlusIcon, UsersIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { MotionPreset } from '@/components/ui/motion-preset'
import { NumberTicker } from '@/components/ui/number-ticker'

import RegularUpdatesRippleBg from '@/components/blocks/features/regular-updates-ripple-bg'

import Logo from '@/assets/svg/flow-logo'

export type NotificationCard = {
  id: string
  seedId: string
  domain: string
  percentageChange: number
  stats: {
    seeds: number
    domains: number
    passRate: number
  }
}

const notificationsList: NotificationCard[] = [
  {
    id: '1',
    seedId: 'seed_financiamiento_001',
    domain: 'automotive.sales',
    percentageChange: 12.5,
    stats: { seeds: 2432, domains: 6, passRate: 94 }
  },
  {
    id: '2',
    seedId: 'seed_triage_rural_012',
    domain: 'medical.consultation',
    percentageChange: 8.3,
    stats: { seeds: 1235, domains: 6, passRate: 91 }
  },
  {
    id: '3',
    seedId: 'seed_due_diligence_007',
    domain: 'legal.advisory',
    percentageChange: 15.1,
    stats: { seeds: 2696, domains: 6, passRate: 97 }
  }
]

const RegularUpdatesCard = () => {
  const [notifications, setNotifications] = useState<NotificationCard[]>(notificationsList)
  const [activeIndex, setActiveIndex] = useState<NotificationCard>(notificationsList[0])

  useEffect(() => {
    const interval = setInterval(() => {
      setNotifications(prevCards => {
        const newArray = [...prevCards]

        setActiveIndex(newArray[newArray.length - 1])
        newArray.unshift(newArray.pop()!)

        return newArray
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Card className='gap-12 shadow-none'>
      <MotionPreset
        fade
        slide={{ direction: 'down', offset: 35 }}
        delay={0.15}
        transition={{ duration: 0.5 }}
        className='relative flex h-full justify-center'
      >
        <div className='absolute inset-x-3.5 flex min-h-29 justify-center gap-4'>
          <div className='bg-card flex w-27 flex-col items-start gap-2.5 rounded-xl border p-3 shadow-lg'>
            <div className='grid size-9.5 place-content-center rounded-full border'>
              <UsersIcon className='size-5' />
            </div>
            <div className='space-y-1'>
              <p className='font-medium'>
                <NumberTicker value={activeIndex.stats.seeds} />
              </p>
              <p className='text-muted-foreground text-xs'>Seeds Processed</p>
            </div>
          </div>
          <div className='bg-card flex w-27 flex-col items-start gap-2.5 rounded-xl border p-3 shadow-lg'>
            <div className='grid size-9.5 place-content-center rounded-full border'>
              <UserPlusIcon className='size-5' />
            </div>
            <div className='space-y-1'>
              <p className='font-medium'>
                <NumberTicker value={activeIndex.stats.domains} />
              </p>
              <p className='text-muted-foreground text-xs'>Domains Active</p>
            </div>
          </div>
          <div className='bg-card flex w-27 flex-col items-start gap-2.5 rounded-xl border p-3 shadow-lg'>
            <div className='grid size-9.5 place-content-center rounded-full border'>
              <TriangleAlertIcon className='size-5' />
            </div>
            <div className='space-y-1'>
              <p className='font-medium'>
                <NumberTicker value={activeIndex.stats.passRate} />%
              </p>
              <p className='text-muted-foreground text-xs'>Quality Pass Rate</p>
            </div>
          </div>
        </div>
        <RegularUpdatesRippleBg className='text-border pointer-events-none size-118 select-none' />
        <Logo className='absolute top-1/2 size-30 -translate-y-1/2' />

        {notifications.map((notification, index) => (
          <motion.div
            key={notification.id}
            className='bg-card absolute bottom-0 left-1/2 flex h-20 w-72 -translate-x-1/2 items-center justify-between rounded-xl border p-4 shadow-xl md:w-75 xl:w-72'
            style={{
              transformOrigin: 'bottom center'
            }}
            animate={{
              bottom: (index - 2) * -8,
              scale: 1 - index * 0.1,
              opacity: 1 - index * 0.25,
              zIndex: notifications.length - index
            }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut'
            }}
          >
            <div className='flex flex-col gap-1'>
              <p className='text-xl font-semibold'>{notification.seedId}</p>
              <Badge className='bg-primary/10 [a&]:hover:bg-primary/5 focus-visible:ring-primary/20 dark:focus-visible:ring-primary/40 text-primary focus-visible:outline-none'>
                {notification.percentageChange > 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
                {notification.percentageChange}%
              </Badge>
            </div>

            <Badge variant='outline' className='shrink-0 text-xs'>{notification.domain}</Badge>
          </motion.div>
        ))}
      </MotionPreset>

      <CardContent className='flex flex-col gap-4'>
        <MotionPreset
          component='h3'
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={0.3}
          transition={{ duration: 0.5 }}
          className='text-2xl font-semibold'
        >
          Multi-Domain Processing
        </MotionPreset>
        <MotionPreset
          component='p'
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={0.45}
          transition={{ duration: 0.5 }}
          className='text-muted-foreground'
        >
          Process seeds across all six industry namespaces simultaneously — each domain carries its own constraints and
          quality thresholds.
        </MotionPreset>
      </CardContent>
    </Card>
  )
}

export default RegularUpdatesCard
