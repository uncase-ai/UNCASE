'use client'

import { useRouter } from 'next/navigation'
import { PlayIcon } from 'lucide-react'

import { activateDemo } from '@/lib/demo'
import { SecondaryFlowButton } from '@/components/ui/flow-button'

export default function DemoQuickButton() {
  const router = useRouter()

  const handleDemo = () => {
    activateDemo()
    router.push('/dashboard')
  }

  return (
    <SecondaryFlowButton className="w-full *:w-full" onClick={handleDemo}>
      <PlayIcon className="size-4" />
      Explore Demo Dashboard
    </SecondaryFlowButton>
  )
}
