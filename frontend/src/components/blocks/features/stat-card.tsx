import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

type Props = {
  className?: string
  avatarIcon: React.ReactNode
  title: string
  statNumber: string
  percentage: number
}

const StatCard = ({ className, avatarIcon, title, statNumber, percentage }: Props) => {
  return (
    <div className={cn('flex w-71.5 flex-col gap-4 rounded-xl border p-4 shadow-sm', className)}>
      <div className='flex items-center justify-between'>
        <div className='flex items-center gap-2'>
          <Avatar className='size-8 rounded-sm'>
            <AvatarFallback className='bg-primary/10 text-primary shrink-0 rounded-sm'>{avatarIcon}</AvatarFallback>
          </Avatar>
          <span>{title}</span>
        </div>
        <Button variant='outline' className='h-7 px-2 py-1 text-xs'>
          Details
        </Button>
      </div>
      <div className='flex items-center gap-2'>
        <span className='text-2xl font-semibold'>{statNumber}</span>
        <Badge className='bg-primary/10 [a&]:hover:bg-primary/5 focus-visible:ring-primary/20 dark:focus-visible:ring-primary/40 text-primary rounded-sm focus-visible:outline-none'>
          {percentage > 0 && '+'}
          {percentage}%
        </Badge>
      </div>
    </div>
  )
}

export default StatCard
