'use client'

import { useCallback, useEffect, useState } from 'react'

import { ExternalLink, Lock, LogOut, Menu, Moon, PanelLeftClose, PanelLeftOpen, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'

import { checkApiHealth } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/auth-context'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

import { DashboardBreadcrumbs } from './breadcrumbs'

interface TopbarProps {
  sidebarCollapsed: boolean
  onToggleSidebar: () => void
  onOpenMobile: () => void
}

export function Topbar({ sidebarCollapsed, onToggleSidebar, onOpenMobile }: TopbarProps) {
  const { theme, setTheme } = useTheme()
  const { user, isDemo, logout } = useAuth()
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

  const initials = user?.display_name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) ?? '?'

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
      <img src="/images/logo/logo-dark.svg" alt="UNCASE" className="h-4 w-auto dark:hidden" />
      <img src="/images/logo/logo-white.svg" alt="UNCASE" className="hidden h-4 w-auto dark:block" />

      {/* Breadcrumbs */}
      <div className="ml-2 hidden md:block">
        <DashboardBreadcrumbs />
      </div>

      <div className="flex-1" />

      {/* API status indicator */}
      <div className="hidden items-center gap-3 sm:flex">
        <Tooltip>
          <TooltipTrigger asChild>
            <button className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs" onClick={checkHealth}>
              <span className="relative flex size-2">
                {apiConnected && (
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                )}
                <span
                  className={cn(
                    'relative inline-flex size-2 rounded-full',
                    apiConnected === null && 'animate-pulse bg-muted-foreground',
                    apiConnected === true && 'bg-emerald-500',
                    apiConnected === false && 'bg-destructive'
                  )}
                />
              </span>
              <span className={cn(apiConnected ? 'text-emerald-700 dark:text-emerald-400' : 'text-muted-foreground')}>
                {apiConnected === null ? 'Checking...' : apiConnected ? 'Established' : 'Offline'}
              </span>
            </button>
          </TooltipTrigger>
          <TooltipContent>
            {apiConnected ? 'API connected — click to refresh' : apiConnected === false ? 'API unreachable — click to retry' : 'Checking connectivity...'}
          </TooltipContent>
        </Tooltip>

        {apiConnected && (
          <>
            <span className="h-3 w-px bg-border" />
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <Lock className="size-3" />
              Local
            </span>
            <span className="h-3 w-px bg-border" />
            <a
              href="http://localhost:4000"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
            >
              Manage connections
              <ExternalLink className="size-3" />
            </a>
          </>
        )}
      </div>

      {/* Mobile API dot */}
      <Tooltip>
        <TooltipTrigger asChild>
          <button className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground sm:hidden" onClick={checkHealth}>
            <span className="relative flex size-2">
              {apiConnected && (
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              )}
              <span
                className={cn(
                  'relative inline-flex size-2 rounded-full',
                  apiConnected === null && 'animate-pulse bg-muted-foreground',
                  apiConnected === true && 'bg-emerald-500',
                  apiConnected === false && 'bg-destructive'
                )}
              />
            </span>
          </button>
        </TooltipTrigger>
        <TooltipContent>
          {apiConnected ? 'API connected' : apiConnected === false ? 'Offline' : 'Checking...'}
        </TooltipContent>
      </Tooltip>

      {/* Theme toggle */}
      <Button variant="ghost" size="icon" className="size-8" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
        <Sun className="size-4 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute size-4 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" />
      </Button>

      {/* User menu */}
      {user && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative size-8 rounded-full">
              <Avatar className="size-8">
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-medium">{user.display_name}</span>
                <span className="text-xs text-muted-foreground">{user.email}</span>
                <div className="flex items-center gap-1.5 pt-0.5">
                  <Badge variant="outline" className="px-1.5 py-0 text-xs">{user.role}</Badge>
                  {isDemo && <Badge variant="secondary" className="px-1.5 py-0 text-xs">Demo</Badge>}
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled>Profile</DropdownMenuItem>
            <DropdownMenuItem disabled>Switch Organization</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>
              <LogOut className="mr-2 size-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </header>
  )
}
