'use client'

import {
  Activity,
  ArrowDownToLine,
  BarChart3,
  BookOpen,
  Cable,
  ClipboardList,
  DollarSign,
  FlaskConical,
  GitBranch,
  Layers,
  LayoutDashboard,
  Library,
  LogOut,
  ShieldCheck,
  MessageSquare,
  Package,
  PackageOpen,
  Puzzle,
  Rocket,
  Settings,
  Sprout
} from 'lucide-react'

import type { NavGroup } from '@/types/dashboard'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/auth-context'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

import { SidebarNavItem } from './sidebar-nav-item'

const ROLE_LEVELS: Record<string, number> = { owner: 4, admin: 3, member: 2, viewer: 1 }

function hasRole(userRole: string | undefined, requiredRole: string): boolean {
  return (ROLE_LEVELS[userRole ?? 'viewer'] ?? 0) >= (ROLE_LEVELS[requiredRole] ?? 0)
}

const NAV_GROUPS: NavGroup[] = [
  {
    items: [{ label: 'Overview', href: '/dashboard', icon: LayoutDashboard }]
  },
  {
    label: 'Data Pipeline',
    items: [
      { label: 'Pipeline', href: '/dashboard/pipeline', icon: GitBranch },
      { label: 'Seeds', href: '/dashboard/pipeline/seeds', icon: Sprout },
      { label: 'Scenarios', href: '/dashboard/pipeline/scenarios', icon: Layers },
      { label: 'Import', href: '/dashboard/pipeline/import', icon: ArrowDownToLine },
      { label: 'Generate', href: '/dashboard/pipeline/generate', icon: Rocket },
      { label: 'Evaluate', href: '/dashboard/pipeline/evaluate', icon: FlaskConical },
      { label: 'Export', href: '/dashboard/pipeline/export', icon: PackageOpen }
    ]
  },
  {
    label: 'Resources',
    items: [
      { label: 'Conversations', href: '/dashboard/conversations', icon: MessageSquare },
      { label: 'Knowledge', href: '/dashboard/knowledge', icon: Library },
      { label: 'Templates', href: '/dashboard/templates', icon: BookOpen },
      { label: 'Tools', href: '/dashboard/tools', icon: Puzzle },
      { label: 'Plugins', href: '/dashboard/plugins', icon: Package },
      { label: 'Connectors', href: '/dashboard/connectors', icon: Cable }
    ]
  },
  {
    label: 'Insights',
    items: [
      { label: 'Evaluations', href: '/dashboard/evaluations', icon: BarChart3 },
      { label: 'Jobs', href: '/dashboard/jobs', icon: ClipboardList },
      { label: 'Costs', href: '/dashboard/costs', icon: DollarSign, requiredRole: 'admin' },
      { label: 'Blockchain', href: '/dashboard/blockchain', icon: ShieldCheck }
    ]
  },
  {
    items: [
      { label: 'Activity', href: '/dashboard/activity', icon: Activity },
      { label: 'Settings', href: '/dashboard/settings', icon: Settings, requiredRole: 'admin' }
    ]
  }
]

interface SidebarProps {
  collapsed: boolean
  onNavigate?: () => void
}

export function Sidebar({ collapsed, onNavigate }: SidebarProps) {
  const { user, isDemo, logout } = useAuth()
  const userRole = user?.role

  const initials = user?.display_name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) ?? '?'

  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-sidebar-border bg-sidebar transition-[width] duration-200',
        collapsed ? 'w-14' : 'w-56'
      )}
    >
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-2 py-2">
          {NAV_GROUPS.map((group, gi) => {
            const visibleItems = group.items.filter(
              item => !item.requiredRole || hasRole(userRole, item.requiredRole)
            )

            if (visibleItems.length === 0) return null

            return (
              <div key={gi}>
                {gi > 0 && <Separator className="my-2" />}
                {group.label && !collapsed && (
                  <span className="mb-1 block px-3 pt-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    {group.label}
                  </span>
                )}
                {visibleItems.map(item => (
                  <SidebarNavItem key={item.href} item={item} collapsed={collapsed} onNavigate={onNavigate} />
                ))}
              </div>
            )
          })}
        </nav>

      {/* User info */}
      {user && (
        <div className="border-t border-sidebar-border px-2 py-2">
          {collapsed ? (
            <div className="flex flex-col items-center gap-1">
              <Avatar className="size-8">
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
              <Button variant="ghost" size="icon" className="size-8" onClick={logout}>
                <LogOut className="size-4" />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded-md px-1 py-1.5">
              <Avatar className="size-8 shrink-0">
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
              <div className="flex min-w-0 flex-1 flex-col">
                <span className="truncate text-sm font-medium leading-tight">{user.display_name}</span>
                <div className="flex items-center gap-1">
                  <Badge variant="outline" className="px-1.5 py-0 text-[10px]">{user.role}</Badge>
                  {isDemo && <Badge variant="secondary" className="px-1.5 py-0 text-[10px]">Demo</Badge>}
                </div>
              </div>
              <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={logout}>
                <LogOut className="size-3.5" />
              </Button>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}

export { NAV_GROUPS }
