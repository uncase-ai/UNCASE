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
    <div className="grid h-dvh grid-rows-[auto_1fr] overflow-hidden lg:grid-cols-[auto_1fr]">
      {/* Desktop sidebar — spans both rows */}
      <aside className="row-span-2 hidden lg:block">
        <Sidebar collapsed={collapsed} />
      </aside>

      {/* Mobile sidebar */}
      <MobileSidebar open={mobileOpen} onOpenChange={setMobileOpen} />

      {/* Header row */}
      <div className="min-w-0">
        <DemoBanner />
        <Topbar sidebarCollapsed={collapsed} onToggleSidebar={toggle} onOpenMobile={() => setMobileOpen(true)} />
      </div>

      {/* Content row — single scrollable area */}
      <main className="min-h-0 min-w-0 overflow-y-auto">
        <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6">{children}</div>
      </main>
    </div>
  )
}
