'use client'

import { useEffect, useState } from 'react'

import { BookOpenIcon, ExternalLinkIcon, TerminalIcon } from 'lucide-react'

import Link from 'next/link'

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { PrimaryFlowButton, SecondaryFlowButton } from '@/components/ui/flow-button'
import { ModeToggle } from '@/components/layout/mode-toggle'

import { HeaderNavigation, HeaderNavigationSmallScreen, type Navigation } from '@/components/layout/header-navigation'

import { cn } from '@/lib/utils'

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
        'sticky top-0 z-50 h-16 w-full transition-all duration-300',
        {
          'bg-card/75 backdrop-blur-sm': isScrolled
        },
        className
      )}
    >
      <div className='flex h-full items-center justify-between gap-4 border-b px-4 sm:px-6 lg:px-8'>
        {/* Logo */}
        <Link href='/#home'>
          <img
            src='/images/logo/logo-horizontal.png'
            alt='UNCASE'
            className='-my-3 h-11 w-auto dark:invert'
          />
        </Link>

        {/* Navigation */}
        <HeaderNavigation
          navigationData={navigationData}
          navigationClassName='[&_[data-slot="navigation-menu-list"]]:gap-1'
        />

        {/* Actions */}
        <div className='flex gap-4 sm:gap-6'>
          <ModeToggle />

          <SecondaryFlowButton size='lg' className='max-lg:hidden' asChild>
            <Link href='https://github.com/uncase-ai/UNCASE/blob/main/UNCASE_PublicWhitepaper_TechnicalFoundations_v1.0.pdf' target='_blank' rel='noopener noreferrer'>
              <BookOpenIcon />
              Read Whitepapers
            </Link>
          </SecondaryFlowButton>

          <PrimaryFlowButton size='lg' className='max-lg:hidden' asChild>
            <Link href='https://github.com/uncase-ai/UNCASE'>
              <TerminalIcon />
              Instalación
            </Link>
          </PrimaryFlowButton>

          <Tooltip>
            <TooltipTrigger asChild>
              <SecondaryFlowButton size='icon-lg' className='lg:hidden max-sm:hidden' asChild>
                <Link href='https://github.com/uncase-ai/UNCASE/blob/main/UNCASE_PublicWhitepaper_TechnicalFoundations_v1.0.pdf' target='_blank' rel='noopener noreferrer'>
                  <BookOpenIcon />
                  <span className='sr-only'>Read Whitepapers</span>
                </Link>
              </SecondaryFlowButton>
            </TooltipTrigger>
            <TooltipContent>Read Whitepapers</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <PrimaryFlowButton size='icon-lg' className='lg:hidden max-sm:hidden' asChild>
                <Link href='https://github.com/uncase-ai/UNCASE'>
                  <ExternalLinkIcon />
                  <span className='sr-only'>Instalación</span>
                </Link>
              </PrimaryFlowButton>
            </TooltipTrigger>
            <TooltipContent>Instalación</TooltipContent>
          </Tooltip>

          <HeaderNavigationSmallScreen navigationData={navigationData} />
        </div>
      </div>
    </header>
  )
}

export default Header
