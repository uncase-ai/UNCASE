'use client'

import { useEffect, useState } from 'react'

import Link from 'next/link'
import { ArrowLeft, Bot, Code2, User, Wrench } from 'lucide-react'

import type { Conversation, ConversationTurn } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

import { JsonViewer } from '../json-viewer'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

interface ConversationDetailPageProps {
  id: string
}

function loadConversation(id: string): Conversation | null {
  if (typeof window === 'undefined') return null

  try {
    const raw = localStorage.getItem('uncase-conversations')
    const all: Conversation[] = raw ? JSON.parse(raw) : []

    return all.find(c => c.conversation_id === id) ?? null
  } catch {
    return null
  }
}

function TurnBubble({ turn }: { turn: ConversationTurn }) {
  const isAssistant = turn.rol.toLowerCase().includes('asistente') || turn.rol.toLowerCase().includes('assistant') || turn.rol.toLowerCase().includes('agente') || turn.rol.toLowerCase().includes('agent')
  const hasTools = (turn.tool_calls?.length ?? 0) > 0 || (turn.tool_results?.length ?? 0) > 0

  return (
    <div className={cn('flex gap-3', isAssistant ? 'flex-row' : 'flex-row-reverse')}>
      <div className={cn('flex size-8 shrink-0 items-center justify-center rounded-full', isAssistant ? 'bg-violet-100 dark:bg-violet-900' : 'bg-blue-100 dark:bg-blue-900')}>
        {isAssistant ? <Bot className="size-4 text-violet-600 dark:text-violet-400" /> : <User className="size-4 text-blue-600 dark:text-blue-400" />}
      </div>
      <div className={cn('max-w-[75%] space-y-2', isAssistant ? 'items-start' : 'items-end')}>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium">{turn.rol}</span>
          <span className="text-[10px] text-muted-foreground">Turn {turn.turno}</span>
        </div>
        <div className={cn('rounded-lg px-3 py-2 text-sm', isAssistant ? 'bg-muted' : 'bg-primary text-primary-foreground')}>
          {turn.contenido}
        </div>

        {/* Tool calls */}
        {turn.tool_calls?.map(tc => (
          <div key={tc.tool_call_id} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 dark:border-amber-800 dark:bg-amber-950">
            <div className="flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-400">
              <Wrench className="size-3" />
              Tool Call: {tc.tool_name}
            </div>
            <pre className="mt-1 text-[11px] text-amber-600 dark:text-amber-300">
              {JSON.stringify(tc.arguments, null, 2)}
            </pre>
          </div>
        ))}

        {/* Tool results */}
        {turn.tool_results?.map(tr => (
          <div key={tr.tool_call_id} className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 dark:border-emerald-800 dark:bg-emerald-950">
            <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400">
              <Code2 className="size-3" />
              Result: {tr.tool_name}
              <StatusBadge variant={tr.status === 'success' ? 'success' : 'error'}>{tr.status}</StatusBadge>
            </div>
            <pre className="mt-1 text-[11px] text-emerald-600 dark:text-emerald-300">
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
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [showMeta, setShowMeta] = useState(false)

  useEffect(() => {
    setConversation(loadConversation(id))
  }, [id])

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

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Conversation ${conversation.conversation_id.slice(0, 12)}...`}
        description={`${conversation.turnos.length} turns — ${conversation.dominio} — ${conversation.es_sintetica ? 'Synthetic' : 'Real'}`}
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

      <div className="flex gap-4">
        {/* Chat view */}
        <div className="flex-1 space-y-4">
          {conversation.turnos.map(turn => (
            <TurnBubble key={turn.turno} turn={turn} />
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
    </div>
  )
}
