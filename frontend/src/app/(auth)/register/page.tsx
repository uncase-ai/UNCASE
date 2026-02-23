import type { Metadata } from 'next'

import Register from '@/components/auth/register/register'

export const metadata: Metadata = {
  title: 'Register',
  robots: 'noindex,nofollow',
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_APP_URL}/register`
  }
}

const RegisterPage = () => {
  return <Register />
}

export default RegisterPage
