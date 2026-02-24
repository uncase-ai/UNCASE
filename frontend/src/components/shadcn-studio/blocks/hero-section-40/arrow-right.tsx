import { motion } from 'motion/react'

import { cn } from '@/lib/utils'

const ArrowRight = ({ delay = 0, className }: { delay?: number; className?: string }) => {
  return (
    <motion.svg
      width='71'
      height='15'
      viewBox='0 0 71 15'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={cn(
        'absolute top-1/2 left-full -translate-x-1.5 translate-y-[calc(-50%+0.9375rem)] max-md:hidden',
        className
      )}
    >
      <motion.path
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 0.4,
          ease: 'easeInOut',
          delay
        }}
        d='M6 1.35791L12 7.35791L6 13.3579L0 7.35791L6 1.35791Z'
        fill='color-mix(in oklab,var(--foreground)15%,var(--background))'
        className='dark:fill-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
      />
      <motion.path
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{
          duration: 0.4,
          ease: 'easeInOut',
          delay: delay + 0.24
        }}
        d='M6 7.35791H70'
        stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
        strokeWidth='2'
        className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
      />
      <motion.path
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{
          pathLength: {
            duration: 0.3,
            ease: 'easeInOut',
            delay: delay + 0.64
          },
          opacity: { duration: 0.1, delay: delay + 0.64 }
        }}
        d='M63.4941 1L69.8768 7.35817L63.4944 13.7158'
        stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
        strokeWidth='2'
        strokeLinecap='round'
        strokeLinejoin='round'
        className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
      />
    </motion.svg>
  )
}

export default ArrowRight
