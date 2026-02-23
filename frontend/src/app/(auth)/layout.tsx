import type { ReactNode } from 'react'

import AuthBackgroundShape from '@/assets/svg/auth-background-shape'
import { BorderBeam } from '@/components/ui/border-beam'

const AuthLayout = ({ children }: Readonly<{ children: ReactNode }>) => {
  return (
    <div className='h-dvh lg:grid lg:grid-cols-6'>
      {/* Dashboard Preview */}
      <div className='max-lg:hidden lg:col-span-3 xl:col-span-4'>
        <div className='bg-muted relative z-1 flex h-full items-center justify-center px-6'>
          <div className='outline-border relative shrink rounded-[20px] p-2.5 outline-2 -outline-offset-2'>
            <img
              src='/images/dashboard.webp'
              className='max-h-111 w-full rounded-lg object-contain dark:hidden'
              alt='Dashboards'
            />
            <img
              src='/images/dashboard-dark.webp'
              className='hidden max-h-111 w-full rounded-lg object-contain dark:inline-block'
              alt='Dashboards'
            />

            <BorderBeam duration={8} borderWidth={2} size={100} />
          </div>

          <div className='absolute -z-1'>
            <AuthBackgroundShape className='max-xl:scale-90' />
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
