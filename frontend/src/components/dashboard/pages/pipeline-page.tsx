'use client'

import Link from 'next/link'
import {
  ArrowDownToLine,
  ArrowRight,
  CheckCircle2,
  Circle,
  FlaskConical,
  PackageOpen,
  Rocket,
  Sprout
} from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

import { PageHeader } from '../page-header'

const STAGES = [
  {
    id: 'seed',
    label: 'Seed Engineering',
    description: 'Create or manage seed schemas that define conversation structure, domain, roles, and quality constraints.',
    icon: Sprout,
    href: '/dashboard/pipeline/seeds',
    color: 'text-emerald-500 border-emerald-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-950/30',
    details: [
      'Define domain (automotive, medical, legal...)',
      'Set roles and turn structure',
      'Configure factual parameters',
      'Set quality thresholds'
    ]
  },
  {
    id: 'import',
    label: 'Data Import',
    description: 'Upload raw conversational data in CSV or JSONL format. Auto-detect format, validate, and parse into conversations.',
    icon: ArrowDownToLine,
    href: '/dashboard/pipeline/import',
    color: 'text-blue-500 border-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
    details: [
      'Drag-and-drop CSV/JSONL files',
      'Auto-detect format',
      'PII removal at ingestion',
      'Validation and error reporting'
    ]
  },
  {
    id: 'evaluate',
    label: 'Quality Evaluation',
    description: 'Run quality metrics on conversations: ROUGE-L, fidelity, lexical diversity, dialogue coherence, and privacy gate.',
    icon: FlaskConical,
    href: '/dashboard/pipeline/evaluate',
    color: 'text-amber-500 border-amber-500',
    bgColor: 'bg-amber-50 dark:bg-amber-950/30',
    details: [
      'ROUGE-L >= 0.65',
      'Factual Fidelity >= 0.90',
      'Lexical Diversity (TTR) >= 0.55',
      'Dialogue Coherence >= 0.85',
      'Privacy Score = 0.00 (mandatory)'
    ]
  },
  {
    id: 'generate',
    label: 'Synthetic Generation',
    description: 'Generate new synthetic conversations from validated seeds using LLM providers via LiteLLM.',
    icon: Rocket,
    href: '/dashboard/pipeline/generate',
    color: 'text-violet-500 border-violet-500',
    bgColor: 'bg-violet-50 dark:bg-violet-950/30',
    details: [
      'Multi-provider LLM support (Claude, Gemini, Qwen, LLaMA)',
      'Domain-aware generation',
      'Tool call simulation',
      'Re-evaluation after generation'
    ]
  },
  {
    id: 'export',
    label: 'Dataset Export',
    description: 'Bundle certified conversations into training-ready datasets. Apply templates, version, and download.',
    icon: PackageOpen,
    href: '/dashboard/pipeline/export',
    color: 'text-rose-500 border-rose-500',
    bgColor: 'bg-rose-50 dark:bg-rose-950/30',
    details: [
      'Apply chat template formatting',
      'Export as JSONL for fine-tuning',
      'Dataset versioning',
      'Quality certificate per export'
    ]
  }
]

export function PipelinePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Pipeline"
        description="End-to-end workflow for producing certified synthetic training data"
      />

      {/* Visual pipeline flow */}
      <div className="space-y-4">
        {STAGES.map((stage, i) => (
          <div key={stage.id} className="relative">
            {/* Connector line */}
            {i > 0 && (
              <div className="absolute -top-4 left-6 h-4 w-px bg-border" />
            )}

            <Card className={cn('transition-colors hover:shadow-sm', stage.bgColor)}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn('flex size-12 items-center justify-center rounded-full border-2', stage.color)}>
                      <stage.icon className="size-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[10px]">
                          Stage {i + 1}
                        </Badge>
                        <CardTitle className="text-base">{stage.label}</CardTitle>
                      </div>
                      <CardDescription className="mt-0.5">{stage.description}</CardDescription>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <Link href={stage.href}>
                      Open <ArrowRight className="ml-1 size-3" />
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="grid gap-1 sm:grid-cols-2 lg:grid-cols-3">
                  {stage.details.map(detail => (
                    <li key={detail} className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Circle className="size-1.5 shrink-0 fill-current" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>

      {/* Flywheel note */}
      <Card className="border-dashed">
        <CardContent className="flex items-center gap-3 py-4">
          <CheckCircle2 className="size-5 shrink-0 text-emerald-500" />
          <div>
            <p className="text-sm font-medium">Flywheel Loop</p>
            <p className="text-xs text-muted-foreground">
              After export, deploy your LoRA adapter to production. Collect feedback and feed it back as new seeds — closing the loop for continuous improvement.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
