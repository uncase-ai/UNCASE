'use client'

import { useCallback, useMemo, useState } from 'react'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Ban,
  CheckCircle2,
  MessageSquare,
  MoreHorizontal,
  Pencil,
  Trash2
} from 'lucide-react'

import type { Conversation } from '@/types/api'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
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
  'automotive.sales': '',
  'medical.consultation': '',
  'legal.advisory': '',
  'finance.advisory': '',
  'industrial.support': '',
  'education.tutoring': ''
}

export function ConversationsPage() {
  const router = useRouter()
  const [conversations, setConversations] = useState<Conversation[]>(() => loadConversations())
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [syntheticFilter, setSyntheticFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [deleteTarget, setDeleteTarget] = useState<Conversation | null>(null)

  const persist = useCallback(
    (updated: Conversation[]) => {
      setConversations(updated)
      saveConversations(updated)
    },
    []
  )

  const handleToggleStatus = useCallback(
    (id: string) => {
      const updated = conversations.map(c => {
        if (c.conversation_id !== id) return c
        const current = c.status ?? 'valid'

        return { ...c, status: current === 'valid' ? 'invalid' as const : 'valid' as const }
      })

      persist(updated)
    },
    [conversations, persist]
  )

  const handleDelete = useCallback(
    (id: string) => {
      const updated = conversations.filter(c => c.conversation_id !== id)

      persist(updated)
      setDeleteTarget(null)
    },
    [conversations, persist]
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

    return result
  }, [conversations, search, domainFilter, syntheticFilter, statusFilter])

  const invalidCount = useMemo(
    () => conversations.filter(c => c.status === 'invalid').length,
    [conversations]
  )

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
      key: 'status',
      header: 'Status',
      cell: row => {
        const status = row.status ?? 'valid'

        return (
          <StatusBadge variant={status === 'valid' ? 'success' : 'warning'} dot={false}>
            {status === 'valid' ? 'Valid' : 'Invalid'}
          </StatusBadge>
        )
      }
    },
    {
      key: 'date',
      header: 'Created',
      cell: row => (
        <span className="text-xs text-muted-foreground">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    },
    {
      key: 'actions',
      header: '',
      className: 'w-10',
      cell: row => {
        const status = row.status ?? 'valid'

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="size-8 p-0">
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => router.push(`/dashboard/conversations/${row.conversation_id}`)}>
                <Pencil className="size-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleToggleStatus(row.conversation_id)}>
                {status === 'valid' ? (
                  <>
                    <Ban className="size-4" />
                    Mark as Invalid
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="size-4" />
                    Mark as Valid
                  </>
                )}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem variant="destructive" onClick={() => setDeleteTarget(row)}>
                <Trash2 className="size-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      }
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
      <PageHeader
        title="Conversations"
        description={`${conversations.length} conversations${invalidCount > 0 ? ` (${invalidCount} invalid)` : ''}`}
      />

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
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="valid">Valid</SelectItem>
            <SelectItem value="invalid">Invalid</SelectItem>
          </SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{filtered.length} results</span>
      </div>

      <DataTable columns={columns} data={filtered} rowKey={r => r.conversation_id} />

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={open => { if (!open) setDeleteTarget(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Conversation</DialogTitle>
            <DialogDescription>
              This will permanently remove conversation{' '}
              <span className="font-mono">{deleteTarget?.conversation_id.slice(0, 12)}...</span>{' '}
              from your local store. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button variant="destructive" onClick={() => deleteTarget && handleDelete(deleteTarget.conversation_id)}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
