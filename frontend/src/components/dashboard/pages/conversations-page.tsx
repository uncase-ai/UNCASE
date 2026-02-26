'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import Link from 'next/link'
import {
  Ban,
  Bot,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  Keyboard,
  MessageSquare,
  MousePointerClick,
  Plus,
  Save,
  ShieldCheck,
  Star,
  Trash2,
  User,
  Wrench,
  X
} from 'lucide-react'

import type { Conversation, ConversationTurn, ToolDefinition } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import {
  fetchConversations as apiFetchConversations,
  bulkCreateConversations,
  updateConversationApi,
  deleteConversationApi
} from '@/lib/api/conversations'
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
const ONBOARDING_KEY = 'uncase-conversations-onboarding-seen'

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
// Must stay in sync with the backend _ROLE_MAP used across all templates
// (chatml.py, llama.py, mistral.py, etc.) and the JSONL parser role maps.

const ASSISTANT_ROLES = new Set([
  'asistente', 'assistant', 'agente', 'agent', 'vendedor', 'gpt', 'bot', 'model'
])

const SYSTEM_ROLES = new Set(['system', 'sistema'])

const TOOL_ROLES = new Set(['herramienta', 'tool', 'function'])

function isAssistantRole(rol: string): boolean {
  return ASSISTANT_ROLES.has(rol.toLowerCase())
}

function isSystemRole(rol: string): boolean {
  return SYSTEM_ROLES.has(rol.toLowerCase())
}

function isToolRole(rol: string): boolean {
  return TOOL_ROLES.has(rol.toLowerCase())
}

type MessageRole = 'system' | 'user' | 'assistant' | 'tool_call' | 'tool_result'

function getMessageRole(turn: ConversationTurn): MessageRole {
  if (isSystemRole(turn.rol)) return 'system'
  if (isAssistantRole(turn.rol)) return 'assistant'
  if (isToolRole(turn.rol)) return 'tool_result'

  return 'user'
}

// ─── Format compatibility ───
// Maps template names to the OSS models they target.

interface FormatInfo {
  template: string
  label: string
  models: string[]
}

const FORMAT_CATALOG: FormatInfo[] = [
  { template: 'chatml', label: 'ChatML', models: ['Qwen', 'Yi', 'OpenChat'] },
  { template: 'llama', label: 'Llama', models: ['Llama 3', 'CodeLlama'] },
  { template: 'mistral', label: 'Mistral', models: ['Mistral', 'Mixtral'] },
  { template: 'alpaca', label: 'Alpaca', models: ['Alpaca', 'Vicuna'] },
  { template: 'openai_api', label: 'OpenAI', models: ['GPT-4', 'GPT-3.5'] },
  { template: 'qwen', label: 'Qwen', models: ['Qwen 2.5'] },
  { template: 'nemotron', label: 'Nemotron', models: ['Nemotron'] },
  { template: 'moonshot', label: 'Moonshot', models: ['Kimi'] },
]

/**
 * Determine which templates a conversation is compatible with based on its
 * structure (has system prompt, has tool calls, turn count).
 */
