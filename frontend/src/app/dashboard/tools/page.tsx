import type { Metadata } from 'next'

import { ToolsPage } from '@/components/dashboard/pages/tools-page'

export const metadata: Metadata = {
  title: 'Tools',
}

export default function Page() {
  return <ToolsPage />
}
