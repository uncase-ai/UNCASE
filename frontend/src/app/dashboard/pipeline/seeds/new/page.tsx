import type { Metadata } from 'next'

import { SeedCreatePage } from '@/components/dashboard/pages/seed-create-page'

export const metadata: Metadata = {
  title: 'Create Seed',
}

export default function Page() {
  return <SeedCreatePage />
}
