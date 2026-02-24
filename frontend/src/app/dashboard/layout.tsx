import type { ReactNode } from 'react'

import type { Metadata } from 'next'

import { DashboardShell } from '@/components/dashboard/dashboard-shell'

export const metadata: Metadata = {
  title: {
    template: '%s | UNCASE Dashboard',
    default: 'Dashboard | UNCASE'
  }
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>
}
