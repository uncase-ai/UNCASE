import Link from 'next/link'

import { CalendarDaysIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'

import { BackgroundRippleEffect } from '@/components/ui/background-ripple-effect'
import { MotionPreset } from '@/components/ui/motion-preset'
import { PrimaryFlowButton } from '@/components/ui/flow-button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card'

import type { PostMetadata } from '@/lib/posts'

const HeroSection = ({ posts }: { posts: PostMetadata[] }) => {
  return (
    <section id='home' className='relative px-4 py-8 sm:px-6 sm:py-16 lg:px-8 lg:py-24'>
      <BackgroundRippleEffect rows={10} />
      <div className='pointer-events-none absolute inset-x-0 top-0 z-5 h-148 bg-[radial-gradient(transparent_20%,var(--background)_90%)]' />
      <div className='space-y-12 sm:space-y-16 lg:space-y-24'>
        <div className='flex flex-col items-center gap-4'>
          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            className='z-10'
          >
            <Badge variant='outline' className='bg-background text-sm font-normal'>
              Trusted by 5,000+ growing businesses
            </Badge>
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.2}
            component='h1'
            className='z-10 max-w-2xl text-center text-3xl font-semibold md:text-4xl lg:text-5xl lg:leading-[1.29167]'
          >
            Insights That Power Smarter Product Growth
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.4}
            component='p'
            className='text-muted-foreground z-10 max-w-4xl text-center text-xl'
          >
            From product discovery to revenue metrics, explore actionable insights, proven strategies, and real-world
            frameworks to help you build, measure, and scale successful products with confidence.
          </MotionPreset>

          <MotionPreset
            fade
            slide={{ direction: 'down' }}
            transition={{ duration: 0.5 }}
            inView={false}
            delay={0.6}
            className='z-10 flex items-center justify-center gap-3 max-sm:flex-col'
          >
            <Input
              type='email'
              placeholder='Your email'
              className='bg-background dark:bg-background h-10 sm:w-72'
              required
            />
            <PrimaryFlowButton size='lg' className='shrink-0'>
              Subscribe
            </PrimaryFlowButton>
          </MotionPreset>
        </div>

        <MotionPreset
          fade
          slide={{ direction: 'down' }}
          transition={{ duration: 0.5 }}
          inView={false}
          delay={0.8}
          className='relative z-10 grid grid-cols-1 gap-4 lg:grid-cols-2'
        >
          {posts.slice(0, 1).map(post => (
            <Link key={post.slug} href={`/blog/${post.slug}`}>
              <Card className='group h-full shadow-none'>
                <CardContent className='flex h-full flex-col gap-6'>
                  <div className='overflow-hidden rounded-md'>
                    <img
                      src={post.image}
                      alt={post.title}
                      className='h-65 w-full object-cover transition-transform duration-300 group-hover:scale-105 max-lg:h-full max-sm:h-50 sm:max-lg:max-h-65'
                    />
                  </div>
                  <div className='flex items-center justify-between'>
                    <div className='text-muted-foreground flex items-center gap-1.5'>
                      <CalendarDaysIcon className='size-4.5' />
                      {new Date(post.publishedAt ?? '').toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: '2-digit'
                      })}
                    </div>
                    <Badge className='text-primary bg-primary/10 h-fit text-sm font-medium'>{post.category}</Badge>
                  </div>
                  <div className='space-y-3'>
                    <CardTitle className='text-xl font-medium'>{post.title}</CardTitle>
                    <CardDescription className='line-clamp-2 text-base'>{post.description}</CardDescription>
                  </div>
                  <p className='flex flex-1 items-end font-medium'>{post.author?.name}</p>
                </CardContent>
              </Card>
            </Link>
          ))}

          <div className='flex flex-col justify-between gap-4'>
            {posts.slice(1, 4).map(post => (
              <Link key={post.slug} href={`/blog/${post.slug}`}>
                <Card className='group py-5 shadow-none'>
                  <CardContent className='flex justify-between gap-6 max-sm:flex-col-reverse'>
                    <div className='flex flex-1 flex-col justify-center gap-3.5'>
                      <div className='flex justify-between'>
                        <span className='text-muted-foreground flex items-center gap-1.5'>
                          <CalendarDaysIcon className='size-4.5' />
                          {new Date(post.publishedAt ?? '').toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: '2-digit'
                          })}
                        </span>
                        <Badge className='text-primary bg-primary/10 border-0 text-sm font-medium'>
                          {post.category}
                        </Badge>
                      </div>

                      <div>
                        <CardTitle className='mb-1.5 line-clamp-1 text-base font-medium'>{post.title}</CardTitle>
                        <CardDescription className='text-base'>{post.author?.name}</CardDescription>
                      </div>
                    </div>
                    <div className='overflow-hidden rounded-md'>
                      <img
                        src={post.image}
                        alt={post.title}
                        className='h-50 w-full rounded-md object-cover transition-transform duration-300 group-hover:scale-105 sm:size-30'
                      />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </MotionPreset>
      </div>
    </section>
  )
}

export default HeroSection
