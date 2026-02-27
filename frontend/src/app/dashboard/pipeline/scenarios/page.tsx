import type { Metadata } from 'next'

import { ScenariosPage } from '@/components/dashboard/pages/scenarios-page'

export const metadata: Metadata = {
  title: 'Scenarios',
}

export default function Page() {
  return <ScenariosPage />
}
