import type { Metadata } from 'next'

import { SandboxBootstrap } from './sandbox-bootstrap'

export const metadata: Metadata = {
  title: 'Connecting to Sandbox...'
}

export default function SandboxPage() {
  return <SandboxBootstrap />
}
