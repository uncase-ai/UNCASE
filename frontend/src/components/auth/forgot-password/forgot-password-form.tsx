'use client'

import { useRouter } from 'next/navigation'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

const ForgotPasswordForm = () => {
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    router.push('/reset-password')
  }

  return (
    <form className='space-y-4' onSubmit={handleSubmit}>
      {/* Email */}
      <div className='space-y-1'>
        <Label className='leading-5' htmlFor='userEmail'>
          Email address*
        </Label>
        <Input type='email' id='userEmail' placeholder='Enter your email address' />
      </div>

      <PrimaryFlowButton className='w-full *:w-full [&>button]:after:-inset-55' type='submit'>
        Reset password
      </PrimaryFlowButton>
    </form>
  )
}

export default ForgotPasswordForm
