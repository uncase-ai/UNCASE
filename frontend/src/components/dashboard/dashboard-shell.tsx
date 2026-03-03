'use client'

import type { ReactNode } from 'react'
import { useState } from 'react'

import { useSidebar } from '@/hooks/use-dashboard'

import { DemoBanner } from './demo-banner'
import { MobileSidebar } from './mobile-sidebar'
import { Sidebar } from './sidebar'
import { Topbar } from './topbar'

export function DashboardShell({ children }: { children: ReactNode }) {
  const { collapsed, toggle } = useSidebar()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="fixed inset-0 flex overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex">
        <Sidebar collapsed={collapsed} />
      </div>

      {/* Mobile sidebar */}
      <MobileSidebar open={mobileOpen} onOpenChange={setMobileOpen} />

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <DemoBanner />
        <Topbar sidebarCollapsed={collapsed} onToggleSidebar={toggle} onOpenMobile={() => setMobileOpen(true)} />
        <main className="flex min-h-0 flex-1 flex-col overflow-hidden">
          <div className="mx-auto flex min-h-0 w-full max-w-7xl flex-1 flex-col overflow-y-auto px-4 py-6 sm:px-6">{children}</div>
        </main>
      </div>
    </div>
  )
}
