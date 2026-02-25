'use client'

import { useCallback, useMemo, useRef, useState } from 'react'

import Link from 'next/link'
import {
  Ban,
  Bot,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  MessageSquare,
  Plus,
  Save,
  ShieldCheck,
  Star,
  Trash2,
  User,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, ConversationTurn } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Rating } from '@/components/ui/rating'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { SearchInput } from '../search-input'
import { StatusBadge } from '../status-badge'

// ─── Local store ───

const STORE_KEY = 'uncase-conversations'

function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function saveConversations(conversations: Conversation[]) {
  localStorage.setItem(STORE_KEY, JSON.stringify(conversations))
}

export function appendConversations(newConvs: Conversation[]) {
  const existing = loadConversations()
  const ids = new Set(existing.map(c => c.conversation_id))
  const unique = newConvs.filter(c => !ids.has(c.conversation_id))

  saveConversations([...existing, ...unique])
}

// ─── Role helpers ───

function isAssistantRole(rol: string): boolean {
  const lower = rol.toLowerCase()

  return (
    lower.includes('asistente') ||
    lower.includes('assistant') ||
    lower.includes('agente') ||
    lower.includes('agent')
  )
}

function isSystemRole(rol: string): boolean {
  return rol.toLowerCase() === 'system' || rol.toLowerCase() === 'sistema'
}

type MessageRole = 'system' | 'user' | 'assistant' | 'tool_call' | 'tool_result'

function getMessageRole(turn: ConversationTurn): MessageRole {
  if (isSystemRole(turn.rol)) return 'system'
  if (isAssistantRole(turn.rol)) return 'assistant'

  return 'user'
}

// ─── Flatten turns ───

interface FlatItem {
  role: MessageRole
  turnIndex: number
  turn: ConversationTurn
  toolCallIndex?: number
  toolResultIndex?: number
  key: string
}

function flattenTurns(turnos: ConversationTurn[]): FlatItem[] {
  const items: FlatItem[] = []

  for (let i = 0; i < turnos.length; i++) {
    const turn = turnos[i]
    const role = getMessageRole(turn)

    items.push({ role, turnIndex: i, turn, key: `turn-${turn.turno}-msg` })

    if (turn.tool_calls) {
      for (let tc = 0; tc < turn.tool_calls.length; tc++) {
        items.push({ role: 'tool_call', turnIndex: i, turn, toolCallIndex: tc, key: `turn-${turn.turno}-tc-${tc}` })
      }
    }

    if (turn.tool_results) {
      for (let tr = 0; tr < turn.tool_results.length; tr++) {
        items.push({
          role: 'tool_result',
          turnIndex: i,
          turn,
          toolResultIndex: tr,
          key: `turn-${turn.turno}-tr-${tr}`
        })
      }
    }
  }

  return items
}

// ─── Style config per role ───

const ROLE_STYLES: Record<MessageRole, { label: string; labelClass: string; bgClass: string; borderClass: string; icon: typeof Bot; iconClass: string }> = {
  system: {
    label: 'SYSTEM',
    labelClass: 'text-violet-700 dark:text-violet-300',
    bgClass: 'bg-violet-50/60 dark:bg-violet-950/20',
    borderClass: 'border-violet-200 dark:border-violet-800/50',
    icon: ShieldCheck,
    iconClass: 'text-violet-500 dark:text-violet-400'
  },
  user: {
    label: 'USER',
    labelClass: 'text-sky-700 dark:text-sky-300',
    bgClass: 'bg-sky-50/50 dark:bg-sky-950/20',
    borderClass: 'border-sky-200 dark:border-sky-800/50',
    icon: User,
    iconClass: 'text-sky-500 dark:text-sky-400'
  },
  assistant: {
    label: 'ASSISTANT',
    labelClass: 'text-zinc-600 dark:text-zinc-300',
    bgClass: 'bg-zinc-50/60 dark:bg-zinc-900/40',
    borderClass: 'border-zinc-200 dark:border-zinc-700/50',
    icon: Bot,
    iconClass: 'text-zinc-500 dark:text-zinc-400'
  },
  tool_call: {
    label: 'TOOL CALL',
    labelClass: 'text-amber-700 dark:text-amber-300',
    bgClass: 'bg-amber-50/50 dark:bg-amber-950/20',
    borderClass: 'border-amber-200 dark:border-amber-800/50',
    icon: Wrench,
    iconClass: 'text-amber-500 dark:text-amber-400'
  },
  tool_result: {
    label: 'TOOL RESULT',
    labelClass: 'text-teal-700 dark:text-teal-300',
    bgClass: 'bg-teal-50/50 dark:bg-teal-950/20',
    borderClass: 'border-teal-200 dark:border-teal-800/50',
    icon: Code2,
    iconClass: 'text-teal-500 dark:text-teal-400'
  }
}

