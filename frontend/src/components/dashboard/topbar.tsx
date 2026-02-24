'use client'

import { useCallback, useEffect, useState } from 'react'

import { Menu, Moon, PanelLeftClose, PanelLeftOpen, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'

import { checkApiHealth } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

import { DashboardBreadcrumbs } from './breadcrumbs'

interface TopbarProps {
  sidebarCollapsed: boolean
  onToggleSidebar: () => void
  onOpenMobile: () => void
}

export function Topbar({ sidebarCollapsed, onToggleSidebar, onOpenMobile }: TopbarProps) {
  const { theme, setTheme } = useTheme()
  const [apiConnected, setApiConnected] = useState<boolean | null>(null)

  const checkHealth = useCallback(async () => {
    const ok = await checkApiHealth()

    setApiConnected(ok)
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    checkHealth()
    const id = setInterval(checkHealth, 15000)

    return () => clearInterval(id)
  }, [checkHealth])

  return (
    <header className="flex h-12 shrink-0 items-center gap-2 border-b border-border bg-background px-4">
      {/* Mobile hamburger */}
      <Button variant="ghost" size="icon" className="size-8 lg:hidden" onClick={onOpenMobile}>
        <Menu className="size-4" />
      </Button>

      {/* Desktop sidebar toggle */}
      <Button variant="ghost" size="icon" className="hidden size-8 lg:flex" onClick={onToggleSidebar}>
        {sidebarCollapsed ? <PanelLeftOpen className="size-4" /> : <PanelLeftClose className="size-4" />}
      </Button>

      {/* Logo */}
      <img src="/images/logo/icon.png" alt="UNCASE" className="size-5 dark:invert" />
      <span className="text-sm font-bold tracking-tight">UNCASE</span>

      {/* Breadcrumbs */}
      <div className="ml-2 hidden md:block">
        <DashboardBreadcrumbs />
      </div>

      <div className="flex-1" />

      {/* API status indicator */}
      <Tooltip>
        <TooltipTrigger asChild>
          <button className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground" onClick={checkHealth}>
            <span
              className={cn(
                'size-2 rounded-full',
                apiConnected === null && 'bg-muted-foreground animate-pulse',
                apiConnected === true && 'bg-foreground',
                apiConnected === false && 'bg-destructive'
              )}
            />
            <span className="hidden sm:inline">{apiConnected === null ? 'Checking...' : apiConnected ? 'API' : 'Offline'}</span>
          </button>
        </TooltipTrigger>
        <TooltipContent>
          {apiConnected ? 'API connected' : apiConnected === false ? 'API unreachable — click to retry' : 'Checking connectivity...'}
        </TooltipContent>
      </Tooltip>

      {/* Theme toggle */}
      <Button variant="ghost" size="icon" className="size-8" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
        <Sun className="size-4 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute size-4 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" />
      </Button>
    </header>
  )
}
