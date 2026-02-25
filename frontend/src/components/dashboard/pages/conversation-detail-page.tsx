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
  ChevronDown,
  ChevronRight,
  Code2,
  Plus,
  ShieldCheck,
  Trash2,
  User,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, ConversationTurn } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'

import { JsonViewer } from '../json-viewer'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

// ─── Types ───

interface ConversationDetailPageProps {
  id: string
}

type MessageRole = 'system' | 'user' | 'assistant' | 'tool_call' | 'tool_result'

interface FlatItem {
  role: MessageRole
  turnIndex: number
  turn: ConversationTurn
  toolCallIndex?: number
  toolResultIndex?: number
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

function isSystemRole(rol: string): boolean {
  return rol.toLowerCase() === 'system' || rol.toLowerCase() === 'sistema'
}

function getMessageRole(turn: ConversationTurn): MessageRole {
  if (isSystemRole(turn.rol)) return 'system'
  if (isAssistantRole(turn.rol)) return 'assistant'

  return 'user'
}

// ─── Flatten turns ───

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

// ─── Parse tool_call blocks from content ───

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

// ─── Helpers ───

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

    return <ToolCallBlock toolName={tc.tool_name} toolCallId={tc.tool_call_id} args={tc.arguments} />
  }

  // Tool result rendering
  if (item.role === 'tool_result' && item.toolResultIndex !== undefined) {
    const tr = item.turn.tool_results![item.toolResultIndex]

    return <ToolResultBlock toolName={tr.tool_name} status={tr.status} result={tr.result} durationMs={tr.duration_ms} />
  }

  const { textParts, toolBlocks } = parseToolCallsFromContent(item.turn.contenido)

  return (
    <div className={cn('rounded-lg border p-3', style.bgClass, style.borderClass)}>
      <div className="mb-2 flex items-center gap-2">
        <Icon className={cn('size-3.5', style.iconClass)} />
        <span className={cn('text-[11px] font-bold uppercase tracking-wide', style.labelClass)}>
          {style.label}
        </span>
        <span className="font-mono text-[10px] text-muted-foreground">#{item.turn.turno}</span>
      </div>

      {isEditing ? (
        <div className="space-y-2">
          <Textarea
            ref={textareaRef}
            value={editValue}
            onChange={e => handleTextareaChange(e.target.value)}
            className="min-h-20 resize-none border-primary/30 bg-background text-sm focus-visible:ring-primary/20"
            autoFocus
            onKeyDown={e => { if (e.key === 'Escape') onEditCancel() }}
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
          {textParts.map((text, i) => (
            <p key={`text-${i}`} className="whitespace-pre-wrap text-sm leading-relaxed">{text}</p>
          ))}

          {toolBlocks.map((block, i) => (
            <div key={`tool-inline-${i}`} className="mt-2">
              <div className="rounded-md border border-amber-200 bg-amber-50/60 p-2 dark:border-amber-800/50 dark:bg-amber-950/30">
                <div className="mb-1 flex items-center gap-1.5">
                  <Wrench className="size-3 text-amber-600 dark:text-amber-400" />
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-300">
                    Tool Call
                  </span>
                </div>
                <pre className="overflow-x-auto text-[11px] leading-relaxed text-amber-900 dark:text-amber-200">
                  {block}
                </pre>
              </div>
            </div>
          ))}

          {item.turn.herramientas_usadas.length > 0 && !item.turn.tool_calls?.length && (
            <div className="mt-2 flex flex-wrap gap-1">
              {item.turn.herramientas_usadas.map(h => (
                <Badge key={h} variant="outline" className="text-[10px]">
                  <Wrench className="mr-0.5 size-2.5" />{h}
                </Badge>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Tool call block ───

function ToolCallBlock({ toolName, toolCallId, args }: { toolName: string; toolCallId: string; args: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="ml-6 rounded-lg border border-amber-200 bg-amber-50/40 dark:border-amber-800/50 dark:bg-amber-950/20">
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-center gap-2 px-3 py-2 text-left">
        {expanded ? <ChevronDown className="size-3 text-amber-600 dark:text-amber-400" /> : <ChevronRight className="size-3 text-amber-600 dark:text-amber-400" />}
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

// ─── Tool result block ───

function ToolResultBlock({ toolName, status, result, durationMs }: { toolName: string; status: 'success' | 'error' | 'timeout'; result: Record<string, unknown> | string; durationMs?: number }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="ml-6 rounded-lg border border-teal-200 bg-teal-50/40 dark:border-teal-800/50 dark:bg-teal-950/20">
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-center gap-2 px-3 py-2 text-left">
        {expanded ? <ChevronDown className="size-3 text-teal-600 dark:text-teal-400" /> : <ChevronRight className="size-3 text-teal-600 dark:text-teal-400" />}
        <Code2 className="size-3 text-teal-600 dark:text-teal-400" />
        <span className="text-xs font-semibold text-teal-700 dark:text-teal-300">{toolName}</span>
        <StatusBadge variant={status === 'success' ? 'success' : 'error'} className="text-[10px]">{status}</StatusBadge>
        {durationMs !== undefined && <span className="font-mono text-[10px] text-muted-foreground">{durationMs}ms</span>}
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

// ─── Main page component ───

export function ConversationDetailPage({ id }: ConversationDetailPageProps) {
  const router = useRouter()

  const [conversation, setConversation] = useState<Conversation | null>(() => {
    const all = loadAllConversations()

    return all.find(c => c.conversation_id === id) ?? null
  })

  const [editingTurn, setEditingTurn] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const [showDelete, setShowDelete] = useState(false)
  const [showMeta, setShowMeta] = useState(false)
  const [newTag, setNewTag] = useState('')

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

  // ─── Status & delete ───

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

  // ─── Tags ───

  const addTag = () => {
    if (!conversation) return
    const tag = newTag.trim()

    if (!tag) return
    const tags = conversation.tags ?? []

    if (tags.includes(tag)) return
    persistConversation({ ...conversation, tags: [...tags, tag] })
    setNewTag('')
  }

  const removeTag = (tag: string) => {
    if (!conversation) return
    persistConversation({ ...conversation, tags: (conversation.tags ?? []).filter(t => t !== tag) })
  }

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
  const toolNames = getToolCallNames(conversation)
  const userCount = conversation.turnos.filter(t => !isAssistantRole(t.rol) && !isSystemRole(t.rol)).length
  const assistantCount = conversation.turnos.filter(t => isAssistantRole(t.rol)).length
  const tags = conversation.tags ?? []

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Conversation ${conversation.conversation_id.slice(0, 12)}...`}
        description={`${conversation.turnos.length} messages — ${conversation.dominio} — ${conversation.es_sintetica ? 'Synthetic' : 'Real'}`}
        actions={
          <div className="flex gap-2">
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

      {/* Summary bar */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <StatusBadge variant={status === 'valid' ? 'success' : 'warning'} dot={false}>
          {status === 'valid' ? 'Valid' : 'Invalid'}
        </StatusBadge>
        <span className="flex items-center gap-1"><User className="size-3" /> {userCount} user</span>
        <span className="flex items-center gap-1"><Bot className="size-3" /> {assistantCount} assistant</span>
        {toolNames.length > 0 && (
          <span className="flex items-center gap-1">
            <Wrench className="size-3" /> {toolNames.length} tool{toolNames.length > 1 ? 's' : ''}
          </span>
        )}
        <span className="font-mono">{conversation.idioma}</span>
      </div>

      {/* Invalid banner */}
      {status === 'invalid' && (
        <div className="flex items-center gap-2 rounded-lg border px-4 py-2.5 bg-destructive/5">
          <Ban className="size-3.5 text-destructive/70" />
          <span className="text-xs text-destructive/80">
            Marked as invalid — excluded from exports and evaluations.
          </span>
          <Button variant="outline" size="sm" className="ml-auto h-6 text-[10px]" onClick={handleToggleStatus}>
            Restore
          </Button>
        </div>
      )}

      <div className="flex gap-4">
        {/* Messages */}
        <div className="flex-1 space-y-2">
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

          {/* Review section */}
          <Separator className="my-4" />

          <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
            {/* Tags */}
            <div>
              <label className="text-xs font-semibold text-muted-foreground">Tags</label>
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                {tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="gap-1 pr-1">
                    {tag}
                    <button onClick={() => removeTag(tag)} className="rounded-full p-0.5 hover:bg-foreground/10">
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
                  value={conversation.rating ?? 0}
                  onValueChange={v => persistConversation({ ...conversation, rating: v })}
                  variant="yellow"
                  size={18}
                />
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="text-xs font-semibold text-muted-foreground">Notes</label>
              <Textarea
                value={conversation.notes ?? ''}
                onChange={e => persistConversation({ ...conversation, notes: e.target.value })}
                placeholder="Review notes..."
                className="mt-1 min-h-16 resize-none text-sm"
              />
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 py-2">
            <Button variant="outline" size="sm" className="gap-1.5" onClick={() => persistConversation({ ...conversation, status: 'valid' })}>
              <CheckCircle2 className="size-3.5" />
              Validate
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5" onClick={handleToggleStatus}>
              {status === 'valid' ? <><Ban className="size-3.5" /> Mark Invalid</> : <><CheckCircle2 className="size-3.5" /> Mark Valid</>}
            </Button>
            <div className="flex-1" />
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

        {/* Metadata sidebar */}
        {showMeta && (
          <Card className="hidden w-80 shrink-0 lg:block">
            <CardContent className="space-y-3 p-4 text-xs">
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
                    <Badge key={r} variant="secondary" className="text-[10px]">{r}</Badge>
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

      {/* Delete dialog */}
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
            <Button variant="destructive" onClick={handleDelete}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
