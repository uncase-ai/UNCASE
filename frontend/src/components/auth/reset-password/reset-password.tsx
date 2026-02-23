import { ChevronLeftIcon } from 'lucide-react'

import Link from 'next/link'

import { Button } from '@/components/ui/button'

import Logo from '@/components/logo'
import ResetPasswordForm from '@/components/auth/reset-password/reset-password-form'

const ResetPassword = () => {
  return (
    <div className='flex flex-col gap-6'>
      <Link href='/'>
        <Logo />
      </Link>

      <div>
        <h1 className='mb-2 text-2xl font-semibold'>Reset Password</h1>
        <p className='text-muted-foreground'>Time for a fresh start! Go ahead and set a new password.</p>
      </div>

      <div className='space-y-3'>
        {/* Form */}
        <ResetPasswordForm />

        <Button asChild variant='ghost' className='group w-full'>
          <Link href='/login'>
            <ChevronLeftIcon className='transition-transform duration-200 group-hover:-translate-x-0.5' />
            <p>Back to login</p>
          </Link>
        </Button>
      </div>
    </div>
  )
}

export default ResetPassword
