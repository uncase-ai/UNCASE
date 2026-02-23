import type { Metadata } from 'next'

import DocsPage from '@/components/docs/docs-page'

export const metadata: Metadata = {
  title: 'Documentation',
  description:
    'UNCASE documentation — installation, architecture, API reference, CLI, privacy, deployment, and more.',
  alternates: {
    canonical: '/docs',
  },
}

export default function Page() {
  return <DocsPage />
}
