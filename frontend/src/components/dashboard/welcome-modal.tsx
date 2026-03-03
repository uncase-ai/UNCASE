'use client'

import { useState } from 'react'

import { BookOpen, BrainCircuit, Check, MessageSquare, Search, Shield, Sparkles, Zap } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const STORAGE_KEY = 'uncase-welcome-dismissed'

const offlineFeatures = [
  { icon: BookOpen, label: 'Seed Library', desc: 'Browse, create, and edit conversation seeds' },
  { icon: Zap, label: 'Demo Generation', desc: 'Generate sample conversations from any seed' },
  { icon: Check, label: 'Quality Reports', desc: 'View evaluation scores and metrics' },
  { icon: MessageSquare, label: 'Conversations', desc: 'Browse and inspect generated dialogues' },
  { icon: Shield, label: 'Blockchain Anchoring', desc: 'View integrity verification status' },
]

const apiFeatures = [
  { icon: Sparkles, label: 'AI Interview', desc: 'Guided seed extraction through conversation' },
  { icon: BrainCircuit, label: 'Mass Generation', desc: 'Bulk synthetic conversation creation via pipeline' },
  { icon: Search, label: 'LLM-as-Judge', desc: 'Semantic fidelity and quality scoring' },
  { icon: BookOpen, label: 'Knowledge Extraction', desc: 'Process domain documents for seed enrichment' },
]

function shouldShowWelcome(): boolean {
  if (typeof window === 'undefined') return false

  return !localStorage.getItem(STORAGE_KEY)
}

export function WelcomeModal() {
  const [open, setOpen] = useState(shouldShowWelcome)
  const [dontShow, setDontShow] = useState(false)

  function handleDismiss() {
    if (dontShow) {
      localStorage.setItem(STORAGE_KEY, 'true')
    }

    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="size-5 text-primary" />
            Welcome to UNCASE
          </DialogTitle>
          <DialogDescription>
            Synthetic conversation framework for regulated industries. Here is what you can do right away.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Offline features */}
          <div>
            <div className="mb-2 flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">Works out of the box</Badge>
              <span className="text-[10px] text-muted-foreground">No API needed</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {offlineFeatures.map(f => (
                <div key={f.label} className="flex items-start gap-2.5 rounded-md border p-2.5">
                  <f.icon className="mt-0.5 size-4 shrink-0 text-primary" />
                  <div>
                    <p className="text-xs font-medium">{f.label}</p>
                    <p className="text-[11px] text-muted-foreground">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API features */}
          <div>
            <div className="mb-2 flex items-center gap-2">
              <Badge variant="outline" className="text-xs">Requires LLM API</Badge>
              <span className="text-[10px] text-muted-foreground">Connect your provider to unlock</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {apiFeatures.map(f => (
                <div key={f.label} className="flex items-start gap-2.5 rounded-md border border-dashed p-2.5 opacity-80">
                  <f.icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                  <div>
                    <p className="text-xs font-medium">{f.label}</p>
                    <p className="text-[11px] text-muted-foreground">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Getting started */}
          <div className="rounded-md bg-muted/50 p-3">
            <p className="mb-2 text-xs font-semibold">Getting started</p>
            <ol className="space-y-1.5 text-[11px] text-muted-foreground">
              <li>1. Explore the <strong className="text-foreground">Seed Library</strong> to see pre-loaded conversation templates</li>
              <li>2. Click <strong className="text-foreground">Generate</strong> on any seed to create demo conversations instantly</li>
              <li>3. Check the <strong className="text-foreground">Pipeline</strong> to see the full SCSF workflow</li>
            </ol>
          </div>
        </div>

        <DialogFooter className="flex-row items-center justify-between sm:justify-between">
          <label className="flex items-center gap-2 text-xs text-muted-foreground">
            <Checkbox checked={dontShow} onCheckedChange={v => setDontShow(v === true)} />
            Don&apos;t show again
          </label>
          <Button size="sm" onClick={handleDismiss}>
            Get Started
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
