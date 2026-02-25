'use client'

import { useEffect, useState, useCallback } from 'react'

import { motion, AnimatePresence } from 'motion/react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { MotionPreset } from '@/components/ui/motion-preset'

import { pipelineSteps } from '@/assets/data/pipeline'

import { cn } from '@/lib/utils'

const CYCLE_DURATION = 3000

const PipelineTimeline = () => {
  const [activeIndex, setActiveIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isPaused, setIsPaused] = useState(false)

  const totalSteps = pipelineSteps.length

  const advance = useCallback(() => {
    setActiveIndex(prev => (prev + 1) % totalSteps)
    setProgress(0)
  }, [totalSteps])

  useEffect(() => {
    if (isPaused) return

    const interval = 50
    const increment = (interval / CYCLE_DURATION) * 100

    const timer = setInterval(() => {
      setProgress(prev => {
        const next = prev + increment

        if (next >= 100) {
          advance()

          return 0
        }

        return next
      })
    }, interval)

    return () => clearInterval(timer)
  }, [isPaused, advance])

  const handleStepClick = (index: number) => {
    setActiveIndex(index)
    setProgress(0)
  }

  const ActiveIcon = pipelineSteps[activeIndex].icon

  return (
    <section id='pipeline' className='py-8 sm:py-16 lg:py-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        {/* Section header */}
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
          className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'
        >
          <p className='text-primary text-sm font-medium uppercase'>Pipeline</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>From Expert Knowledge to LoRA Adapter</h2>

          <p className='text-muted-foreground mx-auto max-w-2xl text-base sm:text-xl'>
            5 layers. Zero real data. Every step delivers value independently.
          </p>
        </MotionPreset>

        {/* Timeline */}
        <MotionPreset fade slide={{ direction: 'down', offset: 35 }} delay={0.3} transition={{ duration: 0.5 }}>
          <div
            className='space-y-8'
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
          >
            {/* Horizontal step indicator (desktop) */}
            <div className='hidden md:block'>
              <div className='relative flex items-center justify-between'>
                {pipelineSteps.map((step, index) => {
                  const isActive = index === activeIndex
                  const isCompleted = index < activeIndex
                  const StepIcon = step.icon

                  return (
                    <div key={step.step} className='relative z-10 flex flex-1 flex-col items-center'>
                      {/* Connector line + progress */}
                      {index > 0 && (
                        <div className='absolute top-5 right-1/2 left-[-50%] h-0.5'>
                          <div className='bg-border h-full w-full' />
                          <motion.div
                            className='bg-primary absolute inset-y-0 left-0'
                            initial={{ width: '0%' }}
                            animate={{
                              width:
                                index < activeIndex
                                  ? '100%'
                                  : index === activeIndex
                                    ? `${progress}%`
                                    : '0%'
                            }}
                            transition={{ duration: 0.1, ease: 'linear' }}
                          />
                        </div>
                      )}

                      {/* Step circle */}
                      <button
                        type='button'
                        onClick={() => handleStepClick(index)}
                        className={cn(
                          'relative flex size-10 shrink-0 cursor-pointer items-center justify-center rounded-full border-2 transition-all duration-300',
                          isActive
                            ? 'border-primary bg-primary text-primary-foreground scale-110 shadow-lg'
                            : isCompleted
                              ? 'border-primary bg-primary/10 text-primary'
                              : 'border-border bg-background text-muted-foreground'
                        )}
                      >
                        <StepIcon className='size-4.5' />
                      </button>

                      {/* Step label */}
                      <span
                        className={cn(
                          'mt-3 text-center text-xs font-medium transition-colors duration-300',
                          isActive ? 'text-foreground' : 'text-muted-foreground'
                        )}
                      >
                        Layer {step.step - 1}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Vertical step indicator (mobile) */}
            <div className='flex gap-1.5 overflow-x-auto pb-2 md:hidden'>
              {pipelineSteps.map((step, index) => {
                const isActive = index === activeIndex

                return (
                  <button
                    key={step.step}
                    type='button'
                    onClick={() => handleStepClick(index)}
                    className='flex flex-col items-center gap-1.5'
                  >
                    <div className='relative h-1 w-14 overflow-hidden rounded-full'>
                      <div className='bg-border absolute inset-0' />
                      <motion.div
                        className='bg-primary absolute inset-y-0 left-0 rounded-full'
                        initial={{ width: '0%' }}
                        animate={{
                          width:
                            index < activeIndex
                              ? '100%'
                              : index === activeIndex
                                ? `${progress}%`
                                : '0%'
                        }}
                        transition={{ duration: 0.1, ease: 'linear' }}
                      />
                    </div>
                    <span
                      className={cn(
                        'whitespace-nowrap text-[10px] font-medium transition-colors duration-300',
                        isActive ? 'text-foreground' : 'text-muted-foreground'
                      )}
                    >
                      L{step.step - 1}
                    </span>
                  </button>
                )
              })}
            </div>

            {/* Active step content */}
            <AnimatePresence mode='wait'>
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
              >
                <Card className='shadow-none'>
                  <CardContent className='flex flex-col items-start gap-6 md:flex-row md:items-center md:gap-10'>
                    {/* Icon area */}
                    <div className='flex shrink-0 flex-col items-center gap-3'>
                      <div className='bg-primary/10 text-primary flex size-16 items-center justify-center rounded-2xl md:size-20'>
                        <ActiveIcon className='size-8 md:size-10' />
                      </div>
                      <Badge variant='secondary' className='font-mono text-xs'>
                        Layer {pipelineSteps[activeIndex].step - 1}
                      </Badge>
                    </div>

                    {/* Text content */}
                    <div className='flex flex-1 flex-col gap-3'>
                      <h3 className='text-xl font-semibold md:text-2xl'>{pipelineSteps[activeIndex].title}</h3>

                      <p className='text-muted-foreground leading-relaxed'>{pipelineSteps[activeIndex].description}</p>

                      {/* Progress bar */}
                      <div className='mt-2 h-1 w-full overflow-hidden rounded-full'>
                        <div className='bg-border h-full w-full' />
                        <motion.div
                          className='bg-primary -mt-1 h-1 rounded-full'
                          initial={{ width: '0%' }}
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 0.1, ease: 'linear' }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </AnimatePresence>
          </div>
        </MotionPreset>
      </div>
    </section>
  )
}

export default PipelineTimeline
