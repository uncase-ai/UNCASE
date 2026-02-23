'use client'

import { useEffect, useState } from 'react'

import { CircleIcon } from 'lucide-react'

import Link from 'next/link'

import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

export interface TocItem {
  slug: string
  text: string
  depth: number
  children: TocItem[]
}

interface TableOfContentsProps {
  headings: { slug: string; text: string; depth: number }[]
}

const HEADER_OFFSET = 150

function buildTocTree(headings: { slug: string; text: string; depth: number }[]): TocItem[] {
  const root: TocItem[] = []
  const stack: TocItem[] = []

  headings.forEach(heading => {
    const item: TocItem = {
      slug: heading.slug,
      text: heading.text,
      depth: heading.depth,
      children: []
    }

    // Find the appropriate parent
    while (stack.length > 0 && stack[stack.length - 1].depth >= heading.depth) {
      stack.pop()
    }

    // Add to parent's children or root
    if (stack.length === 0) {
      root.push(item)
    } else {
      stack[stack.length - 1].children.push(item)
    }

    stack.push(item)
  })

  return root
}

const TableOfContents = ({ headings }: TableOfContentsProps) => {
  const [activeId, setActiveId] = useState<string>('')
  const groupedHeadings = buildTocTree(headings)

  useEffect(() => {
    const handleScroll = () => {
      const headingElements = Array.from(document.querySelectorAll<HTMLElement>('h2[id], h3[id], h4[id]'))

      if (headingElements.length === 0) return

      const scrollY = window.scrollY || window.pageYOffset
      let currentActiveId = ''

      // Find the last heading above the scroll position
      for (let i = headingElements.length - 1; i >= 0; i--) {
        const heading = headingElements[i]
        const headingTop = heading.getBoundingClientRect().top + scrollY

        if (headingTop - HEADER_OFFSET <= scrollY) {
          currentActiveId = heading.id
          break
        }
      }

      // If no heading is above, highlight the first one
      if (!currentActiveId && headingElements.length > 0) {
        const firstHeadingTop = headingElements[0].getBoundingClientRect().top + scrollY

        if (scrollY < firstHeadingTop) {
          currentActiveId = headingElements[0].id
        }
      }

      setActiveId(currentActiveId)
    }

    handleScroll() // Initial check
    window.addEventListener('scroll', handleScroll, { passive: true })

    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, slug: string) => {
    e.preventDefault()
    const element = document.getElementById(slug)

    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const renderTocItems = (items: TocItem[], depth: number = 0) => {
    return items.map(item => (
      <li key={item.slug}>
        <Link
          href={`#${item.slug}`}
          onClick={e => handleClick(e, item.slug)}
          className={cn(
            'flex gap-2 text-sm transition-colors duration-200',
            activeId === item.slug
              ? 'text-foreground font-medium'
              : depth === 0
                ? 'text-foreground/60 hover:text-foreground'
                : depth === 1
                  ? 'text-foreground/50 hover:text-foreground'
                  : 'text-foreground/40 hover:text-foreground'
          )}
          data-heading-link={item.slug}
          data-depth={depth}
        >
          <CircleIcon className={cn('mt-1.5 size-2 shrink-0', depth === 0 && 'fill-current')} />
          <span className='max-w-65.5'>{item.text}</span>
        </Link>

        {item.children.length > 0 && (
          <ul className='mt-2.5 ml-5 flex list-none flex-col gap-y-2.5'>{renderTocItems(item.children, depth + 1)}</ul>
        )}
      </li>
    ))
  }

  if (groupedHeadings.length === 0) {
    return null
  }

  return (
    <div className='sticky top-20 hidden max-h-[calc(100vh-5rem)] md:block'>
      <div className='mb-4 text-sm font-semibold'>On This Page</div>
      <ScrollArea className='h-[calc(100vh-8rem)]'>
        <nav>
          <ul className='flex list-none flex-col gap-y-3'>{renderTocItems(groupedHeadings)}</ul>
        </nav>
      </ScrollArea>
    </div>
  )
}

export default TableOfContents
