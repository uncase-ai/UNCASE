'use client'

import { useCallback, useState } from 'react'

import { DollarSign, TrendingUp, Zap, BarChart3 } from 'lucide-react'

import type { CostSummary, DailyCost } from '@/types/api'
import { useApi } from '@/hooks/use-api'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { fetchCostSummary, fetchDailyCosts } from '@/lib/api/costs'

type PeriodOption = '7' | '30' | '90'

export function CostsPage() {
  const [period, setPeriod] = useState<PeriodOption>('30')

  const summaryFetcher = useCallback(() => fetchCostSummary(Number(period)), [period])
  const dailyFetcher = useCallback(() => fetchDailyCosts(Number(period)), [period])

  const { data: summary, loading: summaryLoading } = useApi<CostSummary>(summaryFetcher)
  const { data: dailyCosts, loading: dailyLoading } = useApi<DailyCost[]>(dailyFetcher)

  const formatUsd = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

  const formatNumber = (n: number) => new Intl.NumberFormat('en-US').format(n)

  const isLoading = summaryLoading || dailyLoading

  return (
    <div>
      <PageHeader
        title="Cost Tracking"
        description="LLM API spend visibility per organization and provider"
        actions={
          <Select value={period} onValueChange={(v) => setPeriod(v as PeriodOption)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      {/* Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Spend</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : formatUsd(summary?.total_cost_usd ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">Last {period} days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : formatNumber(summary?.total_tokens ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">Input + output</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Calls</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : formatNumber(summary?.event_count ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">LLM requests</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Cost/Call</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading
                ? '...'
                : summary && summary.event_count > 0
                  ? formatUsd(summary.total_cost_usd / summary.event_count)
                  : '$0.00'}
            </div>
            <p className="text-xs text-muted-foreground">Per API call</p>
          </CardContent>
        </Card>
      </div>

      {/* Cost by Provider */}
      <div className="grid gap-4 lg:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Cost by Provider</CardTitle>
          </CardHeader>
          <CardContent>
            {!summary || Object.keys(summary.cost_by_provider).length === 0 ? (
              <p className="text-sm text-muted-foreground">No provider data yet</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(summary.cost_by_provider)
                  .sort(([, a], [, b]) => b - a)
                  .map(([provider, cost]) => {
                    const pct = summary.total_cost_usd > 0 ? (cost / summary.total_cost_usd) * 100 : 0

                    return (
                      <div key={provider} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="capitalize">
                            {provider}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="h-2 w-24 rounded-full bg-muted overflow-hidden">
                            <div
                              className="h-full rounded-full bg-primary"
                              style={{ width: `${Math.min(pct, 100)}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium w-20 text-right">{formatUsd(cost)}</span>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Cost by Event Type</CardTitle>
          </CardHeader>
          <CardContent>
            {!summary || Object.keys(summary.cost_by_event_type).length === 0 ? (
              <p className="text-sm text-muted-foreground">No event data yet</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(summary.cost_by_event_type)
                  .sort(([, a], [, b]) => b - a)
                  .map(([eventType, cost]) => (
                    <div key={eventType} className="flex items-center justify-between">
                      <Badge variant="secondary">{eventType.replace(/_/g, ' ')}</Badge>
                      <span className="text-sm font-medium">{formatUsd(cost)}</span>
                    </div>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Daily Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Daily API Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {!dailyCosts || dailyCosts.length === 0 ? (
            <EmptyState icon={BarChart3} title="No activity" description="No LLM API calls recorded in this period" />
          ) : (
            <div className="space-y-1">
              {dailyCosts.map((day) => {
                const maxEvents = Math.max(...dailyCosts.map((d) => d.event_count), 1)
                const barWidth = (day.event_count / maxEvents) * 100

                return (
                  <div key={day.date} className="flex items-center gap-3 text-sm">
                    <span className="w-24 text-muted-foreground shrink-0">{day.date}</span>
                    <div className="flex-1 h-5 rounded bg-muted overflow-hidden">
                      <div
                        className="h-full rounded bg-primary/60"
                        style={{ width: `${barWidth}%` }}
                      />
                    </div>
                    <span className="w-16 text-right font-medium">{day.event_count}</span>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
