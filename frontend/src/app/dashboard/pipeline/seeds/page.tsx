import type { Metadata } from 'next'

import { SeedsPage } from '@/components/dashboard/pages/seeds-page'

export const metadata: Metadata = {
  title: 'Seeds',
}

export default function Page() {
  return <SeedsPage />
}
