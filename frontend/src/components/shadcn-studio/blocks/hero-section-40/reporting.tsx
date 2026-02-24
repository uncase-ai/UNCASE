'use client'

import { BellRingIcon, FileChartPieIcon, LoaderIcon, MessageSquareTextIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import ArrowRight from '@/components/shadcn-studio/blocks/hero-section-40/arrow-right'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const Reporting = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-center md:space-x-16'>
      <WorkflowItem
        type='input'
        icon={<BellRingIcon />}
        title='Scheduled Trigger'
        description='The agent activates the report workflow.'
        time='0.0 sec'
        className='relative'
      >
        {/* Arrow for large screens */}
        <ArrowRight delay={0.1} />

        {/* Arrow for small screens */}
        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<FileChartPieIcon />}
        title='Data Aggregation'
        time='18 sec'
        delay={1.2}
        className='relative'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-44.png'
              alt='Sheets logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Collecting metrics</span>
          </div>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-40.png'
              alt='Jira logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Analyzing data</span>
          </div>
        </div>
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <div className='text-muted-foreground flex items-center justify-between gap-2'>
            <Badge variant='outline' className='rounded-sm px-1.5'>
              Insight generation...
            </Badge>
            <LoaderIcon className='size-4' />
          </div>
          <p className='text-muted-foreground text-sm'>
            Summaries changes, trends, and anomalies using AI-generated analysis.
          </p>
        </div>

        {/* Arrow for large screens */}
        <ArrowRight delay={1.3} />

        {/* Arrow for small screens */}
        <ArrowBottom delay={1.3} />
      </WorkflowItem>

      <WorkflowItem
        type='output'
        icon={<MessageSquareTextIcon />}
        title='Report Formatted'
        description='Automated weekly or monthly performance reports.'
        time='1.1 sec'
        delay={2.4}
        className='md:w-72.5'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-48.png'
              alt='Gmail logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Report posted</span>
          </div>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-43.png'
              alt='Slack logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Report posted</span>
          </div>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default Reporting
