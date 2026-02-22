import { ChevronLeftIcon } from 'lucide-react'

import Link from 'next/link'

import { Button } from '@/components/ui/button'

import Logo from '@/components/logo'
import ForgotPasswordForm from '@/components/auth/forgot-password/forgot-password-form'

const ForgotPassword = () => {
  return (
    <div className='flex flex-col gap-6'>
      <Link href='/'>
        <Logo />
      </Link>

      <div>
        <h1 className='mb-2 text-2xl font-semibold'>Forgot Password?</h1>
        <p className='text-muted-foreground'>
          Enter your email and we&apos;ll send you instructions to reset your password
        </p>
      </div>

      <div className='space-y-3'>
        {/* Form */}
        <ForgotPasswordForm />

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

export default ForgotPassword
