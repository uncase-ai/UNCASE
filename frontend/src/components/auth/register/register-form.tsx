'use client'

import { useState } from 'react'

import { useRouter } from 'next/navigation'
import { EyeIcon, EyeOffIcon, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

import { register, storeTokens } from '@/lib/api/auth'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { PrimaryFlowButton } from '@/components/ui/flow-button'

const RegisterForm = () => {
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] = useState(false)
  const [agreed, setAgreed] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error('Passwords do not match')

      return
    }

    if (!agreed) {
      toast.error('Please accept the privacy policy & terms')

      return
    }

    setIsSubmitting(true)
    const { data, error } = await register({ email, password, display_name: displayName })

    setIsSubmitting(false)

    if (error) {
      toast.error(error.message || 'Registration failed')

      return
    }

    if (data) {
      storeTokens(data.access_token, data.refresh_token)
      toast.success('Account created successfully')
      router.push('/dashboard')
    }
  }

  return (
    <form className='space-y-4' onSubmit={handleSubmit}>
      {/* Display Name */}
      <div className='space-y-1'>
        <Label className='leading-5' htmlFor='displayName'>
          Display name*
        </Label>
        <Input
          type='text'
          id='displayName'
          placeholder='Enter your name'
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
          disabled={isSubmitting}
        />
      </div>

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
            type={isPasswordVisible ? 'text' : 'password'}
            placeholder='••••••••••••••••'
            className='pr-9'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            disabled={isSubmitting}
          />
          <Button
            variant='ghost'
            size='icon'
            type='button'
            onClick={() => setIsPasswordVisible(prevState => !prevState)}
            className='text-muted-foreground focus-visible:ring-ring/50 absolute inset-y-0 right-0 rounded-l-none hover:bg-transparent'
          >
            {isPasswordVisible ? <EyeOffIcon /> : <EyeIcon />}
            <span className='sr-only'>{isPasswordVisible ? 'Hide password' : 'Show password'}</span>
          </Button>
        </div>
      </div>

      {/* Confirm Password */}
      <div className='w-full space-y-1'>
        <Label className='leading-5' htmlFor='confirmPassword'>
          Confirm password*
        </Label>
        <div className='relative'>
          <Input
            id='confirmPassword'
            type={isConfirmPasswordVisible ? 'text' : 'password'}
            placeholder='••••••••••••••••'
            className='pr-9'
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            disabled={isSubmitting}
          />
          <Button
            variant='ghost'
            size='icon'
            type='button'
            onClick={() => setIsConfirmPasswordVisible(prevState => !prevState)}
            className='text-muted-foreground focus-visible:ring-ring/50 absolute inset-y-0 right-0 rounded-l-none hover:bg-transparent'
          >
            {isConfirmPasswordVisible ? <EyeOffIcon /> : <EyeIcon />}
            <span className='sr-only'>{isConfirmPasswordVisible ? 'Hide password' : 'Show password'}</span>
          </Button>
        </div>
      </div>

      {/* Privacy policy */}
      <div className='flex items-center gap-3'>
        <Checkbox
          id='agreeTerms'
          className='size-6'
          checked={agreed}
          onCheckedChange={(v) => setAgreed(v === true)}
        />
        <Label htmlFor='agreeTerms'>I agree to privacy policy & terms</Label>
      </div>

      <PrimaryFlowButton className='w-full *:w-full [&>button]:after:-inset-55' type='submit' disabled={isSubmitting}>
        {isSubmitting ? <><Loader2 className='mr-2 size-4 animate-spin' />Creating account...</> : 'Create Account'}
      </PrimaryFlowButton>
    </form>
  )
}

export default RegisterForm
