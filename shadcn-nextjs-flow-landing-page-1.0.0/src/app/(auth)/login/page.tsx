import type { Metadata } from 'next'

import Login from '@/components/auth/login/login'

export const metadata: Metadata = {
  title: 'Login',
  robots: 'noindex,nofollow',
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_APP_URL}/login`
  }
}

const LoginPage = () => {
  return <Login />
}

export default LoginPage
