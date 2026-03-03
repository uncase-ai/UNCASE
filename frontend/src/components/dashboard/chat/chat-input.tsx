'use client'

import { useCallback, useRef } from 'react'

import { Send } from 'lucide-react'

import { Button } from '@/components/ui/button'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ onSend, disabled = false, placeholder = 'Escribe tu respuesta...' }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = useCallback(() => {
    const value = textareaRef.current?.value.trim()

    if (!value) return
    onSend(value)

    if (textareaRef.current) {
      textareaRef.current.value = ''
      textareaRef.current.style.height = 'auto'
    }
  }, [onSend])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const handleInput = useCallback(() => {
    const ta = textareaRef.current

    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'
  }, [])

  return (
    <div className="flex items-end gap-2 border-t bg-gray-100 p-3 dark:border-zinc-700 dark:bg-zinc-900">
      <textarea
        ref={textareaRef}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={disabled}
        placeholder={placeholder}
        rows={1}
        className="flex-1 resize-none rounded-2xl border-0 bg-white px-4 py-2.5 text-sm shadow-sm outline-none placeholder:text-gray-400 focus:ring-1 focus:ring-emerald-500 disabled:opacity-50 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-500"
      />
      <Button
        size="icon"
        onClick={handleSend}
        disabled={disabled}
        className="size-10 shrink-0 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
      >
        <Send className="size-4" />
      </Button>
    </div>
  )
}
