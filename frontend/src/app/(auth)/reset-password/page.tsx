import type { Metadata } from 'next'

import ResetPassword from '@/components/auth/reset-password/reset-password'

export const metadata: Metadata = {
  title: 'Reset Password',
  robots: 'noindex,nofollow',
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_APP_URL}/reset-password`
  }
}

const ResetPasswordPage = () => {
  return <ResetPassword />
}

export default ResetPasswordPage
