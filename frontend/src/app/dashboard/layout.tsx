import type { ReactNode } from 'react'

import type { Metadata } from 'next'

import { AuthProvider } from '@/contexts/auth-context'
import { AuthGuard } from '@/components/auth/auth-guard'
import { DashboardShell } from '@/components/dashboard/dashboard-shell'

export const metadata: Metadata = {
  title: {
    template: '%s | UNCASE Dashboard',
    default: 'Dashboard | UNCASE'
  },
  robots: {
    index: false,
    follow: false
  }
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AuthGuard>
        <DashboardShell>{children}</DashboardShell>
      </AuthGuard>
    </AuthProvider>
  )
}
