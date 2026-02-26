import { cn } from '@/lib/utils'

const Logo = ({ className }: { className?: string }) => {
  return (
    <div className={cn('flex items-center', className)}>
      <img
        src='/images/logo/logo-horizontal.png'
        alt='UNCASE'
        className='h-8 w-auto dark:invert'
      />
    </div>
  )
}

export default Logo
