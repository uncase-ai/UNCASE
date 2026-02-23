import type { Metadata } from 'next'

import CTASection from '@/components/blocks/cta/cta'
import HeroSection from '@/components/blog/hero-section/hero-section'
import SectionSeparator from '@/components/section-separator'
import BlogSection from '@/components/blog/blog-section/blog-section'
import { getPosts } from '@/lib/posts'

export const metadata: Metadata = {
  title: 'Blog',
  description: 'Welcome to our blog. Stay updated with the latest news and articles.',
  keywords: ['blog', 'articles', 'news', 'updates', 'insights'],
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_APP_URL}/blog`
  }
}

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
      name: 'Blog',
      description: 'Welcome to our blog. Stay updated with the latest news and articles.',
      url: `${process.env.NEXT_PUBLIC_APP_URL}/blog`,
      isPartOf: {
        '@id': `${process.env.NEXT_PUBLIC_APP_URL}#website`
      },
      potentialAction: {
        '@type': 'ReadAction',
        target: [`${process.env.NEXT_PUBLIC_APP_URL}/blog`]
      }
    }
  ]
}

const BlogPage = async () => {
  const blogPosts = await getPosts()

  const featuredPosts = blogPosts.filter(post => post.featured)

  return (
    <>
      <HeroSection posts={featuredPosts} />

      <SectionSeparator />

      <BlogSection posts={blogPosts} />

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

export default BlogPage
