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
import { useIsMobile } from '@/hooks/use-mobile'

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
  const isMobile = useIsMobile()

  useEffect(() => {
    if (isMobile) return

    const interval = setInterval(() => {
      setNotifications(prevCards => {
        const newArray = [...prevCards]

        setActiveIndex(newArray[newArray.length - 1])
        newArray.unshift(newArray.pop()!)

        return newArray
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [isMobile])

  return (
    <Card className='gap-12 shadow-none'>
      <MotionPreset
        fade
        slide={{ direction: 'down', offset: 35 }}
        delay={0.15}
        transition={{ duration: 0.5 }}
        className='relative flex h-full justify-center'
      >
        <div className='absolute inset-x-3.5 flex min-h-29 justify-center gap-2 sm:gap-4'>
          <div className='bg-card flex w-24 flex-col items-start gap-2 rounded-xl border p-2.5 shadow-lg sm:w-27 sm:gap-2.5 sm:p-3'>
            <div className='grid size-8 place-content-center rounded-full border sm:size-9.5'>
              <UsersIcon className='size-4 sm:size-5' />
            </div>
            <div className='space-y-1'>
              <p className='text-sm font-medium tabular-nums sm:text-base'>
                <NumberTicker value={activeIndex.stats.seeds} />
              </p>
              <p className='text-muted-foreground text-[10px] sm:text-xs'>Seeds Processed</p>
            </div>
          </div>
          <div className='bg-card flex w-24 flex-col items-start gap-2 rounded-xl border p-2.5 shadow-lg sm:w-27 sm:gap-2.5 sm:p-3'>
            <div className='grid size-8 place-content-center rounded-full border sm:size-9.5'>
              <UserPlusIcon className='size-4 sm:size-5' />
            </div>
            <div className='space-y-1'>
              <p className='text-sm font-medium tabular-nums sm:text-base'>
                <NumberTicker value={activeIndex.stats.domains} />
              </p>
              <p className='text-muted-foreground text-[10px] sm:text-xs'>Domains Active</p>
            </div>
          </div>
          <div className='bg-card flex w-24 flex-col items-start gap-2 rounded-xl border p-2.5 shadow-lg sm:w-27 sm:gap-2.5 sm:p-3'>
            <div className='grid size-8 place-content-center rounded-full border sm:size-9.5'>
              <TriangleAlertIcon className='size-4 sm:size-5' />
            </div>
            <div className='space-y-1'>
              <p className='text-sm font-medium tabular-nums sm:text-base'>
                <NumberTicker value={activeIndex.stats.passRate} />%
              </p>
              <p className='text-muted-foreground text-[10px] sm:text-xs'>Quality Pass Rate</p>
            </div>
          </div>
        </div>
        <RegularUpdatesRippleBg className='text-border pointer-events-none size-80 select-none sm:size-118' />
        <Logo className='absolute top-1/2 size-30 -translate-y-1/2' />

        {notifications.map((notification, index) => (
          <motion.div
            key={notification.id}
            className='bg-card absolute bottom-0 left-1/2 flex h-20 w-64 items-center justify-between rounded-xl border p-3 shadow-xl sm:w-72 sm:p-4 md:w-75 xl:w-72'
            style={{
              transformOrigin: 'bottom center',
              zIndex: notifications.length - index
            }}
            animate={
              isMobile
                ? {
                    y: (index - 2) * 8,
                    scale: 1 - index * 0.1,
                    opacity: 1 - index * 0.25,
                    x: '-50%'
                  }
                : {
                    y: (index - 2) * 8,
                    scale: 1 - index * 0.1,
                    opacity: 1 - index * 0.25,
                    x: '-50%'
                  }
            }
            transition={{
              duration: isMobile ? 0 : 0.5,
              ease: 'easeInOut'
            }}
          >
            <div className='flex min-w-0 flex-col gap-1'>
              <p className='truncate text-sm font-semibold sm:text-xl'>{notification.seedId}</p>
              <Badge className='bg-primary/10 [a&]:hover:bg-primary/5 focus-visible:ring-primary/20 dark:focus-visible:ring-primary/40 text-primary focus-visible:outline-none'>
                {notification.percentageChange > 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
                {notification.percentageChange}%
              </Badge>
            </div>

            <Badge variant='outline' className='hidden shrink-0 text-xs sm:inline-flex'>{notification.domain}</Badge>
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
