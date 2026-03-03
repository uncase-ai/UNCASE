'use client'

import type { ReactNode } from 'react'
import { useState } from 'react'

import { useSidebar } from '@/hooks/use-dashboard'

import { DemoBanner } from './demo-banner'
import { MobileSidebar } from './mobile-sidebar'
import { Sidebar } from './sidebar'
import { Topbar } from './topbar'
import { WelcomeModal } from './welcome-modal'

export function DashboardShell({ children }: { children: ReactNode }) {
  const { collapsed, toggle } = useSidebar()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex h-dvh overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden lg:block">
        <Sidebar collapsed={collapsed} />
      </div>

      {/* Mobile sidebar */}
      <MobileSidebar open={mobileOpen} onOpenChange={setMobileOpen} />

      <WelcomeModal />

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        <DemoBanner />
        <Topbar sidebarCollapsed={collapsed} onToggleSidebar={toggle} onOpenMobile={() => setMobileOpen(true)} />
        <main id="dashboard-main" className="flex min-h-0 flex-1 flex-col">
          <div className="mx-auto flex w-full min-h-0 flex-1 flex-col overflow-y-auto max-w-7xl px-4 py-6 sm:px-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
