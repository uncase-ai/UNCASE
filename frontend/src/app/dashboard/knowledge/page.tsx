import type { Metadata } from 'next'

import { KnowledgePage } from '@/components/dashboard/pages/knowledge-page'

export const metadata: Metadata = {
  title: 'Knowledge Base'
}

export default function Page() {
  return <KnowledgePage />
}
