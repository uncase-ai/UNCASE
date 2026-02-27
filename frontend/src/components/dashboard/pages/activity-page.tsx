'use client'

import { useEffect, useState } from 'react'

import {
  Activity,
  ArrowDownToLine,
  BarChart3,
  BookOpen,
  Clock,
  Key,
  PackageOpen,
  Puzzle,
  Rocket,
  Sprout,
  Trash2
} from 'lucide-react'

import type { AuditLogEntry } from '@/types/api'
import type { ActivityEvent, ActivityType } from '@/types/dashboard'
import { fetchAuditLogs } from '@/lib/api/audit'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

const STORE_KEY = 'uncase-activity'

const ACTIVITY_ICONS: Record<ActivityType, typeof Activity> = {
  seed_created: Sprout,
  conversation_imported: ArrowDownToLine,
  conversation_generated: Rocket,
  evaluation_completed: BarChart3,
  dataset_exported: PackageOpen,
  tool_registered: Puzzle,
  api_key_created: Key,
  template_rendered: BookOpen,
  knowledge_uploaded: BookOpen
}

const ACTIVITY_COLORS: Record<ActivityType, string> = {
  seed_created: 'text-muted-foreground bg-muted',
  conversation_imported: 'text-muted-foreground bg-muted',
  conversation_generated: 'text-muted-foreground bg-muted',
  evaluation_completed: 'text-muted-foreground bg-muted',
  dataset_exported: 'text-muted-foreground bg-muted',
  tool_registered: 'text-muted-foreground bg-muted',
  api_key_created: 'text-muted-foreground bg-muted',
  template_rendered: 'text-muted-foreground bg-muted',
  knowledge_uploaded: 'text-muted-foreground bg-muted'
}

export function loadActivity(): ActivityEvent[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(STORE_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function logActivity(event: Omit<ActivityEvent, 'id' | 'timestamp'>) {
  const events = loadActivity()

  const newEvent: ActivityEvent = {
    ...event,
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString()
  }

  const updated = [newEvent, ...events].slice(0, 200)

  localStorage.setItem(STORE_KEY, JSON.stringify(updated))

  return newEvent
}

function timeAgo(date: string): string {
  const now = Date.now()
  const then = new Date(date).getTime()
  const diff = now - then
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)

  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)

  if (days < 7) return `${days}d ago`

  return new Date(date).toLocaleDateString()
}

function auditActionToActivityType(action: string): ActivityType {
  if (action.includes('seed')) return 'seed_created'
  if (action.includes('import')) return 'conversation_imported'
  if (action.includes('generat')) return 'conversation_generated'
  if (action.includes('evaluat')) return 'evaluation_completed'
  if (action.includes('export')) return 'dataset_exported'
  if (action.includes('tool')) return 'tool_registered'
  if (action.includes('key') || action.includes('auth')) return 'api_key_created'
  if (action.includes('template')) return 'template_rendered'
  if (action.includes('knowledge')) return 'knowledge_uploaded'

  return 'seed_created'
}

function auditLogToActivityEvent(log: AuditLogEntry): ActivityEvent {
  return {
    id: log.id,
    type: auditActionToActivityType(log.action),
    title: `${log.action} ${log.resource_type ?? ''}`.trim(),
    description: log.detail ?? (`${log.http_method ?? ''} ${log.endpoint ?? ''}`.trim() || undefined),
    timestamp: log.created_at,
    metadata: { resource_id: log.resource_id, ip: log.ip_address }
  }
}

export function ActivityPage() {
  const [events, setEvents] = useState<ActivityEvent[]>(() => loadActivity())
  const [error, setError] = useState<string | null>(null)

  // Sync with backend audit API on mount
  useEffect(() => {
    let cancelled = false

    fetchAuditLogs({ page: 1, page_size: 100 })
      .then(res => {
        if (cancelled) return

        if (res.data && Array.isArray(res.data) && res.data.length > 0) {
          const auditEvents = res.data.map(auditLogToActivityEvent)

          // Merge: audit data + localStorage-only events
          const auditIds = new Set(auditEvents.map(e => e.id))
          const localOnly = loadActivity().filter(e => !auditIds.has(e.id))

          const merged = [...auditEvents, ...localOnly].sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          ).slice(0, 200)

          setEvents(merged)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load activity logs')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const clearHistory = () => {
    localStorage.removeItem(STORE_KEY)
    setEvents([])
  }

  if (events.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Activity" description="Recent operations and pipeline events" />
        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-destructive text-sm">{error}</p>
          </div>
        )}
        <EmptyState
          icon={Activity}
          title="No activity yet"
          description="Activity events will appear here as you use the pipeline — importing data, generating conversations, running evaluations, and exporting datasets."
        />
      </div>
    )
  }

  // Group by date
  const grouped: Record<string, ActivityEvent[]> = {}

  for (const event of events) {
    const date = new Date(event.timestamp).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })

    if (!grouped[date]) grouped[date] = []
    grouped[date].push(event)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Activity"
        description={`${events.length} events recorded`}
        actions={
          <Button variant="outline" size="sm" onClick={clearHistory}>
            <Trash2 className="mr-1 size-3" />
            Clear History
          </Button>
        }
      />

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
          <p className="text-destructive text-sm">{error}</p>
        </div>
      )}

      {Object.entries(grouped).map(([date, dayEvents]) => (
        <div key={date}>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">{date}</h3>
          <Card>
            <CardContent className="divide-y p-0">
              {dayEvents.map(event => {
                const Icon = ACTIVITY_ICONS[event.type] ?? Activity
                const color = ACTIVITY_COLORS[event.type] ?? 'text-muted-foreground bg-muted'

                return (
                  <div key={event.id} className="flex items-start gap-3 px-4 py-3">
                    <div className={cn('mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full', color)}>
                      <Icon className="size-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{event.title}</p>
                      {event.description && (
                        <p className="text-xs text-muted-foreground">{event.description}</p>
                      )}
                    </div>
                    <span className="flex shrink-0 items-center gap-1 text-[11px] text-muted-foreground">
                      <Clock className="size-3" />
                      {timeAgo(event.timestamp)}
                    </span>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  )
}
