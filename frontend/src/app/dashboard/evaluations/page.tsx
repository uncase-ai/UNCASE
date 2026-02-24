import type { Metadata } from 'next'

import { EvaluationsPage } from '@/components/dashboard/pages/evaluations-page'

export const metadata: Metadata = {
  title: 'Evaluations',
}

export default function Page() {
  return <EvaluationsPage />
}
