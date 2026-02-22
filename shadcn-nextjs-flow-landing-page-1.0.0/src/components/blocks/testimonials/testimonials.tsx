import { ExternalLinkIcon, StarIcon } from 'lucide-react'

import Link from 'next/link'

import TestimonialCard from '@/components/blocks/testimonials/testimonial-card'
import type { TestimonialItem } from '@/components/blocks/testimonials/testimonial-card'

import { Marquee } from '@/components/ui/marquee'
import { MotionPreset } from '@/components/ui/motion-preset'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

const Testimonials = ({ testimonials }: { testimonials: TestimonialItem[] }) => {
  return (
    <section id='testimonials' className='space-y-12 py-8 sm:space-y-16 sm:py-16 lg:space-y-24 lg:py-24'>
      {/* Testimonial Header */}
      <MotionPreset
        className='mx-auto max-w-7xl space-y-4 px-4 text-center sm:px-6 lg:px-8'
        fade
        slide={{ direction: 'down', offset: 50 }}
        blur
        transition={{ duration: 0.5 }}
      >
        <p className='text-primary text-sm font-medium uppercase'>Testimonials</p>

        <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Trusted by People Who Sell Smarter</h2>

        <p className='text-muted-foreground text-xl'>
          Real stories from users who simplified their sales process and grew their revenue with Flow.
        </p>
      </MotionPreset>

      {/* Testimonials Marquee */}
      <div className='w-full'>
        <Marquee pauseOnHover duration={70} gap={2.25} className='overflow-visible overflow-x-clip pb-5 *:items-end'>
          {testimonials.map((testimonial, index) => (
            <TestimonialCard key={index} testimonial={testimonial} />
          ))}
        </Marquee>
      </div>

      <div className='mx-auto max-w-7xl space-y-4 px-4 text-center sm:px-6 lg:px-8'>
        <div className='flex flex-wrap items-center justify-center gap-11'>
          <div>
            <div className='flex items-center gap-1.5'>
              <p className='text-2xl font-semibold'>4.5</p>
              <StarIcon className='fill-amber-600 stroke-amber-600 dark:fill-amber-400 dark:stroke-amber-400'></StarIcon>
            </div>
            <p className='text-muted-foreground text-sm font-medium'>Stars out of 5</p>
          </div>
          <PrimaryFlowButton size='lg' asChild>
            <Link href='#'>
              View all testimonials
              <ExternalLinkIcon />
            </Link>
          </PrimaryFlowButton>
        </div>
      </div>
    </section>
  )
}

export default Testimonials
