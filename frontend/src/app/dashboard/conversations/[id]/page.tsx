import type { Metadata } from 'next'

import { ConversationDetailPage } from '@/components/dashboard/pages/conversation-detail-page'

export const metadata: Metadata = {
  title: 'Conversation Detail',
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  return <ConversationDetailPage id={id} />
}
