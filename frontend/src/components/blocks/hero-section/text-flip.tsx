'use client'

import React, { useState, useEffect } from 'react'

import { motion, AnimatePresence } from 'motion/react'

import { cn } from '@/lib/utils'
import { useIsMobile } from '@/hooks/use-mobile'

const TextFlip = ({
  words = ['Healthcare', 'Finance', 'Legal', 'Automotive', 'Education', 'Manufacturing'],
  duration = 3000
}: {
  words?: string[]
  duration?: number
}) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const isMobile = useIsMobile()

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex(prevIndex => (prevIndex + 1) % words.length)
    }, duration)

    return () => clearInterval(interval)
  }, [words, duration])

  return (
    <motion.span className='bg-background/5 relative inline-flex min-w-36 justify-center overflow-hidden rounded-md border px-3 py-0.5 backdrop-blur-md sm:min-w-48'>
      <AnimatePresence mode='popLayout'>
        <motion.span
          key={currentIndex}
          initial={isMobile ? { opacity: 0 } : { y: -40, filter: 'blur(10px)' }}
          animate={isMobile ? { opacity: 1 } : { y: 0, filter: 'blur(0px)' }}
          exit={isMobile ? { opacity: 0 } : { y: 50, filter: 'blur(10px)', opacity: 0 }}
          transition={{ duration: isMobile ? 0.3 : 0.5 }}
          className={cn('inline-block whitespace-nowrap')}
        >
          {words[currentIndex]}
        </motion.span>
      </AnimatePresence>
    </motion.span>
  )
}

export default TextFlip
