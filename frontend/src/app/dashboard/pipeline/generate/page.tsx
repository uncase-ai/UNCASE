import type { Metadata } from 'next'

import { GeneratePage } from '@/components/dashboard/pages/generate-page'

export const metadata: Metadata = {
  title: 'Generate',
}

export default function Page() {
  return <GeneratePage />
}
