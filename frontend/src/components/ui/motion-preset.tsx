'use client'

import * as React from 'react'

import {
  AnimatePresence,
  motion,
  useInView,
  useReducedMotion,
  type HTMLMotionProps,
  type UseInViewOptions,
  type Transition,
  type Variant
} from 'motion/react'

type MotionComponent = keyof typeof motion

interface MotionPresetProps {
  children?: React.ReactNode
  className?: string
  component?: MotionComponent
  transition?: Transition
  delay?: number
  inView?: boolean
  inViewMargin?: UseInViewOptions['margin']
  inViewOnce?: boolean
  blur?: string | boolean
  slide?:
    | {
        direction?: 'up' | 'down' | 'left' | 'right'
        offset?: number
      }
    | boolean
  fade?: { initialOpacity?: number; opacity?: number } | boolean
  zoom?:
    | {
        initialScale?: number
        scale?: number
      }
    | boolean
  motionProps?: Omit<HTMLMotionProps<any>, 'children' | 'className' | 'ref' | 'transition'>
  ref?: React.Ref<any>
}

const motionComponents = motion as any

function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState(false)

  React.useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)')

    setIsMobile(mq.matches)

    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches)

    mq.addEventListener('change', handler)

    return () => mq.removeEventListener('change', handler)
  }, [])

  return isMobile
}

function MotionPreset({
  ref,
  children,
  className,
  component = 'div',
  transition = { type: 'spring', stiffness: 200, damping: 20 },
  delay = 0,
  inView = true,
  inViewMargin = '0px',
  inViewOnce = true,
  blur = false,
  slide = false,
  fade = false,
  zoom = false,
  motionProps = {}
}: MotionPresetProps) {
  const localRef = React.useRef<any>(null)
  const prefersReducedMotion = useReducedMotion()
  const isMobile = useIsMobile()
  const shouldReduceMotion = prefersReducedMotion || isMobile

  React.useImperativeHandle(ref, () => localRef.current)

  const inViewResult = useInView(localRef, {
    once: inViewOnce,
    margin: inViewMargin
  })

  const isInView = !inView || inViewResult

  const hiddenVariant: Variant = {}
  const visibleVariant: Variant = {}

  if (blur && !shouldReduceMotion) {
    hiddenVariant.filter = blur === true ? 'blur(10px)' : `blur(${blur})`
    visibleVariant.filter = 'blur(0px)'
  }

  if (slide && !shouldReduceMotion) {
    const offset = slide === true ? 100 : (slide.offset ?? 100)
    const direction = slide === true ? 'left' : (slide.direction ?? 'left')
    const axis = direction === 'up' || direction === 'down' ? 'y' : 'x'

    hiddenVariant[axis] = direction === 'left' || direction === 'up' ? -offset : offset
    visibleVariant[axis] = 0
  }

  if (fade) {
    hiddenVariant.opacity = fade === true ? 0 : (fade.initialOpacity ?? 0)
    visibleVariant.opacity = fade === true ? 1 : (fade.opacity ?? 1)
  }

  if (zoom && !shouldReduceMotion) {
    hiddenVariant.scale = zoom === true ? 0.5 : (zoom.initialScale ?? 0.5)
    visibleVariant.scale = zoom === true ? 1 : (zoom.scale ?? 1)
  }

  const effectiveDelay = shouldReduceMotion ? Math.min(delay, 0.15) : delay

  const MotionComponent = motionComponents[component] || motion.div

  return (
    <AnimatePresence>
      <MotionComponent
        ref={localRef}
        initial='hidden'
        animate={isInView ? 'visible' : 'hidden'}
        exit='hidden'
        variants={{
          hidden: hiddenVariant,
          visible: visibleVariant
        }}
        transition={{
          ...transition,
          delay: (transition?.delay ?? 0) + effectiveDelay,
          ...(shouldReduceMotion ? { duration: 0.2 } : {})
        }}
        className={className}
        {...motionProps}
      >
        {children}
      </MotionComponent>
    </AnimatePresence>
  )
}

export { MotionPreset, type MotionPresetProps }
