'use client'

import { motion } from 'motion/react'

import { useIsMobile } from '@/hooks/use-mobile'

const staticVariant = { visible: {} }

const rippleVariant = (delay: number) => ({
  visible: {
    scale: [1, 0.95, 1],
    transition: {
      scale: { delay, duration: 2.75, repeat: Infinity, ease: 'easeOut' as const }
    }
  }
})

const RegularUpdatesRippleBg = ({ className }: { className?: string }) => {
  const isMobile = useIsMobile()

  const v1 = isMobile ? staticVariant : rippleVariant(0.24)
  const v2 = isMobile ? staticVariant : rippleVariant(0.24)
  const v3 = isMobile ? staticVariant : rippleVariant(0.36)
  const v4 = isMobile ? staticVariant : rippleVariant(0.48)

  return (
    <motion.svg
      width='1em'
      height='1em'
      viewBox='0 0 500 500'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={className}
      initial='hidden'
      animate='visible'
    >
      <motion.circle
        strokeOpacity={0.4}
        cx='250'
        cy='250'
        r='252'
        fill='var(--card)'
        stroke='var(--border)'
        strokeWidth='1.485'
        variants={v1}
      />
      <motion.circle
        strokeOpacity={0.4}
        cx='250'
        cy='250'
        r='205.5'
        fill='var(--card)'
        stroke='var(--border)'
        strokeWidth='1.485'
        variants={v2}
      />
      <motion.circle
        strokeOpacity={0.4}
        cx='250'
        cy='250'
        r='159'
        fill='var(--card)'
        stroke='var(--border)'
        strokeWidth='1.485'
        variants={v3}
      />
      <motion.circle
        strokeOpacity={0.4}
        cx='250'
        cy='250'
        r='112'
        fill='var(--card)'
        stroke='var(--border)'
        strokeWidth='1.485'
        variants={v4}
      />
    </motion.svg>
  )
}

export default RegularUpdatesRippleBg
