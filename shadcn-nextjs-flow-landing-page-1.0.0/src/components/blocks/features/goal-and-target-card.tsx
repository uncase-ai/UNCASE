'use client'

import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { MotionPreset } from '@/components/ui/motion-preset'

import { cn } from '@/lib/utils'

const GoalAndTargetCard = () => {
  const max = 25
  const step = 2.5 // This creates one tick in the middle of each 5-unit interval
  const ticks = [...Array(Math.floor(max / step) + 1)].map((_, i) => i * step)
  const [value, setValue] = useState([12.5])

  return (
    <Card className='h-84 shadow-none'>
      <CardContent className='flex flex-col gap-6'>
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={0.15}
          transition={{ duration: 0.5 }}
          className='px-5.75 py-4.75 *:not-first:mt-3'
        >
          <div className='flex items-center justify-between'>
            <Label>Set monthly sales goal</Label>
            <Badge className='px-1.5'>{value[0] === 0 ? 1 : value[0]}K</Badge>
          </div>
          <div>
            <Slider
              aria-label='Slider with ticks'
              defaultValue={[5]}
              max={max}
              step={step}
              onValueChange={setValue}
              value={value}
            />
            <span
              aria-hidden='true'
              className='text-muted-foreground mt-3 flex w-full items-center justify-between gap-1 px-2.75 text-sm font-medium'
            >
              {ticks.map((value, i) => {
                const isMajorTick = value % 5 === 0

                return (
                  <span className='flex w-0 flex-col items-center justify-center gap-2' key={String(i)}>
                    <span className={cn('bg-input h-3 w-px', !isMajorTick && 'h-1.5')} />
                    <span className={cn(!isMajorTick && 'opacity-0')}>{value === 0 ? 1 : value}K</span>
                  </span>
                )
              })}
            </span>
          </div>
        </MotionPreset>

        <div className='flex flex-col gap-4'>
          <MotionPreset
            component='h3'
            fade
            slide={{ direction: 'down', offset: 35 }}
            delay={0.3}
            transition={{ duration: 0.5 }}
            className='text-2xl font-semibold'
          >
            Goals & Targets
          </MotionPreset>

          <MotionPreset
            component='p'
            fade
            slide={{ direction: 'down', offset: 35 }}
            delay={0.45}
            transition={{ duration: 0.5 }}
            className='text-muted-foreground'
          >
            Set user or revenue targets for any timeframe and watch progress update in real time-with clear insights at
            every step.
          </MotionPreset>
        </div>
      </CardContent>
    </Card>
  )
}

export default GoalAndTargetCard
