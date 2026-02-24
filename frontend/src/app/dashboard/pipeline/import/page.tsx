import type { Metadata } from 'next'

import { ImportPage } from '@/components/dashboard/pages/import-page'

export const metadata: Metadata = {
  title: 'Import',
}

export default function Page() {
  return <ImportPage />
}
