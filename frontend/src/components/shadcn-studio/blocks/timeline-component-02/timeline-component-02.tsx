'use client'

import React, { useEffect, useRef, useState } from 'react'

import { useMotionValueEvent, useScroll, useTransform, motion } from 'motion/react'

import { Badge } from '@/components/ui/badge'

import { cn } from '@/lib/utils'

interface TimelineEntry {
  title: string
  content: React.ReactNode
}

const JourneyTimeline = ({ data }: { data: TimelineEntry[] }) => {
  const ref = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [height, setHeight] = useState(0)
  const [activeIndex, setActiveIndex] = useState(0)
  const [firstItemOffset, setFirstItemOffset] = useState(0)
  const [lineHeight, setLineHeight] = useState(0)

  useEffect(() => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect()
      const firstDot = ref.current.querySelector('[data-timeline-dot]')
      const dots = ref.current.querySelectorAll('[data-timeline-dot]')
      let offset = 0

      if (firstDot) {
        const firstDotRect = (firstDot as HTMLElement).getBoundingClientRect()

        offset = firstDotRect.top + firstDotRect.height / 2 - rect.top
        setFirstItemOffset(offset)
      }

      if (dots.length) {
        const lastDot = dots[dots.length - 1] as HTMLElement
        const lastRect = lastDot.getBoundingClientRect()
        const lastOffset = lastRect.top + lastRect.height / 2 - rect.top

        setLineHeight(Math.max(0, lastOffset - offset))
      } else {
        setLineHeight(Math.max(0, rect.height - offset))
      }

      setHeight(rect.height)
    }
  }, [])

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start 0%', 'end 100%']
  })

  const heightTransform = useTransform(scrollYProgress, [0, 1], [0, height])
  const opacityTransform = useTransform(scrollYProgress, [0, 0.1], [0, 1])

  useMotionValueEvent(scrollYProgress, 'change', latest => {
    const totalItems = data.length
    const newIndex = Math.min(Math.floor(latest * totalItems), totalItems - 1)

    setActiveIndex(newIndex)
  })

  return (
    <div className='py-8 sm:py-16 lg:py-24' ref={containerRef}>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        <div className='mb-12 space-y-4 text-center md:mb-16 lg:mb-24'>
          <h2 className='text-2xl font-semibold tracking-tight md:text-3xl lg:text-4xl'>The Journey That Shaped Us</h2>
          <p className='text-muted-foreground text-xl'>
            From a small home setup to building solutions for global clients, our journey reflects passion, persistence,
            and continuous growth. Every milestone has shaped who we are today.
          </p>
        </div>
        <div ref={ref} className='relative mx-auto max-w-7xl space-y-4'>
          {data.map((item, index) => {
            const isEven = index % 2 === 0
            const isActive = index <= activeIndex

            return (
              <div
                key={index}
                data-timeline-item
                className={`flex items-start ${isEven ? 'md:flex-row' : 'md:flex-row-reverse'}`}
              >
                {/* Title Section */}
                <div
                  className={`hidden w-full md:flex md:flex-1 md:items-start ${isEven ? 'md:justify-end' : 'md:justify-start'}`}
                >
                  <Badge
                    className={cn(
                      'transform rounded-sm text-sm font-medium transition-colors duration-300',
                      isActive ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'
                    )}
                  >
                    {item.title}
                  </Badge>
                </div>
                {/* Dot and Line Section */}
                <div className='relative flex flex-col items-center pr-4 md:px-4'>
                  <div data-timeline-dot className='sticky top-40 z-40 flex items-center justify-center'>
                    <span
                      className={cn(
                        'flex size-6 shrink-0 items-center justify-center rounded-full',
                        isActive ? 'bg-primary/10' : 'bg-muted'
                      )}
                    >
                      <span
                        className={cn(
                          'size-3 rounded-full transition-colors duration-300',
                          isActive ? 'bg-primary' : 'bg-muted-foreground'
                        )}
                      />
                    </span>
                  </div>
                </div>
                {/* Content Section */}
                <div className={`w-full md:flex md:flex-1 ${isEven ? 'md:justify-start' : 'md:justify-end'}`}>
                  <Badge
                    className={cn(
                      'mb-4 block transform rounded-sm text-left text-sm font-medium transition-colors duration-300 md:hidden',
                      isActive ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'
                    )}
                  >
                    {item.title}
                  </Badge>
                  {item.content}
                </div>
              </div>
            )
          })}
          <div
            style={{
              height: lineHeight + 'px',
              top: firstItemOffset + 'px'
            }}
            className='bg-border absolute left-3 w-[2px] overflow-hidden md:left-1/2 md:-translate-x-1/2'
          >
            <motion.div
              style={{
                height: heightTransform,
                opacity: opacityTransform
              }}
              className='bg-primary absolute inset-x-0 top-0 w-[2px] rounded-full'
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default JourneyTimeline
