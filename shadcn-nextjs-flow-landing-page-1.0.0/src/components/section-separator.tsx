// Component Imports
import { Separator } from '@/components/ui/separator'

// Util Imports
import { cn } from '@/lib/utils'

type SectionSeparatorProps = {
  className?: string
}

const SectionSeparator = ({ className }: SectionSeparatorProps) => {
  return (
    <div className={cn('relative w-full', className)}>
      <Separator />
      <svg
        width='15'
        height='20'
        viewBox='0 0 15 20'
        fill='none'
        xmlns='http://www.w3.org/2000/svg'
        className='absolute top-1/2 -right-0.5 -translate-y-1/2'
      >
        <path d='M13.1589 20V0M0 10.0215H14' stroke='var(--primary)' strokeWidth='2' />
      </svg>

      <svg
        width='15'
        height='20'
        viewBox='0 0 15 20'
        fill='none'
        xmlns='http://www.w3.org/2000/svg'
        className='absolute top-1/2 -left-0.5 -translate-y-1/2 rotate-y-180'
      >
        <path d='M13.1589 20V0M0 10.0215H14' stroke='var(--primary)' strokeWidth='2' />
      </svg>
    </div>
  )
}

export default SectionSeparator
