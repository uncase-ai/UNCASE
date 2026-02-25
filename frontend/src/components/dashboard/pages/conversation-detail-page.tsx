'use client'

import { useCallback, useRef, useState } from 'react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  Ban,
  Bot,
  Check,
  CheckCircle2,
  Code2,
  GripVertical,
  Pencil,
  Trash2,
  User,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, ConversationTurn } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'

import { JsonViewer } from '../json-viewer'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

// ─── Types ───

interface ConversationDetailPageProps {
  id: string
}

type TurnType = 'user' | 'assistant' | 'tool_call' | 'tool_result'

interface FlattenedItem {
  type: TurnType
  turnIndex: number
  turn: ConversationTurn
  toolCallIndex?: number
  toolResultIndex?: number

  /** Unique key for React rendering and drag identity */
  key: string
}

// ─── localStorage helpers ───

const STORE_KEY = 'uncase-conversations'

function loadAllConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveAllConversations(conversations: Conversation[]) {
  localStorage.setItem(STORE_KEY, JSON.stringify(conversations))
}

// ─── Role detection helpers ───

function isAssistantRole(rol: string): boolean {
  const lower = rol.toLowerCase()

  return (
    lower.includes('asistente') ||
    lower.includes('assistant') ||
    lower.includes('agente') ||
    lower.includes('agent')
  )
}

// ─── Flatten turns into renderable items ───

