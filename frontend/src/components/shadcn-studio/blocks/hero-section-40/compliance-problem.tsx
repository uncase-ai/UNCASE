'use client'

import { AlertTriangleIcon, ScaleIcon, SearchIcon, ShieldAlertIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import ArrowRight from '@/components/shadcn-studio/blocks/hero-section-40/arrow-right'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const ComplianceProblem = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-center md:space-x-16'>
      <WorkflowItem
        type='input'
        icon={<ScaleIcon />}
        title='Compliance Mandate'
        description='Regulated industries need specialized AI agents — but training on real data exposes PII and violates GDPR, HIPAA, and sector-specific regulations.'
        time='Critical'
        hasMenu={false}
        className='relative'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Data exposure risks
          </Badge>
          <div className='flex items-center gap-2'>
            <ShieldAlertIcon className='text-destructive size-4.5' />
            <span className='text-muted-foreground text-sm'>Patient records in training data</span>
          </div>
          <div className='flex items-center gap-2'>
            <ShieldAlertIcon className='text-destructive size-4.5' />
            <span className='text-muted-foreground text-sm'>Financial advisor transcripts leaked</span>
          </div>
          <div className='flex items-center gap-2'>
            <ShieldAlertIcon className='text-destructive size-4.5' />
            <span className='text-muted-foreground text-sm'>Legal consultations memorized by model</span>
          </div>
        </div>

        <ArrowRight delay={0.1} />
        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<SearchIcon />}
        title='Risk Assessment'
        time='Ongoing'
        delay={1.2}
        className='relative'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <div className='flex items-center gap-2'>
            <AlertTriangleIcon className='size-4.5 text-amber-500' />
            <span className='text-muted-foreground text-sm'>Generic models lack domain expertise</span>
          </div>
          <div className='flex items-center gap-2'>
            <AlertTriangleIcon className='size-4.5 text-amber-500' />
            <span className='text-muted-foreground text-sm'>Real data training = regulatory violations</span>
          </div>
          <div className='flex items-center gap-2'>
            <AlertTriangleIcon className='size-4.5 text-amber-500' />
            <span className='text-muted-foreground text-sm'>No audit trail from data to model</span>
          </div>
        </div>

        <ArrowRight delay={1.3} />
        <ArrowBottom delay={1.3} />
      </WorkflowItem>

      <WorkflowItem
        type='pending'
        icon={<ShieldAlertIcon />}
        title='Gap Identified'
        description='The industry needs a framework that captures expert knowledge without touching real data — generating privacy-safe synthetic conversations for domain-specific fine-tuning.'
        time='Now'
        hasMenu={false}
        delay={2.4}
        className='md:w-72.5'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='border-primary text-primary rounded-sm px-1.5'>
            UNCASE solves this
          </Badge>
          <p className='text-muted-foreground text-sm'>
            Zero PII. Full traceability. Domain expertise preserved. Open source.
          </p>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default ComplianceProblem
