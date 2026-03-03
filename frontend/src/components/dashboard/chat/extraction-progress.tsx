'use client'

import { useState } from 'react'

import { ChevronDown, ChevronRight } from 'lucide-react'

import type { ExtractionProgress, FieldProgress } from '@/types/layer0'
import { cn } from '@/lib/utils'
import { Progress } from '@/components/ui/progress'

import { FieldCard } from './field-card'

interface ExtractionProgressPanelProps {
  progress: ExtractionProgress | null
}

function groupFieldsByCategory(fields: Record<string, FieldProgress>): Record<string, Record<string, FieldProgress>> {
  const groups: Record<string, Record<string, FieldProgress>> = {}

  for (const [key, value] of Object.entries(fields)) {
    const parts = key.split('.')
    const category = parts.length > 1 ? parts[0] : 'general'
    const fieldName = parts.length > 1 ? parts.slice(1).join('.') : key

    if (!groups[category]) groups[category] = {}
    groups[category][fieldName] = value
  }

  return groups
}

function CategorySection({ name, fields }: { name: string; fields: Record<string, FieldProgress> }) {
  const [expanded, setExpanded] = useState(true)
  const total = Object.keys(fields).length
  const filled = Object.values(fields).filter(f => f.status === 'extracted' || f.status === 'confirmed').length

  return (
    <div className="border-b border-gray-100 last:border-0 dark:border-zinc-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-zinc-800/50"
      >
        {expanded ? <ChevronDown className="size-3 text-muted-foreground" /> : <ChevronRight className="size-3 text-muted-foreground" />}
        <span className="flex-1 text-xs font-semibold capitalize">{name.replace(/_/g, ' ')}</span>
        <span className="text-[10px] text-muted-foreground">{filled}/{total}</span>
      </button>
      {expanded && (
        <div className="space-y-1 px-3 pb-2">
          {Object.entries(fields).map(([fieldName, field]) => (
            <FieldCard key={fieldName} name={fieldName} field={field} />
          ))}
        </div>
      )}
    </div>
  )
}

export function ExtractionProgressPanel({ progress }: ExtractionProgressPanelProps) {
  if (!progress) {
    return (
      <div className="flex h-full items-center justify-center p-4">
        <p className="text-xs text-muted-foreground">Inicia la entrevista para ver el progreso</p>
      </div>
    )
  }

  const percent = progress.total_fields > 0
    ? Math.round((progress.filled_fields / progress.total_fields) * 100)
    : 0

  const requiredPercent = progress.required_total > 0
    ? Math.round((progress.required_filled / progress.required_total) * 100)
    : 0

  const groups = groupFieldsByCategory(progress.fields)
  const turnsLeft = progress.max_turns - progress.turn

  return (
    <div className="flex h-full flex-col">
      {/* Header stats */}
      <div className="space-y-3 border-b p-3 dark:border-zinc-800">
        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs font-semibold">Progreso General</span>
            <span className="text-xs text-muted-foreground">{percent}%</span>
          </div>
          <Progress value={percent} className="h-2" />
        </div>
        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Campos requeridos</span>
            <span className="text-xs text-muted-foreground">{requiredPercent}%</span>
          </div>
          <Progress value={requiredPercent} className="h-1.5" />
        </div>
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-muted-foreground">Turno {progress.turn}/{progress.max_turns}</span>
          <span className={cn(
            'font-medium',
            turnsLeft <= 2 ? 'text-red-500' : turnsLeft <= 5 ? 'text-amber-500' : 'text-muted-foreground'
          )}>
            {turnsLeft} restante{turnsLeft !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Field groups */}
      <div className="flex-1 overflow-y-auto">
        {Object.entries(groups).map(([category, fields]) => (
          <CategorySection key={category} name={category} fields={fields} />
        ))}
      </div>
    </div>
  )
}
