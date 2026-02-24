import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

type StatusVariant = 'success' | 'error' | 'warning' | 'info' | 'default' | 'running'

const VARIANT_CLASSES: Record<StatusVariant, string> = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-400',
  error: 'border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-400',
  warning: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-400',
  info: 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-400',
  running: 'border-violet-200 bg-violet-50 text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-400',
  default: ''
}

interface StatusBadgeProps {
  variant: StatusVariant
  children: React.ReactNode
  dot?: boolean
  className?: string
}

export function StatusBadge({ variant, children, dot = true, className }: StatusBadgeProps) {
  return (
    <Badge variant="outline" className={cn('gap-1.5 font-normal', VARIANT_CLASSES[variant], className)}>
      {dot && (
        <span
          className={cn(
            'size-1.5 rounded-full',
            variant === 'success' && 'bg-emerald-500',
            variant === 'error' && 'bg-red-500',
            variant === 'warning' && 'bg-amber-500',
            variant === 'info' && 'bg-blue-500',
            variant === 'running' && 'animate-pulse bg-violet-500',
            variant === 'default' && 'bg-muted-foreground'
          )}
        />
      )}
      {children}
    </Badge>
  )
}
