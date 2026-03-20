'use client'

import type { FieldProgress } from '@/types/layer0'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

interface FieldCardProps {
  name: string
  field: FieldProgress
}

function confidenceBadge(confidence: number, status: string) {
  if (status === 'empty') {
    return <Badge variant="outline" className="border-gray-300 text-xs text-gray-400">vacío</Badge>
  }

  if (confidence >= 0.9) {
    return <Badge className="bg-emerald-100 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">{Math.round(confidence * 100)}%</Badge>
  }

  if (confidence >= 0.7) {
    return <Badge className="bg-blue-100 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{Math.round(confidence * 100)}%</Badge>
  }

  return <Badge className="bg-amber-100 text-xs text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{Math.round(confidence * 100)}%</Badge>
}

export function FieldCard({ name, field }: FieldCardProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between rounded-md px-2 py-1.5 text-xs',
        field.status === 'confirmed' && 'bg-emerald-50/50 dark:bg-emerald-950/10',
        field.status === 'extracted' && 'bg-blue-50/50 dark:bg-blue-950/10',
        field.status === 'ambiguous' && 'bg-amber-50/50 dark:bg-amber-950/10',
        field.status === 'empty' && 'bg-transparent'
      )}
    >
      <div className="flex items-center gap-1.5">
        <div
          className={cn(
            'size-1.5 rounded-full',
            field.status === 'confirmed' && 'bg-emerald-500',
            field.status === 'extracted' && 'bg-blue-500',
            field.status === 'ambiguous' && 'bg-amber-500',
            field.status === 'empty' && 'bg-gray-300 dark:bg-zinc-600'
          )}
        />
        <span className={cn(
          'truncate capitalize',
          field.is_required ? 'font-medium' : 'text-muted-foreground'
        )}>
          {name.replace(/_/g, ' ')}
        </span>
        {field.is_required && (
          <span className="text-xs text-red-400">*</span>
        )}
      </div>
      {confidenceBadge(field.confidence, field.status)}
    </div>
  )
}
