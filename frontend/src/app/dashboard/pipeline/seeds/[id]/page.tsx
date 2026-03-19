import type { Metadata } from 'next'

import { SeedDetailPage } from '@/components/dashboard/pages/seed-detail-page'

export const metadata: Metadata = {
  title: 'Seed Detail'
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  return <SeedDetailPage id={id} />
}
