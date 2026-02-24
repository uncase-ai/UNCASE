import type { Metadata } from 'next'

import { ActivityPage } from '@/components/dashboard/pages/activity-page'

export const metadata: Metadata = {
  title: 'Activity',
}

export default function Page() {
  return <ActivityPage />
}
