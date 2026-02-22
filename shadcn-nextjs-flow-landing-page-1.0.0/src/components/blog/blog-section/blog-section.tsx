'use client'

import { useState } from 'react'

import { SearchIcon, ArrowRightIcon, CalendarDaysIcon } from 'lucide-react'

import Link from 'next/link'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { PostMetadata } from '@/lib/posts'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { SecondaryFlowButton } from '@/components/ui/flow-button'
import { MotionPreset } from '@/components/ui/motion-preset'

const BlogGrid = ({
  posts,
  onCategoryClick
}: {
  posts: PostMetadata[]
  onCategoryClick: (category: string) => void
}) => {
  return (
    <div className='grid gap-6 sm:grid-cols-2 lg:grid-cols-3'>
      {posts.map((post, index) => (
        <Card key={index} className='group h-full overflow-hidden shadow-none transition-all duration-300'>
          <CardContent className='flex h-full flex-col gap-3.5'>
            <Link href={`/blog/${post.slug}`} className='mb-2.5 overflow-hidden rounded-lg'>
              <img
                src={post.image}
                alt={post.title}
                className='h-59.5 w-full object-cover transition-transform duration-300 group-hover:scale-105'
              />
            </Link>
            <div className='flex items-center justify-between gap-1.5'>
              <div className='text-muted-foreground flex items-center gap-1.5'>
                <CalendarDaysIcon className='size-4.5' />
                <span className='text-muted-foreground'>
                  {new Date(post.publishedAt ?? '').toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: '2-digit'
                  })}
                </span>
              </div>
              <Badge
                className='bg-primary/10 text-primary cursor-pointer rounded-full text-sm'
                onClick={() => onCategoryClick(post.category ?? '')}
              >
                {post.category}
              </Badge>
            </div>
            <Link href={`/blog/${post.slug}`} className='block'>
              <h3 className='hover:text-primary line-clamp-2 text-lg font-medium transition-colors md:text-xl'>
                {post.title}
              </h3>
            </Link>

            <p className='text-muted-foreground line-clamp-3'>{post.description}</p>

            <div className='flex flex-1 items-end justify-between'>
              <Link href={`/blog/${post.slug}`}>
                <p className='text-sm font-medium'>{post.author?.name}</p>
              </Link>
              <SecondaryFlowButton size='icon' asChild>
                <Link href={`/blog/${post.slug}`}>
                  <ArrowRightIcon className='size-4 -rotate-45' />
                  <span className='sr-only'>Read more: {post.title}</span>
                </Link>
              </SecondaryFlowButton>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

const BlogSection = ({ posts }: { posts: PostMetadata[] }) => {
  const [selectedTab, setSelectedTab] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')

  const filterCategories = Array.from(new Set(posts.map(post => post.category))).filter(Boolean) as string[]
  const categories = ['All', ...filterCategories]

  const handleTabChange = (tab: string) => {
    setSelectedTab(tab)
  }

  const filteredPosts = posts.filter(post => {
    // Category filter
    const matchesCategory = selectedTab === 'All' || post.category === selectedTab

    // Search filter
    if (!searchQuery) return matchesCategory

    const query = searchQuery.toLowerCase()

    const matchesSearch =
      post.title?.toLowerCase().includes(query) ||
      post.description?.toLowerCase().includes(query) ||
      post.author?.name.toLowerCase().includes(query) ||
      post.category?.toLowerCase().includes(query)

    return matchesCategory && matchesSearch
  })

  return (
    <section className='pt-8 sm:pt-16 lg:pt-24'>
      <div className='mx-auto max-w-7xl space-y-8 px-4 sm:px-6 lg:space-y-16 lg:px-8'>
        {/* Header */}
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
          className='space-y-4 text-center'
        >
          <p className='text-sm font-medium uppercase'>Blogs</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Learn How High-Performing Products Grow</h2>

          <p className='text-muted-foreground mx-auto max-w-3xl text-xl'>
            Actionable insights, real-world strategies, and product analytics lessons to help you track what matters,
            move faster, and scale with confidence.
          </p>
        </MotionPreset>

        {/* Tabs and Search */}
        <Tabs value={selectedTab} onValueChange={handleTabChange} className='gap-8 lg:gap-16'>
          <MotionPreset fade slide={{ direction: 'down' }} transition={{ duration: 0.5 }} inView={false} delay={0.2}>
            <div className='flex justify-between gap-4 max-sm:flex-col sm:flex-wrap sm:items-center'>
              <ScrollArea className='w-full sm:w-auto'>
                <TabsList className='gap-1 p-1'>
                  {categories.map(category => (
                    <TabsTrigger
                      key={category}
                      value={category}
                      className='hover:bg-primary/10 dark:data-[state=active]:bg-background dark:data-[state=active]:border-background min-w-30 cursor-pointer px-4 text-base'
                    >
                      {category}
                    </TabsTrigger>
                  ))}
                </TabsList>
                <ScrollBar orientation='horizontal' />
              </ScrollArea>

              <div className='relative w-full max-w-82 max-md:w-full max-md:max-w-89'>
                <div className='text-muted-foreground pointer-events-none absolute inset-y-0 left-0 flex items-center justify-center pl-3 peer-disabled:opacity-50'>
                  <SearchIcon className='size-4' />
                  <span className='sr-only'>Search</span>
                </div>
                <Input
                  type='search'
                  placeholder='Search insights'
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className='peer h-10 ps-9 [&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none [&::-webkit-search-results-button]:appearance-none [&::-webkit-search-results-decoration]:appearance-none'
                />
              </div>
            </div>
          </MotionPreset>

          <MotionPreset fade slide={{ direction: 'down' }} transition={{ duration: 0.5 }} inView={false} delay={0.4}>
            {/* Tabs Content */}
            {categories.map((category, index) => (
              <TabsContent key={index} value={category}>
                {filteredPosts.length > 0 ? (
                  <BlogGrid posts={filteredPosts} onCategoryClick={handleTabChange} />
                ) : (
                  <div className='text-muted-foreground flex min-h-100 flex-col items-center justify-center space-y-4 rounded-lg border border-dashed p-8 text-center'>
                    <SearchIcon className='size-12 opacity-50' />
                    <div className='space-y-2'>
                      <h3 className='text-foreground text-lg font-medium'>No posts found</h3>
                      <p className='text-sm'>
                        {searchQuery
                          ? `No results in "${category}" for "${searchQuery}".`
                          : `No posts in "${category}" category yet.`}
                      </p>
                    </div>
                    {searchQuery && (
                      <SecondaryFlowButton size='sm' onClick={() => setSearchQuery('')}>
                        Clear search
                      </SecondaryFlowButton>
                    )}
                  </div>
                )}
              </TabsContent>
            ))}
          </MotionPreset>
        </Tabs>
      </div>
    </section>
  )
}

export default BlogSection
