import { Card, CardContent } from '@/components/ui/card'

import { Marquee } from '@/components/ui/marquee'

export type brandLogos = {
  image: string
  name: string
}

const TrustedBrands = ({ brandLogos }: { brandLogos: brandLogos[] }) => {
  return (
    <section id='trusted-brands' className='py-4 sm:py-6 lg:py-8'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        {/* Header */}
        <div className='mb-4 space-y-4 text-center sm:mb-6 lg:mb-8'>
          <p className='text-muted-foreground text-xl'>Built on research from leading institutions and validated empirically.</p>
        </div>

        <div className='relative'>
          <div className='from-background pointer-events-none absolute inset-y-0 left-0 z-1 w-35 bg-linear-to-r to-transparent' />
          <div className='from-background pointer-events-none absolute inset-y-0 right-0 z-1 w-35 bg-linear-to-l to-transparent' />
          <div className='w-full overflow-hidden'>
            <Marquee pauseOnHover duration={20} gap={1.5}>
              {brandLogos.map((logo, index) => (
                <Card key={index} className='border-none bg-transparent py-9 shadow-none'>
                  <CardContent className='flex flex-col items-center px-9'>
                    <img src={logo.image} alt={logo.name} className='h-6 opacity-75 grayscale dark:invert' />
                  </CardContent>
                </Card>
              ))}
            </Marquee>
          </div>
        </div>
      </div>
    </section>
  )
}

export default TrustedBrands
