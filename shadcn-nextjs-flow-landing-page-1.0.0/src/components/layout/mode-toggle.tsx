'use client'

import { MoonStarIcon, SunIcon } from 'lucide-react'
import { useTheme } from 'next-themes'

import { SecondaryFlowButton } from '@/components/ui/flow-button'

const ModeToggle = () => {
  const { resolvedTheme, setTheme } = useTheme()

  return (
    <SecondaryFlowButton
      size='icon-lg'
      className='relative'
      onClick={() => setTheme(resolvedTheme === 'light' ? 'dark' : 'light')}
    >
      <MoonStarIcon className='scale-100 dark:scale-0' />
      <SunIcon className='absolute scale-0 dark:scale-100' />
      <span className='sr-only'>Toggle theme</span>
    </SecondaryFlowButton>
  )
}

export { ModeToggle }
