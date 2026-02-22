import FlowLogo from '@/assets/svg/flow-logo'

import { cn } from '@/lib/utils'

const Logo = ({ className }: { className?: string }) => {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <FlowLogo className='size-8' />
      <span className='text-xl font-semibold'>Flow</span>
    </div>
  )
}

export default Logo
