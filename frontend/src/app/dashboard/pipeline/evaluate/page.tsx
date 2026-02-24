import type { Metadata } from 'next'

import { EvaluatePage } from '@/components/dashboard/pages/evaluate-page'

export const metadata: Metadata = {
  title: 'Evaluate',
}

export default function Page() {
  return <EvaluatePage />
}
