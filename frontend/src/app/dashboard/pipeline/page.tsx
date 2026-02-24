import type { Metadata } from 'next'

import { PipelinePage } from '@/components/dashboard/pages/pipeline-page'

export const metadata: Metadata = {
  title: 'Pipeline',
}

export default function Page() {
  return <PipelinePage />
}
