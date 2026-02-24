import type { Metadata } from 'next'

import { ConversationsPage } from '@/components/dashboard/pages/conversations-page'

export const metadata: Metadata = {
  title: 'Conversations',
}

export default function Page() {
  return <ConversationsPage />
}