function flattenTurns(turnos: ConversationTurn[]): FlattenedItem[] {
  const items: FlattenedItem[] = []

  for (let i = 0; i < turnos.length; i++) {
    const turn = turnos[i]
    const baseType: TurnType = isAssistantRole(turn.rol) ? 'assistant' : 'user'

    // Main message bubble
    items.push({
      type: baseType,
      turnIndex: i,
      turn,
      key: `turn-${turn.turno}-msg`
    })

    // Tool calls as separate items (visually grouped under the turn)
    if (turn.tool_calls) {
      for (let tc = 0; tc < turn.tool_calls.length; tc++) {
        items.push({
          type: 'tool_call',
          turnIndex: i,
          turn,
          toolCallIndex: tc,
          key: `turn-${turn.turno}-tc-${tc}`
        })
      }
    }

    // Tool results as separate items
    if (turn.tool_results) {
      for (let tr = 0; tr < turn.tool_results.length; tr++) {
        items.push({
          type: 'tool_result',
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

// ─── Style config per turn type ───

const TURN_STYLES: Record<
  TurnType,
  {
    borderClass: string
    bgClass: string
    labelBgClass: string
    align: 'left' | 'right'
    icon: typeof Bot
    iconColorClass: string
    label: string
  }
> = {
  user: {
    borderClass: 'border-l-blue-500',
    bgClass: 'bg-blue-50 dark:bg-blue-950/30',
    labelBgClass: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300',
    align: 'right',
    icon: User,
    iconColorClass: 'text-blue-600 dark:text-blue-400',
    label: 'User'
  },
  assistant: {
    borderClass: 'border-l-gray-400',
    bgClass: 'bg-muted/60',
    labelBgClass: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300',
    align: 'left',
    icon: Bot,
    iconColorClass: 'text-gray-500 dark:text-gray-400',
    label: 'Assistant'
  },
  tool_call: {
    borderClass: 'border-l-amber-500',
    bgClass: 'bg-amber-50/70 dark:bg-amber-950/20',
    labelBgClass: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300',
    align: 'left',
    icon: Wrench,
    iconColorClass: 'text-amber-600 dark:text-amber-400',
    label: 'Tool Call'
  },
  tool_result: {
    borderClass: 'border-l-emerald-500',
    bgClass: 'bg-emerald-50/70 dark:bg-emerald-950/20',
    labelBgClass: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300',
    align: 'left',
    icon: Code2,
    iconColorClass: 'text-emerald-600 dark:text-emerald-400',
    label: 'Tool Result'
  }
}

// ─── TurnBubble component ───

function TurnBubble({
  item,
  editing,
  editValue,
  onEditStart,
  onEditCancel,
  onEditSave,
  onEditChange,
  isDragging,
  isDropTarget,
  onDragStart,
  onDragOver,
  onDragEnd,
  onDrop
}: {
  item: FlattenedItem
  editing: boolean
  editValue: string
  onEditStart: () => void
  onEditCancel: () => void
  onEditSave: () => void
  onEditChange: (value: string) => void
  isDragging: boolean
  isDropTarget: boolean
  onDragStart: (e: React.DragEvent) => void
  onDragOver: (e: React.DragEvent) => void
  onDragEnd: (e: React.DragEvent) => void
  onDrop: (e: React.DragEvent) => void
}) {
  const style = TURN_STYLES[item.type]
  const IconComponent = style.icon
  const { turn } = item

  const hasTools = (turn.tool_calls?.length ?? 0) > 0 || (turn.tool_results?.length ?? 0) > 0
  const isMainMessage = item.type === 'user' || item.type === 'assistant'

  return (
    <div className="relative">
      {/* Drop target indicator above */}
      {isDropTarget && (
        <div className="absolute -top-1.5 right-0 left-0 z-10 h-0.5 rounded-full bg-blue-500 shadow-sm shadow-blue-500/50" />
      )}

      <div
        draggable={isMainMessage}
        onDragStart={onDragStart}
        onDragOver={onDragOver}
        onDragEnd={onDragEnd}
        onDrop={onDrop}
        className={cn(
          'group relative flex gap-3 transition-opacity duration-200',
          style.align === 'right' ? 'flex-row-reverse' : 'flex-row',
          isDragging && 'opacity-40',
          isMainMessage && 'cursor-grab active:cursor-grabbing'
        )}
      >
        {/* Drag handle (only for main messages) */}
        {isMainMessage && (
          <div
            className={cn(
              'flex shrink-0 items-center opacity-0 transition-opacity group-hover:opacity-100',
              style.align === 'right' ? 'order-first' : ''
            )}
          >
            <GripVertical className="size-4 text-muted-foreground/50" />
          </div>
        )}

        {/* Icon avatar */}
        <div
          className={cn(
            'flex size-8 shrink-0 items-center justify-center rounded-full border',
            item.type === 'tool_call' && 'border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/40',
            item.type === 'tool_result' &&
              'border-emerald-300 bg-emerald-50 dark:border-emerald-700 dark:bg-emerald-950/40',
            item.type === 'user' && 'border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-950/40',
            item.type === 'assistant' && 'border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800'
          )}
        >
          <IconComponent className={cn('size-4', style.iconColorClass)} />
        </div>

        {/* Content area */}
        <div className={cn('max-w-[75%] space-y-1.5', style.align === 'right' ? 'items-end' : 'items-start')}>
          {/* Header row: role label + turn number + edit button */}
          <div className={cn('flex items-center gap-2', style.align === 'right' && 'flex-row-reverse')}>
            <span
              className={cn('inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-semibold', style.labelBgClass)}
            >
              {isMainMessage ? turn.rol : style.label}
            </span>
            <span className="rounded bg-muted px-1 py-0.5 font-mono text-[10px] text-muted-foreground">
              #{turn.turno}
            </span>
            {isMainMessage && !editing && (
              <button
                onClick={onEditStart}
                className="rounded p-0.5 text-muted-foreground/40 transition-colors hover:text-foreground"
              >
                <Pencil className="size-3" />
              </button>
            )}
          </div>

          {/* Render by type */}
          {isMainMessage && editing ? (
            <div className="space-y-2">
              <Textarea
                value={editValue}
                onChange={e => onEditChange(e.target.value)}
                className="min-h-20 text-sm"
                autoFocus
              />
              <div className="flex gap-1">
                <Button size="sm" variant="outline" className="h-7 gap-1 text-xs" onClick={onEditSave}>
                  <Check className="size-3" />
                  Save
                </Button>
                <Button size="sm" variant="ghost" className="h-7 gap-1 text-xs" onClick={onEditCancel}>
                  <X className="size-3" />
                  Cancel
                </Button>
              </div>
            </div>
          ) : isMainMessage ? (
            <>
              <div
                className={cn(
                  'rounded-lg border-l-[3px] px-3 py-2.5 text-sm leading-relaxed',
                  style.borderClass,
                  style.bgClass,
                  item.type === 'user' && 'text-blue-900 dark:text-blue-100'
                )}
              >
                {turn.contenido}
              </div>
              {/* Inline tool tags when no expanded tool_calls */}
              {turn.herramientas_usadas.length > 0 && !hasTools && (
                <div className="flex flex-wrap gap-1">
                  {turn.herramientas_usadas.map(h => (
                    <Badge key={h} variant="outline" className="text-[10px]">
                      {h}
                    </Badge>
                  ))}
                </div>
              )}
            </>
          ) : item.type === 'tool_call' && item.toolCallIndex !== undefined ? (
            <ToolCallCard toolCall={turn.tool_calls![item.toolCallIndex]} borderClass={style.borderClass} bgClass={style.bgClass} />
          ) : item.type === 'tool_result' && item.toolResultIndex !== undefined ? (
            <ToolResultCard toolResult={turn.tool_results![item.toolResultIndex]} borderClass={style.borderClass} bgClass={style.bgClass} />
          ) : null}
        </div>
      </div>
    </div>
  )
}

// ─── Tool Call sub-card ───

function ToolCallCard({
  toolCall,
  borderClass,
  bgClass
}: {
  toolCall: NonNullable<ConversationTurn['tool_calls']>[number]
  borderClass: string
  bgClass: string
}) {
  return (
    <div className={cn('rounded-lg border-l-[3px] px-3 py-2', borderClass, bgClass)}>
      <div className="flex items-center gap-1.5">
        <Wrench className="size-3 text-amber-600 dark:text-amber-400" />
        <span className="text-xs font-semibold text-amber-700 dark:text-amber-300">{toolCall.tool_name}</span>
        <span className="font-mono text-[10px] text-muted-foreground">({toolCall.tool_call_id.slice(0, 8)})</span>
      </div>
      <pre className="mt-1.5 overflow-x-auto rounded bg-amber-100/50 p-2 text-[11px] text-amber-900 dark:bg-amber-950/30 dark:text-amber-200">
        {JSON.stringify(toolCall.arguments, null, 2)}
      </pre>
    </div>
  )
}

// ─── Tool Result sub-card ───

function ToolResultCard({
  toolResult,
  borderClass,
  bgClass
}: {
  toolResult: NonNullable<ConversationTurn['tool_results']>[number]
  borderClass: string
  bgClass: string
}) {
  return (
    <div className={cn('rounded-lg border-l-[3px] px-3 py-2', borderClass, bgClass)}>
      <div className="flex items-center gap-1.5">
        <Code2 className="size-3 text-emerald-600 dark:text-emerald-400" />
        <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300">{toolResult.tool_name}</span>
        <StatusBadge variant={toolResult.status === 'success' ? 'success' : 'error'}>{toolResult.status}</StatusBadge>
        {toolResult.duration_ms !== undefined && (
          <span className="font-mono text-[10px] text-muted-foreground">{toolResult.duration_ms}ms</span>
        )}
      </div>
      <pre className="mt-1.5 overflow-x-auto rounded bg-emerald-100/50 p-2 text-[11px] text-emerald-900 dark:bg-emerald-950/30 dark:text-emerald-200">
        {typeof toolResult.result === 'string' ? toolResult.result : JSON.stringify(toolResult.result, null, 2)}
      </pre>
    </div>
  )
}

// ─── Main page component ───

export function ConversationDetailPage({ id }: ConversationDetailPageProps) {
  const router = useRouter()

  const [conversation, setConversation] = useState<Conversation | null>(() => {
    const all = loadAllConversations()

    return all.find(c => c.conversation_id === id) ?? null
  })

  const [showMeta, setShowMeta] = useState(false)
  const [editingTurn, setEditingTurn] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const [showDelete, setShowDelete] = useState(false)

  // Drag-and-drop state
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null)
  const dragCounter = useRef(0)

  const persistConversation = useCallback(
    (updated: Conversation) => {
      setConversation(updated)
      const all = loadAllConversations()
      const idx = all.findIndex(c => c.conversation_id === updated.conversation_id)

      if (idx >= 0) {
        all[idx] = updated
        saveAllConversations(all)
      }
    },
    []
  )

  // ─── Editing handlers ───

  const handleEditStart = useCallback(
    (turnIndex: number) => {
      if (!conversation) return

      setEditingTurn(turnIndex)
      setEditValue(conversation.turnos[turnIndex].contenido)
    },
    [conversation]
  )

  const handleEditSave = useCallback(() => {
    if (!conversation || editingTurn === null) return

    const updatedTurnos = [...conversation.turnos]

    updatedTurnos[editingTurn] = { ...updatedTurnos[editingTurn], contenido: editValue }

    persistConversation({ ...conversation, turnos: updatedTurnos })
    setEditingTurn(null)
    setEditValue('')
  }, [conversation, editingTurn, editValue, persistConversation])

  const handleEditCancel = useCallback(() => {
    setEditingTurn(null)
    setEditValue('')
  }, [])

  // ─── Status & delete handlers ───

  const handleToggleStatus = useCallback(() => {
    if (!conversation) return

    const current = conversation.status ?? 'valid'

    persistConversation({ ...conversation, status: current === 'valid' ? 'invalid' : 'valid' })
  }, [conversation, persistConversation])

  const handleDelete = useCallback(() => {
    const all = loadAllConversations()
    const updated = all.filter(c => c.conversation_id !== id)

    saveAllConversations(updated)
    router.push('/dashboard/conversations')
  }, [id, router])

  // ─── Drag-and-drop handlers (operates on turn indices) ───

  const handleDragStart = useCallback(
    (turnIndex: number) => (e: React.DragEvent) => {
      setDragIndex(turnIndex)
      dragCounter.current = 0
      e.dataTransfer.effectAllowed = 'move'
      e.dataTransfer.setData('text/plain', String(turnIndex))
    },
    []
  )

  const handleDragOver = useCallback(
    (turnIndex: number) => (e: React.DragEvent) => {
      e.preventDefault()
      e.dataTransfer.dropEffect = 'move'

      if (dragIndex !== null && turnIndex !== dragIndex) {
        setDropTargetIndex(turnIndex)
      }
    },
    [dragIndex]
  )

  const handleDrop = useCallback(
    (turnIndex: number) => (e: React.DragEvent) => {
      e.preventDefault()
      setDropTargetIndex(null)
      dragCounter.current = 0

      if (!conversation || dragIndex === null || dragIndex === turnIndex) {
        setDragIndex(null)

        return
      }

      const newTurnos = [...conversation.turnos]
      const [moved] = newTurnos.splice(dragIndex, 1)

      newTurnos.splice(turnIndex, 0, moved)

      // Re-number turno fields sequentially
      const renumbered = newTurnos.map((t, i) => ({ ...t, turno: i + 1 }))

      persistConversation({ ...conversation, turnos: renumbered })
      setDragIndex(null)
    },
    [conversation, dragIndex, persistConversation]
  )

  const handleDragEnd = useCallback(() => {
    setDragIndex(null)
    setDropTargetIndex(null)
    dragCounter.current = 0
  }, [])

  // ─── Render ───

  if (!conversation) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Conversation Not Found"
          actions={
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/conversations">
                <ArrowLeft className="mr-1 size-3" /> Back
              </Link>
            </Button>
          }
        />
        <p className="text-sm text-muted-foreground">No conversation with ID &quot;{id}&quot; found in local store.</p>
      </div>
    )
  }

  const status = conversation.status ?? 'valid'
  const flatItems = flattenTurns(conversation.turnos)

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Conversation ${conversation.conversation_id.slice(0, 12)}...`}
        description={`${conversation.turnos.length} turns — ${conversation.dominio} — ${conversation.es_sintetica ? 'Synthetic' : 'Real'}`}
        actions={
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={handleToggleStatus}
            >
              {status === 'valid' ? (
                <>
                  <Ban className="size-3" />
                  Mark Invalid
                </>
              ) : (
                <>
                  <CheckCircle2 className="size-3" />
                  Mark Valid
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={() => setShowDelete(true)}
            >
              <Trash2 className="size-3" />
              Delete
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowMeta(!showMeta)}>
              {showMeta ? 'Hide' : 'Show'} Metadata
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/conversations">
                <ArrowLeft className="mr-1 size-3" /> Back
              </Link>
            </Button>
          </div>
        }
      />

      {/* Status banner when invalid */}
      {status === 'invalid' && (
        <div className="flex items-center gap-2 rounded-lg border border-dashed px-4 py-2.5">
          <Ban className="size-4 shrink-0 text-muted-foreground" />
          <p className="text-xs text-muted-foreground">
            This conversation is marked as <span className="font-medium">invalid</span> and will be excluded from
            exports and evaluations.
          </p>
          <Button variant="outline" size="sm" className="ml-auto h-7 gap-1 text-xs" onClick={handleToggleStatus}>
            <CheckCircle2 className="size-3" />
            Restore
          </Button>
        </div>
      )}

      <div className="flex gap-4">
        {/* Chat view */}
        <div className="flex-1 space-y-3">
          {flatItems.map(item => {
            const isMainMsg = item.type === 'user' || item.type === 'assistant'

            return (
              <TurnBubble
                key={item.key}
                item={item}
                editing={isMainMsg && editingTurn === item.turnIndex}
                editValue={editValue}
                onEditStart={() => handleEditStart(item.turnIndex)}
                onEditCancel={handleEditCancel}
                onEditSave={handleEditSave}
                onEditChange={setEditValue}
                isDragging={isMainMsg && dragIndex === item.turnIndex}
                isDropTarget={isMainMsg && dropTargetIndex === item.turnIndex}
                onDragStart={isMainMsg ? handleDragStart(item.turnIndex) : (e: React.DragEvent) => e.preventDefault()}
                onDragOver={isMainMsg ? handleDragOver(item.turnIndex) : (e: React.DragEvent) => e.preventDefault()}
                onDrop={isMainMsg ? handleDrop(item.turnIndex) : (e: React.DragEvent) => e.preventDefault()}
                onDragEnd={handleDragEnd}
              />
            )
          })}
        </div>

        {/* Metadata sidebar */}
        {showMeta && (
          <Card className="hidden w-80 shrink-0 lg:block">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div>
                <span className="text-muted-foreground">Conversation ID</span>
                <p className="font-mono">{conversation.conversation_id}</p>
              </div>
              <Separator />
              <div>
                <span className="text-muted-foreground">Status</span>
                <div className="mt-1">
                  <StatusBadge variant={status === 'valid' ? 'success' : 'warning'} dot={false}>
                    {status === 'valid' ? 'Valid' : 'Invalid'}
                  </StatusBadge>
                </div>
              </div>
              <Separator />
              <div>
                <span className="text-muted-foreground">Seed ID</span>
                <p className="font-mono">{conversation.seed_id}</p>
              </div>
              <Separator />
              <div>
                <span className="text-muted-foreground">Domain</span>
                <p>{conversation.dominio}</p>
              </div>
              <Separator />
              <div>
                <span className="text-muted-foreground">Language</span>
                <p>{conversation.idioma}</p>
              </div>
              <Separator />
              <div>
                <span className="text-muted-foreground">Roles</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {[...new Set(conversation.turnos.map(t => t.rol))].map(r => (
                    <Badge key={r} variant="secondary" className="text-[10px]">
                      {r}
                    </Badge>
                  ))}
                </div>
              </div>
              {Object.keys(conversation.metadata).length > 0 && (
                <>
                  <Separator />
                  <div>
                    <span className="text-muted-foreground">Extra Metadata</span>
                    <JsonViewer data={conversation.metadata} maxHeight="200px" />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Delete confirmation dialog */}
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
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
