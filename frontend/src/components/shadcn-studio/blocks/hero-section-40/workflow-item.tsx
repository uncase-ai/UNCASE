import type { ReactNode } from 'react'

import {
  CircleCheckIcon,
  CirclePlayIcon,
  Clock8Icon,
  EllipsisVerticalIcon,
  PencilLineIcon,
  TriangleAlertIcon
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { MotionPreset } from '@/components/ui/motion-preset'

import { cn } from '@/lib/utils'

type WorkflowItemProps = {
  type: 'input' | 'action' | 'pending' | 'output'
  icon: ReactNode
  title: string
  description?: string
  time: string
  hasMenu?: boolean
  listItems?: string[]
  className?: string
  children?: ReactNode
  delay?: number
}

const WorkflowItem = ({
  type,
  icon,
  title,
  description,
  time,
  className,
  children,
  delay = 0,
  hasMenu = true,
  listItems = ['Share', 'Update', 'Refresh']
}: WorkflowItemProps) => {
  return (
    <MotionPreset
      fade
      transition={{ duration: 0.5 }}
      delay={delay}
      inView={false}
      className={cn('relative z-1 w-full pt-7.5 max-md:max-w-xs max-md:mx-auto sm:max-md:max-w-sm md:w-82.5', className)}
    >
      <div
        className={cn('absolute top-0 left-0 -z-1 flex items-center gap-2.5 rounded-t-xl p-4 pt-1.5 capitalize', {
          'bg-[color-mix(in_oklab,var(--color-sky-600)20%,var(--background))] text-sky-600 dark:bg-[color-mix(in_oklab,var(--color-sky-400)20%,var(--background))] dark:text-sky-400':
            type === 'input',
          'bg-[color-mix(in_oklab,var(--color-amber-600)20%,var(--background))] text-amber-600 dark:bg-[color-mix(in_oklab,var(--color-amber-400)20%,var(--background))] dark:text-amber-400':
            type === 'action',
          'text-destructive bg-[color-mix(in_oklab,var(--destructive)20%,var(--background))]': type === 'pending',
          'bg-[color-mix(in_oklab,var(--color-green-600)20%,var(--background))] text-green-600 dark:bg-[color-mix(in_oklab,var(--color-green-400)20%,var(--background))] dark:text-green-400':
            type === 'output'
        })}
      >
        {type === 'input' && <PencilLineIcon className='size-4' />}
        {type === 'action' && <CirclePlayIcon className='size-4' />}
        {type === 'pending' && <TriangleAlertIcon className='size-4' />}
        {type === 'output' && <CircleCheckIcon className='size-4' />}
        <span className='text-sm font-medium'>{type}</span>
      </div>

      <div className='bg-card text-card-foreground flex flex-col gap-3.5 rounded-xl border p-4 shadow-lg'>
        <div className='flex flex-col gap-2'>
          <div className='flex w-full items-center gap-2.5'>
            <span className='[&>svg]:size-5'>{icon}</span>
            <div className='grow font-medium'>{title}</div>
            {hasMenu ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant='ghost' size='icon' className='text-muted-foreground size-6 rounded-full'>
                    <EllipsisVerticalIcon />
                    <span className='sr-only'>Menu</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align='end'>
                  <DropdownMenuGroup>
                    {listItems.map((item, index) => (
                      <DropdownMenuItem key={index}>{item}</DropdownMenuItem>
                    ))}
                  </DropdownMenuGroup>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <span className='text-muted-foreground text-xs font-light'>{time}</span>
            )}
          </div>
          {description && <p className='text-muted-foreground text-sm'>{description}</p>}
        </div>

        {children}

        {!(!hasMenu && type !== 'action' && type !== 'pending') && (
          <div className='flex items-end justify-end gap-2.5'>
            {hasMenu && (
              <Badge variant='outline' className='text-muted-foreground rounded-sm px-1.5 font-light'>
                <Clock8Icon />
                {time}
              </Badge>
            )}
            {type === 'action' && (
              <Badge
                variant='outline'
                className='border-primary text-primary bg-primary/10 h-7.5 gap-1.5 rounded-sm p-1.5 font-light'
              >
                <img
                  src='https://cdn.shadcnstudio.com/ss-assets/template/landing-page/orion/image-49.png'
                  alt='ChatGPT logo'
                  className='size-4 dark:invert'
                />
                <span className='text-sm font-light'>GPT-4-1 Mini</span>
              </Badge>
            )}
            {type === 'pending' && (
              <Button className='h-6.5 cursor-pointer rounded-lg px-2 py-1 text-xs'>Approve</Button>
            )}
          </div>
        )}
      </div>
    </MotionPreset>
  )
}

export default WorkflowItem
