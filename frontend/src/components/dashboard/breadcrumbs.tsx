'use client'

import { Fragment } from 'react'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator
} from '@/components/ui/breadcrumb'

const LABEL_MAP: Record<string, string> = {
  dashboard: 'Dashboard',
  pipeline: 'Pipeline',
  seeds: 'Seeds',
  import: 'Import',
  evaluate: 'Evaluate',
  generate: 'Generate',
  export: 'Export',
  conversations: 'Conversations',
  templates: 'Templates',
  tools: 'Tools',
  evaluations: 'Evaluations',
  activity: 'Activity',
  settings: 'Settings'
}

export function DashboardBreadcrumbs() {
  const pathname = usePathname()
  const segments = pathname.split('/').filter(Boolean)

  if (segments.length <= 1) return null

  const crumbs = segments.map((seg, i) => ({
    label: LABEL_MAP[seg] ?? decodeURIComponent(seg),
    href: '/' + segments.slice(0, i + 1).join('/')
  }))

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {crumbs.map((crumb, i) => (
          <Fragment key={crumb.href}>
            {i > 0 && <BreadcrumbSeparator />}
            <BreadcrumbItem>
              {i === crumbs.length - 1 ? (
                <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
              ) : (
                <BreadcrumbLink asChild>
                  <Link href={crumb.href}>{crumb.label}</Link>
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
          </Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
