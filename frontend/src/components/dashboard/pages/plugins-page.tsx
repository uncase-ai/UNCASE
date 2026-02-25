'use client'

import { useCallback, useMemo, useState } from 'react'

import {
  Car,
  Check,
  ChevronDown,
  ChevronUp,
  Clock,
  Download,
  Factory,
  GraduationCap,
  HeartPulse,
  Landmark,
  Loader2,
  Package,
  Scale,
  Search,
  Settings2,
  ShieldCheck,
  Trash2,
  Users,
  Wrench
} from 'lucide-react'

import type { InstalledPluginListResponse, InstalledPluginResponse, PluginManifest } from '@/types/api'
import { SUPPORTED_DOMAINS } from '@/types/api'
import { cn } from '@/lib/utils'
import { useApi } from '@/hooks/use-api'
import { fetchInstalledPlugins, fetchPlugins, installPlugin, uninstallPlugin, updatePluginConfig } from '@/lib/api/plugins'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

// ─── Icon mapping ───

const DOMAIN_ICONS: Record<string, React.ElementType> = {
  'automotive.sales': Car,
  'medical.consultation': HeartPulse,
  'legal.advisory': Scale,
  'finance.advisory': Landmark,
  'industrial.support': Factory,
  'education.tutoring': GraduationCap
}

const PLUGIN_ICONS: Record<string, React.ElementType> = {
  car: Car,
  'heart-pulse': HeartPulse,
  scale: Scale,
  landmark: Landmark,
  factory: Factory,
  'graduation-cap': GraduationCap,
  puzzle: Package,
  wrench: Wrench
}

// ─── Main Component ───

