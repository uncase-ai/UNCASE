'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import type { ReactNode } from 'react'

import { FastForward, Pause, Play, SkipForward } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'

interface ChatPlaybackProps {
  totalMessages: number
  children: (visibleCount: number, isTyping: boolean) => ReactNode
}

const SPEEDS = [0.5, 1, 1.5, 2, 3]
const BASE_DELAY_MS = 1200

export function ChatPlayback({ totalMessages, children }: ChatPlaybackProps) {
  const [visibleCount, setVisibleCount] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [speedIndex, setSpeedIndex] = useState(1) // default 1x
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const speed = SPEEDS[speedIndex]

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const revealNext = useCallback(() => {
    setVisibleCount(prev => {
      const next = prev + 1

      if (next >= totalMessages) {
        setIsPlaying(false)
        setIsTyping(false)

        return totalMessages
      }

      return next
    })
    setIsTyping(false)
  }, [totalMessages])

  useEffect(() => {
    if (!isPlaying || visibleCount >= totalMessages) {
      clearTimer()

      return
    }

    // Show typing indicator first, then reveal after delay
    const typingDelay = (BASE_DELAY_MS * 0.4) / speed
    const messageDelay = (BASE_DELAY_MS * 0.6) / speed

    timerRef.current = setTimeout(() => {
      setIsTyping(true)
      timerRef.current = setTimeout(() => {
        setIsTyping(false)
        timerRef.current = setTimeout(revealNext, messageDelay)
      }, typingDelay)
    }, 0)

    return clearTimer
  }, [isPlaying, visibleCount, totalMessages, speed, revealNext, clearTimer])

  const handlePlayPause = () => {
    if (visibleCount >= totalMessages) {
      setVisibleCount(0)
      setIsPlaying(true)
    } else {
      setIsPlaying(!isPlaying)
    }
  }

  const handleSkip = () => {
    clearTimer()
    setVisibleCount(totalMessages)
    setIsPlaying(false)
    setIsTyping(false)
  }

  const handleSpeedCycle = () => {
    setSpeedIndex(i => (i + 1) % SPEEDS.length)
  }

  return (
    <div className="flex flex-col">
      {/* Playback controls */}
      <div className="flex items-center gap-2 border-b bg-muted/30 px-4 py-2 dark:border-zinc-800">
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={handlePlayPause}>
          {isPlaying ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
        </Button>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={handleSkip} disabled={visibleCount >= totalMessages}>
          <SkipForward className="size-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs" onClick={handleSpeedCycle}>
          <FastForward className="size-3" />
          {speed}x
        </Button>
        <div className="flex-1">
          <Slider
            value={[visibleCount]}
            max={totalMessages}
            step={1}
            onValueChange={([v]) => {
              setVisibleCount(v)
              setIsPlaying(false)
              setIsTyping(false)
            }}
            className="h-1"
          />
        </div>
        <span className="text-xs text-muted-foreground">
          {visibleCount}/{totalMessages}
        </span>
      </div>

      {/* Content rendered by parent */}
      {children(visibleCount, isTyping)}
    </div>
  )
}
