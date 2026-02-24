import { FileQuestion } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/dashboard/empty-state'

export default function DashboardNotFound() {
  return (
    <EmptyState
      icon={FileQuestion}
      title="Page not found"
      description="The page you're looking for doesn't exist or has been moved."
      action={
        <Button asChild variant="outline">
          <Link href="/dashboard">Back to Dashboard</Link>
        </Button>
      }
    />
  )
}
