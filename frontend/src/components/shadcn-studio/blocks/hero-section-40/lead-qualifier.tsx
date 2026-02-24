'use client'

import { ArrowDownUpIcon, FileInputIcon, MessageSquareTextIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const LeadQualifier = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-start'>
      <WorkflowItem
        type='input'
        icon={<FileInputIcon />}
        title='New Lead Inquiry'
        description='Automatically qualify new inbound leads from email or forms.'
        time='0.0 sec'
        className='relative md:mr-22'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Fetching detail...
          </Badge>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-44.png'
              alt='Sheets logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Company details</span>
          </div>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-47.png'
              alt='LinkedIn logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>LinkedIn profiles</span>
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
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 0.1
            }}
            d='M6 0L12 6L6 12L0 6L6 0Z'
            fill='color-mix(in oklab,var(--foreground)15%,var(--background))'
            className='dark:fill-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 0.4
            }}
            d='M6 6H93.2683C104.314 6 113.268 14.9543 113.268 26V85.671'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: {
                duration: 0.35,
                ease: 'easeInOut',
                delay: 0.9
              },
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

        {/* Arrow for small screens */}
        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<ArrowDownUpIcon />}
        title='Scoring & Categorization'
        time='1.8 sec'
        delay={1.2}
        className='relative md:mt-68 md:mr-15'
      >
        <div className='bg-muted rounded-lg px-2.5 py-3'>
          <p className='text-muted-foreground text-sm'>
            Using AI logic, the lead is scored based on size, industry, and engagement.
          </p>
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
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 1.3
            }}
            d='M6 108.626L12 114.626L6 120.626L0 114.626L6 108.626Z'
            fill='color-mix(in oklab,var(--foreground)15%,var(--background))'
            className='dark:fill-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 1.6
            }}
            d='M6 114.626V27.3579C6 16.3122 14.9543 7.35791 26 7.35791H149.146'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
          <motion.path
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: {
                duration: 0.35,
                ease: 'easeInOut',
                delay: 2.1
              },
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

        {/* Arrow for small screens */}
        <ArrowBottom delay={1.3} />
      </WorkflowItem>

      <WorkflowItem
        type='output'
        icon={<MessageSquareTextIcon />}
        title='Response'
        description='The agent have prepared a tailored response.'
        time='0.0 sec'
        delay={2.4}
        className='md:mt-17'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Answer
          </Badge>
          <p className='text-muted-foreground text-sm'>
            Lead status, notes, and follow-up are logged in the CRM, ready for the sales team.
          </p>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-45.png'
              alt='Notion logo'
              className='size-4.5 dark:invert'
            />
            <span className='text-muted-foreground text-sm'>File updated</span>
          </div>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default LeadQualifier
