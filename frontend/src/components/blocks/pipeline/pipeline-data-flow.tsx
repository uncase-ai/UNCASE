'use client'

import { useState } from 'react'

import { motion, AnimatePresence } from 'motion/react'
import { ArrowRightIcon, CheckCircle2Icon } from 'lucide-react'

import { MotionPreset } from '@/components/ui/motion-preset'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

import { cn } from '@/lib/utils'

import { dataFlowSteps } from '@/assets/data/pipeline'

function formatValue(value: string | number | boolean) {
  if (typeof value === 'boolean') {
    return value ? (
      <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
        true
      </Badge>
    ) : (
      <Badge className='bg-red-600/15 text-red-600 border-red-600/20 dark:bg-red-500/15 dark:text-red-400 dark:border-red-500/20'>
        false
      </Badge>
    )
  }

  if (typeof value === 'number') {
    return <span className='font-mono tabular-nums'>{value.toLocaleString('en-US')}</span>
  }

  return <span>{value}</span>
}

const PipelineDataFlow = () => {
  const [activeStep, setActiveStep] = useState(0)

  return (
    <section id='data-flow' className='py-8 sm:py-16 lg:py-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        {/* Header */}
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
          className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'
        >
          <p className='text-primary text-sm font-medium uppercase'>Data Flow</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Real Data Transformation</h2>

          <p className='text-muted-foreground mx-auto max-w-2xl text-xl'>
            See how a seed from the automotive.sales domain flows through all 5 layers.
          </p>
        </MotionPreset>

        {/* Step Tabs */}
        <MotionPreset fade slide={{ direction: 'down', offset: 35 }} delay={0.2} transition={{ duration: 0.5 }}>
          <div className='mb-8 flex flex-wrap items-center justify-center gap-2 sm:gap-3'>
            {dataFlowSteps.map((step, index) => (
              <button
                key={index}
                onClick={() => setActiveStep(index)}
                className={cn(
                  'relative flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-all duration-200 sm:px-4 sm:py-2.5',
                  activeStep === index
                    ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                    : 'bg-card text-muted-foreground border-border hover:text-foreground hover:border-foreground/20'
                )}
              >
                <span
                  className={cn(
                    'flex size-5 shrink-0 items-center justify-center rounded-full text-xs font-semibold',
                    activeStep === index ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'
                  )}
                >
                  {index < activeStep ? <CheckCircle2Icon className='size-3.5' /> : index + 1}
                </span>
                <span className='hidden sm:inline'>{step.title}</span>
                {index < dataFlowSteps.length - 1 && (
                  <ArrowRightIcon className='text-muted-foreground/40 ml-1 hidden size-3.5 lg:inline' />
                )}
              </button>
            ))}
          </div>
        </MotionPreset>

        {/* Step Content */}
        <MotionPreset fade slide={{ direction: 'down', offset: 35 }} delay={0.4} transition={{ duration: 0.5 }}>
          <Card className='mx-auto max-w-2xl shadow-none'>
            <CardContent>
              <AnimatePresence mode='wait'>
                <motion.div
                  key={activeStep}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                >
                  {/* Step title inside card */}
                  <div className='mb-6 flex items-center gap-3'>
                    <span className='bg-primary text-primary-foreground flex size-7 items-center justify-center rounded-full text-xs font-semibold'>
                      {activeStep + 1}
                    </span>
                    <h3 className='text-lg font-semibold'>{dataFlowSteps[activeStep].title}</h3>
                  </div>

                  {/* Key-value rows */}
                  <div className='divide-border divide-y rounded-lg border'>
                    {Object.entries(dataFlowSteps[activeStep].content).map(([key, value]) => (
                      <div key={key} className='flex items-center justify-between gap-4 px-4 py-3'>
                        <span className='text-muted-foreground shrink-0 font-mono text-sm'>{key}</span>
                        <span className='text-right text-sm font-medium'>{formatValue(value)}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </AnimatePresence>
            </CardContent>
          </Card>
        </MotionPreset>
      </div>
    </section>
  )
}

export default PipelineDataFlow
