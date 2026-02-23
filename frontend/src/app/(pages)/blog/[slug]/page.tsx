import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'

import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react'

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator
} from '@/components/ui/breadcrumb'
import MDXContent from '@/components/mdx-content'
import TableOfContents from '@/components/blog/table-of-contents'

import { getPostBySlug, getPosts } from '@/lib/posts'
import { extractHeadings } from '@/lib/extract-headings'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'

import RelatedBlogSection from '@/components/blog/related-blog-section/related-blog-section'
import SectionSeparator from '@/components/section-separator'
import CTASection from '@/components/blocks/cta/cta'
import { SecondaryFlowButton } from '@/components/ui/flow-button'

export async function generateStaticParams() {
  const posts = await getPosts()

  return posts.map(post => ({ slug: post.slug }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params

  const post = await getPostBySlug(slug)

  if (!post) {
    return {}
  }

  const { metadata } = post

  return {
    title: `Blog: ${metadata.title}`,
    description: metadata.description,
    keywords: metadata.keywords,
    alternates: {
      canonical: `${process.env.NEXT_PUBLIC_APP_URL}/blog/${metadata.slug}`
    }
  }
}

export const dynamicParams = false

const BlogDetailsPage = async ({ params }: { params: Promise<{ slug: string }> }) => {
  const { slug } = await params
  const posts = await getPosts()

  const post = await getPostBySlug(slug)

  if (!post) {
    notFound()
  }

  const { metadata, content } = post

  // Sort posts by published date
  const allPosts = posts.sort(
    (a, b) => new Date(a.publishedAt ?? '').getTime() - new Date(b.publishedAt ?? '').getTime()
  )

  // Find the current post index
  const currentPostIndex = allPosts.findIndex(p => p.slug === slug)
  const previousPost = currentPostIndex > 0 ? allPosts[currentPostIndex - 1] : null
  const nextPost = currentPostIndex < allPosts.length - 1 ? allPosts[currentPostIndex + 1] : null

  const sameCategoryPosts = allPosts.filter(p => p.category === metadata.category && p.slug !== slug)
  const otherCategoryPosts = allPosts.filter(p => p.category !== metadata.category && p.slug !== slug)
  const relatedPosts = [...sameCategoryPosts, ...otherCategoryPosts].slice(0, 3)

  // Extract headings for TOC
  const headings = extractHeadings(content)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': `${process.env.NEXT_PUBLIC_APP_URL}#website`,
        name: 'Flow',
        description:
          'Grow your product faster with an all-in-one sales and analytics platform. Track performance, automate follow-ups, and make smarter decisions easily.',
        url: `${process.env.NEXT_PUBLIC_APP_URL}`,
        inLanguage: 'en-US'
      },
      {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        '@id': `${process.env.NEXT_PUBLIC_APP_URL}#webpage`,
        name: `Blog: ${metadata.title}`,
        description: metadata.description,
        url: `${process.env.NEXT_PUBLIC_APP_URL}/blog/${metadata.slug}`,
        isPartOf: {
          '@id': `${process.env.NEXT_PUBLIC_APP_URL}#website`
        },
        potentialAction: {
          '@type': 'ReadAction',
          target: [`${process.env.NEXT_PUBLIC_APP_URL}/blog/${metadata.slug}`]
        }
      },
      {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Home',
            item: `${process.env.NEXT_PUBLIC_APP_URL}`
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: 'Blog',
            item: `${process.env.NEXT_PUBLIC_APP_URL}/blog`
          },
          {
            '@type': 'ListItem',
            position: 3,
            name: metadata.title,
            item: `${process.env.NEXT_PUBLIC_APP_URL}/blog/${metadata.slug}`
          }
        ]
      }
    ]
  }

  return (
    <>
      <section className='py-8 sm:py-16'>
        <div className='mx-auto grid w-full max-w-7xl grid-cols-1 px-4 sm:px-6 lg:grid-cols-[250px_1fr] lg:gap-12 lg:px-8 xl:gap-16'>
          <aside className='hidden lg:block'>
            <TableOfContents headings={headings} />
          </aside>

          <div>
            <Breadcrumb className='mb-6'>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink asChild>
                    <Link href='/'>Home</Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbLink asChild>
                    <Link href='/blog'>Blog</Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>{metadata.category}</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>

            <h1 className='mb-6 text-2xl font-semibold md:text-3xl lg:text-4xl'>{metadata.title}</h1>

            <p className='text-muted-foreground'>{metadata.description}</p>

            <Separator className='my-6' />

            <div className='mb-16 flex flex-wrap items-center justify-between gap-6'>
              <div className='flex items-center gap-2'>
                <Avatar className='size-11.5'>
                  <AvatarImage src={metadata.author?.picture} alt={metadata.author?.name} />
                  <AvatarFallback>{metadata.author?.name.charAt(0)}</AvatarFallback>
                </Avatar>
                <div className='flex flex-col text-sm'>
                  <span className='text-muted-foreground mb-1'>Written by</span>
                  <span className='font-medium'>{metadata.author?.name}</span>
                </div>
              </div>

              <div className='flex flex-col text-sm'>
                <span className='text-muted-foreground mb-1.5'>Read Time</span>
                <span className='font-medium'>{metadata.readTime}</span>
              </div>

              <div className='flex flex-col text-sm'>
                <span className='text-muted-foreground mb-1.5'>Posted on</span>
                <span className='font-medium'>
                  {new Date(metadata.publishedAt ?? '').toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: '2-digit'
                  })}
                </span>
              </div>
            </div>

            <img src={metadata.image} alt={metadata.title} className='mb-16 max-h-110 w-full rounded-xl object-cover' />

            <MDXContent source={content} />

            <div className='flex items-center justify-between gap-4 pt-8 sm:pt-16'>
              {previousPost ? (
                <SecondaryFlowButton asChild size='lg'>
                  <Link href={`/blog/${previousPost.slug}`}>
                    <ChevronLeftIcon className='max-sm:hidden' />
                    Previous Post
                  </Link>
                </SecondaryFlowButton>
              ) : (
                <SecondaryFlowButton size='lg' className='pointer-events-none opacity-50'>
                  <ChevronLeftIcon className='max-sm:hidden' />
                  Previous Post
                </SecondaryFlowButton>
              )}
              {nextPost ? (
                <SecondaryFlowButton asChild size='lg'>
                  <Link href={`/blog/${nextPost.slug}`}>
                    Next Post
                    <ChevronRightIcon className='max-sm:hidden' />
                  </Link>
                </SecondaryFlowButton>
              ) : (
                <SecondaryFlowButton size='lg' className='pointer-events-none opacity-50'>
                  Next Post
                  <ChevronRightIcon className='max-sm:hidden' />
                </SecondaryFlowButton>
              )}
            </div>
          </div>
        </div>
      </section>

      <SectionSeparator />

      <RelatedBlogSection posts={relatedPosts} />

      <CTASection />

      {/* Add JSON-LD to your page */}
      <script
        type='application/ld+json'
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c')
        }}
      />
    </>
  )
}

export default BlogDetailsPage
