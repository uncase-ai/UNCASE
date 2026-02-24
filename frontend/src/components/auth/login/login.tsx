import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

import Logo from '@/components/logo'
import LoginForm from '@/components/auth/login/login-form'
import DemoQuickButton from '@/components/auth/login/demo-quick-button'

const Login = () => {
  return (
    <div className='flex flex-col gap-6'>
      <Link href='/'>
        <Logo />
      </Link>

      <div>
        <h1 className='mb-3 text-2xl font-semibold md:text-3xl lg:text-4xl'>Welcome Back 👋</h1>
        <p className='text-muted-foreground'>Lets get started with your 30 days free trial</p>
      </div>

      {/* Quick Login Buttons */}
      <div className='flex flex-wrap gap-3'>
        <Button variant='outline' className='grow' asChild>
          <Link href='#'>Login with Google</Link>
        </Button>
        <Button variant='outline' className='grow' asChild>
          <Link href='#'>Login with Facebook</Link>
        </Button>
      </div>

      <div className='flex items-center gap-4'>
        <Separator className='flex-1' />
        <p>Or</p>
        <Separator className='flex-1' />
      </div>

      <div className='space-y-6'>
        {/* Form */}
        <LoginForm />

        <div className='flex items-center gap-4'>
          <Separator className='flex-1' />
          <p className='text-xs text-muted-foreground whitespace-nowrap'>or explore without signing in</p>
          <Separator className='flex-1' />
        </div>

        <DemoQuickButton />

        <p className='text-muted-foreground text-center'>
          Don&apos;t have an account yet?{' '}
          <Link href='/register' className='text-foreground hover:underline'>
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login
