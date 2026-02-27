'use client'

import { useState } from 'react'

import { useRouter } from 'next/navigation'
import { AlertTriangle, Cloud, FlaskConical, Loader2, PlayIcon } from 'lucide-react'

import { activateDemo } from '@/lib/demo'
import { useSandboxDemo } from '@/hooks/use-sandbox-demo'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { SecondaryFlowButton } from '@/components/ui/flow-button'

const DOMAINS = [
  { value: 'automotive.sales', label: 'Automotive Sales' },
  { value: 'medical.consultation', label: 'Medical Consultation' },
  { value: 'legal.advisory', label: 'Legal Advisory' },
  { value: 'finance.advisory', label: 'Financial Advisory' },
  { value: 'industrial.support', label: 'Industrial Support' },
  { value: 'education.tutoring', label: 'Education Tutoring' }
] as const

export default function DemoQuickButton() {
  const router = useRouter()
  const sandbox = useSandboxDemo()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [domain, setDomain] = useState('automotive.sales')

  const handleLaunchSandbox = async () => {
    const result = await sandbox.start(domain)

    if (result) {
      setDialogOpen(false)
      router.push('/dashboard')
    }
  }

  const handleFallbackLocal = async () => {
    setDialogOpen(false)
    await activateDemo()
    router.push('/dashboard')
  }

  return (
    <>
      <SecondaryFlowButton className="w-full *:w-full" onClick={() => setDialogOpen(true)}>
        <PlayIcon className="size-4" />
        Instant Demo
      </SecondaryFlowButton>

      <Dialog open={dialogOpen} onOpenChange={(open) => !sandbox.booting && setDialogOpen(open)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Launch Instant Demo</DialogTitle>
            <DialogDescription>
              Spin up a live sandbox with pre-loaded seeds and a real API — no installation needed.
            </DialogDescription>
          </DialogHeader>

          {!sandbox.booting && !sandbox.error && (
            <div className="space-y-4 pt-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Industry Domain</label>
                <Select value={domain} onValueChange={setDomain}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {DOMAINS.map((d) => (
                      <SelectItem key={d.value} value={d.value}>
                        {d.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  3 demo seeds will be pre-loaded for this domain.
                </p>
              </div>

              <div className="flex gap-2">
                <Button className="flex-1" onClick={handleLaunchSandbox}>
                  <Cloud className="mr-1.5 size-4" />
                  Launch Live Sandbox
                </Button>
                <Button variant="outline" onClick={handleFallbackLocal}>
                  <FlaskConical className="mr-1.5 size-4" />
                  Local Demo
                </Button>
              </div>

              <p className="text-center text-[11px] text-muted-foreground">
                Live sandbox runs for 30 minutes, then auto-destroys.
              </p>
            </div>
          )}

          {sandbox.booting && (
            <div className="space-y-4 py-6">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="size-8 animate-spin text-muted-foreground" />
                <p className="text-sm font-medium">Provisioning sandbox...</p>
                <p className="text-xs text-muted-foreground">
                  Installing dependencies and starting the API. This may take up to 90 seconds.
                </p>
              </div>
              <Progress value={undefined} className="animate-pulse" />
            </div>
          )}

          {sandbox.error && (
            <div className="space-y-4 pt-2">
              <div className="flex items-start gap-3 rounded-md border border-destructive/20 bg-destructive/5 p-3">
                <AlertTriangle className="mt-0.5 size-4 shrink-0 text-destructive" />
                <div className="space-y-1">
                  <p className="text-sm font-medium">Sandbox failed to start</p>
                  <p className="text-xs text-muted-foreground">{sandbox.error}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" onClick={handleLaunchSandbox}>
                  Retry
                </Button>
                <Button className="flex-1" onClick={handleFallbackLocal}>
                  <FlaskConical className="mr-1.5 size-4" />
                  Use Local Demo Instead
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
