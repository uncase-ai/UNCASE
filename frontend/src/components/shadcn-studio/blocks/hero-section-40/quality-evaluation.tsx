'use client'

import { CheckCircle2Icon, FileSearchIcon, GaugeIcon, ShieldCheckIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import ArrowRight from '@/components/shadcn-studio/blocks/hero-section-40/arrow-right'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const QualityEvaluation = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-center md:space-x-16'>
      <WorkflowItem
        type='input'
        icon={<FileSearchIcon />}
        title='Raw Synthetic Data'
        description='Generated conversations enter the 6-gate quality evaluation pipeline.'
        time='Layer 2'
        hasMenu={false}
        className='relative'
      >
        <ArrowRight delay={0.1} />
        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<GaugeIcon />}
        title='6-Gate Evaluation'
        time='~5 sec'
        delay={1.2}
        className='relative'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Hard-gated metrics
          </Badge>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>ROUGE-L</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              &ge; 0.65
            </Badge>
          </div>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>Factual Fidelity</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              &ge; 0.90
            </Badge>
          </div>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>Lexical Diversity</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              &ge; 0.55
            </Badge>
          </div>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>Coherence</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              &ge; 0.85
            </Badge>
          </div>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>Privacy Score</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              = 0.00
            </Badge>
          </div>
          <div className='flex items-center justify-between gap-2'>
            <span className='text-muted-foreground text-sm'>Memorization</span>
            <Badge className='bg-green-600/15 text-green-600 border-green-600/20 dark:bg-green-500/15 dark:text-green-400 dark:border-green-500/20'>
              &lt; 0.01
            </Badge>
          </div>
        </div>

        <ArrowRight delay={1.3} />
        <ArrowBottom delay={1.3} />
      </WorkflowItem>

      <WorkflowItem
        type='output'
        icon={<CheckCircle2Icon />}
        title='Certified Dataset'
        description='Only conversations that pass ALL six gates proceed to LoRA training. No exceptions.'
        time='< 10 sec'
        hasMenu={false}
        delay={2.4}
        className='md:w-72.5'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Composite formula
          </Badge>
          <p className='text-muted-foreground font-mono text-xs'>
            Q = min(ROUGE, Fidelidad, TTR, Coherencia)
          </p>
          <p className='text-muted-foreground text-xs'>if privacy=0 AND memorization&lt;0.01, else Q=0</p>
          <div className='mt-1 flex items-center gap-2'>
            <ShieldCheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>Zero tolerance for PII residual</span>
          </div>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default QualityEvaluation
