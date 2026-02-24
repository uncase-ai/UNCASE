'use client'

import { useEffect, useRef, useState, type ReactNode } from 'react'

import { useMedia } from 'react-use'
import { ChevronRightIcon, CircleSmallIcon, MenuIcon } from 'lucide-react'

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle
} from '@/components/ui/navigation-menu'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetTrigger
} from '@/components/ui/sheet'
import { PrimaryOrionButton } from '@/components/ui/orion-button'

import { cn } from '@/lib/utils'

import OrionLogo from '@/assets/svg/orion-logo'

type NavigationSection = {
  type: 'section'
  title: string
  items: NavigationItem[]
}

type NavigationItem = {
  title: string
  href: string
  icon?: ReactNode
  badge?: ReactNode
  description?: string
}

type Navigation = {
  title: string
  contentClassName?: string
} & (
  | {
      items: NavigationSection[]
      splitItems: true
      href?: never
    }
  | {
      items: NavigationItem[]
      splitItems?: never | false
      href?: never
    }
  | {
      items?: never
      splitItems?: never
      href: string
    }
)

const ListItem = (props: {
  title: NavigationItem['title']
  href: NavigationItem['href']
  icon?: NavigationItem['icon']
  badge?: NavigationItem['badge']
  description?: NavigationItem['description']
  splitItems?: boolean
}) => {
  const { title, href, icon, badge, description, splitItems } = props

  return (
    <li className={cn({ 'h-19.5': description && splitItems })}>
      <NavigationMenuLink href={href} className={cn({ 'flex flex-row items-start gap-2': icon })}>
        {icon && (
          <span className='bg-popover [&>svg]:text-popover-foreground! flex aspect-square size-7.5 shrink-0 items-center justify-center rounded-sm border [&>svg]:size-4.5!'>
            {icon}
          </span>
        )}
        {description ? (
          <div className='space-y-1'>
            <div className={cn('font-medium', { 'flex items-center gap-1.5': badge })}>
              {title}
              {badge}
            </div>
            <p className='text-muted-foreground line-clamp-2'>{description}</p>
          </div>
        ) : (
          <div className={cn('font-medium', { 'flex items-center gap-1.5': badge })}>
            {title}
            {badge}
          </div>
        )}
      </NavigationMenuLink>
    </li>
  )
}

