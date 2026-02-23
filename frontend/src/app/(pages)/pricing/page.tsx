import type { Metadata } from 'next'

import CTASection from '@/components/blocks/cta/cta'
import PricingDetail from '@/components/pricing/pricing-detail'

import { plans, pricingFeatures } from '@/assets/data/pricing-details'

export const metadata: Metadata = {
  title: 'Pricing',
  description: 'Explore our pricing plans and find the perfect fit for your needs.',
  keywords: ['pricing', 'plans', 'subscription', 'cost', 'features'],
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`
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
      name: 'Pricing',
      description: 'Explore our pricing plans and find the perfect fit for your needs.',
      url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
      isPartOf: {
        '@id': `${process.env.NEXT_PUBLIC_APP_URL}#website`
      },
      potentialAction: {
        '@type': 'ReadAction',
        target: [`${process.env.NEXT_PUBLIC_APP_URL}/pricing`]
      }
    }
  ]
}

const PricingPage = () => {
  return (
    <>
      <PricingDetail plans={plans} features={pricingFeatures} />

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

export default PricingPage
