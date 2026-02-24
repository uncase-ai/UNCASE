'use client'

import type { LucideIcon } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { NumberTicker } from '@/components/ui/number-ticker'

interface StatsCardProps {
  title: string
  value: number | null
  icon: LucideIcon
  description?: string
  trend?: { value: number; label: string }
  className?: string
}

export function StatsCard({ title, value, icon: Icon, description, trend, className }: StatsCardProps) {
  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">{title}</span>
          <Icon className="size-4 text-muted-foreground" />
        </div>
        <div className="mt-2">
          {value === null ? (
            <Skeleton className="h-8 w-20" />
          ) : (
            <div className="text-2xl font-bold">
              <NumberTicker value={value} />
            </div>
          )}
        </div>
        {(description || trend) && (
          <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
            {trend && (
              <span className={cn('font-medium', trend.value < 0 && 'text-destructive')}>
                {trend.value >= 0 ? '+' : ''}
                {trend.value}%
              </span>
            )}
            <span>{description ?? trend?.label}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
