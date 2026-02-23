import Hero from '@/components/blocks/hero-section/hero-section'
import TrustedBrands from '@/components/blocks/trusted-brands/trusted-brands'
import Features from '@/components/blocks/features/features'
import Benefits from '@/components/blocks/benefits/benefits'
import Testimonials from '@/components/blocks/testimonials/testimonials'
import Pricing from '@/components/blocks/pricing/pricing'
import FAQ from '@/components/blocks/faq/faq'
import CTA from '@/components/blocks/cta/cta'

import { logos } from '@/assets/data/trusted-brands'
import { plans } from '@/assets/data/pricing'
import { testimonials } from '@/assets/data/testimonials'
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
        'Open source framework for generating high-quality synthetic conversational data for LoRA fine-tuning in privacy-sensitive industries.',
      url: `${process.env.NEXT_PUBLIC_APP_URL}`,
      inLanguage: 'es'
    }
  ]
}

const Home = () => {
  return (
    <>
      <Hero />

      <SectionSeparator />

      <TrustedBrands brandLogos={logos} />

      <SectionSeparator />

      <Features />

      <SectionSeparator />

      <Benefits featuresList={benefits} />

      <SectionSeparator />

      <Testimonials testimonials={testimonials} />

      <SectionSeparator />

      <Pricing plans={plans} />

      <SectionSeparator />

      <FAQ faqItems={faqItems} />

      <CTA />

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

export default Home
