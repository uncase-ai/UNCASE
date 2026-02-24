'use client'

import { useCallback, useState } from 'react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  Ban,
  Bot,
  Check,
  CheckCircle2,
  Code2,
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

interface ConversationDetailPageProps {
  id: string
}

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

function TurnBubble({
  turn,
  editing,
  editValue,
  onEditStart,
  onEditCancel,
  onEditSave,
  onEditChange
}: {
  turn: ConversationTurn
  editing: boolean
  editValue: string
  onEditStart: () => void
  onEditCancel: () => void
  onEditSave: () => void
  onEditChange: (value: string) => void
}) {
  const isAssistant =
    turn.rol.toLowerCase().includes('asistente') ||
    turn.rol.toLowerCase().includes('assistant') ||
    turn.rol.toLowerCase().includes('agente') ||
    turn.rol.toLowerCase().includes('agent')

  const hasTools = (turn.tool_calls?.length ?? 0) > 0 || (turn.tool_results?.length ?? 0) > 0

  return (
    <div className={cn('flex gap-3', isAssistant ? 'flex-row' : 'flex-row-reverse')}>
      <div className={cn('flex size-8 shrink-0 items-center justify-center rounded-full bg-muted')}>
        {isAssistant ? (
          <Bot className="size-4 text-muted-foreground" />
        ) : (
          <User className="size-4 text-muted-foreground" />
        )}
      </div>
      <div className={cn('max-w-[75%] space-y-2', isAssistant ? 'items-start' : 'items-end')}>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium">{turn.rol}</span>
          <span className="text-[10px] text-muted-foreground">Turn {turn.turno}</span>
          {!editing && (
            <button
              onClick={onEditStart}
              className="rounded p-0.5 text-muted-foreground/50 transition-colors hover:text-foreground"
            >
              <Pencil className="size-3" />
            </button>
          )}
        </div>

        {editing ? (
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
        ) : (
          <div
            className={cn(
              'rounded-lg px-3 py-2 text-sm',
              isAssistant ? 'bg-muted' : 'bg-primary text-primary-foreground'
            )}
          >
            {turn.contenido}
          </div>
        )}

        {/* Tool calls */}
        {turn.tool_calls?.map(tc => (
          <div key={tc.tool_call_id} className="rounded-md border bg-muted/40 px-3 py-2">
            <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Wrench className="size-3" />
              Tool Call: {tc.tool_name}
            </div>
            <pre className="mt-1 text-[11px] text-muted-foreground">{JSON.stringify(tc.arguments, null, 2)}</pre>
          </div>
        ))}

        {/* Tool results */}
        {turn.tool_results?.map(tr => (
          <div key={tr.tool_call_id} className="rounded-md border bg-muted/40 px-3 py-2">
            <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Code2 className="size-3" />
              Result: {tr.tool_name}
              <StatusBadge variant={tr.status === 'success' ? 'success' : 'error'}>{tr.status}</StatusBadge>
            </div>
            <pre className="mt-1 text-[11px] text-muted-foreground">
              {typeof tr.result === 'string' ? tr.result : JSON.stringify(tr.result, null, 2)}
            </pre>
          </div>
        ))}

        {turn.herramientas_usadas.length > 0 && !hasTools && (
          <div className="flex gap-1">
            {turn.herramientas_usadas.map(h => (
              <Badge key={h} variant="outline" className="text-[10px]">
                {h}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

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
        <div className="flex-1 space-y-4">
          {conversation.turnos.map((turn, i) => (
            <TurnBubble
              key={turn.turno}
              turn={turn}
              editing={editingTurn === i}
              editValue={editValue}
              onEditStart={() => handleEditStart(i)}
              onEditCancel={handleEditCancel}
              onEditSave={handleEditSave}
              onEditChange={setEditValue}
            />
          ))}
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
