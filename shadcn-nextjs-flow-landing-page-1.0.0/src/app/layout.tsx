import type { ReactNode } from 'react'

import { Geist, Geist_Mono } from 'next/font/google'
import type { Metadata } from 'next'

import { ThemeProvider } from '@/components/theme-provider'
import { TooltipProvider } from '@/components/ui/tooltip'

import { cn } from '@/lib/utils'

import './globals.css'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin']
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin']
})

export const metadata: Metadata = {
  title: {
    template: '%s | UNCASE',
    default: 'UNCASE — Open Source Synthetic Data Framework for Regulated Industries'
  },
  description:
    'Generate high-quality synthetic conversational data for LoRA fine-tuning in privacy-sensitive industries. Healthcare, finance, legal, and more — without exposing real data.',
  robots: 'index,follow',
  keywords: [
    'synthetic data',
    'LoRA fine-tuning',
    'privacy AI',
    'open source framework',
    'regulated industries',
    'conversational AI',
    'GDPR compliant AI',
    'seed engineering'
  ],
  icons: {
    icon: [
      {
        url: '/favicon/favicon-16x16.png',
        sizes: '16x16',
        type: 'image/png'
      },
      {
        url: '/favicon/favicon-32x32.png',
        sizes: '32x32',
        type: 'image/png'
      },
      {
        url: '/favicon/favicon.ico',
        sizes: '48x48',
        type: 'image/x-icon'
      }
    ],
    apple: [
      {
        url: '/favicon/apple-touch-icon.png',
        sizes: '180x180',
        type: 'image/png'
      }
    ],
    other: [
      {
        url: '/favicon/android-chrome-192x192.png',
        rel: 'icon',
        sizes: '192x192',
        type: 'image/png'
      },
      {
        url: '/favicon/android-chrome-512x512.png',
        rel: 'icon',
        sizes: '512x512',
        type: 'image/png'
      }
    ]
  },
  metadataBase: new URL(`${process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'}`),
  openGraph: {
    title: {
      template: '%s | UNCASE',
      default: 'UNCASE — Open Source Synthetic Data Framework for Regulated Industries'
    },
    description:
      'Generate high-quality synthetic conversational data for LoRA fine-tuning in privacy-sensitive industries. Healthcare, finance, legal, and more — without exposing real data.',
    type: 'website',
    siteName: 'UNCASE',
    url: `${process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'}`,
    images: [
      {
        url: '/images/og-image.png',
        type: 'image/png',
        width: 1200,
        height: 630,
        alt: 'UNCASE — Synthetic Data Framework'
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: {
      template: '%s | UNCASE',
      default: 'UNCASE — Open Source Synthetic Data Framework for Regulated Industries'
    },
    description:
      'Generate high-quality synthetic conversational data for LoRA fine-tuning in privacy-sensitive industries. Healthcare, finance, legal, and more — without exposing real data.'
  }
}

const RootLayout = ({ children }: Readonly<{ children: ReactNode }>) => {
  return (
    <html
      lang='es'
      className={cn(geistSans.variable, geistMono.variable, 'flex min-h-full w-full scroll-smooth antialiased')}
      suppressHydrationWarning
    >
      <body className='flex min-h-full w-full flex-auto flex-col'>
        <ThemeProvider attribute='class' enableSystem={false} disableTransitionOnChange>
          <TooltipProvider>{children}</TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}

export default RootLayout
