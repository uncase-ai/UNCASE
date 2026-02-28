import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

type StatusVariant = 'success' | 'error' | 'warning' | 'info' | 'default' | 'running'

const VARIANT_CLASSES: Record<StatusVariant, string> = {
  success: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30',
  error: 'bg-destructive/10 text-destructive',
  warning: 'bg-muted/50',
  info: 'bg-muted/50',
  running: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30',
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
            variant === 'error' && 'bg-destructive',
            variant === 'warning' && 'bg-muted-foreground',
            variant === 'info' && 'bg-muted-foreground',
            variant === 'running' && 'animate-pulse bg-emerald-500',
            variant === 'default' && 'bg-muted-foreground'
          )}
        />
      )}
      {children}
    </Badge>
  )
}