function getCompatibleFormats(conv: Conversation): FormatInfo[] {
  const hasToolCalls = conv.turnos.some(t => t.tool_calls && t.tool_calls.length > 0)
  const multiTurn = conv.turnos.filter(t => !isSystemRole(t.rol)).length > 2
  const compatible: FormatInfo[] = []

  for (const fmt of FORMAT_CATALOG) {
    if (fmt.template === 'alpaca' && multiTurn) continue

    compatible.push(fmt)
  }

  // If conversation uses tool calls, only keep formats that support them
  if (hasToolCalls) {
    return compatible.filter(f =>
      ['chatml', 'openai_api', 'mistral', 'qwen', 'nemotron', 'moonshot'].includes(f.template)
    )
  }

  return compatible
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

const ROLE_STYLES: Record<
  MessageRole,
  { label: string; labelClass: string; bgClass: string; borderClass: string; icon: typeof Bot; iconClass: string }
> = {
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

// ─── Built-in tools catalog (fallback when API unavailable) ───

const BUILTIN_TOOLS: { name: string; domain: string }[] = [
  { name: 'buscar_inventario', domain: 'automotive.sales' },
  { name: 'cotizar_vehiculo', domain: 'automotive.sales' },
  { name: 'verificar_disponibilidad', domain: 'automotive.sales' },
  { name: 'solicitar_financiamiento', domain: 'automotive.sales' },
  { name: 'agendar_servicio', domain: 'automotive.sales' },
  { name: 'consultar_historial_medico', domain: 'medical.consultation' },
  { name: 'buscar_medicamentos', domain: 'medical.consultation' },
  { name: 'agendar_cita', domain: 'medical.consultation' },
  { name: 'verificar_laboratorio', domain: 'medical.consultation' },
  { name: 'validar_seguro', domain: 'medical.consultation' },
  { name: 'buscar_jurisprudencia', domain: 'legal.advisory' },
  { name: 'consultar_expediente', domain: 'legal.advisory' },
  { name: 'verificar_plazos', domain: 'legal.advisory' },
  { name: 'buscar_legislacion', domain: 'legal.advisory' },
  { name: 'calcular_honorarios', domain: 'legal.advisory' },
  { name: 'consultar_portafolio', domain: 'finance.advisory' },
  { name: 'analizar_riesgo', domain: 'finance.advisory' },
  { name: 'consultar_mercado', domain: 'finance.advisory' },
  { name: 'verificar_cumplimiento', domain: 'finance.advisory' },
  { name: 'simular_inversion', domain: 'finance.advisory' },
  { name: 'diagnosticar_equipo', domain: 'industrial.support' },
  { name: 'consultar_inventario_partes', domain: 'industrial.support' },
  { name: 'programar_mantenimiento', domain: 'industrial.support' },
  { name: 'buscar_manual_tecnico', domain: 'industrial.support' },
  { name: 'registrar_incidencia', domain: 'industrial.support' },
  { name: 'buscar_curriculum', domain: 'education.tutoring' },
  { name: 'evaluar_progreso', domain: 'education.tutoring' },
  { name: 'generar_ejercicio', domain: 'education.tutoring' },
  { name: 'buscar_recurso_educativo', domain: 'education.tutoring' },
  { name: 'programar_sesion', domain: 'education.tutoring' }
]

// ─── Tool autocomplete hook ───

function useToolAutocomplete({
  domain,
  conversations,
  apiTools
}: {
  domain: string
  conversations: Conversation[]
  apiTools: ToolDefinition[] | null
}) {
  return useMemo(() => {
    // Priority 1: API-fetched tools for this domain
    if (apiTools && apiTools.length > 0) {
      return apiTools.filter(t => t.domains.includes(domain) || t.domains.length === 0).map(t => t.name)
    }

    // Priority 2: tools already used in conversations for this domain
    const used = new Set<string>()

    for (const c of conversations) {
      if (c.dominio !== domain) continue

      for (const t of c.turnos) {
        for (const h of t.herramientas_usadas) used.add(h)

        if (t.tool_calls) {
          for (const tc of t.tool_calls) used.add(tc.tool_name)
        }
      }
    }

    if (used.size > 0) return [...used].sort()

    // Priority 3: built-in tools for this domain
    return BUILTIN_TOOLS.filter(t => t.domain === domain).map(t => t.name)
  }, [domain, conversations, apiTools])
}

// ─── Conversation summary helper ───

function buildSummary(conv: Conversation): string {
  const turns = conv.turnos

  if (turns.length === 0) return 'Empty conversation'

  const userTurns = turns.filter(t => !isAssistantRole(t.rol) && !isSystemRole(t.rol) && !isToolRole(t.rol))
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

// ─── Tool autocomplete dropdown ───

function ToolAutocompleteDropdown({
  tools,
  filter,
  position,
  selectedIndex,
  onSelect
}: {
  tools: string[]
  filter: string
  position: { top: number; left: number }
  selectedIndex: number
  onSelect: (tool: string) => void
}) {
  const filtered = useMemo(() => {
    if (!filter) return tools

    const q = filter.toLowerCase()

    return tools.filter(t => t.toLowerCase().includes(q))
  }, [tools, filter])

  if (filtered.length === 0) return null

  return (
    <div
      className="fixed z-50 max-h-48 w-64 overflow-y-auto rounded-md border bg-popover p-1 shadow-md"
      style={{ top: position.top, left: position.left }}
    >
      <div className="px-2 py-1 text-[10px] font-medium text-muted-foreground">Insert tool call</div>
      {filtered.map((tool, i) => (
        <button
          key={tool}
          className={cn(
            'flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-xs transition-colors',
            i === selectedIndex ? 'bg-accent text-accent-foreground' : 'hover:bg-accent/50'
          )}
          onMouseDown={e => {
            e.preventDefault()
            onSelect(tool)
          }}
        >
          <Wrench className="size-3 shrink-0 text-amber-500" />
          <span className="truncate font-mono">{tool}</span>
        </button>
      ))}
    </div>
  )
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
              <Badge variant="secondary" className="text-[10px]">
                +{tools.length - 2}
              </Badge>
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

// ─── Message bubble (click-to-edit with tool autocomplete) ───

function MessageBubble({
  item,
  isEditing,
  editValue,
  onClickToEdit,
  onEditChange,
  onEditSave,
  onEditCancel,
  availableTools
}: {
  item: FlatItem
  isEditing: boolean
  editValue: string
  onClickToEdit: () => void
  onEditChange: (v: string) => void
  onEditSave: () => void
  onEditCancel: () => void
  availableTools: string[]
}) {
  const style = ROLE_STYLES[item.role]
  const Icon = style.icon
  const isMainMsg = item.role === 'user' || item.role === 'assistant' || item.role === 'system'
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Tool autocomplete state
  const [showToolMenu, setShowToolMenu] = useState(false)
  const [toolFilter, setToolFilter] = useState('')
  const [toolMenuPos, setToolMenuPos] = useState({ top: 0, left: 0 })
  const [toolSelectedIdx, setToolSelectedIdx] = useState(0)
  const triggerPosRef = useRef<number>(0)

  // Filtered tools for the dropdown
  const filteredTools = useMemo(() => {
    if (!toolFilter) return availableTools

    const q = toolFilter.toLowerCase()

    return availableTools.filter(t => t.toLowerCase().includes(q))
  }, [availableTools, toolFilter])

  const insertToolCall = useCallback(
    (toolName: string) => {
      const cursorPos = textareaRef.current?.selectionStart ?? editValue.length
      const before = editValue.slice(0, triggerPosRef.current)
      const after = editValue.slice(cursorPos)
      const snippet = `<tool_call>\n{"name": "${toolName}", "arguments": {}}\n</tool_call>`

      onEditChange(before + snippet + after)
      setShowToolMenu(false)
      setToolFilter('')
      setToolSelectedIdx(0)

      // Focus back and position cursor inside arguments
      requestAnimationFrame(() => {
        if (textareaRef.current) {
          const newCursorPos = before.length + snippet.length - 16 // inside {}

          textareaRef.current.focus()
          textareaRef.current.setSelectionRange(newCursorPos, newCursorPos)
        }
      })
    },
    [editValue, onEditChange]
  )

  // Auto-resize textarea
  const handleTextareaChange = (v: string) => {
    onEditChange(v)

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      if (showToolMenu) {
        setShowToolMenu(false)
        setToolFilter('')

        return
      }

      onEditCancel()

      return
    }

    if (showToolMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setToolSelectedIdx(i => (i + 1) % Math.max(filteredTools.length, 1))

        return
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setToolSelectedIdx(i => (i - 1 + filteredTools.length) % Math.max(filteredTools.length, 1))

        return
      }

      if ((e.key === 'Enter' || e.key === 'Tab') && filteredTools.length > 0) {
        e.preventDefault()
        insertToolCall(filteredTools[toolSelectedIdx] ?? filteredTools[0])

        return
      }
    }
  }

  const handleInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
    const ta = e.currentTarget
    const val = ta.value
    const pos = ta.selectionStart

    // Detect "<" typed at cursor position
    if (pos > 0 && val[pos - 1] === '<' && availableTools.length > 0) {
      // Check it's not inside an existing tag
      const before = val.slice(0, pos - 1)
      const openTags = (before.match(/</g) || []).length
      const closeTags = (before.match(/>/g) || []).length

      if (openTags <= closeTags) {
        triggerPosRef.current = pos - 1
        setToolFilter('')
        setToolSelectedIdx(0)

        // Calculate position for the dropdown
        const rect = ta.getBoundingClientRect()

        setToolMenuPos({
          top: rect.top + Math.min(ta.scrollHeight, 120),
          left: rect.left + 16
        })
        setShowToolMenu(true)

        return
      }
    }

    // Update filter while menu is open
    if (showToolMenu) {
      const typed = val.slice(triggerPosRef.current + 1, pos)

      // Close if user typed a space or backspaced past trigger
      if (pos <= triggerPosRef.current || typed.includes(' ') || typed.includes('\n')) {
        setShowToolMenu(false)
        setToolFilter('')
      } else {
        setToolFilter(typed)
        setToolSelectedIdx(0)
      }
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

    return (
      <ToolResultBlock toolName={tr.tool_name} status={tr.status} result={tr.result} durationMs={tr.duration_ms} />
    )
  }

  // Parse tool_call blocks inside message content
  const { textParts, toolBlocks } = parseToolCallsFromContent(item.turn.contenido)

  return (
    <div className={cn('rounded-lg border p-3', style.bgClass, style.borderClass)}>
      {/* Role label */}
      <div className="mb-2 flex items-center gap-2">
        <Icon className={cn('size-3.5', style.iconClass)} />
        <span className={cn('text-[11px] font-bold uppercase tracking-wide', style.labelClass)}>{style.label}</span>
        <span className="font-mono text-[10px] text-muted-foreground">#{item.turn.turno}</span>
      </div>

      {/* Content — click to edit */}
      {isEditing ? (
        <div className="relative space-y-2">
          <Textarea
            ref={textareaRef}
            value={editValue}
            onChange={e => handleTextareaChange(e.target.value)}
            onInput={handleInput}
            onKeyDown={handleKeyDown}
            onBlur={() => {
              // Delay to allow dropdown clicks
              setTimeout(() => setShowToolMenu(false), 150)
            }}
            className="min-h-20 resize-none border-primary/30 bg-background text-sm focus-visible:ring-primary/20"
            autoFocus
          />
          {availableTools.length > 0 && !showToolMenu && (
            <p className="text-[10px] text-muted-foreground">
              Type <kbd className="rounded border bg-muted px-1 py-0.5 font-mono text-[9px]">&lt;</kbd> to insert a
              tool call
            </p>
          )}
          {showToolMenu && (
            <ToolAutocompleteDropdown
              tools={availableTools}
              filter={toolFilter}
              position={toolMenuPos}
              selectedIndex={toolSelectedIdx}
              onSelect={insertToolCall}
            />
          )}
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
      <pre className="overflow-x-auto text-[11px] leading-relaxed text-amber-900 dark:text-amber-200">{content}</pre>
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
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-center gap-2 px-3 py-2 text-left">
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
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-center gap-2 px-3 py-2 text-left">
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
              <button onClick={() => removeTag(tag)} className="rounded-full p-0.5 hover:bg-foreground/10">
                <X className="size-2.5" />
              </button>
            </Badge>
          ))}
          <div className="flex items-center gap-1">
            <Input
              value={newTag}
              onChange={e => setNewTag(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') addTag()
              }}
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
          <Rating value={rating} onValueChange={v => onUpdate({ rating: v })} variant="yellow" size={18} />
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

// ─── Onboarding dialog ───

function OnboardingDialog() {
  const [open, setOpen] = useState(() => {
    if (typeof window === 'undefined') return false

    return !localStorage.getItem(ONBOARDING_KEY)
  })

  const dismiss = () => {
    setOpen(false)
    localStorage.setItem(ONBOARDING_KEY, '1')
  }

  return (
    <Dialog
      open={open}
      onOpenChange={v => {
        if (!v) dismiss()
      }}
    >
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="size-5" />
            Conversation Editor
          </DialogTitle>
          <DialogDescription>Quick guide to editing conversations</DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <div className="flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sky-100 dark:bg-sky-900/40">
              <MousePointerClick className="size-4 text-sky-600 dark:text-sky-400" />
            </div>
            <div>
              <p className="text-sm font-medium">Click to edit</p>
              <p className="text-xs text-muted-foreground">
                Click any message to edit its content inline. Press{' '}
                <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">Esc</kbd> to cancel.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/40">
              <Keyboard className="size-4 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-sm font-medium">Insert tool calls</p>
              <p className="text-xs text-muted-foreground">
                While editing, type{' '}
                <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">&lt;</kbd> to open the tool picker
                and insert a tool call block.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-amber-50 dark:bg-amber-900/30">
              <Star className="size-4 text-amber-500" />
            </div>
            <div>
              <p className="text-sm font-medium">Rate &amp; tag</p>
              <p className="text-xs text-muted-foreground">
                Use the star rating, tags, and notes at the bottom of the detail panel to organize and review
                conversations.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-900/40">
              <CheckCircle2 className="size-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-medium">Validate or reject</p>
              <p className="text-xs text-muted-foreground">
                Mark conversations as valid or invalid. Invalid conversations are excluded from exports and evaluations.
              </p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button onClick={dismiss} size="sm">
            Got it
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Detail panel ───

function DetailPanel({
  conversation,
  availableTools,
  onPersist,
  onDelete
}: {
  conversation: Conversation
  availableTools: string[]
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
    const next = current === 'valid' ? ('invalid' as const) : ('valid' as const)

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
  const userCount = conversation.turnos.filter(t => !isAssistantRole(t.rol) && !isSystemRole(t.rol) && !isToolRole(t.rol)).length
  const assistantCount = conversation.turnos.filter(t => isAssistantRole(t.rol)).length
  const compatibleFormats = getCompatibleFormats(conversation)

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="shrink-0 border-b p-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              Conversation{' '}
              <span className="font-mono text-base">{conversation.conversation_id.slice(0, 12)}...</span>
            </h2>
            <p className="text-sm text-muted-foreground">
              {conversation.turnos.length} messages &middot; {conversation.dominio} &middot;{' '}
              {conversation.es_sintetica ? 'Synthetic' : 'Real'}
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
          {availableTools.length > 0 && (
            <span className="flex items-center gap-1 rounded bg-muted px-1.5 py-0.5">
              <Code2 className="size-3" /> {availableTools.length} available
            </span>
          )}
          <span className="font-mono">{conversation.idioma}</span>
        </div>

        {/* Format compatibility */}
        {compatibleFormats.length > 0 && (
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-medium text-muted-foreground">Compatible:</span>
            {compatibleFormats.map(fmt => (
              <Badge
                key={fmt.template}
                variant="outline"
                className="gap-1 border-emerald-300 bg-emerald-50/50 text-[10px] text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-300"
                title={fmt.models.join(', ')}
              >
                {fmt.label}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Invalid banner */}
      {status === 'invalid' && (
        <div className="flex items-center gap-2 border-b bg-destructive/5 px-4 py-2">
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
                availableTools={availableTools}
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
          <Button variant="outline" size="sm" className="gap-1.5" onClick={handleValidate}>
            <CheckCircle2 className="size-3.5" />
            Validate
          </Button>
          <Button size="sm" className="gap-1.5" onClick={handleSave} disabled={!hasPendingChanges}>
            <Save className="size-3.5" />
            Save
          </Button>
          <div className="flex-1" />
          <Button variant="outline" size="sm" className="gap-1.5" onClick={handleToggleStatus}>
            {status === 'valid' ? (
              <>
                <Ban className="size-3.5" /> Mark Invalid
              </>
            ) : (
              <>
                <CheckCircle2 className="size-3.5" /> Mark Valid
              </>
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
            <Button
              variant="destructive"
              onClick={() => {
                setShowDelete(false)
                onDelete()
              }}
            >
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
      <span>
        {start}-{end} of {total}
      </span>
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
  const [apiConnected, setApiConnected] = useState(false)

  // Try to load tools from API (best-effort, non-blocking)
  const [apiTools, setApiTools] = useState<ToolDefinition[] | null>(null)

  useEffect(() => {
    let cancelled = false

    import('@/lib/api/tools')
      .then(mod => mod.fetchTools())
      .then(res => {
        if (!cancelled && res.data) setApiTools(res.data)
      })
      .catch(() => {
        // API unavailable — will use fallback tools
      })

    return () => {
      cancelled = true
    }
  }, [])

  // Sync with backend API on mount
  useEffect(() => {
    let cancelled = false

    apiFetchConversations({ page: 1, page_size: 100 })
      .then(res => {
        if (cancelled) return

        if (res.data && res.data.items.length > 0) {
          const apiConvs: Conversation[] = res.data.items.map(item => ({
            conversation_id: item.conversation_id,
            seed_id: item.seed_id ?? '',
            dominio: item.dominio,
            idioma: item.idioma,
            turnos: item.turnos,
            es_sintetica: item.es_sintetica,
            created_at: item.created_at,
            metadata: ((item as unknown as Record<string, unknown>).metadata as Record<string, unknown>) ?? {},
            status: (item.status as 'valid' | 'invalid') ?? undefined,
            rating: item.rating ?? undefined,
            tags: item.tags ?? undefined,
            notes: item.notes ?? undefined
          }))

          // Merge: API data takes precedence, keep localStorage-only items
          const apiIds = new Set(apiConvs.map(c => c.conversation_id))
          const localOnly = loadConversations().filter(c => !apiIds.has(c.conversation_id))
          const merged = [...apiConvs, ...localOnly]

          setConversations(merged)
          saveConversations(merged)
          setApiConnected(true)

          // Push localStorage-only conversations to API (best-effort)
          if (localOnly.length > 0) {
            const payload = localOnly.map(c => ({
              conversation_id: c.conversation_id,
              seed_id: c.seed_id || null,
              dominio: c.dominio,
              idioma: c.idioma,
              turnos: c.turnos,
              es_sintetica: c.es_sintetica,
              metadata: c.metadata,
              status: c.status ?? null,
              rating: c.rating ?? null,
              tags: c.tags ?? null,
              notes: c.notes ?? null
            }))

            bulkCreateConversations(payload).catch(() => {})
          }
        } else if (res.data) {
          // API connected but no data — push localStorage data to API
          setApiConnected(true)
          const local = loadConversations()

          if (local.length > 0) {
            const payload = local.map(c => ({
              conversation_id: c.conversation_id,
              seed_id: c.seed_id || null,
              dominio: c.dominio,
              idioma: c.idioma,
              turnos: c.turnos,
              es_sintetica: c.es_sintetica,
              metadata: c.metadata,
              status: c.status ?? null,
              rating: c.rating ?? null,
              tags: c.tags ?? null,
              notes: c.notes ?? null
            }))

            bulkCreateConversations(payload).catch(() => {})
          }
        }
      })
      .catch(() => {
        // API unavailable — use localStorage data
      })

    return () => {
      cancelled = true
    }
  }, [])

  const persist = useCallback((updated: Conversation[]) => {
    setConversations(updated)
    saveConversations(updated)
  }, [])

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

  // Resolve available tools for the selected conversation's domain
  const selectedDomain = selectedConversation?.dominio ?? ''
  const availableTools = useToolAutocomplete({ domain: selectedDomain, conversations, apiTools })

  const handlePersistConversation = useCallback(
    (updated: Conversation) => {
      const all = conversations.map(c => (c.conversation_id === updated.conversation_id ? updated : c))

      persist(all)

      // Push metadata update to API (best-effort)
      if (apiConnected) {
        updateConversationApi(updated.conversation_id, {
          status: updated.status,
          rating: updated.rating,
          tags: updated.tags,
          notes: updated.notes
        }).catch(() => {})
      }
    },
    [conversations, persist, apiConnected]
  )

  const handleDeleteConversation = useCallback(
    (id: string) => {
      const all = conversations.filter(c => c.conversation_id !== id)

      persist(all)

      if (selectedId === id) setSelectedId(null)

      // Delete from API (best-effort)
      if (apiConnected) {
        deleteConversationApi(id).catch(() => {})
      }
    },
    [conversations, persist, selectedId, apiConnected]
  )

  // Reset page when filters change
  const handleFilterChange =
    <T,>(setter: (v: T) => void) =>
    (v: T) => {
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
      <OnboardingDialog />

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
                    <SelectItem key={d} value={d}>
                      {d.split('.').pop()}
                    </SelectItem>
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
                      {'★'.repeat(r)}
                      {'☆'.repeat(5 - r)}
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
              availableTools={availableTools}
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
