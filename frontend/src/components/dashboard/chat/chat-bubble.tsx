'use client'

import { Bot, User } from 'lucide-react'

import { cn } from '@/lib/utils'

interface ChatBubbleProps {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  showAvatar?: boolean
}

export function ChatBubble({ role, content, timestamp, showAvatar = true }: ChatBubbleProps) {
  if (role === 'system') {
    return (
      <div className="flex justify-center px-4 py-1">
        <div className="max-w-md rounded-lg bg-[#e2f7cb] px-3 py-1.5 text-center text-xs text-gray-600 shadow-sm dark:bg-zinc-700 dark:text-zinc-300">
          {content}
        </div>
      </div>
    )
  }

  const isUser = role === 'user'

  return (
    <div className={cn('flex gap-2 px-4 py-0.5', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      {showAvatar ? (
        <div
          className={cn(
            'flex size-8 shrink-0 items-center justify-center rounded-full',
            isUser ? 'bg-emerald-600' : 'bg-gray-400 dark:bg-zinc-600'
          )}
        >
          {isUser ? (
            <User className="size-4 text-white" />
          ) : (
            <Bot className="size-4 text-white" />
          )}
        </div>
      ) : (
        <div className="w-8 shrink-0" />
      )}

      {/* Bubble */}
      <div className={cn('relative max-w-[75%]', isUser ? 'items-end' : 'items-start')}>
        {/* Tail */}
        <div
          className={cn(
            'absolute top-0 size-0 border-[6px] border-transparent',
            isUser
              ? '-right-2 border-l-[#dcf8c6] dark:border-l-emerald-800'
              : '-left-2 border-r-white dark:border-r-zinc-800'
          )}
        />
        <div
          className={cn(
            'rounded-lg px-3 py-2 shadow-sm',
            isUser
              ? 'rounded-tr-none bg-[#dcf8c6] text-gray-800 dark:bg-emerald-800 dark:text-emerald-50'
              : 'rounded-tl-none bg-white text-gray-800 dark:bg-zinc-800 dark:text-zinc-100'
          )}
        >
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
          {timestamp && (
            <div className={cn('mt-1 flex', isUser ? 'justify-end' : 'justify-start')}>
              <span className="text-xs text-gray-500 dark:text-zinc-400">
                {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              {isUser && (
                <span className="ml-1 text-xs text-blue-500">✓✓</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
