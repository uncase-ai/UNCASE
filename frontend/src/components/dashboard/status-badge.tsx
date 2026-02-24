import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

type StatusVariant = 'success' | 'error' | 'warning' | 'info' | 'default' | 'running'

const VARIANT_CLASSES: Record<StatusVariant, string> = {
  success: 'bg-muted/50',
  error: 'bg-destructive/10 text-destructive',
  warning: 'bg-muted/50',
  info: 'bg-muted/50',
  running: 'bg-muted/50',
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
            variant === 'success' && 'bg-foreground',
            variant === 'error' && 'bg-destructive',
            variant === 'warning' && 'bg-muted-foreground',
            variant === 'info' && 'bg-muted-foreground',
            variant === 'running' && 'animate-pulse bg-foreground',
            variant === 'default' && 'bg-muted-foreground'
          )}
        />
      )}
      {children}
    </Badge>
  )
}
