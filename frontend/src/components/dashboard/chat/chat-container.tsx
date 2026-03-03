'use client'

import { useEffect, useRef } from 'react'

import type { ChatMessage } from '@/types/layer0'

import { ChatBubble } from './chat-bubble'

interface ChatContainerProps {
  messages: ChatMessage[]
  className?: string
}

export function ChatContainer({ messages, className }: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  return (
    <div className={`whatsapp-bg-pattern flex-1 overflow-y-auto ${className ?? ''}`}>
      <div className="flex flex-col gap-1 py-4">
        {messages.map((msg, i) => {
          const prevMsg = i > 0 ? messages[i - 1] : null
          const showAvatar = !prevMsg || prevMsg.role !== msg.role

          return (
            <ChatBubble
              key={msg.id}
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
              showAvatar={showAvatar}
            />
          )
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
