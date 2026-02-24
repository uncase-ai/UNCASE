'use client'

import {
  Activity,
  ArrowDownToLine,
  BarChart3,
  BookOpen,
  FlaskConical,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  PackageOpen,
  Puzzle,
  Rocket,
  Settings,
  Sprout
} from 'lucide-react'

import type { NavGroup } from '@/types/dashboard'
import { cn } from '@/lib/utils'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

import { SidebarNavItem } from './sidebar-nav-item'

const NAV_GROUPS: NavGroup[] = [
  {
    items: [{ label: 'Overview', href: '/dashboard', icon: LayoutDashboard }]
  },
  {
    label: 'Pipeline',
    items: [
      { label: 'Pipeline', href: '/dashboard/pipeline', icon: GitBranch },
      { label: 'Seeds', href: '/dashboard/pipeline/seeds', icon: Sprout },
      { label: 'Import', href: '/dashboard/pipeline/import', icon: ArrowDownToLine },
      { label: 'Evaluate', href: '/dashboard/pipeline/evaluate', icon: FlaskConical },
      { label: 'Generate', href: '/dashboard/pipeline/generate', icon: Rocket },
      { label: 'Export', href: '/dashboard/pipeline/export', icon: PackageOpen }
    ]
  },
  {
    label: 'Workbench',
    items: [
      { label: 'Conversations', href: '/dashboard/conversations', icon: MessageSquare },
      { label: 'Templates', href: '/dashboard/templates', icon: BookOpen },
      { label: 'Tools', href: '/dashboard/tools', icon: Puzzle }
    ]
  },
  {
    label: 'Insights',
    items: [{ label: 'Evaluations', href: '/dashboard/evaluations', icon: BarChart3 }]
  },
  {
    items: [
      { label: 'Activity', href: '/dashboard/activity', icon: Activity },
      { label: 'Settings', href: '/dashboard/settings', icon: Settings }
    ]
  }
]

interface SidebarProps {
  collapsed: boolean
  onNavigate?: () => void
}

export function Sidebar({ collapsed, onNavigate }: SidebarProps) {
  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-sidebar-border bg-sidebar transition-[width] duration-200',
        collapsed ? 'w-14' : 'w-56'
      )}
    >
      <ScrollArea className="flex-1 py-2">
        <nav className="flex flex-col gap-1 px-2">
          {NAV_GROUPS.map((group, gi) => (
            <div key={gi}>
              {gi > 0 && <Separator className="my-2" />}
              {group.label && !collapsed && (
                <span className="mb-1 block px-3 pt-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {group.label}
                </span>
              )}
              {group.items.map(item => (
                <SidebarNavItem key={item.href} item={item} collapsed={collapsed} onNavigate={onNavigate} />
              ))}
            </div>
          ))}
        </nav>
      </ScrollArea>
    </aside>
  )
}

export { NAV_GROUPS }
