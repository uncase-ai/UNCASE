'use client'

import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { MotionPreset } from '@/components/ui/motion-preset'

import { cn } from '@/lib/utils'

const GoalAndTargetCard = () => {
  const max = 24
  const step = 3
  const ticks = [...Array(Math.floor(max / step) + 1)].map((_, i) => i * step)
  const [value, setValue] = useState([12])

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
            <Label>Conversation turns per seed</Label>
            <Badge className='px-1.5'>{value[0]}</Badge>
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
                const isMajorTick = value % 6 === 0

                return (
                  <span className='flex w-0 flex-col items-center justify-center gap-2' key={String(i)}>
                    <span className={cn('bg-input h-3 w-px', !isMajorTick && 'h-1.5')} />
                    <span className={cn(!isMajorTick && 'opacity-0')}>{value}</span>
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
            Seed Configuration
          </MotionPreset>

          <MotionPreset
            component='p'
            fade
            slide={{ direction: 'down', offset: 35 }}
            delay={0.45}
            transition={{ duration: 0.5 }}
            className='text-muted-foreground'
          >
            Define conversation structure — min/max turns, expected flow, and quality thresholds. Seeds control every
            aspect of generated data.
          </MotionPreset>
        </div>
      </CardContent>
    </Card>
  )
}

export default GoalAndTargetCard
