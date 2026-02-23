'use client'

import { GlobeIcon, StoreIcon, TrendingUpIcon } from 'lucide-react'

import { Bar, ComposedChart, Line, XAxis } from 'recharts'

import { Card, CardContent } from '@/components/ui/card'
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { Separator } from '@/components/ui/separator'
import { MotionPreset } from '@/components/ui/motion-preset'

import StatCard from '@/components/blocks/features//stat-card'

const chartData = [
  {
    time: 'B1',
    uv: 72,
    pv: 68
  },
  {
    time: 'B2',
    uv: 75,
    pv: 70
  },
  {
    time: 'B3',
    uv: 80,
    pv: 74
  },
  {
    time: 'B4',
    uv: 78,
    pv: 72
  },
  {
    time: 'B5',
    uv: 85,
    pv: 76
  },
  {
    time: 'B6',
    uv: 82,
    pv: 75
  },
  {
    time: 'B7',
    uv: 88,
    pv: 78
  },
  {
    time: 'B8',
    uv: 90,
    pv: 80
  },
  {
    time: 'B9',
    uv: 91,
    pv: 82
  },
  {
    time: 'B10',
    uv: 93,
    pv: 85
  },
  {
    time: 'B11',
    uv: 94,
    pv: 88
  },
  {
    time: 'B12',
    uv: 96,
    pv: 92
  }
]

const totalEarningChartConfig = {
  uv: {
    label: 'Factual Fidelity',
    color: 'color-mix(in oklab, var(--primary) 20%, var(--background))'
  },
  pv: {
    label: 'ROUGE-L',
    color: 'var(--primary)'
  }
} satisfies ChartConfig

const SalesGrowthCard = () => {
  return (
    <Card className='h-full justify-between gap-11 shadow-none'>
      <div className='flex flex-col gap-8'>
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={0.75}
          transition={{ duration: 0.5 }}
          className='px-6'
        >
          <StatCard
            avatarIcon={<TrendingUpIcon className='size-4' />}
            title='Composite Score'
            statNumber='0.92'
            percentage={12}
            className='w-full p-6 shadow-lg'
          />
        </MotionPreset>

        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={0.9}
          transition={{ duration: 0.5 }}
          className='text-muted-foreground flex flex-col gap-4 py-6 text-sm'
        >
          <div className='flex flex-col gap-1 px-6'>
            <div className='flex items-center justify-between gap-2 py-2'>
              <div className='flex items-center gap-2'>
                <GlobeIcon className='size-4' />
                <span>Factual Fidelity</span>
              </div>
              <div className='flex items-center justify-between gap-2 py-2'>
                <span className='font-medium'>0.94</span>
                <span className='text-card-foreground'>&ge;0.90</span>
              </div>
            </div>
            <div className='flex items-center justify-between gap-2'>
              <div className='flex items-center gap-2'>
                <StoreIcon className='size-4' />
                <span>ROUGE-L</span>
              </div>
              <div className='flex items-center justify-between gap-2'>
                <span className='font-medium'>0.72</span>
                <span className='text-card-foreground'>&ge;0.65</span>
              </div>
            </div>
          </div>
          <div className='px-6'>
            <Separator />
          </div>
          <MotionPreset fade slide={{ direction: 'down', offset: 35 }} delay={1.05} transition={{ duration: 0.5 }}>
            <ChartContainer config={totalEarningChartConfig} className='h-39.25 w-full'>
              <ComposedChart data={chartData} margin={{ top: 4, right: 0, left: 0 }}>
                <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                <XAxis
                  dataKey='time'
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                  minTickGap={15}
                  tick={{ fontSize: 14, fill: 'var(--muted-foreground)' }}
                />
                <Bar dataKey='uv' barSize={16} fill='var(--color-uv)' radius={2} />
                <Line type='linear' dataKey='pv' stroke='var(--color-pv)' dot={false} strokeWidth={3} />
              </ComposedChart>
            </ChartContainer>
          </MotionPreset>
        </MotionPreset>
      </div>

      <CardContent className='flex flex-col gap-4'>
        <MotionPreset
          component='h3'
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={1.2}
          inView={false}
          transition={{ duration: 0.5 }}
          className='text-2xl font-semibold'
        >
          Generation Quality
        </MotionPreset>
        <MotionPreset
          component='p'
          fade
          slide={{ direction: 'down', offset: 35 }}
          delay={1.35}
          inView={false}
          transition={{ duration: 0.5 }}
          className='text-muted-foreground'
        >
          Track quality metrics across synthetic conversation batches — composite scores must pass all six hard gates.
        </MotionPreset>
      </CardContent>
    </Card>
  )
}

export default SalesGrowthCard
