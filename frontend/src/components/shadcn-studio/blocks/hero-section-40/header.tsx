'use client'

import { useEffect, useState } from 'react'

import { SecondaryOrionButton } from '@/components/ui/orion-button'

import {
  HeroNavigation,
  HeroNavigationSmallScreen,
  type Navigation
} from '@/components/shadcn-studio/blocks/hero-section-40/hero-navigation'

import { cn } from '@/lib/utils'

import OrionLogo from '@/assets/svg/orion-logo'

type HeaderProps = {
  navigationData: Navigation[]
  className?: string
}

const Header = ({ navigationData, className }: HeaderProps) => {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0)
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll()

    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  return (
    <header
      className={cn(
        'sticky top-0 z-50 h-16 w-full border-b px-4 transition-all duration-300 sm:px-6 lg:px-8',
        {
          'bg-card/75 shadow-md backdrop-blur': isScrolled
        },
        className
      )}
    >
      <div className='mx-auto flex h-full max-w-7xl items-center justify-between gap-4 border-x px-4 sm:px-6 lg:px-8'>
        {/* Logo */}
        <a href='#'>
          <div className='flex items-center gap-3'>
            <OrionLogo className='size-8' />
            <span className='text-xl font-semibold'>Orion</span>
          </div>
        </a>

        {/* Navigation */}
        <HeroNavigation navigationData={navigationData} />

        {/* Actions */}
        <div className='flex gap-3'>
          <SecondaryOrionButton size='lg' asChild>
            <a href='#'>Sign up</a>
          </SecondaryOrionButton>

          <HeroNavigationSmallScreen navigationData={navigationData} />
        </div>
      </div>
    </header>
  )
}

export default Header