// ─── Conversation summary helper ───

function buildSummary(conv: Conversation): string {
  const turns = conv.turnos

  if (turns.length === 0) return 'Empty conversation'

  const userTurns = turns.filter(t => !isAssistantRole(t.rol) && !isSystemRole(t.rol))
  const firstUser = userTurns[0]

  if (!firstUser) return turns[0].contenido.slice(0, 120)

  return firstUser.contenido.slice(0, 120) + (firstUser.contenido.length > 120 ? '...' : '')
}

function getToolCallNames(conv: Conversation): string[] {
  const names = new Set<string>()

  for (const t of conv.turnos) {
    for (const h of t.herramientas_usadas) names.add(h)

    if (t.tool_calls) {
      for (const tc of t.tool_calls) names.add(tc.tool_name)
    }
  }

  return [...names]
}

// ─── Conversation card in the list ───

function ConversationCard({
  conv,
  index,
  isSelected,
  onSelect
}: {
  conv: Conversation
  index: number
  isSelected: boolean
  onSelect: () => void
}) {
  const preview = buildSummary(conv)
  const tools = getToolCallNames(conv)
  const status = conv.status ?? 'valid'

  return (
    <button
      onClick={onSelect}
      className={cn(
        'w-full text-left rounded-lg border p-3 transition-all',
        'hover:border-foreground/20 hover:shadow-sm',
        isSelected
          ? 'border-foreground/30 bg-muted/50 shadow-sm ring-1 ring-foreground/10'
          : 'border-border bg-background'
      )}
    >
      <div className="flex items-start gap-2">
        <span className="shrink-0 font-mono text-xs font-bold text-muted-foreground">#{index + 1}</span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1.5">
            {tools.slice(0, 2).map(t => (
              <Badge key={t} variant="secondary" className="text-[10px] font-medium">
                TC {t}
              </Badge>
            ))}
            {tools.length > 2 && (
              <Badge variant="secondary" className="text-[10px]">+{tools.length - 2}</Badge>
            )}
            <StatusBadge variant={status === 'valid' ? 'success' : 'warning'} dot={false} className="text-[10px]">
              {status === 'valid' ? 'OK' : 'Invalid'}
            </StatusBadge>
          </div>
          <p className="mt-1.5 line-clamp-2 text-sm leading-snug">{preview}</p>
          <div className="mt-1.5 flex items-center gap-2">
            <span className="text-[11px] text-muted-foreground">{conv.turnos.length} msgs</span>
            {(conv.rating ?? 0) > 0 && (
              <div className="flex items-center gap-0.5">
                {Array.from({ length: conv.rating ?? 0 }).map((_, i) => (
                  <Star key={i} className="size-2.5 fill-amber-500 text-amber-500" />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </button>
  )
}

// ─── Message bubble (click-to-edit) ───

function MessageBubble({
  item,
  isEditing,
  editValue,
  onClickToEdit,
  onEditChange,
  onEditSave,
  onEditCancel
}: {
  item: FlatItem
  isEditing: boolean
  editValue: string
  onClickToEdit: () => void
  onEditChange: (v: string) => void
  onEditSave: () => void
  onEditCancel: () => void
}) {
  const style = ROLE_STYLES[item.role]
  const Icon = style.icon
  const isMainMsg = item.role === 'user' || item.role === 'assistant' || item.role === 'system'
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  const handleTextareaChange = (v: string) => {
    onEditChange(v)

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }

  // Tool call rendering
  if (item.role === 'tool_call' && item.toolCallIndex !== undefined) {
    const tc = item.turn.tool_calls![item.toolCallIndex]

    return (
      <ToolCallBlock
        toolName={tc.tool_name}
        toolCallId={tc.tool_call_id}
        args={tc.arguments}
      />
    )
  }

  // Tool result rendering
  if (item.role === 'tool_result' && item.toolResultIndex !== undefined) {
    const tr = item.turn.tool_results![item.toolResultIndex]

    return (
      <ToolResultBlock
        toolName={tr.tool_name}
        status={tr.status}
        result={tr.result}
        durationMs={tr.duration_ms}
      />
    )
  }

  // Parse tool_call blocks inside message content
  const { textParts, toolBlocks } = parseToolCallsFromContent(item.turn.contenido)

  return (
    <div className={cn('rounded-lg border p-3', style.bgClass, style.borderClass)}>
      {/* Role label */}
      <div className="mb-2 flex items-center gap-2">
        <Icon className={cn('size-3.5', style.iconClass)} />
        <span className={cn('text-[11px] font-bold uppercase tracking-wide', style.labelClass)}>
          {style.label}
        </span>
        <span className="font-mono text-[10px] text-muted-foreground">#{item.turn.turno}</span>
      </div>

      {/* Content — click to edit */}
      {isEditing ? (
        <div className="space-y-2">
          <Textarea
            ref={textareaRef}
            value={editValue}
            onChange={e => handleTextareaChange(e.target.value)}
            className="min-h-20 resize-none border-primary/30 bg-background text-sm focus-visible:ring-primary/20"
            autoFocus
            onKeyDown={e => {
              if (e.key === 'Escape') onEditCancel()
            }}
          />
          <div className="flex justify-end gap-1.5">
            <Button size="sm" variant="ghost" className="h-7 gap-1 text-xs" onClick={onEditCancel}>
              Cancel
            </Button>
            <Button size="sm" className="h-7 gap-1 text-xs" onClick={onEditSave}>
              <Check className="size-3" />
              Apply
            </Button>
          </div>
        </div>
      ) : (
        <div
          className={cn(
            'cursor-text rounded-md px-1 py-0.5 -mx-1 -my-0.5 transition-colors',
            isMainMsg && 'hover:bg-foreground/5'
          )}
          onClick={isMainMsg ? onClickToEdit : undefined}
        >
          {/* Render text parts */}
          {textParts.map((text, i) => (
            <p key={`text-${i}`} className="whitespace-pre-wrap text-sm leading-relaxed">
              {text}
            </p>
          ))}

          {/* Render inline tool_call blocks from content */}
          {toolBlocks.map((block, i) => (
            <div key={`tool-inline-${i}`} className="mt-2">
              <InlineToolCallBlock content={block} />
            </div>
          ))}

          {/* Tool usage tags */}
          {item.turn.herramientas_usadas.length > 0 && !item.turn.tool_calls?.length && (
            <div className="mt-2 flex flex-wrap gap-1">
              {item.turn.herramientas_usadas.map(h => (
                <Badge key={h} variant="outline" className="text-[10px]">
                  <Wrench className="mr-0.5 size-2.5" />
                  {h}
                </Badge>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Parse tool_call blocks embedded in content string ───

function parseToolCallsFromContent(content: string): { textParts: string[]; toolBlocks: string[] } {
  const regex = /<tool_call>([\s\S]*?)<\/tool_call>/g
  const textParts: string[] = []
  const toolBlocks: string[] = []
  let lastIndex = 0
  let match = regex.exec(content)

  while (match !== null) {
    const before = content.slice(lastIndex, match.index).trim()

    if (before) textParts.push(before)
    toolBlocks.push(match[1].trim())
    lastIndex = match.index + match[0].length
    match = regex.exec(content)
  }

  const after = content.slice(lastIndex).trim()

  if (after) textParts.push(after)
  if (textParts.length === 0 && toolBlocks.length === 0) textParts.push(content)

  return { textParts, toolBlocks }
}

// ─── Inline tool call block (from content string) ───

function InlineToolCallBlock({ content }: { content: string }) {
  return (
    <div className="rounded-md border border-amber-200 bg-amber-50/60 p-2 dark:border-amber-800/50 dark:bg-amber-950/30">
      <div className="mb-1 flex items-center gap-1.5">
        <Wrench className="size-3 text-amber-600 dark:text-amber-400" />
        <span className="text-[10px] font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-300">
          Tool Call
        </span>
      </div>
      <pre className="overflow-x-auto text-[11px] leading-relaxed text-amber-900 dark:text-amber-200">
        {content}
      </pre>
    </div>
  )
}

// ─── Structured tool call block ───

function ToolCallBlock({
  toolName,
  toolCallId,
  args
}: {
  toolName: string
  toolCallId: string
  args: Record<string, unknown>
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="ml-6 rounded-lg border border-amber-200 bg-amber-50/40 dark:border-amber-800/50 dark:bg-amber-950/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left"
      >
        {expanded ? (
          <ChevronDown className="size-3 text-amber-600 dark:text-amber-400" />
        ) : (
          <ChevronRight className="size-3 text-amber-600 dark:text-amber-400" />
        )}
        <Wrench className="size-3 text-amber-600 dark:text-amber-400" />
        <span className="text-xs font-semibold text-amber-700 dark:text-amber-300">{toolName}</span>
        <span className="font-mono text-[10px] text-muted-foreground">({toolCallId.slice(0, 8)})</span>
      </button>
      {expanded && (
        <div className="border-t border-amber-200/60 px-3 py-2 dark:border-amber-800/40">
          <pre className="overflow-x-auto text-[11px] leading-relaxed text-amber-900 dark:text-amber-200">
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

// ─── Structured tool result block ───

function ToolResultBlock({
  toolName,
  status,
  result,
  durationMs
}: {
  toolName: string
  status: 'success' | 'error' | 'timeout'
  result: Record<string, unknown> | string
  durationMs?: number
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="ml-6 rounded-lg border border-teal-200 bg-teal-50/40 dark:border-teal-800/50 dark:bg-teal-950/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left"
      >
        {expanded ? (
          <ChevronDown className="size-3 text-teal-600 dark:text-teal-400" />
        ) : (
          <ChevronRight className="size-3 text-teal-600 dark:text-teal-400" />
        )}
        <Code2 className="size-3 text-teal-600 dark:text-teal-400" />
        <span className="text-xs font-semibold text-teal-700 dark:text-teal-300">{toolName}</span>
        <StatusBadge variant={status === 'success' ? 'success' : 'error'} className="text-[10px]">
          {status}
        </StatusBadge>
        {durationMs !== undefined && (
          <span className="font-mono text-[10px] text-muted-foreground">{durationMs}ms</span>
        )}
      </button>
      {expanded && (
        <div className="border-t border-teal-200/60 px-3 py-2 dark:border-teal-800/40">
          <pre className="overflow-x-auto text-[11px] leading-relaxed text-teal-900 dark:text-teal-200">
            {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

// ─── Review panel (tags, rating, notes) ───

function ReviewPanel({
  conversation,
  onUpdate
}: {
  conversation: Conversation
  onUpdate: (updates: Partial<Conversation>) => void
}) {
  const [newTag, setNewTag] = useState('')
  const tags = conversation.tags ?? []
  const rating = conversation.rating ?? 0
  const notes = conversation.notes ?? ''

  const addTag = () => {
    const tag = newTag.trim()

    if (!tag || tags.includes(tag)) return
    onUpdate({ tags: [...tags, tag] })
    setNewTag('')
  }

  const removeTag = (tag: string) => {
    onUpdate({ tags: tags.filter(t => t !== tag) })
  }

  return (
    <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
      {/* Tags */}
      <div>
        <label className="text-xs font-semibold text-muted-foreground">Tags</label>
        <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
          {tags.map(tag => (
            <Badge key={tag} variant="secondary" className="gap-1 pr-1">
              {tag}
              <button
                onClick={() => removeTag(tag)}
                className="rounded-full p-0.5 hover:bg-foreground/10"
              >
                <X className="size-2.5" />
              </button>
            </Badge>
          ))}
          <div className="flex items-center gap-1">
            <Input
              value={newTag}
              onChange={e => setNewTag(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') addTag() }}
              placeholder="+ tag"
              className="h-6 w-20 border-dashed px-2 text-[11px]"
            />
            {newTag && (
              <Button size="sm" variant="ghost" className="h-6 px-1" onClick={addTag}>
                <Plus className="size-3" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Rating */}
      <div>
        <label className="text-xs font-semibold text-muted-foreground">Rating</label>
        <div className="mt-1">
          <Rating
            value={rating}
            onValueChange={v => onUpdate({ rating: v })}
            variant="yellow"
            size={18}
          />
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="text-xs font-semibold text-muted-foreground">Notes</label>
        <Textarea
          value={notes}
          onChange={e => onUpdate({ notes: e.target.value })}
          placeholder="Review notes..."
          className="mt-1 min-h-16 resize-none text-sm"
        />
      </div>
    </div>
  )
}

// ─── Detail panel ───

function DetailPanel({
  conversation,
  onPersist,
  onDelete
}: {
  conversation: Conversation
  onPersist: (updated: Conversation) => void
  onDelete: () => void
}) {
  const [editingTurn, setEditingTurn] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const [showDelete, setShowDelete] = useState(false)
  const [pendingChanges, setPendingChanges] = useState<Partial<Conversation>>({})

  const status = conversation.status ?? 'valid'
  const flatItems = flattenTurns(conversation.turnos)

  // Merge pending changes with conversation for display
  const displayConv = { ...conversation, ...pendingChanges }

  const handleEditStart = (turnIndex: number) => {
    setEditingTurn(turnIndex)
    setEditValue(conversation.turnos[turnIndex].contenido)
  }

  const handleEditSave = () => {
    if (editingTurn === null) return

    const updatedTurnos = [...conversation.turnos]

    updatedTurnos[editingTurn] = { ...updatedTurnos[editingTurn], contenido: editValue }
    onPersist({ ...conversation, ...pendingChanges, turnos: updatedTurnos })
    setEditingTurn(null)
    setEditValue('')
  }

  const handleEditCancel = () => {
    setEditingTurn(null)
    setEditValue('')
  }

  const handleToggleStatus = () => {
    const current = conversation.status ?? 'valid'
    const next = current === 'valid' ? 'invalid' as const : 'valid' as const

    onPersist({ ...conversation, ...pendingChanges, status: next })
  }

  const handleReviewUpdate = (updates: Partial<Conversation>) => {
    setPendingChanges(prev => ({ ...prev, ...updates }))
  }

  const handleSave = () => {
    onPersist({ ...conversation, ...pendingChanges })
    setPendingChanges({})
  }

  const handleValidate = () => {
    onPersist({ ...conversation, ...pendingChanges, status: 'valid' })
    setPendingChanges({})
  }

  const hasPendingChanges = Object.keys(pendingChanges).length > 0

  // Conversation summary
  const toolNames = getToolCallNames(conversation)
  const userCount = conversation.turnos.filter(t => !isAssistantRole(t.rol) && !isSystemRole(t.rol)).length
  const assistantCount = conversation.turnos.filter(t => isAssistantRole(t.rol)).length

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="shrink-0 border-b p-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              Conversation <span className="font-mono text-base">{conversation.conversation_id.slice(0, 12)}...</span>
            </h2>
            <p className="text-sm text-muted-foreground">
              {conversation.turnos.length} messages &middot; {conversation.dominio} &middot; {conversation.es_sintetica ? 'Synthetic' : 'Real'}
            </p>
          </div>
          <div className="flex items-center gap-1.5">
            <StatusBadge variant={status === 'valid' ? 'success' : 'warning'} dot={false}>
              {status === 'valid' ? 'Valid' : 'Invalid'}
            </StatusBadge>
          </div>
        </div>

        {/* Summary bar */}
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <User className="size-3" /> {userCount} user
          </span>
          <span className="flex items-center gap-1">
            <Bot className="size-3" /> {assistantCount} assistant
          </span>
          {toolNames.length > 0 && (
            <span className="flex items-center gap-1">
              <Wrench className="size-3" /> {toolNames.length} tool{toolNames.length > 1 ? 's' : ''}
            </span>
          )}
          <span className="font-mono">{conversation.idioma}</span>
        </div>
      </div>

      {/* Invalid banner */}
      {status === 'invalid' && (
        <div className="flex items-center gap-2 border-b px-4 py-2 bg-destructive/5">
          <Ban className="size-3.5 text-destructive/70" />
          <span className="text-xs text-destructive/80">
            Marked as invalid — excluded from exports and evaluations.
          </span>
          <Button variant="outline" size="sm" className="ml-auto h-6 text-[10px]" onClick={handleToggleStatus}>
            Restore
          </Button>
        </div>
      )}

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div className="space-y-2 p-4">
          {flatItems.map(item => {
            const isMainMsg = item.role === 'user' || item.role === 'assistant' || item.role === 'system'

            return (
              <MessageBubble
                key={item.key}
                item={item}
                isEditing={isMainMsg && editingTurn === item.turnIndex}
                editValue={editValue}
                onClickToEdit={() => handleEditStart(item.turnIndex)}
                onEditChange={setEditValue}
                onEditSave={handleEditSave}
                onEditCancel={handleEditCancel}
              />
            )
          })}
        </div>
      </ScrollArea>

      {/* Review panel */}
      <div className="shrink-0 border-t p-4">
        <ReviewPanel conversation={displayConv} onUpdate={handleReviewUpdate} />

        {/* Action buttons */}
        <div className="mt-3 flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={handleValidate}
          >
            <CheckCircle2 className="size-3.5" />
            Validate
          </Button>
          <Button
            size="sm"
            className="gap-1.5"
            onClick={handleSave}
            disabled={!hasPendingChanges}
          >
            <Save className="size-3.5" />
            Save
          </Button>
          <div className="flex-1" />
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={handleToggleStatus}
          >
            {status === 'valid' ? (
              <><Ban className="size-3.5" /> Mark Invalid</>
            ) : (
              <><CheckCircle2 className="size-3.5" /> Mark Valid</>
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 text-destructive hover:bg-destructive/10"
            onClick={() => setShowDelete(true)}
          >
            <Trash2 className="size-3.5" />
            Delete
          </Button>
        </div>
      </div>

      {/* Delete confirmation */}
      <Dialog open={showDelete} onOpenChange={setShowDelete}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Conversation</DialogTitle>
            <DialogDescription>
              This will permanently remove this conversation from your local store. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button variant="destructive" onClick={() => { setShowDelete(false); onDelete() }}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ─── Pagination ───

const PAGE_SIZE = 50

function Pagination({
  total,
  page,
  onPageChange
}: {
  total: number
  page: number
  onPageChange: (p: number) => void
}) {
  const totalPages = Math.ceil(total / PAGE_SIZE)

  if (totalPages <= 1) return null

  const start = page * PAGE_SIZE + 1
  const end = Math.min((page + 1) * PAGE_SIZE, total)

  return (
    <div className="flex items-center justify-center gap-3 py-2 text-xs text-muted-foreground">
      <Button
        variant="ghost"
        size="sm"
        className="h-7 text-xs"
        disabled={page === 0}
        onClick={() => onPageChange(page - 1)}
      >
        Previous
      </Button>
      <span>{start}-{end} of {total}</span>
      <Button
        variant="ghost"
        size="sm"
        className="h-7 text-xs"
        disabled={page >= totalPages - 1}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </Button>
    </div>
  )
}

// ─── Main page ───

export function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>(() => loadConversations())
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [syntheticFilter, setSyntheticFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [ratingFilter, setRatingFilter] = useState<string>('all')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [page, setPage] = useState(0)

  const persist = useCallback(
    (updated: Conversation[]) => {
      setConversations(updated)
      saveConversations(updated)
    },
    []
  )

  const filtered = useMemo(() => {
    let result = conversations

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        c =>
          c.conversation_id.toLowerCase().includes(q) ||
          c.seed_id.toLowerCase().includes(q) ||
          c.turnos.some(t => t.contenido.toLowerCase().includes(q))
      )
    }

    if (domainFilter !== 'all') {
      result = result.filter(c => c.dominio === domainFilter)
    }

    if (syntheticFilter !== 'all') {
      result = result.filter(c => (syntheticFilter === 'synthetic' ? c.es_sintetica : !c.es_sintetica))
    }

    if (statusFilter !== 'all') {
      result = result.filter(c => (c.status ?? 'valid') === statusFilter)
    }

    if (ratingFilter !== 'all') {
      const r = Number(ratingFilter)

      result = result.filter(c => (c.rating ?? 0) === r)
    }

    return result
  }, [conversations, search, domainFilter, syntheticFilter, statusFilter, ratingFilter])

  const paged = useMemo(() => {
    const start = page * PAGE_SIZE
    const end = start + PAGE_SIZE

    return filtered.slice(start, end)
  }, [filtered, page])

  const selectedConversation = useMemo(
    () => (selectedId ? conversations.find(c => c.conversation_id === selectedId) ?? null : null),
    [selectedId, conversations]
  )

  const handlePersistConversation = useCallback(
    (updated: Conversation) => {
      const all = conversations.map(c => (c.conversation_id === updated.conversation_id ? updated : c))

      persist(all)
    },
    [conversations, persist]
  )

  const handleDeleteConversation = useCallback(
    (id: string) => {
      const all = conversations.filter(c => c.conversation_id !== id)

      persist(all)
      if (selectedId === id) setSelectedId(null)
    },
    [conversations, persist, selectedId]
  )

  // Reset page when filters change
  const handleFilterChange = <T,>(setter: (v: T) => void) => (v: T) => {
    setter(v)
    setPage(0)
  }

  if (conversations.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Conversations" description="Browse, search, and inspect conversation data" />
        <EmptyState
          icon={MessageSquare}
          title="No conversations yet"
          description="Import data or generate synthetic conversations to see them here."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/pipeline/import">Import Data</Link>
            </Button>
          }
        />
      </div>
    )
  }

  const invalidCount = conversations.filter(c => c.status === 'invalid').length

  return (
    <div className="flex h-[calc(100vh-6rem)] flex-col">
      <PageHeader
        title="Conversations"
        description={`${conversations.length} conversations${invalidCount > 0 ? ` (${invalidCount} invalid)` : ''}`}
      />

      <div className="flex min-h-0 flex-1 gap-0 overflow-hidden rounded-lg border">
        {/* ─── Left: Conversation list ─── */}
        <div className="flex w-96 shrink-0 flex-col border-r bg-muted/20">
          {/* Filters */}
          <div className="shrink-0 space-y-2 border-b p-3">
            <SearchInput
              value={search}
              onChange={handleFilterChange(setSearch)}
              placeholder="Search conversations..."
              className="w-full"
            />
            <div className="flex flex-wrap gap-1.5">
              <Select value={domainFilter} onValueChange={handleFilterChange(setDomainFilter)}>
                <SelectTrigger className="h-7 w-auto min-w-24 text-xs">
                  <SelectValue placeholder="Domain" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Domains</SelectItem>
                  {SUPPORTED_DOMAINS.map(d => (
                    <SelectItem key={d} value={d}>{d.split('.').pop()}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={syntheticFilter} onValueChange={handleFilterChange(setSyntheticFilter)}>
                <SelectTrigger className="h-7 w-auto min-w-20 text-xs">
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="real">Real</SelectItem>
                  <SelectItem value="synthetic">Synthetic</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={handleFilterChange(setStatusFilter)}>
                <SelectTrigger className="h-7 w-auto min-w-20 text-xs">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="valid">Valid</SelectItem>
                  <SelectItem value="invalid">Invalid</SelectItem>
                </SelectContent>
              </Select>
              <Select value={ratingFilter} onValueChange={handleFilterChange(setRatingFilter)}>
                <SelectTrigger className="h-7 w-auto min-w-20 text-xs">
                  <SelectValue placeholder="Rating" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Ratings</SelectItem>
                  <SelectItem value="0">Unrated</SelectItem>
                  {[1, 2, 3, 4, 5].map(r => (
                    <SelectItem key={r} value={String(r)}>
                      {'★'.repeat(r)}{'☆'.repeat(5 - r)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="text-[11px] text-muted-foreground">{filtered.length} results</div>
          </div>

          {/* Conversation cards */}
          <ScrollArea className="flex-1">
            <div className="space-y-1.5 p-2">
              {paged.map((conv, i) => (
                <ConversationCard
                  key={conv.conversation_id}
                  conv={conv}
                  index={page * PAGE_SIZE + i}
                  isSelected={selectedId === conv.conversation_id}
                  onSelect={() => setSelectedId(conv.conversation_id)}
                />
              ))}
            </div>
          </ScrollArea>

          {/* Pagination */}
          <div className="shrink-0 border-t">
            <Pagination total={filtered.length} page={page} onPageChange={setPage} />
          </div>
        </div>

        {/* ─── Right: Detail panel ─── */}
        <div className="flex-1 bg-background">
          {selectedConversation ? (
            <DetailPanel
              key={selectedConversation.conversation_id}
              conversation={selectedConversation}
              onPersist={handlePersistConversation}
              onDelete={() => handleDeleteConversation(selectedConversation.conversation_id)}
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <MessageSquare className="mx-auto size-10 text-muted-foreground/30" />
                <p className="mt-3 text-sm text-muted-foreground">Select a conversation to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
