'use client'

import { useMemo, useState } from 'react'

import Link from 'next/link'
import { MessageSquare } from 'lucide-react'

import type { Conversation } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { SearchInput } from '../search-input'
import { StatusBadge } from '../status-badge'

// Local store key for imported conversations
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

const DOMAIN_COLORS: Record<string, string> = {
  'automotive.sales': 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  'medical.consultation': 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  'legal.advisory': 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
  'finance.advisory': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300',
  'industrial.support': 'bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300',
  'education.tutoring': 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-300'
}

export function ConversationsPage() {
  const [conversations] = useState<Conversation[]>(() => loadConversations())
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [syntheticFilter, setSyntheticFilter] = useState<string>('all')

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

    return result
  }, [conversations, search, domainFilter, syntheticFilter])

  const columns: Column<Conversation>[] = [
    {
      key: 'id',
      header: 'Conversation',
      cell: row => (
        <Link href={`/dashboard/conversations/${row.conversation_id}`} className="font-mono text-xs hover:underline">
          {row.conversation_id.slice(0, 12)}...
        </Link>
      )
    },
    {
      key: 'seed',
      header: 'Seed',
      cell: row => <span className="font-mono text-xs text-muted-foreground">{row.seed_id.slice(0, 12)}...</span>
    },
    {
      key: 'domain',
      header: 'Domain',
      cell: row => (
        <Badge variant="secondary" className={cn('text-[10px]', DOMAIN_COLORS[row.dominio])}>
          {row.dominio.split('.').pop()}
        </Badge>
      )
    },
    {
      key: 'turns',
      header: 'Turns',
      cell: row => <span className="text-sm">{row.turnos.length}</span>
    },
    {
      key: 'type',
      header: 'Type',
      cell: row => (
        <StatusBadge variant={row.es_sintetica ? 'info' : 'default'} dot={false}>
          {row.es_sintetica ? 'Synthetic' : 'Real'}
        </StatusBadge>
      )
    },
    {
      key: 'date',
      header: 'Created',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    }
  ]

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

  return (
    <div className="space-y-4">
      <PageHeader title="Conversations" description={`${conversations.length} conversations in local store`} />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <SearchInput value={search} onChange={setSearch} placeholder="Search conversations..." className="w-64" />
        <Select value={domainFilter} onValueChange={setDomainFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Domain" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Domains</SelectItem>
            {SUPPORTED_DOMAINS.map(d => (
              <SelectItem key={d} value={d}>
                {d.split('.').pop()}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={syntheticFilter} onValueChange={setSyntheticFilter}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="real">Real</SelectItem>
            <SelectItem value="synthetic">Synthetic</SelectItem>
          </SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{filtered.length} results</span>
      </div>

      <DataTable columns={columns} data={filtered} rowKey={r => r.conversation_id} />
    </div>
  )
}