export function PluginsPage() {
  const { data: plugins, loading, error, execute: refetchPlugins } = useApi<PluginManifest[]>(
    useCallback((signal: AbortSignal) => fetchPlugins(undefined, signal), [])
  )

  const { data: installedData, loading: installedLoading, execute: refetchInstalled } = useApi<InstalledPluginListResponse>(
    useCallback((signal: AbortSignal) => fetchInstalledPlugins(signal), [])
  )

  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({})
  const [expandedPlugin, setExpandedPlugin] = useState<string | null>(null)

  // Config dialog state
  const [configTarget, setConfigTarget] = useState<InstalledPluginResponse | null>(null)
  const [configActive, setConfigActive] = useState(true)
  const [configSaving, setConfigSaving] = useState(false)

  // Filters
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<string>('all')

  const installedItems = useMemo(() => installedData?.items ?? [], [installedData])
  const installedIds = useMemo(() => new Set(installedItems.map(p => p.plugin_id)), [installedItems])

  const installedMap = useMemo(() => {
    const map = new Map<string, InstalledPluginResponse>()

    for (const p of installedItems) map.set(p.plugin_id, p)

    return map
  }, [installedItems])

  const filtered = useMemo(() => {
    if (!plugins) return []
    let result = plugins

    if (search) {
      const q = search.toLowerCase()

      result = result.filter(
        p =>
          p.name.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q) ||
          p.tags.some(t => t.toLowerCase().includes(q))
      )
    }

    if (domainFilter !== 'all') {
      result = result.filter(p => p.domains.includes(domainFilter))
    }

    if (sourceFilter !== 'all') {
      result = result.filter(p => p.source === sourceFilter)
    }

    return result
  }, [plugins, search, domainFilter, sourceFilter])

  const handleInstall = async (pluginId: string) => {
    setActionLoading(prev => ({ ...prev, [pluginId]: true }))
    const res = await installPlugin(pluginId)

    if (res.data) {
      await refetchInstalled()
    }

    setActionLoading(prev => ({ ...prev, [pluginId]: false }))
  }

  const handleUninstall = async (pluginId: string) => {
    setActionLoading(prev => ({ ...prev, [pluginId]: true }))
    await uninstallPlugin(pluginId)
    await refetchInstalled()
    setActionLoading(prev => ({ ...prev, [pluginId]: false }))
  }

  const handleOpenConfig = (installed: InstalledPluginResponse) => {
    setConfigTarget(installed)
    setConfigActive(installed.is_active)
  }

  const handleSaveConfig = async () => {
    if (!configTarget) return
    setConfigSaving(true)
    await updatePluginConfig(configTarget.plugin_id, { is_active: configActive })
    setConfigSaving(false)
    setConfigTarget(null)
    await refetchInstalled()
  }

  const installedCount = installedItems.length
  const totalTools = installedItems.reduce((sum, p) => sum + p.tools_registered.length, 0)

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Plugins" description="Extend the pipeline with domain-specific tool packs" />
        <div className="flex items-center justify-center py-16">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader title="Plugins" description="Extend the pipeline with domain-specific tool packs" />
        <EmptyState
          icon={Package}
          title="Failed to load plugins"
          description={error.message}
          action={<Button variant="outline" onClick={() => refetchPlugins()}>Retry</Button>}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Plugins"
        description="Extend the pipeline with domain-specific tool packs"
        actions={
          <div className="flex items-center gap-3">
            {!installedLoading && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{installedCount} installed</span>
                <span className="text-muted-foreground/40">|</span>
                <span>{totalTools} tools active</span>
              </div>
            )}
          </div>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search plugins..."
            className="pl-9"
          />
        </div>
        <Select value={domainFilter} onValueChange={setDomainFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Domain" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Domains</SelectItem>
            {SUPPORTED_DOMAINS.map(d => (
              <SelectItem key={d} value={d}>
                {d.replace('.', ' / ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={sourceFilter} onValueChange={setSourceFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Source" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sources</SelectItem>
            <SelectItem value="official">Official</SelectItem>
            <SelectItem value="community">Community</SelectItem>
          </SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{filtered.length} plugins</span>
      </div>

      {/* Plugin cards */}
      {!plugins || filtered.length === 0 ? (
        <EmptyState
          icon={Package}
          title="No plugins match"
          description="Try adjusting your search or filter criteria."
          action={
            <Button variant="outline" size="sm" onClick={() => { setSearch(''); setDomainFilter('all'); setSourceFilter('all') }}>
              Clear filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filtered.map(plugin => {
            const isInstalled = installedIds.has(plugin.id)
            const installedRecord = installedMap.get(plugin.id)
            const isLoading = actionLoading[plugin.id]
            const isExpanded = expandedPlugin === plugin.id

            const IconComponent = PLUGIN_ICONS[plugin.icon] ?? Package

            return (
              <Card key={plugin.id} className={cn('transition-colors', isInstalled && 'border-foreground/20')}>
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      'flex size-10 shrink-0 items-center justify-center rounded-lg border',
                      isInstalled ? 'border-foreground/20 bg-foreground/5' : 'bg-muted/50'
                    )}>
                      <IconComponent className="size-5 text-muted-foreground" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-sm">{plugin.name}</CardTitle>
                        {plugin.verified && (
                          <ShieldCheck className="size-3.5 text-foreground" />
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-muted-foreground">v{plugin.version}</span>
                        <span className="text-muted-foreground/40">·</span>
                        <span className="text-[11px] text-muted-foreground">{plugin.author}</span>
                        {plugin.downloads > 0 && (
                          <>
                            <span className="text-muted-foreground/40">·</span>
                            <span className="flex items-center gap-0.5 text-[11px] text-muted-foreground">
                              <Download className="size-2.5" />
                              {plugin.downloads.toLocaleString()}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex shrink-0 items-center gap-1">
                      {isInstalled ? (
                        <>
                          <StatusBadge variant="success">Installed</StatusBadge>
                          {installedRecord && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="size-7"
                              onClick={() => handleOpenConfig(installedRecord)}
                              title="Configure"
                            >
                              <Settings2 className="size-3" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-7 text-destructive"
                            onClick={() => handleUninstall(plugin.id)}
                            disabled={isLoading}
                            title="Uninstall"
                          >
                            {isLoading ? <Loader2 className="size-3 animate-spin" /> : <Trash2 className="size-3" />}
                          </Button>
                        </>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleInstall(plugin.id)}
                          disabled={isLoading}
                          className="gap-1.5"
                        >
                          {isLoading ? (
                            <Loader2 className="size-3 animate-spin" />
                          ) : (
                            <Download className="size-3" />
                          )}
                          Install
                        </Button>
                      )}
                    </div>
                  </div>
                  <CardDescription className="mt-2 text-xs leading-relaxed">
                    {plugin.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  {/* Tags */}
                  <div className="flex flex-wrap gap-1.5">
                    {plugin.domains.map(d => {
                      const DomainIcon = DOMAIN_ICONS[d]

                      return (
                        <Badge key={d} variant="secondary" className="gap-1 text-[10px]">
                          {DomainIcon && <DomainIcon className="size-2.5" />}
                          {d.replace('.', ' / ')}
                        </Badge>
                      )
                    })}
                    <Badge variant="outline" className="gap-1 text-[10px]">
                      <Wrench className="size-2.5" />
                      {plugin.tools.length} tools
                    </Badge>
                    {plugin.source === 'official' && (
                      <Badge variant="outline" className="gap-1 text-[10px]">
                        <Users className="size-2.5" />
                        Official
                      </Badge>
                    )}
                    {plugin.license && (
                      <Badge variant="outline" className="text-[10px]">
                        {plugin.license}
                      </Badge>
                    )}
                    {installedRecord && (
                      <Badge variant="outline" className="gap-1 text-[10px]">
                        <Clock className="size-2.5" />
                        {new Date(installedRecord.created_at).toLocaleDateString()}
                      </Badge>
                    )}
                  </div>

                  {/* Expand/collapse tools */}
                  <div>
                    <button
                      type="button"
                      onClick={() => setExpandedPlugin(isExpanded ? null : plugin.id)}
                      className="flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {isExpanded ? <ChevronUp className="size-3" /> : <ChevronDown className="size-3" />}
                      {isExpanded ? 'Hide' : 'Show'} {plugin.tools.length} tools
                    </button>
                    {isExpanded && (
                      <div className="mt-2 space-y-1.5">
                        <Separator />
                        {plugin.tools.map(tool => {
                          const isRegistered = isInstalled && installedRecord?.tools_registered.includes(tool.name)

                          return (
                            <div
                              key={tool.name}
                              className="flex items-start gap-2 rounded-md px-2 py-1.5"
                            >
                              <code className="shrink-0 text-[11px] font-medium">{tool.name}</code>
                              {isRegistered && <Check className="mt-0.5 size-3 shrink-0 text-foreground" />}
                              <span className="line-clamp-1 text-[11px] text-muted-foreground">
                                {tool.description.split('\n')[0]}
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Plugin config dialog */}
      <Dialog open={!!configTarget} onOpenChange={open => { if (!open) setConfigTarget(null) }}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Plugin Settings</DialogTitle>
            <DialogDescription>
              Configure {configTarget?.plugin_name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="flex items-center justify-between">
              <Label>Active</Label>
              <Switch checked={configActive} onCheckedChange={setConfigActive} />
            </div>
            <p className="text-xs text-muted-foreground">
              When disabled, the plugin&apos;s tools will not be available in the pipeline.
            </p>
            {configTarget && (
              <div className="space-y-1 text-xs text-muted-foreground">
                <p>Version: {configTarget.plugin_version}</p>
                <p>Source: {configTarget.plugin_source}</p>
                <p>Tools: {configTarget.tools_registered.length}</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfigTarget(null)}>Cancel</Button>
            <Button onClick={handleSaveConfig} disabled={configSaving}>
              {configSaving && <Loader2 className="mr-1.5 size-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
