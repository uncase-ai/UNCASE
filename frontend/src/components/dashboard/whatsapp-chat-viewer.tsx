'use client'

import { useState } from 'react'

import { Bot, ChevronDown, ChevronRight, User, Wrench } from 'lucide-react'

import type { Conversation, ConversationTurn } from '@/types/api'
import { cn } from '@/lib/utils'

// ─── Role detection (mirrors conversation-detail-page logic) ───

const USER_ROLES = new Set([
  'user', 'usuario', 'cliente', 'customer', 'paciente', 'patient', 'human',
  'coordinador_operaciones', 'coordinador de operaciones',
  'director_administrativo', 'director administrativo',
  'gerente_compras', 'gerente de compras',
  'gerente_recursos_humanos', 'gerente de recursos humanos',
  'procurement officer', 'fleet manager',
  'customer relations manager', 'finance manager',
])

const SYSTEM_ROLES = new Set(['system', 'sistema'])

function isUserRole(rol: string): boolean {
  return USER_ROLES.has(rol.toLowerCase())
}

function isSystemRole(rol: string): boolean {
  return SYSTEM_ROLES.has(rol.toLowerCase())
}

type BubbleRole = 'user' | 'assistant' | 'system'

function getBubbleRole(turn: ConversationTurn): BubbleRole {
  if (isSystemRole(turn.rol)) return 'system'
  if (isUserRole(turn.rol)) return 'user'
  return 'assistant'
}

// ─── Simulated timestamps ───

function simulateTimestamps(turns: ConversationTurn[]): Date[] {
  const base = new Date()
  base.setHours(10, 0, 0, 0)
  return turns.map((_, i) => new Date(base.getTime() + i * 45000))
}

// ─── Tool Call Card ───

