import type { ImgHTMLAttributes } from 'react'

import { cn } from '@/lib/utils'

const FlowLogo = ({ className, ...props }: Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt'>) => {
  return (
    <img
      src='/images/logo/favicon.png'
      alt='UNCASE'
      className={cn('dark:invert', className)}
      {...props}
    />
  )
}

export default FlowLogo
