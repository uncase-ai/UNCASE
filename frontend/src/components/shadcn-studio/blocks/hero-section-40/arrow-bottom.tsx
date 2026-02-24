import { motion } from 'motion/react'

import { cn } from '@/lib/utils'

const ArrowBottom = ({ delay = 0, className }: { delay?: number; className?: string }) => {
  return (
    <motion.svg
      width='15'
      height='69'
      viewBox='0 0 15 69'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={cn('absolute top-full left-1/2 -translate-x-1/2 -translate-y-1.5 md:hidden', className)}
    >
      <motion.path
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 0.4,
          ease: 'easeInOut',
          delay
        }}
        d='M13.3584 6L7.3584 12L1.3584 6L7.3584 0L13.3584 6Z'
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
        d='M7.3584 6V68'
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
        d='M13.7158 61.4941L7.35765 67.8768L1 61.4944'
        stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
        strokeWidth='2'
        strokeLinecap='round'
        strokeLinejoin='round'
        className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
      />
    </motion.svg>
  )
}

export default ArrowBottom
