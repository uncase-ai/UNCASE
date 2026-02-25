import type { Metadata } from 'next'

import { PluginsPage } from '@/components/dashboard/pages/plugins-page'

export const metadata: Metadata = {
  title: 'Plugins',
}

export default function Page() {
  return <PluginsPage />
}
