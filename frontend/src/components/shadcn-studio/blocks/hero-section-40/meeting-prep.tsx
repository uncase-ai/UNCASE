'use client'

import { CheckIcon, FileIcon, MessageSquareTextIcon, PresentationIcon, SearchIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { Badge } from '@/components/ui/badge'

import ArrowBottom from '@/components/shadcn-studio/blocks/hero-section-40/arrow-bottom'
import WorkflowItem from '@/components/shadcn-studio/blocks/hero-section-40/workflow-item'

const MeetingPrep = () => {
  return (
    <div className='flex max-md:flex-col max-md:space-y-8 md:items-center md:space-x-16'>
      <WorkflowItem
        type='input'
        icon={<PresentationIcon />}
        title='Upcoming Meeting'
        description='Four hours before a scheduled event, the agent triggers prep mode.'
        time='1:32 AM'
        hasMenu={false}
        className='relative md:hidden'
      >
        {/* Arrow for small screens */}
        <ArrowBottom delay={0.1} />
      </WorkflowItem>

      <WorkflowItem
        type='action'
        icon={<SearchIcon />}
        title='Context Gathering'
        time='4 sec'
        delay={1.2}
        className='relative'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Fetching detail...
          </Badge>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-48.png'
              alt='Gmail logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Collect recent emails</span>
          </div>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-43.png'
              alt='Slack logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Check participant messages</span>
          </div>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-42.png'
              alt='Zoom logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Past meeting notes</span>
          </div>
        </div>

        {/* Arrow left for large screens */}
        <motion.svg
          width='243'
          height='78'
          viewBox='0 0 243 78'
          fill='none'
          xmlns='http://www.w3.org/2000/svg'
          className='absolute bottom-19.5 left-full -translate-x-1.5 max-md:hidden'
        >
          <motion.path
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 1.3
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
              delay: 1.6
            }}
            d='M6 6H215.402C226.447 6 235.402 14.9543 235.402 26V75.8754'
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
            d='M241.77 69.6841L235.411 76.0668L229.054 69.6844'
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

      <div className='flex flex-col gap-8 max-md:hidden md:gap-40.5'>
        <WorkflowItem
          type='input'
          icon={<PresentationIcon />}
          title='Upcoming Meeting'
          description='Four hours before a scheduled event, the agent triggers prep mode.'
          time='1:32 AM'
          hasMenu={false}
          className='relative'
        >
          {/* Arrow left for large screens */}
          <motion.svg
            width='236'
            height='109'
            viewBox='0 0 236 109'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
            className='absolute top-full right-1/2 translate-x-1.5 -translate-y-1.5 max-md:hidden'
          >
            <motion.path
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{
                duration: 0.5,
                ease: 'easeInOut',
                delay: 0.1
              }}
              d='M229.891 0L235.891 6L229.891 12L223.891 6L229.891 0Z'
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
              d='M229.823 6V81.1435C229.823 92.1892 220.869 101.144 209.823 101.144H1.00074'
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
              d='M7.38281 94.7856L1.00019 101.144L7.38252 107.501'
              stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'
              className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
            />
          </motion.svg>

          {/* Arrow right for large screens */}
          <motion.svg
            width='235'
            height='109'
            viewBox='0 0 235 109'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
            className='absolute top-full left-1/2 -translate-x-1.5 -translate-y-1.5 max-md:hidden'
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
              d='M6.00195 6V81.1435C6.00195 92.1892 14.9563 101.144 26.002 101.144H233.945'
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
              d='M227.562 94.7856L233.945 101.144L227.563 107.501'
              stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'
              className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
            />
          </motion.svg>
        </WorkflowItem>

        <WorkflowItem
          type='output'
          icon={<MessageSquareTextIcon />}
          title='Meeting Brief Document'
          description='A polished meeting brief sended to the organizer.'
          time='0.8 sec'
          delay={2.4}
          className='relative z-2'
        >
          <div className='bg-muted rounded-lg px-2.5 py-3'>
            <div className='flex items-center gap-2'>
              <img
                src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-50.png'
                alt='Calendar logo'
                className='size-4.5'
              />
              <span className='text-muted-foreground text-sm'>Attached to the calendar</span>
            </div>
          </div>
        </WorkflowItem>
      </div>

      {/* Brief Generation for large screens */}
      <WorkflowItem
        type='action'
        icon={<FileIcon />}
        title='Brief Generation'
        time='1.3 sec'
        delay={1.2}
        className='relative max-md:hidden md:mr-0!'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Generating
          </Badge>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Summaries key points</span>
          </div>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Open tasks</span>
          </div>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Recommended discussion topics</span>
          </div>
        </div>

        {/* Arrow right for large screens */}
        <motion.svg
          width='245'
          height='78'
          viewBox='0 0 245 78'
          fill='none'
          xmlns='http://www.w3.org/2000/svg'
          className='absolute right-full bottom-19.5 w-60.5 translate-x-1.5 max-md:hidden'
        >
          <motion.path
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 1.3
            }}
            d='M238.457 0L244.457 6L238.457 12L232.457 6L238.457 0Z'
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
            d='M238.457 6H27.3579C16.3122 6 7.35792 14.9543 7.35792 26V75.8754'
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
            d='M13.7158 69.6841L7.35765 76.0668L1 69.6844'
            stroke='color-mix(in oklab,var(--foreground)15%,var(--background))'
            strokeWidth='2'
            strokeLinecap='round'
            strokeLinejoin='round'
            className='dark:stroke-[color-mix(in_oklab,var(--foreground)25%,var(--background))]'
          />
        </motion.svg>
      </WorkflowItem>

      {/* Brief Generation for small screens */}
      <WorkflowItem
        type='action'
        icon={<FileIcon />}
        title='Brief Generation'
        time='1.3 sec'
        delay={2.4}
        className='relative md:hidden'
      >
        <div className='bg-muted space-y-2.5 rounded-lg px-2.5 py-3'>
          <Badge variant='outline' className='rounded-sm px-1.5'>
            Generating
          </Badge>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Summaries key points</span>
          </div>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Open tasks</span>
          </div>
          <div className='text-muted-foreground flex items-center gap-2'>
            <CheckIcon className='size-4' />
            <span className='text-sm'>Recommended discussion topics</span>
          </div>
        </div>

        {/* Arrow for small screens */}
        <ArrowBottom delay={2.5} />
      </WorkflowItem>

      <WorkflowItem
        type='output'
        icon={<MessageSquareTextIcon />}
        title='Meeting Brief Document'
        description='A polished meeting brief sended to the organizer.'
        time='0.8 sec'
        delay={3.7}
        className='md:hidden'
      >
        <div className='bg-muted rounded-lg px-2.5 py-3'>
          <div className='flex items-center gap-2'>
            <img
              src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-50.png'
              alt='Calendar logo'
              className='size-4.5'
            />
            <span className='text-muted-foreground text-sm'>Attached to the calendar</span>
          </div>
        </div>
      </WorkflowItem>
    </div>
  )
}

export default MeetingPrep
