import type { ReactNode } from 'react'

const AuthLayout = ({ children }: Readonly<{ children: ReactNode }>) => {
  return (
    <div className='h-dvh lg:grid lg:grid-cols-6'>
      {/* UNCASE Brand Panel */}
      <div className='max-lg:hidden lg:col-span-3 xl:col-span-4'>
        <div className='relative flex h-full flex-col items-center justify-center bg-zinc-950 px-12'>
          {/* Background gradient */}
          <div className='pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.15),transparent_50%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.1),transparent_50%)]' />

          {/* Logo */}
          <div className='relative mb-8'>
            <img
              src='/images/logo/logo-white.svg'
              alt='UNCASE'
              className='h-10 w-auto'
            />
          </div>

          {/* Pipeline screenshot */}
          <div className='relative w-full max-w-lg'>
            <div className='rounded-xl border border-white/10 bg-white/5 p-3 shadow-2xl backdrop-blur-sm'>
              <img
                src='/images/logo/screenshot-pipeline.png'
                className='w-full rounded-lg'
                alt='UNCASE Pipeline — Seed Engineering, Knowledge Base, Data Import'
              />
            </div>
          </div>

          {/* Tagline */}
          <div className='relative mt-8 max-w-md text-center'>
            <h2 className='text-lg font-semibold text-white'>
              Synthetic Training Data for Regulated Industries
            </h2>
            <p className='mt-2 text-sm text-zinc-400'>
              Generate high-quality conversational datasets for LoRA fine-tuning without exposing real data.
              Privacy-first, compliance-ready.
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className='flex h-full flex-col items-center justify-center py-10 sm:px-5 lg:col-span-3 xl:col-span-2'>
        <div className='w-full max-w-lg p-6'>{children}</div>
      </div>
    </div>
  )
}

export default AuthLayout
