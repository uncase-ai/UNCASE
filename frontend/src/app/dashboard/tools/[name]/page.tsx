import type { Metadata } from 'next'

import { ToolDetailPage } from '@/components/dashboard/pages/tool-detail-page'

export const metadata: Metadata = {
  title: 'Tool Detail',
}

export default async function Page({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params

  return <ToolDetailPage name={name} />
}
