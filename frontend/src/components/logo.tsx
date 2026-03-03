import { cn } from '@/lib/utils'

const Logo = ({ className }: { className?: string }) => {
  return (
    <div className={cn('flex items-center', className)}>
      <img
        src='/images/logo/logo-dark.svg'
        alt='UNCASE'
        className='h-8 w-auto dark:hidden'
      />
      <img
        src='/images/logo/logo-white.svg'
        alt='UNCASE'
        className='hidden h-8 w-auto dark:block'
      />
    </div>
  )
}

export default Logo
