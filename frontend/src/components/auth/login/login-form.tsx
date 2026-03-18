'use client'

import { useState } from 'react'

import { useRouter } from 'next/navigation'
import { EyeIcon, EyeOffIcon, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

import { loginWithPassword, storeTokens } from '@/lib/api/auth'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

const LoginForm = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isVisible, setIsVisible] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return

    setIsSubmitting(true)
    const { data, error } = await loginWithPassword(email, password)

    setIsSubmitting(false)

    if (error) {
      toast.error(error.message || 'Invalid credentials')

      return
    }

    if (data) {
      storeTokens(data.access_token, data.refresh_token)
      router.push('/dashboard')
    }
  }

  return (
    <form className='space-y-4' onSubmit={handleSubmit}>
      {/* Email */}
      <div className='space-y-1'>
        <Label className='leading-5' htmlFor='userEmail'>
          Email address*
        </Label>
        <Input
          type='email'
          id='userEmail'
          placeholder='Enter your email address'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isSubmitting}
        />
      </div>

      {/* Password */}
      <div className='w-full space-y-1'>
        <Label className='leading-5' htmlFor='password'>
          Password*
        </Label>
        <div className='relative'>
          <Input
            id='password'
            type={isVisible ? 'text' : 'password'}
            placeholder='••••••••••••••••'
            className='pr-9'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isSubmitting}
          />
          <Button
            variant='ghost'
            size='icon'
            type='button'
            onClick={() => setIsVisible(prevState => !prevState)}
            className='text-muted-foreground focus-visible:ring-ring/50 absolute inset-y-0 right-0 rounded-l-none hover:bg-transparent'
          >
            {isVisible ? <EyeOffIcon /> : <EyeIcon />}
            <span className='sr-only'>{isVisible ? 'Hide password' : 'Show password'}</span>
          </Button>
        </div>
      </div>

      {/* Remember Me and Forgot Password */}
      <div className='flex items-center justify-between gap-y-2'>
        <div className='flex items-center gap-3'>
          <Checkbox id='rememberMe' className='size-6' />
          <Label htmlFor='rememberMe'> Remember Me</Label>
        </div>

        <Link href='/forgot-password' className='hover:underline'>
          Forgot Password?
        </Link>
      </div>

      <PrimaryFlowButton className='w-full *:w-full [&>button]:after:-inset-55' type='submit' disabled={isSubmitting}>
        {isSubmitting ? <><Loader2 className='mr-2 size-4 animate-spin' />Signing in...</> : 'Login to flow'}
      </PrimaryFlowButton>
    </form>
  )
}

export default LoginForm
