import { redirect } from 'next/navigation'

import HeroSection40 from '@/components/shadcn-studio/blocks/hero-section-40/hero-section-40'
import Features from '@/components/blocks/features/features'
import Benefits from '@/components/blocks/benefits/benefits'
import Pricing from '@/components/blocks/pricing/pricing'
import FAQ from '@/components/blocks/faq/faq'
import CTA from '@/components/blocks/cta/cta'
import PipelineTimeline from '@/components/blocks/pipeline/pipeline-timeline'
import PipelineDataFlow from '@/components/blocks/pipeline/pipeline-data-flow'
import Capabilities from '@/components/blocks/capabilities/capabilities'
import Roadmap from '@/components/blocks/roadmap/roadmap'

/*
 * TrustedBrands and Testimonials commented out while UNCASE is in development
 * import TrustedBrands from '@/components/blocks/trusted-brands/trusted-brands'
 * import Testimonials from '@/components/blocks/testimonials/testimonials'
 * import { logos } from '@/assets/data/trusted-brands'
 * import { testimonials } from '@/assets/data/testimonials'
 */

import { plans } from '@/assets/data/pricing'
import { faqItems } from '@/assets/data/faqs'
import { benefits } from '@/assets/data/benefits'

import SectionSeparator from '@/components/section-separator'

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      '@id': `${process.env.NEXT_PUBLIC_APP_URL}#website`,
      name: 'UNCASE',
      description:
        'Open-source framework for turning sensitive conversations into trained AI models with zero PII exposure. LLM Gateway, Privacy Interceptor, and LoRA pipeline for regulated industries.',
      url: `${process.env.NEXT_PUBLIC_APP_URL}`,
      inLanguage: 'en'
    }
  ]
}

const Home = () => {
  // When NEXT_PUBLIC_LANDING is not set (e.g. local dev after git clone),
  // send users straight to the dashboard. The landing page is only shown
  // on the production marketing site (Vercel) where the env var is set.
  if (process.env.NEXT_PUBLIC_LANDING !== 'true') {
    redirect('/dashboard')
  }

  return (
    <>
      <HeroSection40 />

      <SectionSeparator />

      {/*
       * TrustedBrands — commented out while UNCASE is in development
       * <TrustedBrands brandLogos={logos} />
       * <SectionSeparator />
       */}

      <PipelineTimeline />

      <SectionSeparator />

      <PipelineDataFlow />

      <SectionSeparator />

      <Features />

      <SectionSeparator />

      <Capabilities />

      <SectionSeparator />

      <Benefits featuresList={benefits} />

      {/*
       * Testimonials — commented out while UNCASE is in development
       * <SectionSeparator />
       * <Testimonials testimonials={testimonials} />
       */}

      <SectionSeparator />

      <Pricing plans={plans} />

      <SectionSeparator />

      <FAQ faqItems={faqItems} />

      <SectionSeparator />

      <Roadmap />

      <SectionSeparator />

      <CTA />

      <script
        type='application/ld+json'
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c')
        }}
      />
    </>
  )
}

export default Home