function ToolCallCard({ toolName, args }: { toolName: string; args: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mt-1.5 rounded-lg border border-white/20 bg-white/10 dark:border-zinc-600/30 dark:bg-zinc-700/30">
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-center gap-1.5 px-2.5 py-1.5 text-left">
        {expanded ? <ChevronDown className="size-3 opacity-60" /> : <ChevronRight className="size-3 opacity-60" />}
        <Wrench className="size-3 opacity-60" />
        <span className="text-[11px] font-medium opacity-80">{toolName}</span>
      </button>
      {expanded && (
        <div className="border-t border-white/10 px-2.5 py-1.5 dark:border-zinc-600/20">
          <pre className="overflow-x-auto text-[10px] leading-relaxed opacity-70">
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

// ─── WhatsApp Bubble ───

function WhatsAppBubble({
  turn,
  role,
  timestamp,
  showAvatar,
  isEditing,
  editValue,
  onClickToEdit,
  onEditChange,
  onEditSave,
  onEditCancel,
}: {
  turn: ConversationTurn
  role: BubbleRole
  timestamp: Date
  showAvatar: boolean
  isEditing: boolean
  editValue: string
  onClickToEdit: () => void
  onEditChange: (v: string) => void
  onEditSave: () => void
  onEditCancel: () => void
}) {
  if (role === 'system') {
    return (
      <div className="flex justify-center px-4 py-1">
        <div className="max-w-md rounded-lg bg-[#e2f7cb]/80 px-3 py-1.5 text-center text-xs text-gray-600 shadow-sm dark:bg-zinc-700/80 dark:text-zinc-300">
          {turn.contenido}
        </div>
      </div>
    )
  }

  const isUser = role === 'user'

  return (
    <div className={cn('flex gap-2 px-3 py-0.5', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {showAvatar ? (
        <div
          className={cn(
            'flex size-8 shrink-0 items-center justify-center rounded-full shadow-sm',
            isUser ? 'bg-emerald-600' : 'bg-gray-500 dark:bg-zinc-500'
          )}
        >
          {isUser ? <User className="size-4 text-white" /> : <Bot className="size-4 text-white" />}
        </div>
      ) : (
        <div className="w-8 shrink-0" />
      )}

      <div className={cn('relative max-w-[75%]', isUser ? 'items-end' : 'items-start')}>
        {/* Tail */}
        {showAvatar && (
          <div
            className={cn(
              'absolute top-0 size-0 border-[6px] border-transparent',
              isUser
                ? '-right-2 border-l-[#dcf8c6] dark:border-l-emerald-800'
                : '-left-2 border-r-white dark:border-r-zinc-800'
            )}
          />
        )}

        <div
          className={cn(
            'rounded-lg px-3 py-2 shadow-sm',
            showAvatar && (isUser ? 'rounded-tr-none' : 'rounded-tl-none'),
            isUser
              ? 'bg-[#dcf8c6] text-gray-800 dark:bg-emerald-800 dark:text-emerald-50'
              : 'bg-white text-gray-800 dark:bg-zinc-800 dark:text-zinc-100'
          )}
        >
          {/* Role label */}
          {showAvatar && (
            <p className={cn(
              'mb-0.5 text-[11px] font-semibold',
              isUser ? 'text-emerald-700 dark:text-emerald-300' : 'text-blue-600 dark:text-blue-400'
            )}>
              {turn.rol}
            </p>
          )}

          {/* Content */}
          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editValue}
                onChange={e => onEditChange(e.target.value)}
                className="min-h-16 w-full resize-none rounded border bg-white/80 px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-emerald-500 dark:bg-zinc-700"
                autoFocus
              />
              <div className="flex justify-end gap-1">
                <button onClick={onEditCancel} className="rounded px-2 py-0.5 text-[10px] hover:bg-black/5">Cancel</button>
                <button onClick={onEditSave} className="rounded bg-emerald-600 px-2 py-0.5 text-[10px] text-white hover:bg-emerald-700">Apply</button>
              </div>
            </div>
          ) : (
            <div onClick={onClickToEdit} className="cursor-text">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{turn.contenido}</p>
            </div>
          )}

          {/* Tool calls */}
          {turn.tool_calls?.map((tc, i) => (
            <ToolCallCard key={`tc-${i}`} toolName={tc.tool_name} args={tc.arguments} />
          ))}

          {/* Timestamp + checkmarks */}
          <div className={cn('mt-1 flex items-center gap-1', isUser ? 'justify-end' : 'justify-start')}>
            <span className="text-[10px] opacity-50">
              {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
            {isUser && <span className="text-[10px] text-blue-500">✓✓</span>}
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Main viewer ───

interface WhatsAppChatViewerProps {
  conversation: Conversation
  editingTurn: number | null
  editValue: string
  onEditStart: (turnIndex: number) => void
  onEditChange: (v: string) => void
  onEditSave: () => void
  onEditCancel: () => void
}

export function WhatsAppChatViewer({
  conversation,
  editingTurn,
  editValue,
  onEditStart,
  onEditChange,
  onEditSave,
  onEditCancel,
}: WhatsAppChatViewerProps) {
  const timestamps = simulateTimestamps(conversation.turnos)

  return (
    <div className="whatsapp-bg-pattern flex flex-col gap-1 rounded-lg py-4">
      {/* Date header */}
      <div className="flex justify-center py-2">
        <span className="rounded-lg bg-white/80 px-3 py-1 text-[11px] font-medium text-gray-600 shadow-sm dark:bg-zinc-700/80 dark:text-zinc-300">
          Hoy
        </span>
      </div>

      {conversation.turnos.map((turn, i) => {
        const role = getBubbleRole(turn)
        const prevRole = i > 0 ? getBubbleRole(conversation.turnos[i - 1]) : null
        const showAvatar = role !== prevRole

        return (
          <WhatsAppBubble
            key={`wa-${turn.turno}-${i}`}
            turn={turn}
            role={role}
            timestamp={timestamps[i]}
            showAvatar={showAvatar}
            isEditing={editingTurn === i}
            editValue={editValue}
            onClickToEdit={() => onEditStart(i)}
            onEditChange={onEditChange}
            onEditSave={onEditSave}
            onEditCancel={onEditCancel}
          />
        )
      })}
    </div>
  )
}
