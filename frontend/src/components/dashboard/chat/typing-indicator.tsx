'use client'

import { Bot } from 'lucide-react'

export function TypingIndicator() {
  return (
    <div className="flex gap-2 px-4 py-0.5">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gray-400 dark:bg-zinc-600">
        <Bot className="size-4 text-white" />
      </div>
      <div className="relative">
        <div className="absolute -left-2 top-0 size-0 border-[6px] border-transparent border-r-white dark:border-r-zinc-800" />
        <div className="flex items-center gap-1 rounded-lg rounded-tl-none bg-white px-4 py-3 shadow-sm dark:bg-zinc-800">
          <span className="inline-block size-2 animate-bounce rounded-full bg-gray-400 dark:bg-zinc-500" style={{ animationDelay: '0ms' }} />
          <span className="inline-block size-2 animate-bounce rounded-full bg-gray-400 dark:bg-zinc-500" style={{ animationDelay: '150ms' }} />
          <span className="inline-block size-2 animate-bounce rounded-full bg-gray-400 dark:bg-zinc-500" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  )
}
