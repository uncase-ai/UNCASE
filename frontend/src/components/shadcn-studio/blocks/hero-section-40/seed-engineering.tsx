'use client'

import { BrainCircuitIcon, CheckIcon, ShieldCheckIcon, SproutIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const SeedEngineering = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-start'>
      <WorkflowItem
        type='input'
        icon={<BrainCircuitIcon />}
        title='Expert Knowledge'
        description='Domain experts define conversation patterns, roles, tools, and objectives that capture years of institutional knowledge.'
        time='Layer 0'
        hasMenu={false}
        className='relative md:mr-22'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            SeedSchema v1
          </Badge>
          <div className='flex items-center gap-2'>
            <CheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>domain: automotive.sales</span>
          </div>
          <div className='flex items-center gap-2'>
            <CheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>roles: asesor, cliente</span>
          </div>
          <div className='flex items-center gap-2'>
            <CheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>tools: cotizador, simulador_credito</span>
          </div>
        </div>

        {/* Arrow for large screens */}
        <motion.svg
          width='121'
          height='87'
          viewBox='0 0 121 87'
          fill='none'
          xmlns='http://www.w3.org/2000/svg'
          className='absolute right-1.5 bottom-5.5 translate-x-full max-md:hidden'
        >
          <motion.path
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 0.1 }}
            d='M6 0L12 6L6 12L0 6L6 0Z'
            fill='color-mix(in oklab,var(--foreground)15%,var(--background))'
            className='dark:fill-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 0.4 }}
            d='M6 6H93.2683C104.314 6 113.268 14.9543 113.268 26V85.671'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: { duration: 0.35, ease: 'easeInOut', delay: 0.9 },
              opacity: { duration: 0.1, delay: 0.9 }
            }}
            d='M106.91 79.2884L113.268 85.671L119.626 79.2887'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            strokeLinecap='round'
            strokeLinejoin='round'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
        </motion.svg>

        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<ShieldCheckIcon />}
        title='PII Elimination'
        time='< 1 sec'
        delay={1.2}
        className='relative md:mt-68 md:mr-15'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Presidio + SpaCy
          </Badge>
          <div className='flex items-center gap-2'>
            <ShieldCheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>Names → anonymized</span>
          </div>
          <div className='flex items-center gap-2'>
            <ShieldCheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>Phone numbers → removed</span>
          </div>
          <div className='flex items-center gap-2'>
            <ShieldCheckIcon className='size-4.5 text-green-500' />
            <span className='text-muted-foreground text-sm'>Addresses → stripped</span>
          </div>
        </div>

        {/* Arrow for large screens */}
        <motion.svg
          width='151'
          height='121'
          viewBox='0 0 151 121'
          fill='none'
          xmlns='http://www.w3.org/2000/svg'
          className='absolute top-9 right-0 translate-x-15 -translate-y-full max-md:hidden'
        >
          <motion.path
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 1.3 }}
            d='M6 108.626L12 114.626L6 120.626L0 114.626L6 108.626Z'
            fill='color-mix(in oklab,var(--foreground)15%,var(--background))'
            className='dark:fill-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 1.6 }}
            d='M6 114.626V27.3579C6 16.3122 14.9543 7.35791 26 7.35791H149.146'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: { duration: 0.35, ease: 'easeInOut', delay: 2.1 },
              opacity: { duration: 0.1, delay: 2.1 }
            }}
            d='M142.763 1L149.145 7.35817L142.763 13.7158'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            strokeLinecap='round'
            strokeLinejoin='round'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
        </motion.svg>

        <ArrowBottom delay={1.3} />
      </WorkflowItem>

      <WorkflowItem
        type='output'
        icon={<SproutIcon />}
        title='Clean Seed Ready'
        description='Structured seed with full domain knowledge, zero PII — ready for synthetic generation.'
        time='< 2 sec'
        hasMenu={false}
        delay={2.4}
        className='md:mt-17'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Privacy score: 0.00
          </Badge>
          <p className='text-muted-foreground text-sm'>
            seed_id traceable, domain expertise preserved, all PII eliminated.
          </p>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default SeedEngineering