const HeroNavigation = ({
  navigationData,
  navigationClassName
}: {
  navigationData: Navigation[]
  navigationClassName?: string
}) => {
  return (
    <NavigationMenu viewport={false} className={cn('hidden lg:block', navigationClassName)}>
      <NavigationMenuList className='flex-wrap gap-0'>
        {navigationData.map(navItem => {
          if (navItem.href) {
            // Root link item
            return (
              <NavigationMenuItem key={navItem.title}>
                <NavigationMenuLink
                  href={navItem.href}
                  className={cn(
                    navigationMenuTriggerStyle(),
                    'text-muted-foreground hover:text-primary focus:text-primary bg-transparent px-3 py-1.5 text-base hover:bg-transparent focus:bg-transparent'
                  )}
                >
                  {navItem.title}
                </NavigationMenuLink>
              </NavigationMenuItem>
            )
          }

          // Section with dropdown
          return (
            <NavigationMenuItem key={navItem.title}>
              <NavigationMenuTrigger className='text-muted-foreground hover:text-primary focus:text-primary data-[state=open]:text-primary data-[state=open]:focus:text-primary data-[state=open]:hover:text-primary bg-transparent px-3 py-1.5 text-base hover:bg-transparent focus:bg-transparent data-[state=open]:bg-transparent data-[state=open]:hover:bg-transparent data-[state=open]:focus:bg-transparent [&_svg]:ml-2 [&_svg]:size-4'>
                {navItem.title}
              </NavigationMenuTrigger>
              <NavigationMenuContent className='absolute left-1/2 w-auto -translate-x-1/2 shadow-lg!'>
                {navItem.splitItems ? (
                  <div className={cn('grid grid-cols-1 gap-2', navItem.contentClassName)}>
                    {navItem.items.map(section => (
                      <div key={section.title} className='grid grid-cols-1 gap-3'>
                        <div className='text-muted-foreground px-2 text-sm'>{section.title}</div>
                        <ul
                          className={cn('grid grid-cols-1 gap-0.5', {
                            'gap-3': section.items.find(item => item.description)
                          })}
                        >
                          {section.items.map((item, index) => (
                            <ListItem
                              key={index}
                              icon={item.icon}
                              title={item.title}
                              description={item.description}
                              href={item.href}
                              badge={item.badge}
                              splitItems={navItem.splitItems}
                            />
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ul
                    className={cn(
                      'grid grid-cols-1 gap-0.5',
                      { 'gap-2': navItem.items?.find(item => item.description) },
                      navItem.contentClassName
                    )}
                  >
                    {navItem.items?.map((item, index) => (
                      <ListItem
                        key={index}
                        icon={item.icon}
                        title={item.title}
                        description={item.description}
                        href={item.href}
                        badge={item.badge}
                      />
                    ))}
                  </ul>
                )}
              </NavigationMenuContent>
            </NavigationMenuItem>
          )
        })}
      </NavigationMenuList>
    </NavigationMenu>
  )
}

const HeroNavigationSmallScreen = ({
  navigationData,
  triggerClassName,
  screenSize = 1023
}: {
  navigationData: Navigation[]
  triggerClassName?: string
  screenSize?: number
}) => {
  const [open, setOpen] = useState(false)
  const isMobile = useMedia(`(max-width: ${screenSize}px)`, false)

  const handleLinkClick = () => {
    setOpen(false)
  }

  // Close sheet when switching from mobile to desktop
  const prevIsMobile = useRef(isMobile)

  useEffect(() => {
    if (prevIsMobile.current && !isMobile) {
      requestAnimationFrame(() => setOpen(false))
    }

    prevIsMobile.current = isMobile
  }, [isMobile])

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <PrimaryOrionButton size='icon-lg' className={cn('inline-flex lg:hidden', triggerClassName)}>
          <MenuIcon />
          <span className='sr-only'>Menu</span>
        </PrimaryOrionButton>
      </SheetTrigger>
      <SheetContent side='left' className='w-75 gap-0 p-0'>
        <SheetHeader className='p-4'>
          <SheetTitle hidden />
          <SheetDescription hidden />
          <a href='#' onClick={handleLinkClick} className='self-start'>
            <div className='flex items-center gap-3'>
              <OrionLogo className='size-8' />
              <span className='text-xl font-semibold'>Orion</span>
            </div>
          </a>
        </SheetHeader>
        <div className='space-y-0.5 overflow-y-auto p-2'>
          {navigationData.map((navItem, index) => {
            if (navItem.href) {
              return (
                <a
                  key={navItem.title}
                  href={navItem.href}
                  className='hover:bg-accent flex items-center gap-2 rounded-sm px-3 py-2 text-sm'
                  onClick={handleLinkClick}
                >
                  {navItem.title}
                </a>
              )
            }

            return (
              <Collapsible key={index} className='w-full'>
                <CollapsibleTrigger className='hover:bg-accent group flex w-full items-center justify-between rounded-sm px-3 py-2 text-sm'>
                  <div className='flex items-center gap-2'>{navItem.title}</div>
                  <ChevronRightIcon className='size-4 shrink-0 transition-transform duration-300 group-data-[state=open]:rotate-90' />
                </CollapsibleTrigger>
                <CollapsibleContent className='data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down overflow-hidden transition-all duration-300'>
                  {navItem.splitItems
                    ? navItem.items.map((item, i) => (
                        <div key={i} className='mt-1.5'>
                          <div className='text-muted-foreground mb-1 pl-4.5 text-xs font-medium'>{item.title}</div>
                          {item.items.map((subItem, j) => (
                            <a
                              key={j}
                              href={subItem.href}
                              className='hover:bg-accent ml-4.5 flex items-center gap-2 rounded-sm px-3 py-2 text-sm'
                              onClick={handleLinkClick}
                            >
                              {subItem.icon ? subItem.icon : <CircleSmallIcon className='size-4' />}
                              {subItem.title}
                            </a>
                          ))}
                        </div>
                      ))
                    : navItem.items?.map(item => (
                        <a
                          key={item.title}
                          href={item.href}
                          className='hover:bg-accent ml-3 flex items-center gap-2 rounded-sm px-3 py-2 text-sm'
                          onClick={handleLinkClick}
                        >
                          {item.icon ? item.icon : <CircleSmallIcon className='size-4' />}
                          {item.title}
                        </a>
                      ))}
                </CollapsibleContent>
              </Collapsible>
            )
          })}
        </div>
      </SheetContent>
    </Sheet>
  )
}

export { HeroNavigation, HeroNavigationSmallScreen, type Navigation, type NavigationItem, type NavigationSection }
