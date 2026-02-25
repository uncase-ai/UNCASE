import { capabilities, type Capability } from '@/assets/data/capabilities'

import { Card, CardContent } from '@/components/ui/card'
import { MotionPreset } from '@/components/ui/motion-preset'

import { cn } from '@/lib/utils'

const CapabilityCard = ({ capability, index }: { capability: Capability; index: number }) => {
  const Icon = capability.icon

  return (
    <MotionPreset
      fade
      slide={{ direction: 'down', offset: 35 }}
      blur
      delay={0.15 * index}
      transition={{ duration: 0.5 }}
    >
      <Card className='h-full shadow-none'>
        <CardContent className='flex flex-col gap-4'>
          <div
            className={cn(
              'bg-primary/10 text-primary flex size-12 shrink-0 items-center justify-center rounded-full'
            )}
          >
            <Icon className='size-5' />
          </div>

          <h3 className='text-lg font-semibold'>{capability.title}</h3>

          <p className='text-muted-foreground text-sm'>{capability.description}</p>
        </CardContent>
      </Card>
    </MotionPreset>
  )
}

const Capabilities = () => {
  return (
    <section id='capabilities' className='py-8 sm:py-16 lg:py-24'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        <MotionPreset
          fade
          slide={{ direction: 'down', offset: 50 }}
          blur
          transition={{ duration: 0.5 }}
          className='mb-12 space-y-4 text-center sm:mb-16 lg:mb-24'
        >
          <p className='text-primary text-sm font-medium uppercase'>Capabilities</p>

          <h2 className='text-2xl font-semibold md:text-3xl lg:text-4xl'>Everything You Need to Ship Compliant AI</h2>

          <p className='text-muted-foreground mx-auto max-w-3xl text-xl'>
            LLM Gateway, Privacy Interceptor, Connector Hub, and 52 API endpoints — all built with privacy,
            compliance, and auditability as non-negotiable requirements.
          </p>
        </MotionPreset>

        <div className='grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3'>
          {capabilities.map((capability, index) => (
            <CapabilityCard key={index} capability={capability} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default Capabilities
